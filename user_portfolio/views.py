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


def _parse_sort(request, default='-timestamp'):
    sort = request.GET.get('sort')
    if sort == 'date_asc':
        return 'timestamp'
    elif sort == 'date_desc':
        return '-timestamp'
    return default

def _market_closed_note():
    now = timezone.localtime()
    if now.hour >= 18:
        return "The market is closed. Your order will be processed tomorrow at 11:00 AM."
    return None
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


# this is portfolio with other advisor in different table
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from .models import UserStockInvestmentSummary, Advisor, Broker
from .utils import update_user_holdings  # make sure this is in utils.py

@login_required
def portfolio_view(request):
    user = request.user
    update_user_holdings(user)

    qs = UserStockInvestmentSummary.objects.filter(user=user).select_related('stock', 'advisor', 'broker')

    advisor_param = request.GET.get('advisor')        # could be None, 'all', or an id string
    broker_id = request.GET.get('broker')
    search = request.GET.get('search', '').strip()

    selected_advisor = None

    # Default only when the advisor param is truly absent (first load)
    if advisor_param is None:
        default_adv = Advisor.objects.filter(advisor_type__iexact='Thangiv').first()
        if default_adv:
            qs = qs.filter(advisor=default_adv)
            selected_advisor = default_adv
    else:
        # advisor explicitly provided
        if advisor_param and advisor_param.lower() != 'all':
            qs = qs.filter(advisor__id=advisor_param)
            selected_advisor = Advisor.objects.filter(id=advisor_param).first()
        # else: advisor=all (or empty) -> no advisor filter

    if broker_id:
        qs = qs.filter(broker__id=broker_id)
    if search:
        qs = qs.filter(Q(stock__company_name__icontains=search) | Q(stock__scrip_name__icontains=search))

    qs = qs.order_by('-last_updated', '-id')

    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    stock_context = get_user_stock_context(user, request)
    context = {
        'holdings': page_obj,
        'advisors': Advisor.objects.all(),
        'brokers': Broker.objects.all(),
        'selected_advisor': selected_advisor,
        'selected_broker': Broker.objects.filter(id=broker_id).first() if broker_id else None,
        'search_query': search,
        'page_obj': page_obj,
        **stock_context,
    }
    tpl = 'portfolio/includes/portfolio_table.html' if request.headers.get('X-Requested-With') == 'XMLHttpRequest' else 'portfolio/PortfolioList.html'
    return render(request, tpl, context)


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
    search = request.GET.get('search', '').strip()
    advisor_id = request.GET.get('advisor')
    broker_id = request.GET.get('broker')
    ordering = _parse_sort(request, default='-timestamp')

    qs1 = BuyTransaction.objects.filter(user=user).select_related('stock','advisor','broker')
    qs2 = BuyTransactionOtherAdvisor.objects.filter(user=user).select_related('stock','advisor','broker')

    if advisor_id:
        qs1 = qs1.filter(advisor__id=advisor_id)
        qs2 = qs2.filter(advisor__id=advisor_id)
    if broker_id:
        qs1 = qs1.filter(broker__id=broker_id)
        qs2 = qs2.filter(broker__id=broker_id)
    if search:
        for_q = Q(stock__company_name__icontains=search) | Q(stock__scrip_name__icontains=search)
        qs1 = qs1.filter(for_q)
        qs2 = qs2.filter(for_q)

    orders = sorted(chain(qs1, qs2), key=attrgetter('timestamp'), reverse=(ordering.startswith('-')))

    paginator = Paginator(orders, 15)
    page_obj = paginator.get_page(request.GET.get('page'))

    stock_context = get_user_stock_context(user, request)
    context = {
        'orders': page_obj,
        'advisors': Advisor.objects.all(),
        'brokers': Broker.objects.all(),
        'selected_advisor': Advisor.objects.filter(id=advisor_id).first() if advisor_id else None,
        'selected_broker': Broker.objects.filter(id=broker_id).first() if broker_id else None,
        'sort': ordering,
        'search_query': search,
        'page_obj': page_obj,
        'now': timezone.localtime(),
        **stock_context,
    }
    tpl = 'portfolio/includes/buy_orders_table.html' if request.headers.get('X-Requested-With')=='XMLHttpRequest' else 'portfolio/BuyOrdersList.html'
    return render(request, tpl, context)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.paginator import Paginator
from .models import SellTransaction, Advisor, Broker
from .utils import get_user_stock_context  # assuming you have this
from itertools import chain
from operator import attrgetter
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import SellTransaction, SellTransactionOtherAdvisor, Advisor, Broker
from .utils import get_user_stock_context


@login_required
def sell_orders(request):
    user = request.user
    search = request.GET.get('search', '').strip()
    advisor_id = request.GET.get('advisor')
    broker_id = request.GET.get('broker')
    ordering = _parse_sort(request, default='-timestamp')

    qs1 = SellTransaction.objects.filter(user=user).select_related('stock','advisor','broker')
    qs2 = SellTransactionOtherAdvisor.objects.filter(user=user).select_related('stock','advisor','broker')

    status_filter = request.GET.get('status')
    if status_filter:
        qs1 = qs1.filter(status=status_filter)
        qs2 = qs2.filter(status=status_filter)

    if advisor_id:
        qs1 = qs1.filter(advisor__id=advisor_id)
        qs2 = qs2.filter(advisor__id=advisor_id)
    if broker_id:
        qs1 = qs1.filter(broker__id=broker_id)
        qs2 = qs2.filter(broker__id=broker_id)
    if search:
        for_q = Q(stock__company_name__icontains=search) | Q(stock__scrip_name__icontains=search)
        qs1 = qs1.filter(for_q)
        qs2 = qs2.filter(for_q)

    orders = sorted(chain(qs1, qs2), key=attrgetter('timestamp'), reverse=(ordering.startswith('-')))

    paginator = Paginator(orders, 15)
    page_obj = paginator.get_page(request.GET.get('page'))

    stock_context = get_user_stock_context(user, request)
    context = {
        'orders': page_obj,
        'advisors': Advisor.objects.all(),
        'brokers': Broker.objects.all(),
        'selected_advisor': Advisor.objects.filter(id=advisor_id).first() if advisor_id else None,
        'selected_broker': Broker.objects.filter(id=broker_id).first() if broker_id else None,
        'sort': ordering,
        'search_query': search,
        'page_obj': page_obj,
        'now': timezone.localtime(),
        **stock_context,
    }
    tpl = 'portfolio/includes/sell_orders_table.html' if request.headers.get('X-Requested-With')=='XMLHttpRequest' else 'portfolio/SellOrdersList.html'
    return render(request, tpl, context)

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
def buy_stock(request, stock_id):
    stock = get_object_or_404(StockData, id=stock_id)

    if request.method != 'POST':
        return redirect(request.META.get('HTTP_REFERER', '/'))

    try:
        advisor = get_object_or_404(Advisor, id=request.POST.get('advisor'))
        broker = get_object_or_404(Broker, id=request.POST.get('broker'))
        quantity = int(request.POST.get('quantity'))
        order_type = request.POST.get('order_type', 'market')

        if order_type == 'market':
            price_per_share = stock.share_price or Decimal('0')
        else:
            price_per_share = Decimal(request.POST.get('price_per_share'))

        total_amount = price_per_share * quantity

        if advisor.advisor_type.lower() == 'other':
            BuyTransactionOtherAdvisor.objects.create(
                user=request.user, stock=stock, advisor=advisor, broker=broker,
                quantity=quantity, price_per_share=price_per_share,
                order_type=order_type, total_amount=total_amount, status='completed'
            )
        else:
            BuyTransaction.objects.create(
                user=request.user, stock=stock, advisor=advisor, broker=broker,
                quantity=quantity, price_per_share=price_per_share,
                order_type=order_type, total_amount=total_amount, status='processing'
            )

        note = _market_closed_note()
        if note:
            messages.info(request, note)
        messages.success(request, f"Buy order placed for {stock.company_name}.")

    except Exception as e:
        messages.error(request, f"Failed to place order: {e}")

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
# at the imports near sell_stock
from django.db.models import Sum  # add this

@require_POST
@login_required
def sell_stock(request, stock_id):
    stock = get_object_or_404(StockData, id=stock_id)

    if request.method != 'POST':
        return redirect(request.META.get('HTTP_REFERER', '/'))

    try:
        advisor = get_object_or_404(Advisor, id=request.POST.get('advisor'))
        broker = get_object_or_404(Broker, id=request.POST.get('broker'))
        quantity = int(request.POST.get('quantity'))

        price_str = request.POST.get('selling_price')
        selling_price = Decimal(price_str) if price_str else (stock.share_price or Decimal('0'))

        if advisor.advisor_type.lower() == 'other':
            SellTransactionOtherAdvisor.objects.create(
                user=request.user, stock=stock, advisor=advisor, broker=broker,
                quantity=quantity, selling_price=selling_price, status='processing'
            )
        else:
            SellTransaction.objects.create(
                user=request.user, stock=stock, advisor=advisor, broker=broker,
                quantity=quantity, selling_price=selling_price, status='processing'
            )

        note = _market_closed_note()
        if note:
            messages.info(request, note)
        messages.success(request, f"Sell order placed for {stock.company_name}.")

    except Exception as e:
        messages.error(request, f"Failed to place sell order: {e}")

    return redirect(request.META.get('HTTP_REFERER', '/'))


from Share_Transfer.models import DealLetterRecord

# view_deal_letters



from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .utils import get_user_stock_context  # if you use this elsewhere

@login_required
def view_deal_letters(request):
    user = request.user
    stock_context = {}

    # Optional helper, safe if missing
    try:
        stock_context = get_user_stock_context(user, request)
    except Exception:
        pass

    # Filters
    raw_deal_type = request.GET.get('deal_type', '').strip()  # may be "", "BUY", "SELL" (or lower)
    sort_key = request.GET.get('sort_by', 'date_desc')        # one of: date_desc, date_asc, amount_desc, amount_asc

    records = DealLetterRecord.objects.filter(user=user)

    # Be lenient: accept either upper/lower values
    if raw_deal_type:
        # If your model stores uppercase choice values ("BUY"/"SELL"), __iexact keeps it robust.
        records = records.filter(deal_type__iexact=raw_deal_type)

    # Apply sorting (correct directions)
    allowed_sorts = {
        'date_desc':   '-generated_on',  # newest first
        'date_asc':     'generated_on',  # oldest first
        'amount_desc': '-total_amount',  # high -> low
        'amount_asc':   'total_amount',  # low -> high
    }
    records = records.order_by(allowed_sorts.get(sort_key, '-generated_on'))

    # Normalize selected values for the template
    selected_deal_type = raw_deal_type.upper() if raw_deal_type else ''
    selected_sort = sort_key

    return render(request, 'portfolio/view_deal_letters.html', {
        'records': records,
        'selected_deal_type': selected_deal_type,  # "BUY"/"SELL" or ""
        'selected_sort': selected_sort,            # e.g. "date_desc"
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
