from unicodedata import name
from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
    path('', base , name='base'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('verify-email/<int:user_id>/', verify_email, name='verify_email'),
    path('resend-otp/<int:user_id>/', resend_otp, name='resend_otp'),

    path('logout/', logout_view, name='logout'),

    # profile
    path('profile/', view_profile, name='profile'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('download/cmr/<int:cmr_id>/', download_cmr_file, name='download_cmr_file'),
    # contact
    path('contact/', contact, name='contact'),
    path('contactView/', contact_view, name='contactView'),

    # about
    path('about/', about, name='about'),

    # faq
    path('faq/',faq,name='faq'),
    
    # blog
    path('blog/',blog,name='blog'),
    
    path('manage-users/', manage_user_types, name='manage_user_types'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)