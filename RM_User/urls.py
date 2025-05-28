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
        
        path('buyordersummeryRM/',buyordersummeryRM,name='buyordersummeryRM'),        
        
        path('selldersummeryRM/',selldersummeryRM,name='selldersummeryRM'),
        
    ]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
