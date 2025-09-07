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


from django.db import models

class Blog(models.Model):
    banner = models.ImageField(upload_to='blog_banners/', blank=True, null=True)
    date = models.DateField()
    time = models.TimeField(auto_now_add=True)
    heading = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True)
    short_description = models.TextField()
    full_description = models.TextField(blank=True)

    def __str__(self):
        return self.heading
    



from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
from django.utils import timezone
from unlisted_stock_marketplace.models import StockData
from django.db import models
from django.conf import settings
from django.utils import timezone

class Event(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    stock = models.ForeignKey(StockData, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True, null=True)
    paragraph = models.TextField(blank=True, null=True)
    date_time = models.DateTimeField(default=timezone.now)  # default = created time, editable
    image = models.ImageField(upload_to="events/images/", blank=True, null=True)

    # ✅ New field for document upload (e.g., PDF)
    document = models.FileField(
        upload_to="events/documents/",
        blank=True,
        null=True,
        help_text="Upload a PDF document"
    )

    show = models.BooleanField(default=True)

    created_on = models.DateTimeField(auto_now_add=True)  # system creation timestamp
    updated_on = models.DateTimeField(auto_now=True)      # system update timestamp

    def __str__(self):
        return self.title
