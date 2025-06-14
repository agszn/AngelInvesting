from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import *


# 
# 
# ---------------------------------------------------------------------
# ------------------ Wishlist -------------
# ------------------------------------------------------------------
# 
# 


from unlisted_stock_marketplace.models import WishlistGroup, Wishlist
from django.db.models import OuterRef, Subquery, Exists, F, ExpressionWrapper, FloatField

def sidebar_stocks(request):
    if not request.user.is_authenticated:
        return {}

    user = request.user
    stock_list = StockData.objects.all()

    wishlist_subquery = Wishlist.objects.filter(user=user, stock=OuterRef('pk'))
    group_subquery = Wishlist.objects.filter(user=user, stock=OuterRef('pk')).values('group__name')[:1]
    wishlist_id_subquery = Wishlist.objects.filter(user=user, stock=OuterRef('pk')).values('id')[:1]
    group_number_subquery = Wishlist.objects.filter(user=user, stock=OuterRef('pk')).values('group__id')[:1]

    stock_list = stock_list.annotate(
        in_group=Exists(wishlist_subquery),
        group_name=Subquery(group_subquery),
        wishlist_id=Subquery(wishlist_id_subquery),
        group_number=Subquery(group_number_subquery),
        profit=ExpressionWrapper(
            (F('share_price') - F('average_buy_price')) * F('quantity'),
            output_field=FloatField()
        ),
        profit_percentage=ExpressionWrapper(
            ((F('share_price') - F('average_buy_price')) / F('average_buy_price')) * 100,
            output_field=FloatField()
        )
    )

    search_query = request.GET.get('search', '')
    if search_query:
        stock_list = stock_list.filter(company_name__icontains=search_query)

    group_id = request.GET.get('group')
    show_all_unlisted = request.GET.get('unlisted') == '1'
    show_all_angel = request.GET.get('angel') == '1'

    if group_id:
        stock_list = stock_list.filter(group_number=group_id)
    elif show_all_unlisted:
        stock_list = stock_list.filter(is_unlisted=True)
    elif show_all_angel:
        stock_list = stock_list.filter(is_angel=True)

    groups = WishlistGroup.objects.filter(user=user).order_by('created_at')

    return {
        'stock_list': stock_list,
        'groups': groups,
        'search_query': search_query,
        'show_all_unlisted': show_all_unlisted,
        'show_all_angel': show_all_angel,
    }
