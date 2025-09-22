from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator

from .forms import *
from .models import *
from .utils import *

from site_Manager.models import *

from unlisted_stock_marketplace.forms import *
from unlisted_stock_marketplace.models import *
from unlisted_stock_marketplace.utils import *

from django.core.mail import send_mail
from django.conf import settings
import uuid
from django.db.models import Q

from django.http import FileResponse, Http404
from django.forms import inlineformset_factory


from .utils import parse_user_date

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from .models import CustomUser
from .forms import UserTypeUpdateForm

from .otp_delivery import send_otp

def is_admin_or_site_manager(user):
    return user.user_type in ['AD', 'SM']


import json
from site_Manager.models import Broker, Advisor

def tst(request):
    brokers = Broker.objects.values('id', 'name')
    advisors = Advisor.objects.values('id', 'advisor_type')
    return render(request, 'testBuySell.html', {
        'global_brokers_json': json.dumps(list(brokers)),
        'global_advisors_json': json.dumps(list(advisors)),
    })

from django.http import JsonResponse

def stock_autocomplete(request):
    query = request.GET.get('term', '')
    results = list(
        StockData.objects.filter(company_name__icontains=query)
        .values_list('company_name', flat=True)[:10]
    )
    return JsonResponse(results, safe=False)

# @login_required
# @user_passes_test(is_admin_or_site_manager)
# def manage_user_types(request):
#     query = request.GET.get('q', '')
#     users = CustomUser.objects.exclude(user_type='AD')
#     if query:
#         users = users.filter(username__icontains=query) | users.filter(email__icontains=query)

#     if request.method == 'POST':
#         user_id = request.POST.get('user_id')
#         new_type = request.POST.get('user_type')
#         user = get_object_or_404(CustomUser, id=user_id)
#         user.user_type = new_type
#         user.save()
#         return redirect('manage_user_types')

#     return render(request, 'SiteManageUsers/ManageUserAuth.html', {'users': users, 'query': query})


@login_required
@user_passes_test(is_admin_or_site_manager)
def manage_user_types(request):
    query = request.GET.get('q', '')

    users = CustomUser.objects.exclude(user_type='AD').order_by('-date_joined')
    rms = CustomUser.objects.filter(user_type='RM').order_by('username')

    if query:
        users = users.filter(
            Q(username__icontains=query) | Q(email__icontains=query)
        )

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        new_type = request.POST.get('user_type')
        assigned_rm_id = request.POST.get('assigned_rm')

        user = get_object_or_404(CustomUser, id=user_id)
        user.user_type = new_type

        if assigned_rm_id:
            user.assigned_rm_id = assigned_rm_id
        else:
            user.assigned_rm = None

        user.save()
        return redirect('manage_user_types')

    # ✅ Ensure every user has login_records
    for u in users:
        if not hasattr(u, "login_records"):
            u.login_records = []

    return render(request, 'SiteManageUsers/ManageUserAuth.html', {
        'users': users,
        'rms': rms,
        'query': query,
    })



from django.shortcuts import render
from site_Manager.models import HeroSectionBanner, Blog
from unlisted_stock_marketplace.models import StockData

def base(request):
    # Homepage banner
    banner = HeroSectionBanner.objects.filter(is_active=True).first()
    
    # Stocks data with percentage diff
    stocks = StockData.objects.all()
    for stock in stocks:
        if stock.ltp and stock.share_price and stock.share_price > 0:
            stock.percentage_diff = ((stock.ltp - stock.share_price) / stock.share_price) * 100
        else:
            stock.percentage_diff = None

    # Fetch latest 3 blogs
    latest_blogs = Blog.objects.all().order_by('-date', '-time')[:3]


    rms = CustomUser.objects.filter(user_type='RM', phone_number__isnull=False)
    
    return render(request, "base.html", {
        "stocks": stocks,
        "banner": banner,
        "latest_blogs": latest_blogs,

        'rms': rms
    })


# 
# 
# ---------------------------------------------------------------------
# ---------------------------- User Authentication ------------------------
# -------------------------------------------------------------------
# 
# 
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Require email/OTP verification
            user.otp = str(uuid.uuid4().int)[0:6]  # 6-digit OTP

            # Check for phone number explicitly
            if user.phone_number:
                user.set_password(user.phone_number)
            else:
                form.add_error('phone_number', "Phone number is required.")
                messages.error(request, "Phone number is required.")
                return render(request, 'Authentication/register.html', {'form': form})

            user.save()

            # Send OTP to email
            send_mail(
                'Verify Your Account',
                f'Your OTP for verification is: {user.otp}',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
            
            # Send OTP via Twilio
            send_otp(user, f'Your OTP for verification is: {user.otp}')

            messages.success(request, "Check your email for the OTP to verify your account.")
            return redirect('verify_email', user_id=user.id)
        else:
            # Show generic error message
            messages.error(request, "Please fix the errors below and try again.")
            messages.error(request, form.errors)
    else:
        form = CustomUserCreationForm()

    return render(request, 'Authentication/register.html', {'form': form})



def resend_otp(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    # Regenerate OTP
    user.otp = str(uuid.uuid4().int)[0:6]
    user.save()

    # Send OTP to email
    send_mail(
        'Verify Your Account',
        f'Your OTP for verification is: {user.otp}',
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False,
    )
    
    # Send OTP via Twilio
    send_otp(user, f'Your OTP for verification is: {user.otp}')

    messages.success(request, "A new OTP has been sent to your email.")
    return redirect('verify_email', user_id=user.id)

# Email Verification View
def verify_email(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    if request.method == 'POST':
        otp_entered = request.POST.get('otp')
        if otp_entered == user.otp:
            user.is_active = True
            user.otp = None  # Clear the OTP
            user.save()
            messages.success(request, "Email verified! You can now log in.")
            return redirect('login')
        else:
            messages.error(request, "Invalid OTP. Try again.")
    
    return render(request, 'Authentication/verify_email.html', {'user': user})

# Login View
from django.shortcuts import redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .forms import LoginForm  # assuming you have a custom LoginForm


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # messages.success(request, "Login successful!")

            # Superuser redirect
            if user.is_superuser:
                return redirect('SM_User:UnlistedStocksUpdateSM')

            # Redirect based on user_type
            user_type = getattr(user, 'user_type', None)

            if user_type == 'RM':
                return redirect('RM_User:dashboardRM')  # Replace with your actual URL name
            elif user_type == 'AC':
                return redirect('Acc_User:dashboardAcc')
            elif user_type == 'SM'  or user_type == 'AD':
                return redirect('SM_User:UnlistedStocksUpdateSM')
            elif user_type == 'DF':
                return redirect('base')
            elif user_type == 'ST':
                return redirect('ST_User:dashboardST')
            # elif user_type == 'AP':
            #     return redirect('associate_partner_dashboard')
            # elif user_type == 'PT':
            #     return redirect('partner_dashboard')
            else:
                return redirect('base')  # default fallback

    else:
        form = LoginForm()
    
    return render(request, 'Authentication/login.html', {'form': form})


# Logout View
@login_required
def logout_view(request):
    logout(request)
    # messages.success(request, "Logged out successfully.")
    return redirect('login')

# the below form is for the user to update their user type
# and it is not used in the admin panel
# and the below is test and temporary updates
# start - 02082025 => secure "Forgot Password" flow using OTP delivered via email.

from .forms import ForgotPasswordForm, OTPVerificationForm, ResetPasswordForm
from django.utils import timezone
import uuid

# ---------- View ----------
def forgot_password_view(request):
    if request.method == "POST":
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            parsed = form.cleaned_data["email_or_phone"]

            if parsed["type"] == "email":
                user = CustomUser.objects.filter(email__iexact=parsed["value"]).first()
            else:  # phone
                # Adjust field name to your model (e.g., 'phone', 'mobile', etc.)
                user = CustomUser.objects.filter(phone_number=parsed["value"]).first()

            if user:
                # ✅ Generate and save OTP
                user.otp = str(uuid.uuid4().int)[:6]

                # Save fields safely
                fields_to_update = ["otp"]
                if hasattr(user, "otp_created_at"):  # only if model has it
                    user.otp_created_at = timezone.now()
                    fields_to_update.append("otp_created_at")

                user.save(update_fields=fields_to_update)



                # Send OTP via the chosen channel
                if parsed["type"] == "email":
                    send_mail(
                        subject="Verify Your Account",
                        message=f"Your OTP for verification is: {user.otp}",
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[user.email],
                        fail_silently=False,
                    )
                    messages.success(request, "An OTP has been sent to your email.")
                else:
                    # Reuse your existing Twilio helper; make sure it uses user.phone_number
                    send_otp(user, f"Your OTP for verification is: {user.otp}")
                    messages.success(request, "An OTP has been sent to your phone number.")

                return redirect("verify_otp_reset", user_id=user.id)
            else:
                # If you prefer not to reveal whether the account exists, replace with a generic message.
                form.add_error(None, "No user found with this email or phone number.")
    else:
        form = ForgotPasswordForm()

    return render(
        request,
        "Authentication/ForgotPassword/forgot_password.html",
        {"form": form},
    )

# OTP Verification - Step 2
def verify_otp_for_reset_view(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            otp_entered = form.cleaned_data['otp']
            if otp_entered == user.otp:
                messages.success(request, "OTP verified. Now set a new password.")
                return redirect('reset_password', user_id=user.id)
            else:
                messages.error(request, "Invalid OTP.")
    else:
        form = OTPVerificationForm()
    return render(request, 'Authentication/ForgotPassword/verify_otp_reset.html', {'form': form})

# Password Reset - Step 3
def reset_password_view(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_phone = form.cleaned_data['new_phone_number']
            user.phone_number = new_phone
            user.set_password(new_phone)
            user.otp = None
            user.save()
            messages.success(request, "Password reset successfully. You can now log in.")
            return redirect('login')
    else:
        form = ResetPasswordForm()
    return render(request, 'Authentication/ForgotPassword/reset_password.html', {'form': form})

# end - 02082025 => secure "Forgot Password" flow using OTP delivered via email.

#  -------------------------------------------
#  -------------------------------------------


# start - 02082025 -> Phase 2: Change Password (Phone Number) from Profile Page, with OTP verification via email for now.


from .forms import ChangePhoneNumberForm, OTPConfirmationForm
from django.contrib.auth.decorators import login_required
import uuid

# Step 1 – initiate phone number change
@login_required
def initiate_phone_change(request):
    if request.method == 'POST':
        form = ChangePhoneNumberForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['new_phone_number']
            request.session['new_phone'] = phone
            otp = str(uuid.uuid4().int)[:6]
            request.session['phone_change_otp'] = otp

            # Send OTP to current user email for now
            # send_mail(
            #     "OTP to Confirm New Phone Number",
            #     f"Your OTP to change your phone number is: {otp}",
            #     settings.EMAIL_HOST_USER,
            #     [request.user.email],
            #     fail_silently=False,
            # )
            
            send_otp(request.user, f"Your OTP to confirm phone number change is: {otp}")

            messages.success(request, "OTP sent to your registered email.")
            return redirect('verify_phone_otp')
    else:
        form = ChangePhoneNumberForm()
    return render(request, 'Authentication/updatePassword/change_phone.html', {'form': form})


# Step 2 – verify OTP and update phone/password
@login_required
def verify_phone_change_otp(request):
    if request.method == 'POST':
        form = OTPConfirmationForm(request.POST)
        if form.is_valid():
            entered_otp = form.cleaned_data['otp']
            correct_otp = request.session.get('phone_change_otp')
            new_phone = request.session.get('new_phone')

            if entered_otp == correct_otp:
                user = request.user
                user.phone_number = new_phone
                user.set_password(new_phone)
                user.save()

                # Cleanup
                request.session.pop('phone_change_otp', None)
                request.session.pop('new_phone', None)

                messages.success(request, "Phone number & password updated successfully.")
                return redirect('login')
            else:
                messages.error(request, "Invalid OTP.")
    else:
        form = OTPConfirmationForm()
    return render(request, 'Authentication/updatePassword/verify_phone_otp.html', {'form': form})


# end - 02082025 -> Phase 2: Change Password (Phone Number) from Profile Page, with OTP verification via email for now.


# 
# ---------------------------------------
# ------------ Profile ----------------------
# ------------------------------------------
# 
# 

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import UserProfile
from .forms import UserProfileForm  # we'll create this form next

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile
from .forms import UserProfileForm
from site_Manager.models import Broker 

# @login_required
# def view_profile(request):
#     profile, _ = UserProfile.objects.get_or_create(user=request.user)

#     if request.method == 'POST':
#         form = UserProfileForm(request.POST, request.FILES, instance=profile)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Profile updated successfully.")
#             return redirect('profile')  # avoid form resubmission
#         else:
#             messages.error(request, "Please correct the errors below.")
#     else:
#         form = UserProfileForm(instance=profile)

#     return render(request, 'accounts/profile.html', {'profile': profile, 'form': form})

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import UserProfile, Broker, CMRCopy
from .forms import UserProfileForm, CMRForm

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import UserProfile, Broker, CMRCopy
from .forms import UserProfileForm, CMRForm  # assuming you have these forms
# @login_required
# def view_profile(request):
#     profile, _ = UserProfile.objects.get_or_create(user=request.user)
#     brokers = Broker.objects.all()
#     cmr_copies = CMRCopy.objects.filter(user_profile=profile)

#     form = UserProfileForm(instance=profile)
#     cmr_form = CMRForm()

#     if request.method == 'POST':
#         form_type = request.POST.get('form_type')

        
#     if request.method == 'POST':
#         form_type = request.POST.get('form_type')

#         if form_type == 'cmr_form':
#             cmr_id = request.POST.get('cmr_id')
#             broker_id = request.POST.get('broker_id')
#             broker_id_input = request.POST.get('broker_id_input')
#             client_id_input = request.POST.get('client_id_input')
#             cmr_file = request.FILES.get('cmr_file')

#             if not broker_id:
#                 messages.error(request, "Broker selection is required.")
#                 return redirect('profile')

#             broker = Broker.objects.filter(id=broker_id).first()
#             if not broker:
#                 messages.error(request, "Invalid broker selected.")
#                 return redirect('profile')

#             # Create or update CMR copy
#             if cmr_id:
#                 cmr = CMRCopy.objects.filter(pk=cmr_id, user_profile=profile).first()
#                 if not cmr:
#                     messages.error(request, "CMR copy not found.")
#                     return redirect('profile')
#             else:
#                 cmr = CMRCopy(user_profile=profile)

#             cmr.broker = broker
#             cmr.broker_id_input = broker_id_input
#             cmr.client_id_input = client_id_input
#             if cmr_file:
#                 cmr.cmr_file = cmr_file
#             cmr.save()

#             messages.success(request, f"CMR copy {'updated' if cmr_id else 'added'} successfully.")
#             return redirect('profile')

#         elif form_type == 'profile_form':
#             form = UserProfileForm(request.POST, request.FILES, instance=profile)
#             if form.is_valid():
#                 form.save()
#                 messages.success(request, "Profile updated successfully.")
#                 return redirect('profile')
#             else:
#                 messages.error(request, "Please correct the errors below.")

#     return render(request, 'accounts/profile.html', {
#         'profile': profile,
#         'form': form,
#         'cmr_form': cmr_form,
#         'brokers': brokers,
#         'cmr_copies': cmr_copies,
#     })

# user_auth/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile, Broker, CMRCopy
from .forms import UserProfileForm, CMRForm

# @login_required
# def view_profile(request):
#     user = request.user
#     profile, _ = UserProfile.objects.get_or_create(user=user)
#     brokers = Broker.objects.all()
#     cmr_copies = CMRCopy.objects.filter(user_profile=profile)

#     form = UserProfileForm(instance=profile)
#     cmr_form = CMRForm()

#     if request.method == 'POST':
#         form_type = request.POST.get('form_type')

#         if form_type == 'cmr_form':
#             cmr_id = request.POST.get('cmr_id')
#             if cmr_id:
#                 cmr_instance = get_object_or_404(CMRCopy, id=cmr_id, user_profile=profile)
#                 cmr_form = CMRForm(request.POST, request.FILES, instance=cmr_instance)
#             else:
#                 cmr_form = CMRForm(request.POST, request.FILES)

#             if cmr_form.is_valid():
#                 cmr = cmr_form.save(commit=False)
#                 cmr.user_profile = profile
#                 cmr.save()
#                 messages.success(request, "CMR record saved successfully.")
#                 return redirect('profile')
#             else:
#                 messages.error(request, "Please correct the errors in the CMR form.")
        
#         else:
#             form = UserProfileForm(request.POST, request.FILES, instance=profile)
#             if form.is_valid():
#                 form.save()
#                 messages.success(request, "Profile updated.")
#                 return redirect('profile')
#             else:
#                 messages.error(request, "Please correct the errors in the profile form.")

#     context = {
#         'form': form,
#         'cmr_form': cmr_form,
#         'brokers': brokers,
#         'cmr_copies': cmr_copies,
#         'profile': profile,
#     }
#     return render(request, 'accounts/profile.html', context)


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Exists, OuterRef, Subquery

from .models import UserProfile, CMRCopy, Broker
from .forms import UserProfileForm, CMRForm
from unlisted_stock_marketplace.models import StockData, Wishlist, WishlistGroup

from django.db.models import IntegerField

# @login_required
# def view_profile(request):
#     user = request.user
#     profile, _ = UserProfile.objects.get_or_create(user=user)
#     brokers = Broker.objects.all()
#     cmr_copies = CMRCopy.objects.filter(user_profile=profile)

#     form = UserProfileForm(instance=profile)
#     cmr_form = CMRForm()

#     # --- Handle POST for Profile or CMR ---
#     if request.method == 'POST':
#         form_type = request.POST.get('form_type')

#         if form_type == 'cmr_form':
#             cmr_id = request.POST.get('cmr_id')
#             if cmr_id:
#                 cmr_instance = get_object_or_404(CMRCopy, id=cmr_id, user_profile=profile)
#                 cmr_form = CMRForm(request.POST, request.FILES, instance=cmr_instance)
#             else:
#                 cmr_form = CMRForm(request.POST, request.FILES)

#             if cmr_form.is_valid():
#                 cmr = cmr_form.save(commit=False)
#                 cmr.user_profile = profile
#                 cmr.save()
#                 messages.success(request, "CMR record saved successfully.")
#                 return redirect('profile')
#             else:
#                 messages.error(request, "Please correct the errors in the CMR form.")

#         else:
#             form = UserProfileForm(request.POST, request.FILES, instance=profile)
#             if form.is_valid():
#                 form.save()
#                 messages.success(request, "Profile updated.")
#                 return redirect('profile')
#             else:
#                 messages.error(request, "Please correct the errors in the profile form.")

#     # --- Wishlist/Unlisted/Angel Stocks Logic ---
#     show_all_unlisted = request.GET.get("unlisted") == "1"
#     show_all_angel = request.GET.get("angel") == "1"
#     group_id = request.GET.get("group")
#     search_query = request.GET.get("search", "")

#     if group_id:
#         group = get_object_or_404(WishlistGroup, id=group_id, user=user)
#         wishlist_stocks = Wishlist.objects.filter(group=group).values_list("stock", flat=True)
#         stock_list = StockData.objects.filter(id__in=wishlist_stocks)
#     elif show_all_angel:
#         stock_list = StockData.objects.filter(stock_type__iexact="angel")
#     else:
#         # Default to unlisted if nothing specified
#         stock_list = StockData.objects.filter(stock_type__iexact="unlisted")
#         show_all_unlisted = True

#     if search_query:
#         stock_list = stock_list.filter(
#             Q(company_name__istartswith=search_query) |
#             Q(scrip_name__istartswith=search_query)
#         )

#     stock_list = stock_list.annotate(
#         in_group=Exists(
#             Wishlist.objects.filter(stock=OuterRef('pk'), group__user=user)
#         ),
#         group_number=Subquery(
#             Wishlist.objects.filter(stock=OuterRef('pk'), group__user=user)
#             .values('group__name')[:1]
#         ),
#         wishlist_id=Subquery(
#         Wishlist.objects.filter(stock=OuterRef('pk'), group__user=user)
#         .values('id')[:1],
#         output_field=IntegerField()
#     )
#     )

#     groups = WishlistGroup.objects.filter(user=user)

#     context = {
#         'form': form,
#         'cmr_form': cmr_form,
#         'brokers': brokers,
#         'cmr_copies': cmr_copies,
#         'profile': profile,

#         # Stock data
#         'stock_list': stock_list,
#         'groups': groups,
#         'show_all_unlisted': show_all_unlisted,
#         'show_all_angel': show_all_angel,
#         'search_query': search_query,
#     }

#     return render(request, 'accounts/profile.html', context)
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from user_portfolio.utils import get_user_stock_context

def _push_form_errors(request, form, prefix=None):
    for field, errors in form.errors.items():
        label = form.fields.get(field).label or field.replace('_',' ').title()
        for e in errors:
            messages.error(request, f"{prefix + ': ' if prefix else ''}{label}: {e}")
    for e in form.non_field_errors():
        messages.error(request, f"{prefix + ': ' if prefix else ''}{e}")

@login_required
def view_profile(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)
    brokers = Broker.objects.all()
    cmr_copies = CMRCopy.objects.filter(user_profile=profile)

    # Safer PDF flags
    pan_name = (profile.pan_card_photo.name or "") if profile.pan_card_photo else ""
    aadhaar_name = (profile.adhar_card_photo.name or "") if profile.adhar_card_photo else ""
    profile.is_pan_pdf = pan_name.lower().endswith(".pdf")
    profile.is_aadhaar_pdf = aadhaar_name.lower().endswith(".pdf")

    form = UserProfileForm(instance=profile)
    cmr_form = CMRForm()
    last_form_type = ""

    if request.method == 'POST':
        form_type = request.POST.get('form_type')  # 'personal' | 'identity' | 'cmr_form'
        last_form_type = form_type or ""

        if form_type == 'cmr_form':
            cmr_id = request.POST.get('cmr_id')
            if cmr_id:
                cmr_instance = get_object_or_404(CMRCopy, id=cmr_id, user_profile=profile)
                cmr_form = CMRForm(request.POST, request.FILES, instance=cmr_instance)
            else:
                cmr_form = CMRForm(request.POST, request.FILES)

            if cmr_form.is_valid():
                cmr = cmr_form.save(commit=False)
                cmr.user_profile = profile
                cmr.save()
                messages.success(request, "CMR record saved successfully.")
                return redirect('profile')
            else:
                messages.error(request, "Please correct the errors in the CMR form.")
                _push_form_errors(request, cmr_form, prefix="CMR")

        else:
            # Define sections
            identity_fields = [
                "pan_number","pan_card_photo","pan_doc_password",
                "adhar_number","adhar_card_photo","adhar_doc_password"
            ]
            personal_fields = [
                "first_name","middle_name","last_name","email",
                "whatsapp_number","mobile_number","photo"
            ]
            allowed = personal_fields if form_type == 'personal' else identity_fields

            # Build a form instance but keep ONLY the active section's fields
            form = UserProfileForm(request.POST, request.FILES, instance=profile)
            for name in list(form.fields.keys()):
                if name not in allowed:
                    del form.fields[name]

            if form.is_valid():
                form.save()  # only allowed fields are saved; others remain untouched
                messages.success(request, "Profile updated.")
                return redirect('profile')
            else:
                messages.error(request, "Please correct the errors in the profile form.")
                _push_form_errors(request, form, prefix="Profile")

    stock_context = get_user_stock_context(user, request)
    context = {
        'form': form,
        'cmr_form': cmr_form,
        'brokers': brokers,
        'cmr_copies': cmr_copies,
        'profile': profile,
        'last_form_type': last_form_type,
        **stock_context,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('view_profile')
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'accounts/edit_profile.html', {'form': form})

# 
# ------------------------------------------
# -------------------------- Bank Account Details ---------------
# ------------------------------------------
# 
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import BankAccount
from .forms import BankAccountForm  
from django.views.decorators.csrf import csrf_exempt
import json

@login_required
def bankAccDetails(request):
    user = request.user
    bank_accounts = BankAccount.objects.filter(user_profile=user.userprofile)
    return render(request, 'accounts/profile.html', {'bank_accounts': bank_accounts})

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import BankAccount


@login_required
def save_bank_account(request):
    if request.method == "POST":
        account_id = request.POST.get("account_id")
        instance = None
        if account_id:
            instance = get_object_or_404(
                BankAccount, pk=account_id, user_profile=request.user.profile
            )

        form = BankAccountForm(request.POST, request.FILES, instance=instance)

        if form.is_valid():
            bank_account = form.save(commit=False)
            bank_account.user_profile = request.user.profile
            bank_account.save()
            return redirect("profile")

        # --- invalid case ---
        return render(request, "accounts/profile.html", {
            "bank_accounts": request.user.profile.bank_accounts.all(),
            "profile": request.user.profile,

            # 👇 these three are what the template + JS use
            "bank_form_errors": form.errors.get_json_data(),
            "bank_form_post": request.POST.dict(),
            "open_bank_modal": True,
        })

    return redirect("profile")


@csrf_exempt
@login_required
def get_bank_account(request, bank_id):
    bank = get_object_or_404(BankAccount, id=bank_id, user_profile=request.user.userprofile)
    data = {
        'account_holder_name': bank.account_holder_name,
        'bank_name': bank.bank_name,
        'account_type': bank.account_type,
        'account_number': bank.account_number,
        'ifsc_code': bank.ifsc_code,
        'bankDetails_doc_password': bank.bankDetails_doc_password,
        'document_type': bank.document_type,
    }
    return JsonResponse(data)

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from .models import BankAccount


@login_required
def delete_bank_account(request, bank_id):
    profile = UserProfile.objects.get(user=request.user)
    account = get_object_or_404(BankAccount, id=bank_id, user_profile=profile)
    if request.method == 'POST':
        account.delete()
        return redirect('profile')
    return redirect('profile')

# 
# ------------------------------------------
# -------------------------- CMR ---------------
# ------------------------------------------
# 

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages



@login_required
def delete_cmr(request, cmr_id):
    cmr = get_object_or_404(CMRCopy, id=cmr_id, user_profile__user=request.user)
    if request.method == 'POST':
        cmr.delete()
        messages.success(request, "CMR record deleted successfully.")
    else:
        messages.error(request, "Invalid request method.")
    return redirect('profile')

from django.http import FileResponse, Http404

@login_required
def download_cmr_file(request, cmr_id):
    try:
        cmr = CMRCopy.objects.get(id=cmr_id, user_profile__user=request.user)
        if cmr.cmr_file:
            return FileResponse(cmr.cmr_file.open(), as_attachment=True, filename=cmr.cmr_file.name)
        else:
            raise Http404("CMR file not found.")
    except CMRCopy.DoesNotExist:
        raise Http404("CMR record not found.")

# 
# ------------------------------------------
# -------------------- Contact ---------------- 
# ------------------------------------------
# 

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import ContactForm
from .forms import ContactForm
from .models import Contact, UserProfile

def contact(request):
    initial_data = {}
    is_authenticated = request.user.is_authenticated

    if is_authenticated:
        profile = getattr(request.user, 'profile', None)
        if profile:
            name = profile.full_name()
            email = profile.email or request.user.email  # fallback to CustomUser.email if profile email not set
        else:
            name = request.user.get_full_name()
            email = request.user.email

        initial_data = {
            'name': name,
            'email': email,
        }

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_instance = form.save(commit=False)
            if is_authenticated:
                contact_instance.user = request.user
            contact_instance.save()
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contact')
    else:
        form = ContactForm(initial=initial_data)

    return render(request, 'contact/contact.html', {
        'form': form,
        'user_is_authenticated': is_authenticated,
    })


@login_required
def contact_view(request):
    contacts_list = Contact.objects.all()
    paginator = Paginator(contacts_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'contact/contactView.html', {'page_obj': page_obj})

# 
# ------------------------------------------
# -------------------- Others ---------------- 
# ------------------------------------------
# 

# about
def about(request):
    return render(request, 'about/about.html')

# terms
def terms(request):
    return render(request, 'about/terms.html')

# privacy
def privacy(request):
    return render(request, 'about/privacy.html')

# disclaimer
def disclaimer(request):
    return render(request, 'about/disclaimer.html')

# FAQ
def Gendral_User_FAQ(request):
    faqs_G = FAQ_G.objects.all()
    return render(request, 'FAQ/faqG.html', {'faqs_G': faqs_G})

# blog
# user_auth/views.py
def blog(request):
    blogs = Blog.objects.all().order_by('-date')
    return render(request, 'blog/blog.html', {'blogs': blogs})

def user_blog_detail_view(request, blog_id):
    blog = get_object_or_404(Blog, pk=blog_id)
    related_blogs = Blog.objects.exclude(id=blog_id).order_by('-date')[:3]
    return render(request, 'blog/blog_detail.html', {'blog': blog, 'related_blogs': related_blogs})
