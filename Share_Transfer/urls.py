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
        path('buyOrderSummaryST/', buyOrderSummaryST, name='buyOrderSummaryST'),
        path('buyDealLetterrST/', buyDealLetterrST, name='buyDealLetterrST'),
        path('sellorderST/', sellorderST, name='sellorderST'),
        path('SellerSummaryST/', SellerSummaryST, name='SellerSummaryST'),
        path('sellDealLetterrST/', sellDealLetterrST, name='sellDealLetterrST'),
        path('clientST/', clientST, name='clientST'),
        
    ]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
