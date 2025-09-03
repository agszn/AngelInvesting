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


def update_user_holdings(user):
    from user_portfolio.models import BuyTransaction, BuyTransactionOtherAdvisor, SellTransaction
    from unlisted_stock_marketplace.models import StockData
    from .models import UserStockInvestmentSummary

    # Normal BuyTransaction
    buy_stock_ids = BuyTransaction.objects.filter(user=user, status='completed').values_list('stock_id', flat=True).distinct()

    # BuyTransactionOtherAdvisor
    other_buy_stock_ids = BuyTransactionOtherAdvisor.objects.filter(user=user, status='completed').values_list('stock_id', flat=True).distinct()

    # ✅ Update non-Other advisor holdings
    for stock_id in buy_stock_ids:
        stock = StockData.objects.filter(id=stock_id).first()
        if not stock:
            continue
        summary, _ = UserStockInvestmentSummary.objects.get_or_create(user=user, stock=stock, is_other_advisor=False)
        summary.update_from_transactions()
        summary.save()

    # ✅ Update "Other" advisor holdings
    for stock_id in other_buy_stock_ids:
        stock = StockData.objects.filter(id=stock_id).first()
        if not stock:
            continue
        summary, _ = UserStockInvestmentSummary.objects.get_or_create(user=user, stock=stock, is_other_advisor=True)
        summary.update_from_transactions()
        summary.save()




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
