from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import *

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class CustomUserCreationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone_number']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your username',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email',
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your phone number',
            }),
        }

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if not phone.isdigit():
            raise forms.ValidationError("Phone number must contain only digits.")
        if len(phone) < 6:
            raise forms.ValidationError("Phone number must be at least 6 digits.")
        return phone

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Username',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username',
        })
    )
    password = forms.CharField(
        label='Phone Number (as Password)',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your phone number',
        })
    )

# class CustomUserProfileForm(forms.ModelForm):
#     pan_number = forms.CharField(
#         required=False,
#         widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter PAN Number'})
#     )
#     pan_card_photo = forms.ImageField(required=False)
#     adhar_number = forms.CharField(
#         required=False,
#         widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Aadhaar Number'})
#     )
#     adhar_card_photo = forms.ImageField(required=False)

#     class Meta:
#         model = CustomUser
#         fields = [
#             'username', 'first_name', 'last_name', 'email', 'phone_number'
#         ]
#         widgets = {
#             'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your username'}),
#             'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your first name'}),
#             'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your last name'}),
#             'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
#             'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your phone number'}),
#         }

#     def __init__(self, *args, **kwargs):
#         self.user_instance = kwargs.pop('user_instance', None)
#         super().__init__(*args, **kwargs)

#         if self.user_instance:
#             # Get or create UserProfile linked to user
#             user_profile, _ = UserProfile.objects.get_or_create(user=self.user_instance)

#             # Load UserProfile fields
#             self.fields['pan_number'].initial = user_profile.pan_number
#             self.fields['pan_card_photo'].initial = user_profile.pan_card_photo
#             self.fields['adhar_number'].initial = user_profile.adhar_number
#             self.fields['adhar_card_photo'].initial = user_profile.adhar_card_photo

#     def save(self, commit=True):
#         # Save CustomUser fields
#         custom_user = super().save(commit=commit)

#         # Save UserProfile fields
#         user_profile, _ = UserProfile.objects.get_or_create(user=custom_user)
#         user_profile.pan_number = self.cleaned_data.get('pan_number')
#         user_profile.adhar_number = self.cleaned_data.get('adhar_number')

#         if self.cleaned_data.get('pan_card_photo'):
#             user_profile.pan_card_photo = self.cleaned_data.get('pan_card_photo')
#         if self.cleaned_data.get('adhar_card_photo'):
#             user_profile.adhar_card_photo = self.cleaned_data.get('adhar_card_photo')

#         if commit:
#             user_profile.save()

#         return custom_user

from django import forms
from django.forms import inlineformset_factory
from .models import UserProfile, BankAccount, CMRCopy

class CustomUserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['whatsapp_number', 'pan_number', 'pan_card_photo', 'adhar_number', 'adhar_card_photo']


BankAccountFormSet = inlineformset_factory(
    UserProfile,
    BankAccount,
    fields=['account_holder_name', 'bank_name', 'account_number', 'account_type', 'account_status', 'linked_phone_number'],
    extra=1,
    can_delete=True
)

CMRCopyFormSet = inlineformset_factory(
    UserProfile,
    CMRCopy,
    fields=['broker', 'client_id', 'client_name'],
    extra=1,
    can_delete=True
)

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'message']
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
            'message': forms.Textarea(attrs={
                'class': 'form-control', 
                'placeholder': 'Write your message here...', 
                'rows': 5
            }),
        }

