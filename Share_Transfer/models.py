from django.db import models
from django.conf import settings



class DealLetterRecord(models.Model):
    DEAL_TYPE_CHOICES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=100)
    deal_type = models.CharField(max_length=10, choices=DEAL_TYPE_CHOICES)
    invoice_no = models.CharField(max_length=50)
    stock_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    price_per_share = models.DecimalField(max_digits=12, decimal_places=2)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    generated_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.deal_type} - {self.invoice_no} - {self.user.username}"
