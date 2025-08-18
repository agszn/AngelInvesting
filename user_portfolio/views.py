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

from unlisted_stock_marketplace.models import *

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import UserPortfolioSummary, BuyTransaction
from decimal import Decimal


from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render
from .models import UserPortfolioSummary, BuyTransactionOtherAdvisor

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Sum
from decimal import Decimal
from .models import UserPortfolioSummary, BuyTransactionOtherAdvisor

from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from user_portfolio.models import UserStockInvestmentSummary
from user_portfolio.utils import get_user_stock_context

@login_required
def profile_overview(request):
    user = request.user
    summaries = UserStockInvestmentSummary.objects.filter(user=user)

    def aggregate_by_stock_type(stock_type):
        filtered = summaries.filter(stock__stock_type=stock_type)
        return {
            "total_invested": sum((s.investment_amount for s in filtered), Decimal("0.00")),
            "market_value": sum((s.market_value for s in filtered), Decimal("0.00")),
            "overall_gain_loss": sum((s.overall_gain_loss for s in filtered), Decimal("0.00")),
            "todays_gain_loss": sum((s.day_gain_loss for s in filtered), Decimal("0.00")),
        }

    # Aggregated summaries
    unlisted_summary = aggregate_by_stock_type("Unlisted")
    angel_summary = aggregate_by_stock_type("Angel")

    # Combined totals
    total_invested = unlisted_summary["total_invested"] + angel_summary["total_invested"]
    total_market_value = unlisted_summary["market_value"] + angel_summary["market_value"]
    total_gain_loss = unlisted_summary["overall_gain_loss"] + angel_summary["overall_gain_loss"]
    todays_gain = unlisted_summary["todays_gain_loss"] + angel_summary["todays_gain_loss"]

    def percent(numerator, denominator):
        return round((numerator / denominator * 100), 2) if denominator else 0

    context = {
        # Totals for top summary
        "total_invested": total_invested,
        "total_market_value": total_market_value,
        "total_gain_loss": total_gain_loss,
        "todays_gain": todays_gain,
        "overall_gain_loss_percent": percent(total_gain_loss, total_invested),
        "todays_gain_percent": percent(todays_gain, total_invested),

        # Individual summaries for breakdown rows
        "unlisted_summary": unlisted_summary,
        "unlisted_overall_percent": percent(unlisted_summary["overall_gain_loss"], unlisted_summary["total_invested"]),
        "unlisted_today_percent": percent(unlisted_summary["todays_gain_loss"], unlisted_summary["total_invested"]),

        "angel_summary": angel_summary,
        "angel_overall_percent": percent(angel_summary["overall_gain_loss"], angel_summary["total_invested"]),
        "angel_today_percent": percent(angel_summary["todays_gain_loss"], angel_summary["total_invested"]),

        **get_user_stock_context(user, request),
    }

    return render(request, "portfolio/overview.html", context)

from django.contrib import messages

from django.db.models import Sum, F
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import UserPortfolioSummary, UserStockInvestmentSummary
from .utils import get_user_stock_context
from decimal import Decimal

from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

from user_portfolio.models import UserPortfolioSummary, BuyTransactionOtherAdvisor
from user_portfolio.utils import get_user_stock_context

from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

from user_portfolio.models import UserPortfolioSummary, BuyTransactionOtherAdvisor
from user_portfolio.utils import get_user_stock_context

from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from user_portfolio.models import UserStockInvestmentSummary
from user_portfolio.utils import get_user_stock_context

from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from user_portfolio.models import UserStockInvestmentSummary

from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from user_portfolio.models import UserStockInvestmentSummary

@login_required
def unlisted_view(request):
    user = request.user
    unlisted_all = UserStockInvestmentSummary.objects.filter(user=user, stock__stock_type="Unlisted")

    # Split based on is_other_advisor flag
    thangiv_qs = unlisted_all.filter(is_other_advisor=False)
    other_qs = unlisted_all.filter(is_other_advisor=True)

    def get_summary(qs):
        return {
            "total_invested": sum((s.investment_amount for s in qs), Decimal("0.00")),
            "total_market_value": sum((s.market_value for s in qs), Decimal("0.00")),
            "overall_gain_loss": sum((s.overall_gain_loss for s in qs), Decimal("0.00")),
            "todays_gain_loss": sum((s.day_gain_loss for s in qs), Decimal("0.00")),
        }

    thangiv_summary = get_summary(thangiv_qs)
    other_summary = get_summary(other_qs)

    # Combine for top box
    total_invested = thangiv_summary["total_invested"] + other_summary["total_invested"]
    total_market_value = thangiv_summary["total_market_value"] + other_summary["total_market_value"]
    total_gain_loss = thangiv_summary["overall_gain_loss"] + other_summary["overall_gain_loss"]
    todays_gain_loss = thangiv_summary["todays_gain_loss"] + other_summary["todays_gain_loss"]

    def percent(numerator, denominator):
        return round((numerator / denominator * 100), 2) if denominator else 0

    context = {
        # Top summary box
        "total_invested": total_invested,
        "total_market_value": total_market_value,
        "total_gain_loss": total_gain_loss,
        "todays_gain": todays_gain_loss,
        "overall_gain_loss_percent": percent(total_gain_loss, total_invested),
        "todays_gain_percent": percent(todays_gain_loss, total_invested),

        # Thangiv (non-other)
        "portfolio_summary": thangiv_summary,
        "unlisted_overall_percent": percent(thangiv_summary["overall_gain_loss"], thangiv_summary["total_invested"]),
        "unlisted_today_percent": percent(thangiv_summary["todays_gain_loss"], thangiv_summary["total_invested"]),

        # Other
        "advisor_summary": other_summary,
        "advisor_overall_percent": percent(other_summary["overall_gain_loss"], other_summary["total_invested"]),
        "advisor_today_percent": percent(other_summary["todays_gain_loss"], other_summary["total_invested"]),

        **get_user_stock_context(user, request),
    }

    return render(request, 'portfolio/unlistedOverview.html', context)

@login_required
def angel_invest(request):
    user = request.user
    stock_context = get_user_stock_context(user, request)
    
    return render(request, 'portfolio/angelOverview.html',{ **stock_context})

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import *
from .utils import update_user_holdings

from django.core.paginator import Paginator
from django.db.models import Q
from site_Manager.models import Advisor, Broker
from django.utils.timezone import make_aware
from datetime import datetime, timezone
from user_portfolio.models import UserStockInvestmentSummary


#this is portfolio with other advisor in different table
# @login_required
# def portfolio_view(request):
#     user = request.user

#     # 🔄 Update holdings summary
#     update_user_holdings(user)

#     # 📌 Initial queryset
#     holdings = UserStockInvestmentSummary.objects.filter(user=user).order_by('-id')

#     # 📌 GET filters
#     advisor_id = request.GET.get('advisor')
#     broker_id = request.GET.get('broker')
#     transaction_type = request.GET.get('type')  # buy or sell
#     search_query = request.GET.get('search')

#     # 📌 Apply filters to holdings
#     if advisor_id:
#         holdings = holdings.filter(advisor__id=advisor_id)
#     if broker_id:
#         holdings = holdings.filter(broker__id=broker_id)
#     if transaction_type == 'buy':
#         holdings = holdings.filter(total_buys__gt=0)
#     elif transaction_type == 'sell':
#         holdings = holdings.filter(total_sells__gt=0)
#     if search_query:
#         holdings = holdings.filter(stock__company_name__icontains=search_query)

#     # 📌 Pagination
#     paginator = Paginator(holdings, 10)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)

#     # 📌 Filtered "Other Advisor" Sell Transactions
#     other_sells = SellTransaction.objects.filter(
#         user=user,
#         status='completed',
#         advisor__advisor_type='Other'
#     ).select_related('stock', 'advisor', 'broker').order_by('-timestamp')

#     if advisor_id:
#         holdings = holdings.filter(advisor__id=advisor_id)
#     if broker_id:
#         holdings = holdings.filter(broker__id=broker_id)
#     if transaction_type == 'buy':
#         holdings = holdings.filter(buy_order_count__gt=0)  # ✅ FIXED
#     elif transaction_type == 'sell':
#         holdings = holdings.filter(sell_order_count__gt=0)  # ✅ FIXED
#     if search_query:
#         holdings = holdings.filter(stock__company_name__icontains=search_query)


#     # 📌 Dropdown options
#     advisors = Advisor.objects.all()
#     brokers = Broker.objects.all()
#     selected_advisor = Advisor.objects.filter(id=advisor_id).first() if advisor_id else None
#     selected_broker = Broker.objects.filter(id=broker_id).first() if broker_id else None

#     # 📌 Additional context (if any custom logic)
#     stock_context = get_user_stock_context(user, request)

#     # ✅ Final render
#     return render(request, 'portfolio/PortfolioList.html', {
#         'holdings': page_obj,
#         'advisors': advisors,
#         'brokers': brokers,
#         'selected_advisor': selected_advisor,
#         'selected_broker': selected_broker,
#         'current_filters': {
#             'advisor': advisor_id,
#             'broker': broker_id,
#             'type': transaction_type,
#             'search': search_query,
#         },
#         'page_obj': page_obj,
#         'other_sells': other_sells,  # 👈 Included in template context
#         **stock_context
#     })
@login_required
def portfolio_view(request):
    user = request.user

    update_user_holdings(user)
    holdings = UserStockInvestmentSummary.objects.filter(user=user).order_by('-id')

    advisor_id = request.GET.get('advisor')
    broker_id = request.GET.get('broker')
    transaction_type = request.GET.get('type')
    search_query = request.GET.get('search')

    if advisor_id:
        holdings = holdings.filter(advisor__id=advisor_id)
    if broker_id:
        holdings = holdings.filter(broker__id=broker_id)
    if transaction_type == 'buy':
        holdings = holdings.filter(buy_order_count__gt=0)
    elif transaction_type == 'sell':
        holdings = holdings.filter(sell_order_count__gt=0)
    if search_query:
        holdings = holdings.filter(stock__company_name__icontains=search_query)

    paginator = Paginator(holdings, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    advisors = Advisor.objects.all()
    brokers = Broker.objects.all()
    selected_advisor = Advisor.objects.filter(id=advisor_id).first() if advisor_id else None
    selected_broker = Broker.objects.filter(id=broker_id).first() if broker_id else None

    stock_context = get_user_stock_context(user, request)

    context = {
        'holdings': page_obj,
        'advisors': advisors,
        'brokers': brokers,
        'selected_advisor': selected_advisor,
        'selected_broker': selected_broker,
        'current_filters': {
            'advisor': advisor_id,
            'broker': broker_id,
            'type': transaction_type,
            'search': search_query,
        },
        'page_obj': page_obj,
        **stock_context
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'portfolio/includes/portfolio_table.html', context)

    return render(request, 'portfolio/PortfolioList.html', context)


from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render
from user_portfolio.models import BuyTransaction, BuyTransactionOtherAdvisor
from user_portfolio.utils import get_user_stock_context  # Assuming this exists

from itertools import chain
from operator import attrgetter
from django.utils.timezone import make_aware

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.paginator import Paginator
from itertools import chain
from operator import attrgetter
from .models import BuyTransaction, BuyTransactionOtherAdvisor, Advisor, Broker

@login_required
def buy_orders(request):
    user = request.user

    # GET filters
    search_query = request.GET.get('search', '')
    advisor_id = request.GET.get('advisor')
    broker_id = request.GET.get('broker')
    transaction_type = request.GET.get('type')  # optional if needed

    # Fetch base buy orders
    buy_orders = BuyTransaction.objects.filter(user=user).select_related('stock', 'advisor', 'broker')
    buy_orders_other = BuyTransactionOtherAdvisor.objects.filter(user=user).select_related('stock', 'advisor', 'broker')

    # Apply filters
    if advisor_id:
        buy_orders = buy_orders.filter(advisor__id=advisor_id)
        buy_orders_other = buy_orders_other.filter(advisor__id=advisor_id)

    if broker_id:
        buy_orders = buy_orders.filter(broker__id=broker_id)
        buy_orders_other = buy_orders_other.filter(broker__id=broker_id)

    if transaction_type == 'buy':  # Optional use case
        pass  # You can add specific filtering if needed
    elif transaction_type == 'other':
        pass

    if search_query:
        buy_orders = buy_orders.filter(stock__company_name__icontains=search_query)
        buy_orders_other = buy_orders_other.filter(stock__company_name__icontains=search_query)

    # Mark whether from other advisor
    for order in buy_orders:
        order.is_other = False
    for order in buy_orders_other:
        order.is_other = True

    # Combine and sort
    combined_orders = sorted(
        chain(buy_orders, buy_orders_other),
        key=attrgetter('timestamp'),
        reverse=True
    )

    # Pagination
    paginator = Paginator(combined_orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Filter selections
    advisors = Advisor.objects.all()
    brokers = Broker.objects.all()
    selected_advisor = Advisor.objects.filter(id=advisor_id).first() if advisor_id else None
    selected_broker = Broker.objects.filter(id=broker_id).first() if broker_id else None

    stock_context = get_user_stock_context(user, request)

    context = {
        'page_obj': page_obj,
        'advisors': advisors,
        'brokers': brokers,
        'selected_advisor': selected_advisor,
        'selected_broker': selected_broker,
        'current_filters': {
            'advisor': advisor_id,
            'broker': broker_id,
            'type': transaction_type,
            'search': search_query,
        },
        **stock_context,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'portfolio/includes/buy_orders_table.html', context)

    return render(request, 'portfolio/BuyOrdersList.html', context)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.paginator import Paginator
from .models import SellTransaction, Advisor, Broker
from .utils import get_user_stock_context  # assuming you have this

@login_required
def sell_orders(request):
    user = request.user
    search_query = request.GET.get('search', '')
    advisor_id = request.GET.get('advisor')
    broker_id = request.GET.get('broker')
    transaction_type = request.GET.get('type')  # Optional: for extensibility

    # Fetch base queryset
    sell_orders_qs = SellTransaction.objects.filter(user=user).select_related('stock', 'advisor', 'broker')

    # Apply filters
    if advisor_id:
        sell_orders_qs = sell_orders_qs.filter(advisor__id=advisor_id)

    if broker_id:
        sell_orders_qs = sell_orders_qs.filter(broker__id=broker_id)

    if search_query:
        sell_orders_qs = sell_orders_qs.filter(stock__company_name__icontains=search_query)

    # Order by timestamp
    sell_orders_qs = sell_orders_qs.order_by('-timestamp')

    # Pagination
    paginator = Paginator(sell_orders_qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Dropdown data
    advisors = Advisor.objects.all()
    brokers = Broker.objects.all()
    selected_advisor = Advisor.objects.filter(id=advisor_id).first() if advisor_id else None
    selected_broker = Broker.objects.filter(id=broker_id).first() if broker_id else None

    # Extra context
    stock_context = get_user_stock_context(user, request)

    context = {
        'page_obj': page_obj,
        'advisors': advisors,
        'brokers': brokers,
        'selected_advisor': selected_advisor,
        'selected_broker': selected_broker,
        'current_filters': {
            'advisor': advisor_id,
            'broker': broker_id,
            'type': transaction_type,
            'search': search_query,
        },
        **stock_context,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'portfolio/includes/sell_orders_table.html', context)

    return render(request, 'portfolio/SellOrdersList.html', context)




# testing

# 
# 
# ---------------------------------------------------------------------
# ------------------ Buy stocks -------------
# ------------------------------------------------------------------
# 
# 
# user_portfolio/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import BuyTransaction, SellTransaction
from unlisted_stock_marketplace.models import *
from site_Manager.models import *
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from decimal import Decimal

from .models import BuyTransaction
from site_Manager.models import Broker, Advisor
from unlisted_stock_marketplace.models import StockData

from django.http import JsonResponse


def load_advisors_brokers(request):
    advisors = list(Advisor.objects.values('id', 'advisor_type'))
    brokers = list(Broker.objects.values('id', 'name'))
    return JsonResponse({
        'advisors': advisors,
        'brokers': brokers
    })


from .models import BuyTransaction, BuyTransactionOtherAdvisor
from user_auth.decorators import require_complete_profile

@require_POST
@login_required
@require_complete_profile
def buy_stock(request, stock_id):
    stock = get_object_or_404(StockData, id=stock_id)
    advisor_id = request.POST.get('advisor')
    broker = get_object_or_404(Broker, id=request.POST.get('broker'))
    quantity = int(request.POST.get('quantity'))
    price_per_share = Decimal(request.POST.get('price_per_share'))
    order_type = request.POST.get('order_type')

    # ✅ Force correct price for market orders
    if order_type == "market":
        price_per_share = stock.share_price  # use DB's latest price
    else:
        price_str = request.POST.get('price_per_share')
        if not price_str:
            messages.error(request, "Please enter a price per share for limit orders.")
            return redirect(request.META.get('HTTP_REFERER', '/'))
        try:
            price_per_share = Decimal(price_str)
        except (TypeError, ValueError, InvalidOperation):
            messages.error(request, "Invalid price per share.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

    total_amount = quantity * price_per_share

    advisor = get_object_or_404(Advisor, id=advisor_id)

    if advisor.advisor_type.lower() != 'other':
        BuyTransaction.objects.create(
            user=request.user,
            stock=stock,
            advisor=advisor,
            broker=broker,
            quantity=quantity,
            price_per_share=price_per_share,
            order_type=order_type,
            total_amount=total_amount,
        )
        messages.success(request, f"Buy order placed for {stock.company_name} with Advisor '{advisor.advisor_type}'.")
    else:
        BuyTransactionOtherAdvisor.objects.create(
            user=request.user,
            stock=stock,
            advisor=advisor,
            broker=broker,
            quantity=quantity,
            price_per_share=price_per_share,
            order_type=order_type,
            total_amount=total_amount,
        )
        messages.success(request, f"Buy order placed for {stock.company_name} with Advisor 'Other'.")

    return redirect(request.META.get('HTTP_REFERER', '/'))


# 
# 
# ---------------------------------------------------------------------
# ------------------ Sell stocks -------------
# ------------------------------------------------------------------
# 
# 
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from .models import StockData, SellTransaction, Advisor, Broker
from decimal import Decimal, InvalidOperation

from decimal import Decimal, InvalidOperation
from .models import SellTransaction, SellTransactionOtherAdvisor, UserStockInvestmentSummary

from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from decimal import Decimal, InvalidOperation
from .models import StockData, SellTransaction, Advisor, Broker, UserStockInvestmentSummary

@require_POST
@login_required
def sell_stock(request, stock_id):
    stock = get_object_or_404(StockData, id=stock_id)

    try:
        advisor_id = request.POST.get('advisor')
        broker_id = request.POST.get('broker')
        quantity = int(request.POST.get('quantity'))

        # Parse selling price
        selling_price_str = request.POST.get('selling_price')
        if selling_price_str:
            try:
                selling_price = Decimal(selling_price_str)
            except InvalidOperation:
                raise ValueError("Invalid selling price format.")
        elif stock.share_price is not None:
            selling_price = stock.share_price
        else:
            raise ValueError("Selling price is required and stock price is not available.")

        advisor = get_object_or_404(Advisor, id=advisor_id)
        broker = get_object_or_404(Broker, id=broker_id)

        # Only check availability if advisor is NOT 'other'
        if advisor.advisor_type.lower() != 'other':
            try:
                summary = UserStockInvestmentSummary.objects.get(user=request.user, stock=stock)
                held_qty = summary.quantity_held

                # Calculate pending sell quantity
                pending_qty = SellTransaction.objects.filter(
                    user=request.user,
                    stock=stock,
                    status__in=['processing', 'on_hold']
                ).aggregate(total=models.Sum('quantity'))['total'] or 0

                available_qty = held_qty - pending_qty

                if quantity > available_qty:
                    messages.error(request, f"You only have {available_qty} shares available for selling. Cannot sell {quantity} shares.")
                    return redirect(request.META.get('HTTP_REFERER', '/'))

            except UserStockInvestmentSummary.DoesNotExist:
                messages.error(request, f"You do not hold any shares of {stock.company_name}. Cannot sell.")
                return redirect(request.META.get('HTTP_REFERER', '/'))

        # Save transaction
        SellTransaction.objects.create(
            user=request.user,
            advisor=advisor,
            broker=broker,
            stock=stock,
            quantity=quantity,
            selling_price=selling_price,
        )

        if advisor.advisor_type.lower() == 'other':
            messages.success(request, f"Sell order placed for {stock.company_name} with Advisor 'Other'")
        else:
            messages.success(request, f"Sell order placed for {stock.company_name} ({quantity} shares at ₹{selling_price})")

    except Exception as e:
        import traceback
        traceback.print_exc()
        messages.error(request, f"Failed to place sell order: {str(e)}")

    return redirect(request.META.get('HTTP_REFERER', '/'))

from Share_Transfer.models import DealLetterRecord

# view_deal_letters



from django.db.models import Q

@login_required
def view_deal_letters(request):
    user = request.user
    stock_context = get_user_stock_context(user, request)

    # Filters
    deal_type = request.GET.get('deal_type')
    sort_by = request.GET.get('sort_by', '-generated_on')  # default sort

    records = DealLetterRecord.objects.filter(user=user)

    if deal_type:
        records = records.filter(deal_type=deal_type)

    # Apply sorting
    allowed_sorts = {
        'date_asc': '-generated_on',
        'date_desc': 'generated_on',
        'amount_asc': 'total_amount',
        'amount_desc': '-total_amount'
    }
    records = records.order_by(allowed_sorts.get(sort_by, '-generated_on'))

    return render(request, 'portfolio/view_deal_letters.html', {
        'records': records,
        'selected_deal_type': deal_type,
        'selected_sort': sort_by,
        **stock_context
    })



# sidebar live filter
from django.http import JsonResponse
from django.template.loader import render_to_string
from user_portfolio.utils import get_user_stock_context

def ajax_filtered_stocks(request):
    context = get_user_stock_context(request.user, request)
    html = render_to_string("accounts/includes/sidebar_stock_list.html", context, request=request)
    return JsonResponse({"html": html})
