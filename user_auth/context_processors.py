from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import *
from unlisted_stock_marketplace.models import *

def profile_context(request):
    if not request.user.is_authenticated:
        return {}

    # Search and filters
    search_query = request.GET.get('search', '').strip()
    stock_type_filter = request.GET.get('stock_type', '').strip()
    selected_group_id = request.GET.get('group')
    show_all_unlisted = request.GET.get('unlisted') == '1'
    show_all_angel = request.GET.get('angel') == '1'

    user = request.user
    groups = WishlistGroup.objects.filter(user=user).order_by('created_on')
    stock_list = []
    wishlist_data = []
    wishlist_items = Wishlist.objects.filter(user=user).select_related('stock')

    # Show Unlisted or Angel stocks
    if show_all_unlisted or show_all_angel:
        stock_type = "Unlisted" if show_all_unlisted else "Angel"
        stock_list = StockData.objects.filter(stock_type=stock_type)
        if search_query:
            stock_list = stock_list.filter(
                Q(company_name__icontains=search_query) |
                Q(scrip_name__icontains=search_query)
            )
    else:
        if selected_group_id:
            selected_group = get_object_or_404(WishlistGroup, id=selected_group_id, user=user)
            wishlist_items = wishlist_items.filter(group=selected_group)

        if search_query:
            wishlist_items = wishlist_items.filter(
                Q(stock__company_name__icontains=search_query) |
                Q(stock__scrip_name__icontains=search_query)
            )

        wishlist_data = wishlist_items

    # Profile and Transactions
    profile, created = UserProfile.objects.get_or_create(user=user)

    return {
        'wishlist_items': wishlist_items,
        'wishlist_data': wishlist_data,
        'groups': groups,
        'stock_list': stock_list,
        'search_query': search_query,
        'selected_stock_type': stock_type_filter,
        'show_all_unlisted': show_all_unlisted,
        'show_all_angel': show_all_angel,
        'profile': profile,
        'bank_accounts': profile.bank_accounts.all() if profile else [],
        'cmr_copies': profile.cmr_copies.all() if profile else [],
    }


# 
# 
# ---------------------------------------------------------------------
# ------------------ Navbar Marquee -------------
# ------------------------------------------------------------------
# 
# 

def marquee_stocks(request):
    stocks = StockData.objects.all()
    for stock in stocks:
        if stock.share_price is not None and stock.ltp and stock.ltp > 0:
            stock.percentage_diff = ((stock.share_price - stock.ltp) / stock.ltp) * 100
        else:
            stock.percentage_diff = None
    return {'marquee_stocks': stocks}
