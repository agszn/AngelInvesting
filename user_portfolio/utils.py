# app_name : user_portfolio
# utils.py
# from user_portfolio.models import *
# from unlisted_stock_marketplace.models import StockData

# def update_user_holdings(user):
#     stocks = StockData.objects.filter(buytransaction__user=user, buytransaction__status='completed').distinct()

#     for stock in stocks:
#         summary, _ = UserStockInvestmentSummary.objects.get_or_create(user=user, stock=stock)
#         summary.update_from_transactions()
#         summary.save()
 










# def update_user_holdings(user):
#     from user_portfolio.models import BuyTransaction, SellTransaction, BuyTransactionOtherAdvisor
#     from unlisted_stock_marketplace.models import StockData
#     from .models import UserStockInvestmentSummary

#     # Get stock IDs from all relevant sources
#     buy_stock_ids = BuyTransaction.objects.filter(user=user, status='completed').values_list('stock_id', flat=True)
    
#     other_buy_stock_ids = BuyTransactionOtherAdvisor.objects.filter(user=user, status='completed').values_list('stock_id', flat=True)

#     sell_stock_ids = SellTransaction.objects.filter(user=user,status='completed').values_list('stock_id', flat=True)

#     # Union of all stock IDs
#     stock_ids = set(list(buy_stock_ids) + list(other_buy_stock_ids) + list(sell_stock_ids))

#     for stock_id in stock_ids:
#         stock = StockData.objects.get(id=stock_id)
#         summary, _ = UserStockInvestmentSummary.objects.get_or_create(user=user, stock=stock)
#         summary.update_from_transactions()  
#         summary.save()
from decimal import Decimal

def update_user_holdings(user):
    """
    Recompute UserStockInvestmentSummary per (stock, advisor, broker) bucket.

    Rules:
    - "Normal" advisors: quantity_held = total_buys - total_sells (excluding 'Other' advisor sells).
    - "Other" advisor: quantity_held = total_buys only (no sells applied).
    - Weighted Avg Price = sum(qty * price_per_share) / sum(qty) from buys only.
    - Combine rows only when BOTH advisor AND broker match.
    """
    from django.db.models import Sum, F, Count, Value, DecimalField, ExpressionWrapper
    from django.db.models.functions import Coalesce

    from user_portfolio.models import (
        BuyTransaction, BuyTransactionOtherAdvisor,
        SellTransaction, UserStockInvestmentSummary
    )
    from unlisted_stock_marketplace.models import StockData

    # Optional: resolve 'Other' advisor id if available in your project
    other_adv_id = None
    try:
        from site_Manager.models import Advisor  # adjust app label if different
        other_adv_id = Advisor.objects.filter(advisor_type__iexact='Other') \
                                      .values_list('id', flat=True).first()
    except Exception:
        other_adv_id = None

    # Buckets keyed by (stock_id, advisor_id, broker_id, is_other_advisor)
    buckets = {}

    def _ensure_bucket(key):
        if key not in buckets:
            buckets[key] = {
                'buy_qty': 0, 'buy_amt': Decimal('0'),
                'buy_count': 0, 'buy_total': Decimal('0'),
                'sell_qty': 0, 'sell_amt': Decimal('0'),
                'sell_count': 0, 'sell_total': Decimal('0'),
            }
        return buckets[key]

    # ---- helpers for decimal expressions ----
    DEC = DecimalField(max_digits=20, decimal_places=2)
    ZERO_DEC = Value(0, output_field=DEC)

    # quantity * price_per_share as Decimal
    buy_value_expr  = ExpressionWrapper(F('quantity') * F('price_per_share'), output_field=DEC)
    # quantity * selling_price as Decimal
    sell_value_expr = ExpressionWrapper(F('quantity') * F('selling_price'),   output_field=DEC)

    # ---- NORMAL BUYS ----
    normal_buys = (BuyTransaction.objects
                   .filter(user=user, status='completed')
                   .values('stock_id', 'advisor_id', 'broker_id')
                   .annotate(
                       buy_qty   = Coalesce(Sum('quantity'), 0),
                       buy_amt   = Coalesce(Sum(buy_value_expr), ZERO_DEC),
                       buy_count = Coalesce(Count('id'), 0),
                       buy_total = Coalesce(Sum('total_amount', output_field=DEC), ZERO_DEC),
                   ))
    for r in normal_buys:
        key = (r['stock_id'], r['advisor_id'], r['broker_id'], False)
        b = _ensure_bucket(key)
        b['buy_qty']   += int(r['buy_qty'] or 0)
        b['buy_amt']   += Decimal(r['buy_amt'] or 0)
        b['buy_count'] += int(r['buy_count'] or 0)
        b['buy_total'] += Decimal(r['buy_total'] or 0)

    # ---- NORMAL SELLS (exclude 'Other' advisor sells if known) ----
    normal_sells_qs = SellTransaction.objects.filter(user=user, status='completed')
    if other_adv_id:
        normal_sells_qs = normal_sells_qs.exclude(advisor_id=other_adv_id)

    normal_sells = (normal_sells_qs
                    .values('stock_id', 'advisor_id', 'broker_id')
                    .annotate(
                        sell_qty   = Coalesce(Sum('quantity'), 0),
                        sell_amt   = Coalesce(Sum(sell_value_expr), ZERO_DEC),
                        sell_count = Coalesce(Count('id'), 0),
                        sell_total = Coalesce(Sum('total_value', output_field=DEC), ZERO_DEC),
                    ))
    for r in normal_sells:
        key = (r['stock_id'], r['advisor_id'], r['broker_id'], False)
        b = _ensure_bucket(key)
        b['sell_qty']   += int(r['sell_qty'] or 0)
        b['sell_amt']   += Decimal(r['sell_amt'] or 0)
        b['sell_count'] += int(r['sell_count'] or 0)
        b['sell_total'] += Decimal(r['sell_total'] or 0)

    # ---- OTHER-ADVISOR BUYS (no sells applied) ----
    other_buys_qs = BuyTransactionOtherAdvisor.objects.filter(user=user, status='completed')

    # Some schemas may not have broker on this model; try with broker, fall back without it
    try:
        other_buys = (other_buys_qs
                      .values('stock_id', 'advisor_id', 'broker_id')
                      .annotate(
                          buy_qty   = Coalesce(Sum('quantity'), 0),
                          buy_amt   = Coalesce(Sum(buy_value_expr), ZERO_DEC),
                          buy_count = Coalesce(Count('id'), 0),
                          buy_total = Coalesce(Sum('total_amount', output_field=DEC), ZERO_DEC),
                      ))
        include_broker = True
    except Exception:
        other_buys = (other_buys_qs
                      .values('stock_id', 'advisor_id')
                      .annotate(
                          buy_qty   = Coalesce(Sum('quantity'), 0),
                          buy_amt   = Coalesce(Sum(buy_value_expr), ZERO_DEC),
                          buy_count = Coalesce(Count('id'), 0),
                          buy_total = Coalesce(Sum('total_amount', output_field=DEC), ZERO_DEC),
                      ))
        include_broker = False

    for r in other_buys:
        advisor_id = r.get('advisor_id') or other_adv_id
        broker_id  = r.get('broker_id') if include_broker else None
        key = (r['stock_id'], advisor_id, broker_id, True)
        b = _ensure_bucket(key)
        b['buy_qty']   += int(r['buy_qty'] or 0)
        b['buy_amt']   += Decimal(r['buy_amt'] or 0)
        b['buy_count'] += int(r['buy_count'] or 0)
        b['buy_total'] += Decimal(r['buy_total'] or 0)

    # ----- Upsert summaries per bucket -----
    stock_ids = {k[0] for k in buckets.keys()}
    stocks    = {s.id: s for s in StockData.objects.filter(id__in=stock_ids)}

    # Pull previous-day closes from History tab (best-effort)
    prev_close_by_stock = {}
    try:
        from django.utils import timezone
        today = timezone.localdate()

        # Try a few common history model/field shapes — adjust if yours differ
        candidates = [
            ('unlisted_stock_marketplace', 'StockPriceHistory', 'close'),
            ('unlisted_stock_marketplace', 'PriceHistory', 'close'),
            ('unlisted_stock_marketplace', 'StockHistory', 'close'),
            ('unlisted_stock_marketplace', 'StockDailyOHLC', 'close'),
            ('unlisted_stock_marketplace', 'StockDailyPrice', 'close'),
            # fallbacks if field isn't 'close'
            ('unlisted_stock_marketplace', 'StockPriceHistory', 'ltp'),
            ('unlisted_stock_marketplace', 'StockPriceHistory', 'price'),
        ]
        for app_label, model_name, field_name in candidates:
            try:
                mod = __import__(f"{app_label}.models", fromlist=[model_name])
                HistoryModel = getattr(mod, model_name)
                rows = (HistoryModel.objects
                        .filter(stock_id__in=stock_ids, date__lt=today)
                        .order_by('stock_id', '-date')
                        .values('stock_id', 'date', field_name))
                for r in rows:
                    sid = r['stock_id']
                    if sid not in prev_close_by_stock:
                        prev_close_by_stock[sid] = Decimal(r[field_name] or 0)
                if prev_close_by_stock:
                    break
            except Exception:
                continue
    except Exception:
        prev_close_by_stock = {}

    for (stock_id, advisor_id, broker_id, is_other), data in buckets.items():
        stock = stocks.get(stock_id)

        buy_qty  = data['buy_qty']
        sell_qty = data['sell_qty']
        net_qty  = buy_qty if is_other else max(buy_qty - sell_qty, 0)

        avg_price = (Decimal(data['buy_amt']) / buy_qty) if buy_qty else Decimal('0')

        # Market numbers
        if stock:
            share_price = Decimal(getattr(stock, 'share_price', 0) or 0)

            # Use History close if available; otherwise treat as today's price (so day P/L = 0)
            previous_day_price = prev_close_by_stock.get(stock_id, share_price)

            ltp = share_price  # swap if you store distinct LTP
        else:
            share_price        = Decimal('0')
            previous_day_price = Decimal('0')
            ltp                = Decimal('0')

        investment_amount    = avg_price * net_qty
        market_value         = share_price * net_qty
        overall_gain_loss    = market_value - investment_amount
        overall_gain_percent = (overall_gain_loss / investment_amount * 100) if investment_amount > 0 else Decimal('0')
        day_gain_loss        = net_qty * (share_price - previous_day_price)
        day_gain_percent     = (day_gain_loss / investment_amount * 100) if investment_amount > 0 else Decimal('0')

        summary, _ = UserStockInvestmentSummary.objects.get_or_create(
            user=user,
            stock_id=stock_id,
            advisor_id=advisor_id,
            broker_id=broker_id,
            is_other_advisor=is_other,
        )

        summary.quantity_held        = int(net_qty or 0)
        summary.avg_price            = avg_price
        summary.share_price          = share_price
        summary.ltp                  = ltp
        summary.previous_day_price   = previous_day_price
        summary.market_value         = market_value
        summary.investment_amount    = investment_amount
        summary.overall_gain_loss    = overall_gain_loss
        summary.overall_gain_percent = overall_gain_percent
        summary.day_gain_loss        = day_gain_loss
        summary.day_gain_percent     = day_gain_percent
        summary.buy_order_count      = int(data['buy_count'] or 0)
        summary.buy_order_total      = Decimal(data['buy_total'] or 0)

        if not is_other:
            summary.sell_order_count = int(data['sell_count'] or 0)
            summary.sell_order_total = Decimal(data['sell_total'] or 0)
        else:
            summary.sell_order_count = 0
            summary.sell_order_total = Decimal('0')

        summary.save(update_fields=[
            'quantity_held', 'avg_price',
            'share_price', 'ltp', 'previous_day_price',
            'market_value', 'investment_amount',
            'overall_gain_loss', 'overall_gain_percent',
            'day_gain_loss', 'day_gain_percent',
            'buy_order_count', 'buy_order_total',
            'sell_order_count', 'sell_order_total',
            'advisor', 'broker', 'last_updated',
        ])


# user_portfolio/utils.py or a shared module 

from django.db.models import Q, Exists, OuterRef, Subquery, IntegerField
from unlisted_stock_marketplace.models import Wishlist, WishlistGroup, StockData

# def get_user_stock_context(user, request):
#     show_all_unlisted = request.GET.get("unlisted") == "1"
#     show_all_angel = request.GET.get("angel") == "1"
#     group_id = request.GET.get("group")
#     search_query = request.GET.get("search", "")

#     if group_id:
#         group = WishlistGroup.objects.filter(id=group_id, user=user).first()
#         wishlist_stocks = Wishlist.objects.filter(group=group).values_list("stock", flat=True)
#         stock_list = StockData.objects.filter(id__in=wishlist_stocks)
#     elif show_all_angel:
#         stock_list = StockData.objects.filter(stock_type__iexact="angel")
#     else:
#         stock_list = StockData.objects.filter(stock_type__iexact="unlisted")
#         show_all_unlisted = True

#     if search_query:
#         stock_list = stock_list.filter(
#             Q(company_name__istartswith=search_query) |
#             Q(scrip_name__istartswith=search_query)
#         )

#     stock_list = stock_list.annotate(
#         in_group=Exists(
#             Wishlist.objects.filter(stock=OuterRef('pk'), group__user=user)
#         ),
#         group_number=Subquery(
#             Wishlist.objects.filter(stock=OuterRef('pk'), group__user=user)
#             .values('group__name')[:1]
#         ),
#         wishlist_id=Subquery(
#             Wishlist.objects.filter(stock=OuterRef('pk'), group__user=user)
#             .values('id')[:1],
#             output_field=IntegerField()
#         )
#     )

#     groups = WishlistGroup.objects.filter(user=user)

#     return {
#         'stock_list': stock_list,
#         'groups': groups,
#         'show_all_unlisted': show_all_unlisted,
#         'show_all_angel': show_all_angel,
#         'search_query': search_query,
#         'current_group_id': int(group_id) if group_id else None, 
#     }
from django.db.models import Q, Exists, OuterRef, Subquery, IntegerField, Case, When

def get_user_stock_context(user, request):
    show_all_unlisted = request.GET.get("unlisted") == "1"
    show_all_angel = request.GET.get("angel") == "1"
    group_id = request.GET.get("group")
    sidebar_search_query = request.GET.get("sidebar_search", "")

    stock_list = StockData.objects.none()
    preserved_order = None

    if group_id:
        group = WishlistGroup.objects.filter(id=group_id, user=user).first()
        wishlist_items = Wishlist.objects.filter(group=group).order_by('-added_on')
        stock_ids = list(wishlist_items.values_list("stock", flat=True))
        stock_list = StockData.objects.filter(id__in=stock_ids)

        # Preserve wishlist order (most recently added first)
        preserved_order = Case(
            *[When(pk=pk, then=pos) for pos, pk in enumerate(stock_ids)],
            output_field=IntegerField()
        )
    elif show_all_angel:
        stock_list = StockData.objects.filter(stock_type__iexact="angel")
    else:
        stock_list = StockData.objects.filter(stock_type__iexact="unlisted")
        show_all_unlisted = True

    # Apply sidebar search
    if sidebar_search_query:
        stock_list = stock_list.filter(
            Q(company_name__istartswith=sidebar_search_query) |
            Q(scrip_name__istartswith=sidebar_search_query)
        )

    # Annotate additional info for template usage
    stock_list = stock_list.annotate(
        in_group=Exists(
            Wishlist.objects.filter(stock=OuterRef('pk'), group__user=user)
        ),
        group_number=Subquery(
            Wishlist.objects.filter(stock=OuterRef('pk'), group__user=user)
            .values('group__name')[:1]
        ),
        wishlist_id=Subquery(
            Wishlist.objects.filter(stock=OuterRef('pk'), group__user=user)
            .values('id')[:1],
            output_field=IntegerField()
        )
    )

    # Apply preserved order only for group view
    if preserved_order:
        stock_list = stock_list.order_by(preserved_order)

    # Sort groups by latest created
    groups = WishlistGroup.objects.filter(user=user).order_by('-created_on')

    return {
        'stock_list': stock_list,
        'groups': groups,
        'show_all_unlisted': show_all_unlisted,
        'show_all_angel': show_all_angel,
        'sidebar_search_query': sidebar_search_query,
        'current_group_id': int(group_id) if group_id else None,
    }
