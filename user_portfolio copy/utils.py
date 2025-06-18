# app_name : user_portfolio
# utils.py
from user_portfolio.models import *
from unlisted_stock_marketplace.models import StockData

def update_user_holdings(user):
    stocks = StockData.objects.filter(buytransaction__user=user, buytransaction__status='completed').distinct()

    for stock in stocks:
        summary, _ = UserStockInvestmentSummary.objects.get_or_create(user=user, stock=stock)
        summary.update_from_transactions()
        summary.save()
 


# utils.py or a shared module like user_helpers.py

from django.db.models import Q, Exists, OuterRef, Subquery, IntegerField
from unlisted_stock_marketplace.models import Wishlist, WishlistGroup, StockData

def get_user_stock_context(user, request):
    show_all_unlisted = request.GET.get("unlisted") == "1"
    show_all_angel = request.GET.get("angel") == "1"
    group_id = request.GET.get("group")
    search_query = request.GET.get("search", "")

    if group_id:
        group = WishlistGroup.objects.filter(id=group_id, user=user).first()
        wishlist_stocks = Wishlist.objects.filter(group=group).values_list("stock", flat=True)
        stock_list = StockData.objects.filter(id__in=wishlist_stocks)
    elif show_all_angel:
        stock_list = StockData.objects.filter(stock_type__iexact="angel")
    else:
        stock_list = StockData.objects.filter(stock_type__iexact="unlisted")
        show_all_unlisted = True

    if search_query:
        stock_list = stock_list.filter(
            Q(company_name__istartswith=search_query) |
            Q(scrip_name__istartswith=search_query)
        )

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

    groups = WishlistGroup.objects.filter(user=user)

    return {
        'stock_list': stock_list,
        'groups': groups,
        'show_all_unlisted': show_all_unlisted,
        'show_all_angel': show_all_angel,
        'search_query': search_query,
    }
