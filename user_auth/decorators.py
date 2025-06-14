# user_auth/decorators.py

from django.shortcuts import redirect
from django.contrib import messages
from user_auth.models import UserProfile, BankAccount, CMRCopy

def require_complete_profile(view_func):
    def _wrapped_view(request, *args, **kwargs):
        user = request.user

        # Ensure user has a profile
        try:
            profile = user.profile
        except UserProfile.DoesNotExist:
            messages.error(request, "Please complete your profile before proceeding.")
            return redirect('edit_profileprofile')  

        # Validate PAN & Aadhaar
        if not profile.pan_number or not profile.adhar_number:
            messages.warning(request, "Please complete your PAN and Aadhaar details.")
            return redirect('profile')

        # Validate at least one bank account
        if not BankAccount.objects.filter(user_profile=profile).exists():
            messages.warning(request, "Please add your bank account details before proceeding.")
            return redirect('profile')  

        # Validate at least one CMR copy
        if not CMRCopy.objects.filter(user_profile=profile, cmr_file__isnull=False).exists():
            messages.warning(request, "Please upload your CMR copy before proceeding.")
            return redirect('profile')  

        return view_func(request, *args, **kwargs)
    return _wrapped_view
