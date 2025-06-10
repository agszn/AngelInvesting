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

def is_admin_or_site_manager(user):
    return user.user_type in ['AD', 'SM']

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
    users = CustomUser.objects.exclude(user_type='AD')
    rms = CustomUser.objects.filter(user_type='RM')

    if query:
        users = users.filter(username__icontains=query) | users.filter(email__icontains=query)

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

    return render(request, 'SiteManageUsers/ManageUserAuth.html', {
        'users': users,
        'rms': rms,
        'query': query,
    })

def base(request):
    # homepage banner
    banner = HeroSectionBanner.objects.filter(is_active=True).first()
    
    # Base.html Stocks Displayed
    stocks = StockData.objects.all()
    for stock in stocks:
        if stock.ltp and stock.share_price and stock.share_price > 0:
            stock.percentage_diff = ((stock.ltp - stock.share_price) / stock.share_price) * 100
        else:
            stock.percentage_diff = None  # Handle missing or zero share price
    return render(request, "base.html", {"stocks": stocks,"banner": banner})

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
        'Your New OTP for Account Verification',
        f'Your new OTP is: {user.otp}',
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False,
    )

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
            messages.success(request, "Login successful!")

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
                return redirect('profile')
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
    messages.success(request, "Logged out successfully.")
    return redirect('login')

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

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile, Broker, CMRCopy
from .forms import UserProfileForm, CMRForm

@login_required
def view_profile(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)
    brokers = Broker.objects.all()
    cmr_copies = CMRCopy.objects.filter(user_profile=profile)

    form = UserProfileForm(instance=profile)
    cmr_form = CMRForm()

    if request.method == 'POST':
        form_type = request.POST.get('form_type')

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
        
        else:
            form = UserProfileForm(request.POST, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, "Profile updated.")
                return redirect('profile')
            else:
                messages.error(request, "Please correct the errors in the profile form.")

    context = {
        'form': form,
        'cmr_form': cmr_form,
        'brokers': brokers,
        'cmr_copies': cmr_copies,
        'profile': profile,
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
from .forms import BankAccountForm  # Create this form
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

@csrf_exempt
@login_required
def save_bank_account(request):
    if request.method == 'POST':
        account_id = request.POST.get('account_id')

        if account_id:  
            bank = get_object_or_404(BankAccount, id=account_id, user_profile=request.user.profile)
        else:  
            bank = BankAccount(user_profile=request.user.profile)
        bank.account_holder_name = request.POST.get('account_holder_name', '')
        bank.bank_name = request.POST.get('bank_name', '')
        bank.account_type = request.POST.get('account_type', '')
        bank.account_number = request.POST.get('account_number', '')
        bank.ifsc_code = request.POST.get('ifsc_code', '')
        bank.save()

        return redirect('profile')
    return JsonResponse({'status': 'error'}, status=400)


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

# contact
@login_required
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()  
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contact')  
    else:
        form = ContactForm()
    return render(request, 'contact/contact.html', {'form': form})


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

# FAQ
def faq(request):
    return render(request, 'FAQ/faq.html')


# blog
def blog(request):
    return render(request, 'blog/blog.html')

