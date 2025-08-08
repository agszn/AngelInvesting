from unicodedata import name
from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

from django.conf import settings
from django.conf.urls.static import static


app_name = 'unlisted_stock_marketplace'

urlpatterns = [

    path('', stock_list, name='stock_list'),
    path('ajax/all-stocks/', all_stocks_ajax, name='all_stocks_ajax'),
    path('stocks/suggestions/', stock_suggestions, name='stock_suggestions'),
    
    path('stock/<int:stock_id>/', stock_detail, name='stock_detail'),

    path('StockDetailedListings/', StockListingTableFormat, name='StockListingTableFormat'),
    
    path('get-next-wishlist-group-name/', get_next_wishlist_group_name, name='get_next_wishlist_group_name'),
    path('add-to-wishlist/', add_to_wishlist, name='add_to_wishlist'),
    
    path('add-to-group/<int:stock_id>/', add_to_group, name='add_to_group'),
    
    path('remove_from_group/<int:wishlist_id>/', remove_from_group, name='remove_from_group'),
        
    # path('wishlist/', wish_list, name='wish_list'),


    ]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
