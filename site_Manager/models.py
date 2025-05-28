from django.db import models

class HeroSectionBanner(models.Model):
    title = models.CharField(max_length=100, default="Homepage Banner")
    image = models.ImageField(upload_to='banners/')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

from django.db import models

class Broker(models.Model):
    broker_id = models.AutoField(primary_key=True)  
    name = models.CharField(max_length=100)
    pan = models.CharField(max_length=10, unique=True)
    email = models.EmailField(unique=True)
    contact = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return self.name

from django.db import models

class Advisor(models.Model):
    ADVISOR_TYPE_CHOICES = [
        ('Thangiv', 'Thangiv'),
        ('Other', 'Other'),
    ]

    advisor_type = models.CharField(max_length=20, choices=ADVISOR_TYPE_CHOICES, default='Other')

    def __str__(self):
        return self.advisor_type
