from unicodedata import name
from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

from django.conf import settings
from django.conf.urls.static import static


app_name = 'SM_User'

urlpatterns = [
        path('BlogSM/', BlogSM, name='BlogSM'),
        path('HomepageBannerSM/upload/', HomepageBannerSM, name='HomepageBannerSM'),
        
        path('banner/delete/', delete_banner, name='delete_banner'),

        path('UnlistedStocksUpdateSM/', UnlistedStocksUpdateSM, name='UnlistedStocksUpdateSM'),
        
        path('unlisted-stocks/download-csv/', download_unlisted_stocks_csv, name='download_unlisted_stocks_csv'),

        path('unlisted-stocks/upload-csv/', upload_unlisted_stocks_csv, name='upload_unlisted_stocks_csv'),
    ]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
