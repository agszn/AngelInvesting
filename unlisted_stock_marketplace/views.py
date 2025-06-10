from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from django.views.decorators.csrf import csrf_exempt

from django.utils.timezone import localtime
from django.utils import timezone

from decimal import Decimal
from django.db.models import Q

from django.core.paginator import Paginator
from django.contrib import messages
from django.http import JsonResponse

import json
from collections import defaultdict

from .forms import *
from .models import *
from .utils import *
from .views import *

# 
# 
# ---------------------------------------------------------------------
# ------------------ stock list Unlisted index.html ------------------------
# -------------------------------------------------------------------
# 
# 

def stock_list(request):
    query = request.GET.get('q', '')
    stocks = StockData.objects.filter(company_name__icontains=query) if query else StockData.objects.all()
    return render(request, 'stocks/stock_list.html', {'stocks': stocks, 'query': query})

from .models import CustomFieldDefinition, CustomFieldValue, TableHeader

# balance Sheet chash flow etc
def get_sheet_data(stock_id, model_type):
    field_definitions = CustomFieldDefinition.objects.filter(stock_id=stock_id, model_type=model_type)
    field_values = CustomFieldValue.objects.filter(field_definition__in=field_definitions)
    headers = TableHeader.objects.filter(custom_field_values__in=field_values).distinct().order_by('order')
    particulars_header = headers.filter(title__iexact="PARTICULARS").first()
    data_headers = headers.exclude(id=particulars_header.id if particulars_header else None)
    
    parent_rows = field_values.filter(parent_field_value__isnull=True)
    child_values = field_values.filter(parent_field_value__isnull=False)

    table_rows = []
    for parent in parent_rows:
        row = {
            'name': parent.name,
            'text_style': parent.text_style,
            'values': {},
        }
        if parent.table_header:
            row['values'][parent.table_header.id] = parent.display_value()
        children = child_values.filter(parent_field_value=parent)
        for child in children:
            if child.table_header:
                row['values'][child.table_header.id] = child.display_value()
        table_rows.append(row)

    return {
        'headers': data_headers,
        'particulars_header': particulars_header,
        'rows': table_rows
    }

# Stock Detail - onclick on stock name
def stock_detail(request, stock_id):
    stock = get_object_or_404(StockData, id=stock_id)
    price_history = StockHistory.objects.filter(stock=stock).order_by('timestamp')
    

    if not price_history.exists():
        print("❌ No stock history found for this stock.")

    stock_dates = [
        localtime(timestamp).strftime('%Y-%m-%d')
        for timestamp in price_history.values_list('timestamp', flat=True)
        if timestamp is not None
    ]
    
    stock_prices = [float(price) for price in price_history.values_list('price', flat=True)]

    # 
    # 
    # 
    # Fetching related directors
    # 
    # 
    directors = stock.directors.all()

    # 
    # 
    # 
    # Fetch the most searched stocks
    # 
    # 
    stock_searched = StockData.objects.order_by('-number_of_times_searched').first()

    if stock_searched and stock_searched.share_price is not None and stock_searched.ltp is not None:
        percentage_diff = ((stock_searched.ltp - stock_searched.share_price) / stock_searched.share_price) * 100
    else:
        percentage_diff = 0
    # 
    # 
    # 



    # 
    # 
    # 
    # 
    # report
    # 
    # 
    # 
    reports = Report.objects.filter(stock=stock)  
    # 
    # 
    # 
    

    # 
    # 
    # 
    # 
    #  company subsidiary and associate    
    relations = stock.related_companies.all()
    # 
    # 
    # 
    # 

    # 
    # 
    # 
    # 
    # PrincipalBusinessActivity
    # 
    # 
    # principalBusinessActivity = StockData.PrincipalBusinessActivity.all()
    principal_activities = stock.business_activities.all()
    # 
    # 
    # 
    

    # 
    # 
    # 
    stock_holder = get_object_or_404(StockData, pk=stock_id)
    shareholdings = stock_holder.shareholdings.all()  # uses related_name
    # 
    # 
    # 
    

    # company FAQ
    faqs = stock.faqs.all()
    # 
    # 
    # 
    

    # 
    # 
    # 
    # Fetching multiple stocks to display in the cards section
    all_stocks = StockData.objects.all()  # Fetch all stocks or customize this query as needed
    # 
    # 
    # 

    context = {
        'stock': stock,
        'directors': directors,
        'stock_searched': stock_searched,
        'percentage_diff': percentage_diff,
        'stock_dates': json.dumps(stock_dates),
        'stock_prices': json.dumps(stock_prices),

        # balance sheet, cashflow, and other tables
        'balance_sheet_data': get_sheet_data(stock.id, 'BalanceSheet'),
        'pl_account_data': get_sheet_data(stock.id, 'PLAccount'),
        'cash_flow_data': get_sheet_data(stock.id, 'CashFlow'),
        'financial_ratios_data': get_sheet_data(stock.id, 'FinancialRatios'),
        'dividend_data': get_sheet_data(stock.id, 'Dividend'),
        # end balance sheet, cashflow, and other tables
        
            
        'reports': reports,

        'principalBusinessActivity':principal_activities,

        'relations': relations,

        'shareholdings': shareholdings,

        'faqs': faqs,

        'all_stocks': all_stocks, 

    }
    return render(request, 'stocks/stock_detail.html', context)


# stock list in table list format  other page/ blue page list DO not delete
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.paginator import Paginator
from .models import StockData, StockHistory
import json

from django.core.paginator import Paginator
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
import json
from .models import StockData, StockHistory

@login_required
def StockListingTableFormat(request):
    stocks = StockData.objects.all()

    # Search Filter
    search_query = request.GET.get('search', '')
    if search_query:
        stocks = stocks.filter(company_name__icontains=search_query)

    # Sector Filter (optional future use)
    selected_sector = request.GET.get('sector', '')
    if selected_sector:
        stocks = stocks.filter(sector=selected_sector)

    # Entries per page
    try:
        per_page = int(request.GET.get('entries', 10))
    except ValueError:
        per_page = 10

    # Pagination
    paginator = Paginator(stocks, per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Chart data mapping
    stock_history_data = {
        stock.id: list(StockHistory.objects.filter(stock=stock).order_by('-timestamp')[:30].values('timestamp', 'price'))
        for stock in page_obj
    }

    return render(request, 'stocks/StockListTable.html', {
        'page_obj': page_obj,
        'stock_history_data': json.dumps(stock_history_data, default=str),
        'search_query': search_query,
        'selected_sector': selected_sector,
        'per_page': per_page,
        'total_count': paginator.count,
        'start_index': page_obj.start_index(),
        'end_index': page_obj.end_index(),
    })



# 
# 
# ---------------------------------------------------------------------
# ------------------ Wishlist -------------
# ------------------------------------------------------------------
# 
# 

def get_next_wishlist_group_name(request):
    user = request.user
    base_name = "List"
    groups = WishlistGroup.objects.filter(user=user).order_by("name")
    group_index = 1

    for group in groups:
        if group.wishlist_items.count() < 20:
            return JsonResponse({'group_name': group.name})
        group_index += 1

    # No existing group with space, create a new one
    group_name = f"{base_name} {group_index}"
    WishlistGroup.objects.create(user=user, name=group_name)
    return JsonResponse({'group_name': group_name})


@require_POST
@login_required
def add_to_wishlist(request):
    stock_id = request.POST.get("stock_id")
    group_name = request.POST.get("custom_list_name")

    if not stock_id or not group_name:
        return JsonResponse({"error": "Missing stock_id or group name"}, status=400)

    stock = get_object_or_404(StockData, id=stock_id)
    group, _ = WishlistGroup.objects.get_or_create(user=request.user, name=group_name)

    Wishlist.objects.get_or_create(user=request.user, stock=stock, defaults={'group': group})
    return redirect('unlisted_stock_marketplace:wish_list')


@login_required
def wish_list(request):
    search_query = request.GET.get('search', '')
    selected_group_id = request.GET.get('group')
    show_all_unlisted = request.GET.get('unlisted') == '1'
    show_all_angel = request.GET.get('angel') == '1'

    groups = WishlistGroup.objects.filter(user=request.user).order_by('created_on')
    stock_list = []
    wishlist_data = []

    # If viewing Unlisted or Angel stocks directly
    if show_all_unlisted or show_all_angel:
        stock_type = "Unlisted" if show_all_unlisted else "Angel"
        stocks = StockData.objects.filter(stock_type=stock_type)

        if search_query:
            stocks = stocks.filter(
                Q(company_name__icontains=search_query) |
                Q(scrip_name__icontains=search_query)
            )

        stock_list = stocks  # Send queryset directly to the template

    else:
        # Viewing wishlist (with optional group filter)
        if selected_group_id:
            selected_group = get_object_or_404(WishlistGroup, id=selected_group_id, user=request.user)
            wishlist_items = Wishlist.objects.filter(user=request.user, group=selected_group).select_related('stock')
        else:
            wishlist_items = Wishlist.objects.filter(user=request.user).select_related('stock')

        if search_query:
            wishlist_items = wishlist_items.filter(
                Q(stock__company_name__icontains=search_query) |
                Q(stock__scrip_name__icontains=search_query)
            )

        wishlist_data = wishlist_items

    return render(request, 'accounts/profile.html', {
        'groups': groups,
        'wishlist_data': wishlist_data,
        'stock_list': stock_list,
        'search_query': search_query,
        'show_all_unlisted': show_all_unlisted,
        'show_all_angel': show_all_angel,
    })


# add to wishlist from group 1,2,
@login_required
def add_to_group(request, stock_id):
    stock = get_object_or_404(StockData, id=stock_id)
    group = WishlistGroup.objects.filter(user=request.user).order_by('-created_on').first()

    if group:
        exists = Wishlist.objects.filter(user=request.user, stock=stock, group=group).exists()
        if exists:
            messages.warning(request, f"{stock.company_name} is already added in Group {group.name}.")
        else:
            Wishlist.objects.create(user=request.user, stock=stock, group=group)
            messages.success(request, f"{stock.company_name} added to Group {group.name} successfully.")
    
    return redirect(request.META.get('HTTP_REFERER', 'accounts:profile'))

@login_required
def remove_from_group(request, wishlist_id):
    wishlist_item = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)
    wishlist_item.delete()
    return redirect(request.META.get('HTTP_REFERER', 'accounts:profile'))



