from unicodedata import name
from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

from django.conf import settings
from django.conf.urls.static import static


app_name = 'RM_User'

urlpatterns = [

        path('dashboardRM/',dashboardRM,name='dashboardRM'),
        path('buyorderRM/',buyorderRM,name='buyorderRM'),
        path('clientRM/',clientRM,name='clientRM'),
        path('ordersRM/',ordersRM,name='ordersRM'),
        path('sellorderRM/',sellorderRM,name='sellorderRM'),
        path('ShareListRM/',ShareListRM,name='ShareListRM'),
        path('unlistedSharesRM/',unlistedSharesRM,name='unlistedSharesRM'),
        path('angelInvestRM/',angelInvestRM,name='angelInvestRM'),
        path('ReportRM/',ReportRM,name='ReportRM'),
        

        path('buyordersummary/<str:order_id>/', buyordersummeryRM, name='buyordersummery'),
        
        path('selldersummeryRM/<str:order_id>/',selldersummeryRM,name='selldersummeryRM'),
        
        path('payment/add/<str:order_id>/', add_or_edit_payment, name='add_payment'),
        path('payment/edit/<int:payment_id>/', add_or_edit_payment, name='edit_payment'),
        
        path('payment/delete/<int:payment_id>/',delete_payment, name='delete_payment'),
        
        path('transaction/<int:pk>/edit/', edit_buy_transaction, name='edit_transaction'),
        
        path('transaction/<int:pk>/edit/ajax/', ajax_transaction_handler, name='ajax_transaction_handler'),

        path('sell-transaction/<int:pk>/edit/ajax/', ajax_sell_transaction_handler, name='ajax_sell_transaction_handler'),



        path('transaction/<int:pk>/delete/', delete_buy_transaction, name='delete_transaction'),
        
        path('AllbuyTransactionSummary/',AllbuyTransactionSummary,name='AllbuyTransactionSummary'),


        path('AllsellTransactionSummary/',AllsellTransactionSummary,name='AllsellTransactionSummary'),

        path('edit-sell-transaction/<int:pk>/', edit_sell_transaction, name='edit_sell_transaction'),


            
    ]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
