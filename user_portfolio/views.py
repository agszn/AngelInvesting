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

# @login_required
# def profile_overview(request):
#     user = request.user
#     summary = getattr(user, 'portfolio_summary', None)

#     # Group by advisor name for per-advisor summary
#     advisor_data = {}
#     completed_buys = BuyTransaction.objects.filter(user=user, status='completed')

#     for tx in completed_buys:
#         key = tx.advisor.advisor_type if tx.advisor else 'Other Advisor'
#         if key not in advisor_data:
#             advisor_data[key] = {
#                 'invested': Decimal('0'),
#                 'market_value': Decimal('0'),
#                 'today_gain': Decimal('0'),
#             }
#         advisor_data[key]['invested'] += tx.total_amount
#         if tx.stock.ltp:
#             advisor_data[key]['market_value'] += tx.quantity * tx.stock.ltp
#             advisor_data[key]['today_gain'] += (tx.stock.ltp - tx.stock.share_price) * tx.quantity

#     for advisor in advisor_data.values():
#         advisor['overall_gain'] = advisor['market_value'] - advisor['invested']
#         advisor['gain_percent'] = (
#             (advisor['overall_gain'] / advisor['invested']) * 100
#             if advisor['invested'] > 0 else 0
#         )
#         advisor['today_gain_percent'] = (
#             (advisor['today_gain'] / advisor['invested']) * 100
#             if advisor['invested'] > 0 else 0
#         )

#     context = {
#         'summary': summary,
#         'advisor_data': advisor_data,
#     }
#     return render(request, 'portfolio/overview.html', context)




from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render
from .models import UserPortfolioSummary, BuyTransactionOtherAdvisor

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Sum
from decimal import Decimal
from .models import UserPortfolioSummary, BuyTransactionOtherAdvisor


@login_required
def profile_overview(request):
    user = request.user

    # Fetch portfolio summary
    try:
        portfolio_summary = UserPortfolioSummary.objects.get(user=user)
    except UserPortfolioSummary.DoesNotExist:
        portfolio_summary = None

    # Aggregate advisor transactions
    advisor_transactions = BuyTransactionOtherAdvisor.objects.filter(user=user)
    advisor_summary = {
        "total_invested": sum((tx.invested_amount for tx in advisor_transactions), Decimal("0.00")),
        "market_value": sum((tx.market_value for tx in advisor_transactions), Decimal("0.00")),
        "overall_gain_loss": sum((tx.overall_gain_loss for tx in advisor_transactions), Decimal("0.00")),
        "todays_gain_loss": sum((tx.todays_gain_loss for tx in advisor_transactions), Decimal("0.00")),
    }

    # Calculate individual summary percentages
    unlisted_invested = portfolio_summary.total_invested if portfolio_summary else Decimal("0.00")
    unlisted_gain = portfolio_summary.overall_gain_loss if portfolio_summary else Decimal("0.00")
    unlisted_today_gain = portfolio_summary.todays_gain_loss if portfolio_summary else Decimal("0.00")

    advisor_invested = advisor_summary["total_invested"]
    advisor_gain = advisor_summary["overall_gain_loss"]
    advisor_today_gain = advisor_summary["todays_gain_loss"]

    # Total calculations
    total_invested = unlisted_invested + advisor_invested
    total_market_value = (portfolio_summary.total_market_value if portfolio_summary else Decimal("0.00")) + advisor_summary["market_value"]
    total_gain_loss = unlisted_gain + advisor_gain
    total_todays_gain = unlisted_today_gain + advisor_today_gain

    # Percentages
    def percent(numerator, denominator):
        return round((numerator / denominator * 100), 2) if denominator else 0

    stock_context = get_user_stock_context(user, request)

    context = {
        "portfolio_summary": portfolio_summary,
        "advisor_summary": advisor_summary,
        "total_invested": total_invested,
        "total_market_value": total_market_value,
        "total_gain_loss": total_gain_loss,
        "todays_gain": total_todays_gain,
        "overall_gain_loss_percent": percent(total_gain_loss, total_invested),
        "todays_gain_percent": percent(total_todays_gain, total_invested),
        "unlisted_overall_percent": percent(unlisted_gain, unlisted_invested),
        "unlisted_today_percent": percent(unlisted_today_gain, unlisted_invested),
        "advisor_overall_percent": percent(advisor_gain, advisor_invested),
        "advisor_today_percent": percent(advisor_today_gain, advisor_invested),
        **stock_context,
    }

    return render(request, 'portfolio/overview.html', context)

from django.contrib import messages

@login_required
def unlisted_view(request):
    try:
        user = request.user
        summary = UserPortfolioSummary.objects.get(user=request.user)
        stock_context = get_user_stock_context(user, request)
    except UserPortfolioSummary.DoesNotExist:
        messages.error(request, "No portfolio summary found. Please create one first.")
        return redirect('user_portfolio:profile_overview')  # or any safe fallback
    return render(request, 'portfolio/unlistedOverview.html', {'summary': summary, **stock_context})


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

@login_required
def portfolio_view(request):
    update_user_holdings(request.user)  # Refresh summary data

    holdings = UserStockInvestmentSummary.objects.filter(user=request.user)

    # Filters
    advisor_id = request.GET.get('advisor')
    broker_id = request.GET.get('broker')
    transaction_type = request.GET.get('type')  # buy or sell
    search_query = request.GET.get('search')

    if advisor_id:
        holdings = holdings.filter(advisor__id=advisor_id)
    if broker_id:
        holdings = holdings.filter(broker__id=broker_id)
    if transaction_type == 'buy':
        holdings = holdings.filter(total_buys__gt=0)
    elif transaction_type == 'sell':
        holdings = holdings.filter(total_sells__gt=0)
    if search_query:
        holdings = holdings.filter(stock__company_name__icontains=search_query)

    # Pagination
    paginator = Paginator(holdings, 10)  # 10 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # For dropdowns
    advisors = Advisor.objects.all()
    brokers = Broker.objects.all()

    user = request.user
    stock_context = get_user_stock_context(user, request)
    return render(request, 'portfolio/PortfolioList.html', {
        'holdings': page_obj,
        'advisors': advisors,
        'brokers': brokers,
        'current_filters': {
            'advisor': advisor_id,
            'broker': broker_id,
            'type': transaction_type,
            'search': search_query,
        },
        'page_obj': page_obj,
        **stock_context
    })

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render
from user_portfolio.models import BuyTransaction, BuyTransactionOtherAdvisor
from user_portfolio.utils import get_user_stock_context  # Assuming this exists
@login_required
def buy_orders(request):
    user = request.user
    search_query = request.GET.get('search', '')

    buy_orders = BuyTransaction.objects.filter(user=user).select_related('stock', 'advisor', 'broker').order_by('-timestamp')
    if search_query:
        buy_orders = buy_orders.filter(stock__company_name__icontains=search_query)

    paginator = Paginator(buy_orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Other advisor orders
    buy_orders_Advisor = BuyTransactionOtherAdvisor.objects.filter(user=user).select_related('stock', 'advisor', 'broker').order_by('-timestamp')

    # DEBUG: Log the count
    # print("Other Advisor Orders:", buy_orders_Advisor.count())

    stock_context = get_user_stock_context(user, request)

    return render(request, 'portfolio/BuyOrdersList.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'buy_orders_Advisor': buy_orders_Advisor,
        **stock_context
    })

@login_required
def sell_orders(request):
    user = request.user
    stock_context = get_user_stock_context(user, request)
    Sell_orders_value = SellTransaction.objects.filter(user=request.user).select_related('stock', 'advisor', 'broker').order_by('-timestamp')
    
    # Optional: Search
    search_query = request.GET.get('search', '')
    if search_query:
        Sell_orders_value = Sell_orders_value.filter(stock__company_name__icontains=search_query)
        
    # Optional: Pagination
    paginator = Paginator(Sell_orders_value, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'portfolio/SellOrdersList.html',{'Sell_orders_value':Sell_orders_value, 'page_obj':page_obj,**stock_context})




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


# user_portfolio/views.py
# @require_POST
# def buy_stock(request, stock_id):
#     stock = get_object_or_404(StockData, id=stock_id)
#     try:
#         advisor_id = request.POST.get('advisor')
#         broker_id = request.POST.get('broker')
#         quantity = int(request.POST.get('quantity'))
#         price_per_share = Decimal(request.POST.get('price_per_share'))
#         order_type = request.POST.get('order_type')

#         total_amount = quantity * price_per_share

#         advisor = get_object_or_404(Advisor, id=advisor_id)
#         broker = get_object_or_404(Broker, id=broker_id)

#         BuyTransaction.objects.create(
#             user=request.user,
#             stock=stock,
#             advisor=advisor,
#             broker=broker,
#             quantity=quantity,
#             price_per_share=price_per_share,
#             order_type=order_type,
#             total_amount=total_amount,
#         )

#         messages.success(request, f"Buy order placed for {stock.company_name} successfully.")
#     except Exception as e:
#         messages.error(request, f"Buy order failed: {str(e)}")

#     return redirect(request.META.get('HTTP_REFERER', '/'))


##################################################
# current main #########################################
# @require_POST
# def buy_stock(request, stock_id):
#     stock = get_object_or_404(StockData, id=stock_id)
#     advisor = get_object_or_404(Advisor, id=request.POST.get('advisor'))
#     broker = get_object_or_404(Broker, id=request.POST.get('broker'))
#     quantity = int(request.POST.get('quantity'))
#     price_per_share = Decimal(request.POST.get('price_per_share'))
#     order_type = request.POST.get('order_type')
    
#     total_amount = quantity * price_per_share

#     BuyTransaction.objects.create(
#         user=request.user,
#         stock=stock,
#         advisor=advisor,
#         broker=broker,
#         quantity=quantity,
#         price_per_share=price_per_share,
#         order_type=order_type,
#         total_amount=total_amount,
#     )
#     messages.success(request, f"Buy order placed for {stock.company_name} successfully.")
#     return redirect(request.META.get('HTTP_REFERER', '/'))

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

@require_POST
@login_required
def sell_stock(request, stock_id):
    stock = get_object_or_404(StockData, id=stock_id)

    try:
        advisor_id = request.POST.get('advisor')
        broker_id = request.POST.get('broker')
        quantity = int(request.POST.get('quantity'))

        # Get the selling price safely
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

        SellTransaction.objects.create(
            user=request.user,
            advisor=advisor,
            broker=broker,
            stock=stock,
            quantity=quantity,
            selling_price=selling_price,
        )

        messages.success(request, f"Sell order placed for {stock.company_name} ({quantity} shares at ₹{selling_price})")
    except Exception as e:
        import traceback
        traceback.print_exc()
        messages.error(request, f"Failed to place sell order: {str(e)}")

    return redirect(request.META.get('HTTP_REFERER', '/'))
