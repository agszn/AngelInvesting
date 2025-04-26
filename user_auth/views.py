from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, LoginForm
from django.contrib import messages
from django.core.paginator import Paginator

from user_auth.forms import *
from user_auth.models import *
from user_auth.utils import *

from unlisted_stock_marketplace.forms import *
from unlisted_stock_marketplace.models import *
from unlisted_stock_marketplace.utils import *

def base(request):
    stocks = StockData.objects.all()

    # Calculate percentage difference and store it in a new attribute
    for stock in stocks:
        if stock.ltp and stock.share_price and stock.share_price > 0:
            stock.percentage_diff = ((stock.ltp - stock.share_price) / stock.share_price) * 100
        else:
            stock.percentage_diff = None  # Handle missing or zero share price

    return render(request, "base.html", {"stocks": stocks})


# def base(request):
#     query = request.GET.get('q', '')
#     stocks = StockData.objects.filter(company_name__icontains=query) if query else StockData.objects.all()
#     return render(request, 'base.html', {'stocks': stocks, 'query': query})

# def register_view(request):
#     if request.method == 'POST':
#         form = CustomUserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             return redirect('login_view')
#     else:
#         form = CustomUserCreationForm()
#     return render(request, 'accounts/register.html', {'form': form})

# def login_view(request):
#     if request.method == 'POST':
#         form = LoginForm(data=request.POST)
#         if form.is_valid():
#             user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
#             if user is not None:
#                 login(request, user)
#                 return redirect('base')
#     else:
#         form = LoginForm()
#     return render(request, 'accounts/login.html', {'form': form})

from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from .forms import CustomUserCreationForm, LoginForm, CustomUserProfileForm
from .models import CustomUser
import uuid

# User Registration View
# def register_view(request):
#     if request.method == 'POST':
#         form = CustomUserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.is_active = False  # User will be activated after email verification
#             user.otp = str(uuid.uuid4())[:6]  # Generate a 6-digit OTP
#             user.save()
            
#             # Send verification email
#             send_mail(
#                 'Verify Your Account',
#                 f'Your OTP for verification is {user.otp}',
#                 settings.EMAIL_HOST_USER,
#                 [user.email],
#                 fail_silently=False,
#             )
#             messages.success(request, "Check your email for the OTP to verify your account.")
#             return redirect('verify_email', user_id=user.id)
#     else:
#         form = CustomUserCreationForm()
    
#     return render(request, 'accounts/register.html', {'form': form})

from django.contrib import messages

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
                return render(request, 'accounts/register.html', {'form': form})

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

    return render(request, 'accounts/register.html', {'form': form})

import uuid
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import CustomUser

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
    
    return render(request, 'accounts/verify_email.html', {'user': user})

# Login View
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('view_profile')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})

# Logout View
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('login')

# profile
# @login_required
# def view_profile(request):
#     return render(request, 'accounts/profile.html', {'user': request.user})

# @login_required
# def edit_profile(request):
#     user = request.user

#     if request.method == 'POST':
#         form = CustomUserProfileForm(request.POST, request.FILES, instance=user, user_instance=user)
#         if form.is_valid():
#             form.save()
#             return redirect('view_profile')
#     else:
#         form = CustomUserProfileForm(instance=user, user_instance=user)

#     return render(request, 'accounts/edit_profile.html', {'form': form})

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import CustomUserProfileForm, BankAccountFormSet, CMRCopyFormSet
from .models import UserProfile

@login_required
def view_profile(request):
    profile = UserProfile.objects.get(user=request.user)
    return render(request, 'accounts/profile.html', {
            'profile': profile,
            'bank_accounts': profile.bank_accounts.all(),
            'cmr_copies': profile.cmr_copies.all(),
        })
from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory
from django.shortcuts import render, redirect
from .forms import CustomUserProfileForm
from .models import UserProfile, BankAccount, CMRCopy

@login_required
def edit_profile(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    # Get extra form counts from GET query (default 1)
    extra_bank = int(request.GET.get('extra_bank', 1))
    extra_cmr = int(request.GET.get('extra_cmr', 1))

    # Inline formsets with dynamic extra
    BankAccountFormSet = inlineformset_factory(
        UserProfile, BankAccount, fields='__all__', extra=extra_bank, can_delete=True
    )
    CMRCopyFormSet = inlineformset_factory(
        UserProfile, CMRCopy, fields='__all__', extra=extra_cmr, can_delete=True
    )

    if request.method == 'POST':
        form = CustomUserProfileForm(request.POST, request.FILES, instance=profile)
        bank_formset = BankAccountFormSet(request.POST, instance=profile)
        cmr_formset = CMRCopyFormSet(request.POST, instance=profile)

        if form.is_valid() and bank_formset.is_valid() and cmr_formset.is_valid():
            form.save()
            bank_formset.save()
            cmr_formset.save()
            return redirect('view_profile')
    else:
        form = CustomUserProfileForm(instance=profile)
        bank_formset = BankAccountFormSet(instance=profile)
        cmr_formset = CMRCopyFormSet(instance=profile)

    return render(request, 'accounts/edit_profile.html', {
        'form': form,
        'bank_formset': bank_formset,
        'cmr_formset': cmr_formset,
        'extra_bank': extra_bank,
        'extra_cmr': extra_cmr,
    })

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

# about
def about(request):
    return render(request, 'about/about.html')

# FAQ
def faq(request):
    return render(request, 'FAQ/faq.html')

