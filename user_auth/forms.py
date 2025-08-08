from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import *

from django import forms
from .models import CustomUser

class CustomUserCreationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone_number']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your username (no spaces)',
                'style': 'padding: 10px; border: 1px solid #ccc; border-radius: 4px; width: 100%;',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email',
                'style': 'padding: 10px; border: 1px solid #ccc; border-radius: 4px; width: 100%;',
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your phone number',
                'style': 'padding: 10px; border: 1px solid #ccc; border-radius: 4px; width: 100%;',
            }),
        }

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if not phone.isdigit():
            raise forms.ValidationError("Phone number must contain only digits.")
        if len(phone) < 6:
            raise forms.ValidationError("Phone number must be at least 6 digits.")
        return phone

from django import forms
from .models import CustomUser

class UserTypeUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['user_type']
        widgets = {
            'user_type': forms.Select(attrs={'class': 'form-control'}),
        }


from django import forms
from django.contrib.auth.forms import AuthenticationForm

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Username',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your Username',
            'style': (
                'padding: 16px; '
                'border: 1px solid #ced4da; '
                'border-radius: 8px; '
                'font-size: 18px; '
                'height: 52px;'
                'width: 100%;'
                
            ),
        })
    )
    password = forms.CharField(
        label='Password (Phone Number)',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password (mobile number)',
            'style': (
                'padding: 16px; '
                'border: 1px solid #ced4da; '
                'border-radius: 8px; '
                'font-size: 18px; '
                'height: 52px;'
                'width: 100%;'
            ),
        })
    )



from django import forms
from django.forms import inlineformset_factory
from .models import UserProfile, BankAccount, CMRCopy

# profile
from django import forms
from .models import UserProfile

from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'middle_name', 'last_name', 'email',
                  'whatsapp_number', 'mobile_number', 'photo',
                  'pan_number', 'pan_card_photo', 'adhar_number', 'adhar_card_photo']
        widgets = {
            'email': forms.EmailInput(attrs={'type': 'email'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].required = False  # Make all fields optional


# bank acc
from django import forms
from .models import BankAccount

class BankAccountForm(forms.ModelForm):
    class Meta:
        model = BankAccount
        fields = ['account_holder_name', 'bank_name', 'account_type', 'account_number', 'ifsc_code']



# CMR
class CMRForm(forms.ModelForm):
    class Meta:
        model = CMRCopy
        fields = ['broker', 'client_id_input', 'cmr_file']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['broker'].queryset = Broker.objects.all()
        self.fields['broker'].empty_label = "-- Select Broker --"
        self.fields['broker'].required = True



# contact
from django import forms
from .models import Contact

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'subject', 'message'] 
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter your full name', 
                'maxlength': '100'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter your email address'
            }),
            'subject': forms.TextInput(attrs={  
                'class': 'form-control',
                'placeholder': 'Enter subject',
                'maxlength': '200'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control', 
                'placeholder': 'Write your message here...', 
                'rows': 5
            }),
        }



# ------------- G User FAQ -------------

from django import forms
from .models import FAQ_G

class FAQForm(forms.ModelForm):
    class Meta:
        model = FAQ_G
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6, 'id': 'id_description'}),
            'style': forms.Select(attrs={'id': 'id_style'}),
        }

# the below form is for the user to update their user type
# and it is not used in the admin panel
# and the below is test and temporary updates
# start - 02082025  => secure "Forgot Password" flow using OTP delivered via email.

# ForgotPasswordForm
class ForgotPasswordForm(forms.Form):
    email_or_username = forms.CharField(label="Email or Username", max_length=100)

# OTPVerificationForm
class OTPVerificationForm(forms.Form):
    otp = forms.CharField(label="OTP", max_length=6)

# ResetPasswordForm
class ResetPasswordForm(forms.Form):
    new_phone_number = forms.CharField(label="New Phone Number", max_length=12)
    confirm_phone_number = forms.CharField(label="Confirm Phone Number", max_length=12)

    def clean(self):
        cleaned_data = super().clean()
        phone1 = cleaned_data.get("new_phone_number")
        phone2 = cleaned_data.get("confirm_phone_number")
        if phone1 != phone2:
            raise forms.ValidationError("Phone numbers do not match.")
        if not phone1.isdigit() or len(phone1) < 6:
            raise forms.ValidationError("Enter a valid phone number.")
        return cleaned_data

# end - 02082025 => secure "Forgot Password" flow using OTP delivered via email.

#  -------------------------------------------
#  -------------------------------------------


# start - 02082025 -> Phase 2: Change Password (Phone Number) from Profile Page, with OTP verification via email for now.


class ChangePhoneNumberForm(forms.Form):
    new_phone_number = forms.CharField(max_length=12, label="New Phone Number")

    def clean_new_phone_number(self):
        phone = self.cleaned_data['new_phone_number']
        if not phone.isdigit() or len(phone) < 6:
            raise forms.ValidationError("Enter a valid phone number.")
        return phone


class OTPConfirmationForm(forms.Form):
    otp = forms.CharField(max_length=6, label="Enter OTP")


# end - 02082025 -> Phase 2: Change Password (Phone Number) from Profile Page, with OTP verification via email for now.