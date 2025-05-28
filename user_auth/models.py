from django.contrib.auth.models import AbstractUser, Group, Permission
from django.conf import settings
from django.db import models

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


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
    ]

    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    user_type = models.CharField(max_length=2, choices=USER_TYPE_CHOICES, default='DF')

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

class Broker(models.Model):
    broker_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    photo = models.ImageField(upload_to='broker_photos/', blank=True, null=True)
    def __str__(self):
        return f"{self.broker_id} - {self.name}"
    

from django.db import models
from django.conf import settings

class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    whatsapp_number = models.CharField(max_length=15, blank=True, null=True)
    pan_number = models.CharField(max_length=10, blank=True, null=True)
    pan_card_photo = models.ImageField(upload_to='pan_cards/', blank=True, null=True)
    adhar_number = models.CharField(max_length=12, blank=True, null=True)
    adhar_card_photo = models.ImageField(upload_to='adhar_cards/', blank=True, null=True)
    photo = models.ImageField(upload_to='user_photos/', blank=True, null=True)  

    def __str__(self):
        return self.user.username

class BankAccount(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='bank_accounts')
    account_holder_name = models.CharField(max_length=100)
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=20)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPE_CHOICES)
    account_status = models.CharField(max_length=10, choices=ACCOUNT_STATUS_CHOICES)
    linked_phone_number = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.bank_name} - {self.account_number}"


from django.core.validators import FileExtensionValidator

class CMRCopy(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='cmr_copies')
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE)
    client_id = models.CharField(max_length=50)
    client_name = models.CharField(max_length=100)
    cmr_file = models.FileField(
        upload_to='cmr_files/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])],
        help_text="Upload a scanned copy or PDF"
    )

    @property
    def broker_id(self):
        return self.broker.broker_id

    @property
    def broker_name(self):
        return self.broker.name

    def __str__(self):
        return f"{self.client_name} - {self.broker.broker_id} - {self.broker.name}"


    
class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()

    def __str__(self):
        return self.name
