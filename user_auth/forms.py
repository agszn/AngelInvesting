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
        fields = ['username', 'email', 'phone_number', 'residency_status']
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
            'residency_status': forms.RadioSelect(choices=CustomUser.RESIDENCY_CHOICES),

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
        fields = [
            'first_name', 'middle_name', 'last_name', 'email',
            'whatsapp_number', 'mobile_number', 'photo',
            'pan_number', 'pan_card_photo', 'pan_doc_password',
            'adhar_number', 'adhar_card_photo', 'adhar_doc_password'
        ]
        widgets = {
            'email': forms.EmailInput(attrs={'type': 'email'}),
            'pan_doc_password': forms.PasswordInput(render_value=True),
            'adhar_doc_password': forms.PasswordInput(render_value=True),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make all fields optional
        for field in self.fields:
            self.fields[field].required = False  

        # Always show password fields (no hiding)
        self.fields['pan_doc_password'].widget.attrs.pop('hidden', None)
        self.fields['adhar_doc_password'].widget.attrs.pop('hidden', None)


# bank acc
# forms.py
from django import forms
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
from .models import BankAccount

# If you created JointAccountHolder as suggested
try:
    from .models import JointAccountHolder
    HAS_JOINT_HOLDER = True
except Exception:
    HAS_JOINT_HOLDER = False


def _is_pdf(upload) -> bool:
    return bool(upload) and str(upload.name).lower().endswith('.pdf')


class BankAccountForm(forms.ModelForm):
    # Override to control messages and digit counting (and hide 9223… message)
    # Because your model is BigIntegerField, we cap at 19 digits here.
    account_number = forms.CharField(
        max_length=19,
        strip=True,
        label="Account Number",
        widget=forms.TextInput(attrs={
            "inputmode": "numeric",
            "pattern": r"\d{10,19}",
            "placeholder": "Enter 10–19 digit account number",
        })
    )

    class Meta:
        model = BankAccount
        fields = [
            "account_holder_name",
            "bank_name",
            "account_type",
            "account_number",
            "account_status",
            "linked_phone_number",
            "ifsc_code",
            "statementPaper",
            "document_type",
            "bankDetails_doc_password",
        ]
        labels = {
            "account_holder_name": "Primary Account Holder Name",
            "bank_name": "Bank Name",
            "account_type": "Account Type",
            "account_number": "Account Number",
            "account_status": "Account Status",
            "linked_phone_number": "Linked Phone Number (SMS/OTP)",
            "ifsc_code": "IFSC Code",
            "statementPaper": "Statement / Cheque / Passbook (PDF/XLSX)",
            "document_type": "Uploaded Document Type",
            "bankDetails_doc_password": "Document Password (if PDF)",
        }
        widgets = {
            "linked_phone_number": forms.TextInput(attrs={"placeholder": "e.g. +91XXXXXXXXXX"}),
            "ifsc_code": forms.TextInput(attrs={"placeholder": "e.g. SBIN0001234", "style": "text-transform:uppercase"}),
            "statementPaper": forms.ClearableFileInput(attrs={"accept": ".pdf,.xlsx"}),
        }

    # ----- Field-level validations -----

    def clean_account_number(self):
        raw = (self.cleaned_data.get("account_number") or "").strip()
        digits = "".join(ch for ch in raw if ch.isdigit())
        count = len(digits)

        # For BigIntegerField, allow 10–19 digits
        if count < 10:
            raise ValidationError(f"Account number must be at least 10 digits. You entered {count}.")
        if count > 19:
            raise ValidationError(f"Account number can be at most 19 digits on this system. You entered {count}.")

        # Convert to int for the model (BigIntegerField).
        # If you migrate the model to CharField(20), just `return digits` and adjust limits to 20.
        return int(digits)

    # ----- Form-level validations -----

    def clean(self):
        cleaned = super().clean()

        # Normalize IFSC to uppercase (model regex expects uppercase)
        ifsc = cleaned.get("ifsc_code")
        if ifsc:
            cleaned["ifsc_code"] = ifsc.upper()

        # Require password ONLY for bank_statement PDFs
        statement = cleaned.get("statementPaper")
        doc_password = (cleaned.get("bankDetails_doc_password") or "").strip()
        doc_type = cleaned.get("document_type")

        if doc_type == "bank_statement":
            if _is_pdf(statement) and not doc_password:
                self.add_error("bankDetails_doc_password", "Password is required for bank statement PDFs.")
        else:
            # Clear password for other doc types to avoid confusion
            cleaned["bankDetails_doc_password"] = ""

        return cleaned


# ---------- Joint Holder (optional; if your model has it) ----------

if HAS_JOINT_HOLDER:
    class JointAccountHolderForm(forms.ModelForm):
        class Meta:
            model = JointAccountHolder
            fields = [
                "full_name",
                "aadhaar_doc",
                "aadhaar_doc_password",
                "pan_doc",
                "pan_doc_password",
            ]
            labels = {
                "full_name": "Joint Holder Full Name",
                "aadhaar_doc": "Aadhaar (PDF/JPG/PNG)",
                "aadhaar_doc_password": "Aadhaar PDF Password (if PDF)",
                "pan_doc": "PAN (PDF/JPG/PNG)",
                "pan_doc_password": "PAN PDF Password (if PDF)",
            }
            widgets = {
                "aadhaar_doc": forms.ClearableFileInput(attrs={"accept": ".pdf,.jpg,.jpeg,.png"}),
                "pan_doc": forms.ClearableFileInput(attrs={"accept": ".pdf,.jpg,.jpeg,.png"}),
            }

        def clean(self):
            cleaned = super().clean()
            aadhaar = cleaned.get("aadhaar_doc")
            pan = cleaned.get("pan_doc")

            if _is_pdf(aadhaar) and not cleaned.get("aadhaar_doc_password"):
                self.add_error("aadhaar_doc_password", "Password is required for Aadhaar PDF.")
            if _is_pdf(pan) and not cleaned.get("pan_doc_password"):
                self.add_error("pan_doc_password", "Password is required for PAN PDF.")

            return cleaned

    JointHolderFormSet = inlineformset_factory(
        BankAccount,
        JointAccountHolder,
        form=JointAccountHolderForm,
        extra=1,
        can_delete=True,
        min_num=1,
        validate_min=True,
    )
else:
    JointAccountHolderForm = None
    JointHolderFormSet = None


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
        fields = ['name', 'email', 'phone', 'subject', 'message']  # added phone here
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
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your 10-digit phone number',
                'maxlength': '10',
                'pattern': '[0-9]{10}',  # HTML5 validation
                'title': 'Enter a valid 10-digit phone number'
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

import re
from django import forms

# ---------- Helpers ----------
def is_valid_email(value: str) -> bool:
    # Simple email check; you can also use Django's EmailValidator
    return re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value) is not None

def normalize_phone(raw: str) -> str | None:
    """
    Strip spaces, dashes, parentheses; allow optional +; require 7–15 digits.
    Returns normalized number or None if invalid.
    """
    s = re.sub(r"[()\s-]+", "", raw)
    if re.fullmatch(r"\+?\d{7,15}", s):
        return s
    return None

# ---------- Form ----------
class ForgotPasswordForm(forms.Form):
    email_or_phone = forms.CharField(label="Email or Phone Number", max_length=100)

    def clean_email_or_phone(self):
        value = self.cleaned_data["email_or_phone"].strip()

        if is_valid_email(value):
            return {"type": "email", "value": value.lower()}

        phone = normalize_phone(value)
        if phone:
            return {"type": "phone", "value": phone}

        raise forms

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