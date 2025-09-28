from unicodedata import name
from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

from django.conf import settings
from django.conf.urls.static import static


app_name = 'SM_User'

urlpatterns = [
        path('blogs/', BlogSM, name='BlogSM'),
        path('blogs/create/', create_blog, name='create_blog'),
        path('blogs/<int:blog_id>/edit/', edit_blog, name='edit_blog'),
        path('blogs/<int:blog_id>/delete/', delete_blog, name='delete_blog'),
        path('blogs/<int:blog_id>/', blog_detail_view_SM, name='SM_blog_detail'),
        
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
        
        path('stockdata/', stockdata_crud, name='stockdata_crud'),
        path("stock/new/", create_stockdata, name="create_stockdata"),
        path('<int:pk>/edit/', edit_stockdata, name='edit_stockdata'),
        path("stock/<int:pk>/delete/", delete_stockdata, name="stockdata_delete"),
        
        path("stock/<int:pk>/edit-overview/", edit_company_overview, name="edit_company_overview"),
        path("stock/<int:pk>/edit-outlooks/", edit_outlooks, name="edit_outlooks"),
        path("stock/<int:pk>/edit-shareholding-note/", edit_shareholding_note, name="edit_shareholding_note"),
        
        # site_Manager/urls.py
        path('convert/', convert_docx_to_html, name='convert_docx_to_html'),
        











        # View grouped stock + model overview
        path('custom-values/', stock_model_overview, name='custom_value_list'),

        # View all values for a definition
        path('custom-values/<int:def_id>/', values_for_definition, name='custom_value_detail'),

        
        path('custom-values/add/', add_custom_value, name='add_custom_value'),
        path('custom-values/update/<int:pk>/', update_custom_value, name='update_custom_value'),
        
        path('custom-values/delete/<int:pk>/', delete_custom_value, name='delete_custom_value'),
        
        path('custom-values/bulk/', bulk_upload_values, name='bulk_upload_values'),
        
        path('custom-values/reorder/', reorder_custom_values, name='reorder_custom_values'),












        # history start 
        path("history/", stockhistory_list, name="Historylist"),
        path("history/new/", stockhistory_create, name="Historycreate"),
        path("stocks/<int:stock_id>/history/", stockhistory_list, name="Historylist_by_stock"),
        path("stocks/<int:stock_id>/history/new/", stockhistory_create, name="Historycreate_for_stock"),

        path("history/<int:pk>/", stockhistory_detail, name="Historydetail"),
        path("history/<int:pk>/edit/", stockhistory_update, name="Historyupdate"),
        path("history/<int:pk>/delete/", stockhistory_delete, name="Historydelete"),
        

        # Events
        path("event_list/", event_list, name="event_list"),
        path("<int:pk>/", event_detail, name="event_detail"),
        path("create/", event_create, name="event_create"),
        path("<int:pk>/update/", event_update, name="event_update"),
        path("<int:pk>/delete/", event_delete, name="event_delete"),
        
        path("events/<int:pk>/download/", event_pdf, name="event_pdf"),

    ]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
