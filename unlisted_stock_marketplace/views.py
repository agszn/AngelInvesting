# unlisted_stock_marketplace/views.py
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

from django.http import JsonResponse
from .models import StockData

def stock_suggestions(request):
    query = request.GET.get('q', '')
    if query:
        stocks = StockData.objects.filter(company_name__icontains=query)[:10]
        results = [{'id': stock.id, 'company_name': stock.company_name} for stock in stocks]
    else:
        results = []
    return JsonResponse(results, safe=False)


def stock_list(request):
    query = request.GET.get('q', '')
    stocks = StockData.objects.filter(company_name__icontains=query) if query else StockData.objects.all()
    return render(request, 'stocks/stock_list.html', {'stocks': stocks, 'query': query})

def all_stocks_ajax(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        stocks = StockData.objects.all()
        data = []

        for stock in stocks:
            data.append({
                'id': stock.id,
                'company_name': stock.company_name,
                'logo': request.build_absolute_uri(stock.logo.url) if stock.logo else '',
            })

        return JsonResponse(data, safe=False)
    return JsonResponse({'error': 'Invalid request'}, status=400)

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

    # stock_dates = [
    #     localtime(timestamp).strftime('%Y-%m-%d')
    #     for timestamp in price_history.values_list('timestamp', flat=True)
    #     if timestamp is not None
    # ]
    stock_dates = [
        ts.isoformat()
        for ts in price_history.values_list('timestamp', flat=True)
        if ts is not None
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
        'pl_account_data': get_sheet_data(stock.id, 'ProfitLossStatement'),
        'cash_flow_data': get_sheet_data(stock.id, 'CashFlow'),
        'financial_ratios_data': get_sheet_data(stock.id, 'FinancialRatios'),
        'dividend_data': get_sheet_data(stock.id, 'DividendHistory'),
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

    return render(request, 'stocks/stockListTable.html', {
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
# 
# ---------------------------------------------------------------------
# ------------------ Wishlist -------------
# ------------------------------------------------------------------
# 
# 



from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import WishlistGroup, Wishlist

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Count


@login_required
def get_next_wishlist_group_name(request):
    try:
        stock_id = request.GET.get('stock_id')
        if not stock_id:
            return JsonResponse({'error': 'Missing stock ID'}, status=400)

        stock = StockData.objects.get(id=stock_id)

        # Find group with < 20 items
        group = (
            WishlistGroup.objects.filter(user=request.user)
            .annotate(count=Count('wishlist_items'))
            .filter(count__lt=20)
            .order_by('created_on')
            .first()
        )

        if not group:
            group = WishlistGroup.objects.create(user=request.user)

        return JsonResponse({'group_name': group.name})

    except Exception as e:
        # Temporary debug output
        return JsonResponse({'error': str(e)}, status=500)



@require_POST
@login_required
def add_to_wishlist(request):
    stock_id = request.POST.get("stock_id")
    group_name = request.POST.get("custom_list_name")

    if not stock_id or not group_name:
        return JsonResponse({"error": "Missing stock_id or group name"}, status=400)

    stock = get_object_or_404(StockData, id=stock_id)
    group, _ = WishlistGroup.objects.get_or_create(user=request.user, name=group_name)

    wishlist, created = Wishlist.objects.get_or_create(user=request.user, stock=stock, defaults={'group': group})

    if not created:
        request.session['popup_message'] = f"{stock.company_name} already exists in {wishlist.group.name}"
    else:
        request.session['popup_message'] = f"{stock.company_name} added to {group.name}"

    return redirect('profile')

# @login_required
# def wish_list(request):
#     user = request.user
#     groups = WishlistGroup.objects.filter(user=user).prefetch_related('wishlist_items__stock')

#     show_all_unlisted = request.GET.get('unlisted') == '1'
#     show_all_angel = request.GET.get('angel') == '1'
#     group_id = request.GET.get('group')

#     search_query = request.GET.get('search', '').strip()

#     if group_id:
#         # Show only stocks in the selected group
#         selected_group = get_object_or_404(WishlistGroup, id=group_id, user=user)
#         stock_list = [item.stock for item in selected_group.wishlist_items.select_related('stock')]
#     else:
#         # Show unlisted stocks (default)
#         stock_list = StockData.objects.filter(category='unlisted')

#         # Filter search if needed
#         if search_query:
#             stock_list = stock_list.filter(
#                 Q(company_name__istartswith=search_query) |
#                 Q(scrip_name__istartswith=search_query)
#             )

#         # Show full list, annotate wishlist info
#         user_wishlist = Wishlist.objects.filter(user=user).select_related('group', 'stock')
#         wishlist_map = {
#             w.stock.id: w.group.name for w in user_wishlist
#         }

#         for stock in stock_list:
#             stock.in_group = stock.id in wishlist_map
#             stock.group_number = wishlist_map.get(stock.id, '')

#     popup_message = request.session.pop('popup_message', None)

#     return render(request, 'accounts/profile.html', {
#         'popup_message': popup_message,
#         'groups': groups,
#         'stock_list': stock_list,
#         'show_all_unlisted': show_all_unlisted,
#         'show_all_angel': show_all_angel,
#         'search_query': search_query,
#     })

# add to wishlist from group 1,2,
@login_required
def add_to_group(request, stock_id):
    if request.method == 'POST':
        stock = get_object_or_404(StockData, id=stock_id)
        user = request.user

        existing_entry = Wishlist.objects.filter(user=user, stock=stock).first()
        if existing_entry:
            return JsonResponse({'status': 'exists', 'stock_name': stock.company_name, 'group_name': existing_entry.group.name})

        # Try to find group with space
        groups = WishlistGroup.objects.filter(user=user).order_by('created_on')
        for group in groups:
            if group.wishlist_items.count() < 20:
                Wishlist.objects.create(user=user, stock=stock, group=group)
                return JsonResponse({'status': 'added', 'stock_name': stock.company_name, 'group_name': group.name})

        # No space, create a new group
        new_group = WishlistGroup.objects.create(user=user)
        Wishlist.objects.create(user=user, stock=stock, group=new_group)
        return JsonResponse({'status': 'added', 'stock_name': stock.company_name, 'group_name': new_group.name})

    return JsonResponse({'status': 'error'})

# unlisted_stock_marketplace/views.py
from django.views.decorators.http import require_POST

@require_POST
@login_required
def remove_from_group(request, wishlist_id):
    wishlist_item = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)
    wishlist_item.delete()
    return redirect(request.META.get('HTTP_REFERER', 'accounts:profile'))


