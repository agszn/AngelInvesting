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
        path('SellerSummaryST/', SellerSummaryST, name='SellerSummaryST'),
        path('sellDealLetterrST/', sellDealLetterrST, name='sellDealLetterrST'),
        path('clientST/', clientST, name='clientST'),
        
        path('transaction/<int:pk>/edit/', edit_buy_transaction, name='edit_transaction'),
        
    ]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
