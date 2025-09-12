# app: user_auth
# models.py
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.conf import settings
from django.db import models

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
# ===============================
# Custom User Model
# ===============================
class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = [
        ('RM', 'Relationship Manager'),
        ('AC', 'Accounts'),
        ('SM', 'Site Manager'),
        ('ST', 'Share Transfer'),
        ('AD', 'Admin'),
        ('DF', 'Default User'),
        ('AP', 'Associate Partner'),
        ('Other', 'Other'),
    ]

    RESIDENCY_CHOICES = [
        ('Resident', 'Resident'),
        ('Non-Resident', 'Non-Resident'),
    ]
    
    phone_number = models.CharField(
        max_length=12,
        validators=[RegexValidator(r'^\+?\d{10,12}$', 'Enter valid phone number')],
        unique=True,
        blank=True,
        null=True
    )
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    user_type = models.CharField(max_length=5, choices=USER_TYPE_CHOICES, default='DF')

    residency_status = models.CharField(
        max_length=20,
        choices=RESIDENCY_CHOICES,
        default='Resident'
    )
    groups = models.ManyToManyField(
        Group,
        related_name="customuser_set",
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="customuser_set",
        blank=True
    )

    assigned_rm = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        limit_choices_to={'user_type': 'RM'},
        related_name='assigned_users'
    )

    # 🔹 Login tracking fields
    daily_login_count = models.PositiveIntegerField(default=0)
    weekly_login_count = models.PositiveIntegerField(default=0)
    monthly_login_count = models.PositiveIntegerField(default=0)
    last_login_date = models.DateField(null=True, blank=True)

    def update_login_stats(self):
        """Update login counters for day, week, month."""
        today = timezone.now().date()
        current_week = today.isocalendar()[1]
        current_month = today.month

        if self.last_login_date != today:
            # Reset daily counter if new day
            self.daily_login_count = 0

        # Count this login
        self.daily_login_count += 1

        # Weekly & monthly reset logic
        if not self.last_login_date or self.last_login_date.isocalendar()[1] != current_week:
            self.weekly_login_count = 0
        if not self.last_login_date or self.last_login_date.month != current_month:
            self.monthly_login_count = 0

        self.weekly_login_count += 1
        self.monthly_login_count += 1
        self.last_login_date = today

        self.save(update_fields=[
            "daily_login_count", "weekly_login_count",
            "monthly_login_count", "last_login_date"
        ])



from django.db import models
from django.conf import settings





from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator

class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    # Personal Information
    first_name = models.CharField(max_length=50, blank=True, null=True)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    whatsapp_number = models.CharField(max_length=12, validators=[RegexValidator(r'^\+?\d{10,12}$', 'Enter valid phone number')],
    blank=True, null=True)


    mobile_number = models.CharField(max_length=12, validators=[RegexValidator(r'^\+?\d{10,12}$', 'Enter valid phone number')],
    blank=True, null=True)
    photo = models.ImageField(upload_to='user_photos/', blank=True, null=True)
    
    # KYC Information
    pan_number = models.CharField(max_length=20, validators=[RegexValidator(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}', 'Enter valid PAN number')], blank=True, null=True)
    # pan_card_photo = models.ImageField(upload_to='pan_cards/', blank=True, null=True)
    pan_card_photo = models.FileField(
        upload_to='pan_cards/',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'pdf'])],
        blank=True, null=True
    )

    adhar_card_photo = models.FileField(
        upload_to='adhar_cards/',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'pdf'])],
        blank=True, null=True
    )

    adhar_number = models.CharField(max_length=12, validators=[RegexValidator(r'^\d{12}$', 'Enter valid 12-digit Aadhaar number')], blank=True, null=True)
    # adhar_card_photo = models.ImageField(upload_to='adhar_cards/', blank=True, null=True)

    pan_doc_password = models.CharField(max_length=100, blank=True, null=True)
    adhar_doc_password = models.CharField(max_length=100, blank=True, null=True)

    # Meta Info
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    # Custom User ID
    custom_user_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    
    def full_name(self):
        return f"{self.first_name or ''} {self.middle_name or ''} {self.last_name or ''}".strip()

    def __str__(self):
        return f"{self.user.username} Profile"
    
    def save(self, *args, **kwargs):
        if not self.custom_user_id:
            prefix = "thangiv"
            count = 1
            while True:
                candidate_id = f"{prefix}_{str(count).zfill(2)}"
                if not UserProfile.objects.filter(custom_user_id=candidate_id).exists():
                    self.custom_user_id = candidate_id
                    break
                count += 1
        super().save(*args, **kwargs)


# ===============================
# Login History Model
# ===============================
class LoginHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="login_history"
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} logged in at {self.timestamp}"


from django.core.validators import FileExtensionValidator
from django.core.validators import RegexValidator
from django.core.validators import RegexValidator, MaxLengthValidator, MinLengthValidator
from django.core.validators import MinValueValidator, MaxValueValidator
# models.py
from django.db import models
from django.core.validators import (
    MinValueValidator, MaxValueValidator, FileExtensionValidator, RegexValidator
)
from django.core.exceptions import ValidationError

# ---- Reuse your own constants if you already define them elsewhere ----
ACCOUNT_TYPE_CHOICES = [
    ('saving', 'Saving'),
    ('current', 'Current'),
    ('salary', 'Salary'),
    ('nre', 'NRE'),
    ('nro', 'NRO'),
    ('jointAcc', 'Joint Account'),
]

ACCOUNT_STATUS_CHOICES = [
    ('active', 'Active'),
    ('inactive', 'Inactive'),
    ('closed', 'Closed'),
]

DOCUMENT_TYPE_CHOICES = [
    ('cancelled_cheque', 'Cancelled Cheque'),
    ('bank_statement', 'Bank Statement'),
    ('passbook', 'Passbook'),
]

# adjust this import for your project structure
from user_auth.models import UserProfile  # or wherever your UserProfile lives


def _is_pdf(upload) -> bool:
    return bool(upload) and str(upload.name).lower().endswith('.pdf')


class BankAccount(models.Model):
    user_profile = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name='bank_accounts'
    )
    account_holder_name = models.CharField(max_length=100)
    bank_name = models.CharField(max_length=100)

    # NOTE: BigIntegerField drops leading zeros. If they matter, switch to CharField with a regex.
    account_number = models.BigIntegerField(
        validators=[
            MinValueValidator(10**9),          # minimum 10 digits
            MaxValueValidator(10**20 - 1)      # maximum 20 digits
        ]
    )

    account_type = models.CharField(
        max_length=10, choices=ACCOUNT_TYPE_CHOICES, default="saving"
    )

    account_status = models.CharField(
        max_length=10, choices=ACCOUNT_STATUS_CHOICES, default="active"
    )

    linked_phone_number = models.CharField(max_length=15, blank=True, null=True)

    # IFSC Code - regex to enforce the pattern (e.g., SBIN0001234)
    ifsc_code = models.CharField(
        max_length=11,
        validators=[
            RegexValidator(
                regex=r'^[A-Z]{4}0[A-Z0-9]{6}$',
                message='Enter a valid IFSC code (e.g., SBIN0001234)'
            )
        ],
        blank=True, null=True
    )

    statementPaper = models.FileField(
        upload_to='bank_statements/',
        blank=True, null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'xlsx'])]
    )

    # Dropdown to choose what document is uploaded
    document_type = models.CharField(
        max_length=20, choices=DOCUMENT_TYPE_CHOICES, default='cancelled_cheque'
    )

    bankDetails_doc_password = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.bank_name} - {self.account_number}"

    def clean(self):
        """
        Keep model-level checks that don't require knowing related objects.
        Enforcing "requires at least one joint holder when jointAcc" is best done in the formset layer.
        """
        # Example: if you want to ensure statementPaper password when PDF (optional)
        if self.statementPaper and str(self.statementPaper.name).lower().endswith('.pdf'):
            # If you have password rules for this doc, enforce here (optional).
            pass


class JointAccountHolder(models.Model):
    """
    Stores KYC for each joint holder. Required ONLY when `BankAccount.account_type == 'jointAcc'`.
    Use an inline formset in the view/form to enforce at least one row when jointAcc.
    """
    bank_account = models.ForeignKey(
        BankAccount, on_delete=models.CASCADE, related_name='joint_holders'
    )

    full_name = models.CharField(max_length=120)

    # Aadhaar document (image/pdf) + optional password if PDF
    aadhaar_doc = models.FileField(
        upload_to='kyc/aadhaar/',
        validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png'])]
    )
    aadhaar_doc_password = models.CharField(max_length=100, blank=True, null=True)

    # PAN document (image/pdf) + optional password if PDF
    pan_doc = models.FileField(
        upload_to='kyc/pan/',
        validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png'])]
    )
    pan_doc_password = models.CharField(max_length=100, blank=True, null=True)

    def clean(self):
        errors = {}

        if not self.full_name:
            errors['full_name'] = 'Joint account holder name is required.'

        if not self.aadhaar_doc:
            errors['aadhaar_doc'] = 'Aadhaar document is required.'
        elif _is_pdf(self.aadhaar_doc) and not self.aadhaar_doc_password:
            errors['aadhaar_doc_password'] = 'Password is required for Aadhaar PDF.'

        if not self.pan_doc:
            errors['pan_doc'] = 'PAN document is required.'
        elif _is_pdf(self.pan_doc) and not self.pan_doc_password:
            errors['pan_doc_password'] = 'Password is required for PAN PDF.'

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"Joint Holder: {self.full_name}"

from site_Manager.models import Broker 
from django.core.validators import FileExtensionValidator

class CMRCopy(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='cmr_copies', blank=True, null=True)

    broker = models.ForeignKey(Broker, on_delete=models.SET_NULL, null=True, blank=True, help_text="Select a broker from the list")

    client_id_input = models.CharField(max_length=50, blank=True, null=True)

    cmr_file = models.FileField(
        upload_to='cmr_files/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])]
    )

    created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        client_name = self.user_profile.user.get_full_name() or self.user_profile.user.username
        return f"CMR - {client_name} ({self.broker.name if self.broker else 'No Broker'})"



    
from django.db import models
from django.conf import settings

from django.conf import settings
from django.db import models
from django.core.validators import RegexValidator


class Contact(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Optional. Set only if the user is logged in."
    )
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField()
    phone = models.CharField(
        max_length=10,
        validators=[RegexValidator(r'^\d{10}$', 'Enter a valid 10-digit phone number.')],
        help_text="10-digit phone number (digits only).", null=True, blank=True
    )
    subject = models.CharField(max_length=200, null=True, blank=True)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"Message from {self.name or self.email} - {self.subject or 'No subject'}"




# ------------- G User FAQ -------------
from django.db import models

STYLE_CHOICES = [
    ('paragraph', 'Paragraph'),
    ('ul', 'Unordered List'),
    ('ol_number', 'Ordered List (Numbered)'),
    ('ol_alpha', 'Ordered List (Alphabetical)'),
]

class FAQ_G(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.TextField( blank=True, null=True)
    description = models.TextField(help_text="Use '--' before each point for lists.")
    style = models.CharField(max_length=20, choices=STYLE_CHOICES, default='paragraph')
    image = models.ImageField(upload_to='faq_images/', blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
