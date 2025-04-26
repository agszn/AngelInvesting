from unicodedata import name
from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

from django.conf import settings
from django.conf.urls.static import static

app_name = 'unlisted_stock_marketplace'

urlpatterns = [

    path('', stock_list, name='stock_list'),
    path('stock/<int:stock_id>/', stock_detail, name='stock_detail'),

    path('angelStockListing/', angelStockListing, name='angelStockListing'),

    # urls.py
    path('balance_sheet/<int:stock_id>/', balance_sheet_view, name='balance_sheet'),

    ]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
