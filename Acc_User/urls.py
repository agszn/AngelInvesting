from unicodedata import name
from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

from django.conf import settings
from django.conf.urls.static import static


app_name = 'Acc_User'

urlpatterns = [
        path('dashboardAcc/', dashboardAcc, name='dashboardAcc'),
        path('ordersAcc/', ordersAcc, name='ordersAcc'),
        path('buyorderAcc/', buyorderAcc, name='buyorderAcc'),
        path('sellorderAcc/', sellorderAcc, name='sellorderAcc'),
        path('unlistedSharesAcc/', unlistedSharesAcc, name='unlistedSharesAcc'),
        path('ShareListAcc/', ShareListAcc, name='ShareListAcc'),
        path('clientAcc/', clientAcc, name='clientAcc'),
        path('reportsAcc/', reportsAcc, name='reportsAcc'),
        
        path('buyOrderSummaryAcc/<str:order_id>/', buyOrderSummaryAcc, name='buyOrderSummaryAcc'),
        path('SellerSummaryAcc/', SellerSummaryAcc, name='SellerSummaryAcc'),
        path('AngelInvestAcc/', AngelInvestAcc, name='AngelInvestAcc'),
        
        path('transaction/<int:pk>/edit/', edit_buy_transaction, name='edit_transaction'),
        
    ]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
