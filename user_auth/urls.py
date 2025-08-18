# user_auth/urls.py
from unicodedata import name
from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
    path('', base , name='base'),
    path('tst/',tst,name='tst'),
    
    path('stocks/autocomplete/', stock_autocomplete, name='stock_autocomplete'),

    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('verify-email/<int:user_id>/', verify_email, name='verify_email'),
    path('resend-otp/<int:user_id>/', resend_otp, name='resend_otp'),

    path('logout/', logout_view, name='logout'),

    # the below form is for the user to update their user type
    # and it is not used in the admin panel
    # and the below is test and temporary updates
    # start - 02082025 => secure "Forgot Password" flow using OTP delivered via email.
    path('forgot-password/', forgot_password_view, name='forgot_password'),
    path('verify-otp-reset/<int:user_id>/', verify_otp_for_reset_view, name='verify_otp_reset'),
    path('reset-password/<int:user_id>/', reset_password_view, name='reset_password'),
    # end - 02082025 => secure "Forgot Password" flow using OTP delivered via email.

    #  -------------------------------------------
    #  -------------------------------------------


    # start - 02082025 -> Phase 2: Change Password (Phone Number) from Profile Page, with OTP verification via email for now.


    path('change-phone/', initiate_phone_change, name='change_phone'),
    path('verify-phone-otp/', verify_phone_change_otp, name='verify_phone_otp'),

    # end - 02082025 -> Phase 2: Change Password (Phone Number) from Profile Page, with OTP verification via email for now.

    # profile
    path('profile/', view_profile, name='profile'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    # bank
    path('bank-details/', bankAccDetails, name='bank-details'),
    path('save-bank-account/', save_bank_account, name='save_bank_account'),
    path('get-bank-account/<int:bank_id>/', get_bank_account, name='get-bank-account'),
    path('delete-bank-account/<int:bank_id>/', delete_bank_account, name='delete_bank_account'),


    # CMR
    path('delete-cmr/<int:cmr_id>/', delete_cmr, name='delete_cmr'),
    path('download-cmr/<int:cmr_id>/', download_cmr_file, name='download_cmr_file'),

    # contact
    path('contact/', contact, name='contact'),
    path('contactView/', contact_view, name='contactView'),

    # about
    path('about/', about, name='about'),

    # terms
    path('terms/', terms, name='terms'),

    # privacy
    path('privacy/', privacy, name='privacy'),

    # disclaimer
    path('disclaimer/', disclaimer, name='disclaimer'),
    
    # faq
    path('faq/',Gendral_User_FAQ, name='faq'),
    
    # user blog
    path('blog/',blog,name='blog'),
    path('blog_Details/<int:blog_id>/', user_blog_detail_view, name='user_blog_detail'),
    path('manage-users/', manage_user_types, name='manage_user_types'),
    


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)