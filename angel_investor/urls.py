"""
URL configuration for angel_investor project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('adminDFRMACSTA/', admin.site.urls),
    path('',include('user_auth.urls')),
    path('marketplace/',include('unlisted_stock_marketplace.urls')),
    path('portfolio/',include('user_portfolio.urls')),
    
    path('Acc_User/',include('Acc_User.urls')),
    path('RM_User/',include('RM_User.urls')),
    path('ST_User/',include('Share_Transfer.urls')),
    path('SM_User/',include('site_Manager.urls')),
]
