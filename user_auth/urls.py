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
    path('profile/', view_profile, name='view_profile'),
    path('profile/edit/', edit_profile, name='edit_profile'),

    # contact
    path('contact/', contact, name='contact'),
    path('contactView/', contact_view, name='contactView'),

    # about
    path('about/', about, name='about'),

    # faq
    path('faq/',faq,name='faq'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)