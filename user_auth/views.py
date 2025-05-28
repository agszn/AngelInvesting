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

@login_required
@user_passes_test(is_admin_or_site_manager)
def manage_user_types(request):
    query = request.GET.get('q', '')
    users = CustomUser.objects.exclude(user_type='AD')
    if query:
        users = users.filter(username__icontains=query) | users.filter(email__icontains=query)

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        new_type = request.POST.get('user_type')
        user = get_object_or_404(CustomUser, id=user_id)
        user.user_type = new_type
        user.save()
        return redirect('manage_user_types')

    return render(request, 'SiteManageUsers/ManageUserAuth.html', {'users': users, 'query': query})


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

@login_required
def view_profile(request):
    return render(request, 'accounts/profile.html')

@login_required
def edit_profile(request):
    return render(request, 'accounts/edit_profile.html')


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


# 
# ------------------------------------------
# -------------------------- CMR ---------------
# ------------------------------------------
# 
@login_required
def download_cmr_file(request, cmr_id):
    # Get the CMR record
    try:
        cmr = CMRCopy.objects.get(id=cmr_id, user_profile=request.user.profile)
    except CMRCopy.DoesNotExist:
        raise Http404("CMR file not found.")
    
    # Check if a file exists
    if cmr.cmr_file:
        # Return the file as a response
        return FileResponse(cmr.cmr_file, as_attachment=True, filename=cmr.cmr_file.name)
    else:
        raise Http404("CMR file not found.")

