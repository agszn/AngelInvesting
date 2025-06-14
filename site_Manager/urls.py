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
        
        path('upload_unlisted_stocks_excel/', upload_unlisted_stocks_excel, name='upload_unlisted_stocks_excel'),
        
        path('unlisted-stocks/download-csv/', download_unlisted_stocks_csv, name='download_unlisted_stocks_csv'),

        path('unlisted-stocks/upload-csv/', upload_unlisted_stocks_csv, name='upload_unlisted_stocks_csv'),
        
        path('custom-fields/', custom_field_list, name='custom_field_list'),
        path('custom-fields/new/', custom_field_create, name='custom_field_create'),
        path('custom-fields/<int:pk>/edit/', custom_field_edit, name='custom_field_edit'),
        
        path('brokers/', BrokerListView.as_view(), name='broker-list'),
        path('brokers/add/', BrokerCreateView.as_view(), name='broker-add'),
        path('brokers/edit/<int:pk>/', BrokerUpdateView.as_view(), name='broker-edit'),
        path('brokers/delete/<int:pk>/', BrokerDeleteView.as_view(), name='broker-delete'),

        # urls.py
        path('advisor-types/', AdvisorTypeListView.as_view(), name='advisor-type-list'),
        path('advisor-types/add/', AdvisorTypeCreateView.as_view(), name='advisor-type-add'),
        path('advisor-types/delete/<int:pk>/', AdvisorTypeDeleteView.as_view(), name='advisor-type-delete'),

    ]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
