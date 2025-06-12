# app: site_Manager
# models.py
from django.db import models

class HeroSectionBanner(models.Model):
    title = models.CharField(max_length=100, default="Homepage Banner")
    image = models.ImageField(upload_to='banners/')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator

from django.core.validators import RegexValidator
from django.db import models

class Broker(models.Model):
    id = models.AutoField(primary_key=True)
    broker_id = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique Broker ID (e.g., BRK001)"
    )
    name = models.CharField(max_length=100)
    pan = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )
    email = models.EmailField(unique=True)
    contact = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\+?\d{10,15}$', 'Enter valid phone number')]
    )

    def __str__(self):
        return f"{self.name} ({self.broker_id})"



from django.db import models

class Advisor(models.Model):
    advisor_type = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"{self.advisor_type}"




