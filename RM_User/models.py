# app: RM_User
# models.py


# app: RM_User
# models.py

from django.db import models
from django.conf import settings
from user_auth.models import UserProfile, BankAccount, CMRCopy
from user_portfolio.models import BuyTransaction, SellTransaction
from site_Manager.models import Broker, Advisor
from unlisted_stock_marketplace.models import StockData

class RMUserView(models.Model):
    # Relations
    assigned_rm = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='rm_viewed_users', limit_choices_to={'user_type': 'RM'})
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='rm_user_views')

    # Auto-populated User Details (read-only)
    full_name = models.CharField(max_length=150)
    custom_user_id = models.CharField(max_length=100)
    pan_number = models.CharField(max_length=20)
    email = models.EmailField()
    mobile_number = models.CharField(max_length=15)

    # Broker & CMR Copy Details
    broker = models.ForeignKey(Broker, on_delete=models.SET_NULL, null=True, blank=True)
    client_id_input = models.CharField(max_length=50, blank=True, null=True)

    # Bank Info
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=20)
    ifsc_code = models.CharField(max_length=11)

    # Transaction Data
    transaction_type = models.CharField(max_length=4, choices=[('buy', 'Buy'), ('sell', 'Sell')])
    order_id = models.CharField(max_length=20)
    timestamp = models.DateTimeField()
    stock = models.ForeignKey(StockData, on_delete=models.SET_NULL, null=True)
    order_type = models.CharField(max_length=10)
    isin_no = models.CharField(max_length=20, blank=True, null=True)

    # Buy fields (editable)
    buy_quantity = models.PositiveIntegerField(blank=True, null=True)
    price_per_share = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    buy_status = models.CharField(max_length=15, blank=True, null=True)

    # Sell fields (editable)
    sell_quantity = models.PositiveIntegerField(blank=True, null=True)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sell_status = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"RMView - {self.full_name} ({self.order_id})"

    def auto_populate_from_sources(self):
        try:
            profile = self.user.profile
            self.full_name = profile.full_name()
            self.custom_user_id = profile.custom_user_id
            self.pan_number = profile.pan_number
            self.email = profile.email or self.user.email
            self.mobile_number = profile.mobile_number
            self.assigned_rm = self.user.assigned_rm
            bank = profile.bank_accounts.first()
            if bank:
                self.bank_name = bank.bank_name
                self.account_number = bank.account_number
                self.ifsc_code = bank.ifsc_code

            cmr = profile.cmr_copies.first()
            if cmr:
                self.broker = cmr.broker
                self.client_id_input = cmr.client_id_input

            if self.transaction_type == 'buy':
                buy_txn = BuyTransaction.objects.filter(user=self.user, order_id=self.order_id).first()
                if buy_txn:
                    self.buy_quantity = buy_txn.quantity
                    self.price_per_share = buy_txn.price_per_share
                    self.total_amount = buy_txn.total_amount
                    self.buy_status = buy_txn.status
                    self.timestamp = buy_txn.timestamp
                    self.order_type = buy_txn.order_type
                    self.stock = buy_txn.stock
                    self.isin_no = buy_txn.stock.isin_no if buy_txn.stock else None
            elif self.transaction_type == 'sell':
                sell_txn = SellTransaction.objects.filter(user=self.user, order_id=self.order_id).first()
                if sell_txn:
                    self.sell_quantity = sell_txn.quantity
                    self.selling_price = sell_txn.selling_price
                    self.sell_status = sell_txn.status
                    self.timestamp = sell_txn.timestamp
                    self.order_type = 'market'  
                    self.stock = sell_txn.stock
                    self.isin_no = sell_txn.stock.isin_no if sell_txn.stock else None
        except Exception as e:
            print(f"Auto population error: {e}")
            
    def save(self, *args, **kwargs):
        self.auto_populate_from_sources()
        super().save(*args, **kwargs)

RM_Payment_Status_options = [
    ('pending', 'Pending'),
    ('partial', 'Partial Payment'),
    ('approved', 'Payment Received'),
    ('rejected', 'Rejected'),
]
            
AC_Payment_Status_options = [
    ('pending', 'Pending'),
    ('partial', 'Partial Payment'),
    ('approved', 'Payment Received'),
    ('rejected', 'Rejected'),
]
class RMPaymentRecord(models.Model):
    rm_user_view = models.ForeignKey(RMUserView, on_delete=models.CASCADE, related_name='payment_records')
    date = models.DateField()
    time = models.TimeField()
    bank_name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    remaining_amount = models.DecimalField(max_digits=12, decimal_places=2)
    screenshot = models.ImageField(upload_to='payment_screenshots/', blank=True, null=True)
    remark = models.TextField(blank=True, null=True)
    payment_status = models.CharField(
        max_length=20,
        choices=RM_Payment_Status_options,
        default='pending'
    )
    AC_Payment_Status = models.CharField(max_length=15, choices=AC_Payment_Status_options, default='pending')

    def __str__(self):
        return f"Payment - {self.rm_user_view.order_id} - {self.amount}"

