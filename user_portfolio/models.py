# app: user_portfolio
# models.py
from django.contrib.auth import get_user_model
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
from user_auth.models import *
from unlisted_stock_marketplace.models import *
from site_Manager.models import *
# user_portfolio/models.py


User = get_user_model()

ORDER_STATUS_CHOICES = [
    ('processing', 'Processing'),
    ('completed', 'Completed'),
    ('on_hold', 'On Hold'),
    ('cancelled', 'Cancelled'),
]

class BuyTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(StockData, on_delete=models.CASCADE)
    advisor = models.ForeignKey(Advisor, on_delete=models.SET_NULL, null=True)
    broker = models.ForeignKey(Broker, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    price_per_share = models.DecimalField(max_digits=10, decimal_places=2)
    order_type = models.CharField(max_length=10, choices=(('market', 'Market'), ('limit', 'Limit')))
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    status = models.CharField(max_length=15, choices=ORDER_STATUS_CHOICES, default='processing')

    order_id = models.CharField(max_length=20, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.order_id:
            count = BuyTransaction.objects.count() + 1
            self.order_id = f"Ord_B_{count:03d}"
        super().save(*args, **kwargs)



class SellTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(StockData, on_delete=models.CASCADE)
    advisor = models.ForeignKey(Advisor, on_delete=models.SET_NULL, null=True)
    broker = models.ForeignKey(Broker, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    selling_price = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    total_value = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)

    status = models.CharField(max_length=15, choices=ORDER_STATUS_CHOICES, default='processing')
    
    order_id = models.CharField(max_length=20, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.order_id:
            count = SellTransaction.objects.count() + 1
            self.order_id = f"Ord_S_{count:03d}"
        
        # Calculate total value
        if self.quantity and self.selling_price:
            self.total_value = self.quantity * self.selling_price

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Sell Order {self.order_id} - {self.stock.name} x{self.quantity}"
        

class UserPortfolioSummary(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="portfolio_summary")
    total_invested = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_market_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    overall_gain_loss = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    todays_gain_loss = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_quantity = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Portfolio Summary: {self.user.username}"
