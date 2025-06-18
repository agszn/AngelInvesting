from unicodedata import name
from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

from django.conf import settings
from django.conf.urls.static import static

app_name = 'ST_User'

urlpatterns = [
        path('dashboardST/', dashboardST, name='dashboardST'),
        
        path('buyorderST/', buyorderST, name='buyorderST'),
        
        path('buyOrderSummaryST/<str:order_id>/', buyOrderSummaryST, name='buyOrderSummaryST'),
        
        path('buyDealLetterrST/', buyDealLetterrST, name='buyDealLetterrST'),
        
        path('sellorderST/', sellorderST, name='sellorderST'),
        
        path('SellerSummaryST/<str:order_id>/', SellerSummaryST, name='SellerSummaryST'),
        

        path('edit-sell-transaction/<int:pk>/', edit_sell_transactionST, name='edit_sell_transactionST'),
        
        path('sellDealLetterrST/', sellDealLetterrST, name='sellDealLetterrST'),
        path('clientST/', clientST, name='clientST'),
        
        path('transaction/<int:pk>/edit/', edit_buy_transactionST, name='edit_transactionST'),
        
    ]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
