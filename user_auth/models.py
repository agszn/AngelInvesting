# app: user_auth
# models.py
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.conf import settings
from django.db import models

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.core.validators import RegexValidator

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = [
        ('RM', 'Relationship Manager'),
        ('AC', 'Accounts'),
        ('SM', 'Site Manager'),
        ('ST', 'Share Transfer'),
        ('AD', 'Admin'),
        ('DF', 'Default User'),
        ('AP', 'Associate Partner'),   
        ('PT', 'Partner'),   
        ('Other', 'Other'),           
    ]

    phone_number = models.CharField(max_length=12, validators=[RegexValidator(r'^\+?\d{10,12}$', 'Enter valid phone number')], unique=True, blank=True, null=True)
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    user_type = models.CharField(max_length=5, choices=USER_TYPE_CHOICES, default='DF')

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



from django.db import models
from django.conf import settings

ACCOUNT_TYPE_CHOICES = [
    ('saving', 'Saving'),
    ('current', 'Current'),
    ('salary', 'Salary'),
    ('nre', 'NRE'),
    ('nro', 'NRO'),
]

ACCOUNT_STATUS_CHOICES = [
    ('active', 'Active'),
    ('inactive', 'Inactive'),
    ('closed', 'Closed'),
]

from django.db import models
from django.conf import settings


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
    pan_card_photo = models.ImageField(upload_to='pan_cards/', blank=True, null=True)
    adhar_number = models.CharField(max_length=12, validators=[RegexValidator(r'^\d{12}$', 'Enter valid 12-digit Aadhaar number')], blank=True, null=True)
    adhar_card_photo = models.ImageField(upload_to='adhar_cards/', blank=True, null=True)

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

from django.core.validators import FileExtensionValidator
from django.core.validators import RegexValidator

class BankAccount(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='bank_accounts')
    account_holder_name = models.CharField(max_length=100)
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=20)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPE_CHOICES)
    account_status = models.CharField(max_length=10, choices=ACCOUNT_STATUS_CHOICES)
    linked_phone_number = models.CharField(max_length=15)

    ifsc_code = models.CharField(
        max_length=11,
        validators=[
            RegexValidator(
                regex=r'^[A-Z]{4}0[0-9A-Z]{6}$',
                message='Enter a valid IFSC code (e.g., SBIN0001234)'
            )
        ], blank=True, null=True
    )
    statementPaper = models.FileField(
        upload_to='bank_statements/',
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf', 'xlsx'])
        ]
    )

    def __str__(self):
        return f"{self.bank_name} - {self.account_number}"


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
    subject = models.CharField(max_length=200, null=True, blank=True)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"Message from {self.name} - {self.subject}"



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
