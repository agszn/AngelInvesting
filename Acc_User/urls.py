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
        
        path('SellerSummaryAcc/<str:order_id>/', SellerSummaryAcc, name='SellerSummaryAcc'),
        
        path('AngelInvestAcc/', AngelInvestAcc, name='AngelInvestAcc'),
        
        path('transaction/<int:pk>/edit/', edit_buy_transactionAcc, name='edit_transactionAcc'),
        
        path('edit-sell-transaction/<int:pk>/', edit_sell_transactionAcc, name='edit_sell_transactionAcc'),
        
        path('payment/ac_status/edit/<int:payment_id>/', edit_payment_ac_status, name='edit_payment_ac_status'),
        
        path('edit-ac-status/<int:transaction_id>/', edit_transaction_ac_status, name='edit_transaction_ac_status'),
        
        path('edit-sell-ac-status/<int:transaction_id>/', edit_sell_transaction_ac_status, name='edit_sell_transaction_ac_status'),

                        
    ]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
