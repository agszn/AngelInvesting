from unicodedata import name
from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

from django.conf import settings
from django.conf.urls.static import static

app_name = 'user_portfolio'

urlpatterns = [
    
    path('',profile_overview,name='profile_overview'),
    path('unlisted_view/',unlisted_view,name='unlisted_view'),
    path('angel_invest/',angel_invest,name='angel_invest'),
    path('portfolio_view/',portfolio_view,name='portfolio_view'),
    path('buy_orders/',buy_orders,name='buy_orders'),
    path('sell_orders/',sell_orders,name='sell_orders'),
    
    # user_portfolio.urls
    path('buy_stock/<int:stock_id>/', buy_stock, name='buy_stock'),
    path('sell_stock/<int:stock_id>/', sell_stock, name='sell_stock'),
    
    path('load-advisors-brokers/', load_advisors_brokers, name='load_advisors_brokers'),

    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
