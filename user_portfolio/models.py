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

import uuid
from datetime import datetime

User = get_user_model()

ORDER_STATUS_CHOICES = [
    ('processing', 'Processing'),
    ('completed', 'Completed'),
    ('on_hold', 'On Hold'),
    ('cancelled', 'Cancelled'),
]




RM_STATUS_LABELS = {
    'processing': 'Processing',
    'completed': 'Process to Accounts team',
    'on_hold': 'On Hold',
    'cancelled': 'Rejected by RM',
}

AC_STATUS_LABELS = {
    'processing': 'Processing',
    'completed': 'Process to Share Transfer team',
    'on_hold': 'On Hold',
    'cancelled': 'Rejected by AC',
}

ST_STATUS_LABELS = {
    'processing': 'Processing',
    'completed': 'Transfer Share',
    'on_hold': 'On Hold',
    'cancelled': 'Rejected by ST',
}


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
    
    RM_status = models.CharField(max_length=15, choices=RM_STATUS_LABELS, default='processing')
    RMApproved = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='rm_approved_transactions'
    )


    AC_status = models.CharField(max_length=15, choices=AC_STATUS_LABELS, default='processing')
    ACApproved = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='ac_approved_transactions'
    )

    
    status = models.CharField(max_length=15, choices=ST_STATUS_LABELS, default='processing')
    STApproved = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='st_approved_transactions'
    )

    order_id = models.CharField(max_length=20, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = f"Ord_B_{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.order_id} - {self.user.username}"


# class BuyTransactionOtherAdvisor(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     stock = models.ForeignKey(StockData, on_delete=models.CASCADE)
#     advisor = models.ForeignKey(Advisor, on_delete=models.SET_NULL, null=True)
#     broker = models.ForeignKey(Broker, on_delete=models.SET_NULL, null=True)
#     quantity = models.PositiveIntegerField()
#     price_per_share = models.DecimalField(max_digits=10, decimal_places=2)
#     order_type = models.CharField(max_length=10, choices=(('market', 'Market'), ('limit', 'Limit')))
#     total_amount = models.DecimalField(max_digits=12, decimal_places=2)
#     timestamp = models.DateTimeField(auto_now_add=True)

#     status = models.CharField(max_length=15, choices=ORDER_STATUS_CHOICES, default='processing')
#     order_id = models.CharField(max_length=20, unique=True, blank=True, null=True)

#     def save(self, *args, **kwargs):
#         if not self.order_id:
#             self.order_id = f"Ord_OA_{uuid.uuid4().hex[:10].upper()}"
#         super().save(*args, **kwargs)


from decimal import Decimal
from decimal import Decimal
import uuid
from django.db import models

class BuyTransactionOtherAdvisor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(StockData, on_delete=models.CASCADE)
    advisor = models.ForeignKey(Advisor, on_delete=models.SET_NULL, null=True)
    broker = models.ForeignKey(Broker, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    price_per_share = models.DecimalField(max_digits=10, decimal_places=2)
    order_type = models.CharField(max_length=10, choices=(('market', 'Market'), ('limit', 'Limit')))
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    # Optional: keep status if you still want transaction tracking
    status = models.CharField(max_length=15, choices=ST_STATUS_LABELS, default='completed')
    order_id = models.CharField(max_length=20, unique=True, blank=True, null=True)

    # Calculated and stored values
    invested_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    market_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    overall_gain_loss = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    todays_gain_loss = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = f"Ord_OA_{uuid.uuid4().hex[:10].upper()}"

        # Compute derived values
        self.invested_amount = self.total_amount
        self.market_value = Decimal(self.quantity) * self.stock.share_price
        self.overall_gain_loss = self.market_value - self.invested_amount

        if self.stock.ltp:
            change_per_share = self.stock.share_price - self.stock.ltp
            self.todays_gain_loss = Decimal(self.quantity) * change_per_share
        else:
            self.todays_gain_loss = Decimal('0.00')

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} - {self.stock} - {self.order_id}"


from decimal import Decimal
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required


@csrf_exempt
@login_required
def edit_sell_transaction_ac_status(request, transaction_id):
    if request.method == 'POST':
        transaction = get_object_or_404(SellTransaction, id=transaction_id)

        if request.user.user_type == 'AC':
            new_status = request.POST.get('AC_status')
            transaction.AC_status = new_status

            if new_status == 'completed':
                transaction.ACApproved = request.user

            transaction.save()
            messages.success(request, "Accounts Approval Status updated successfully.")
        else:
            messages.error(request, "Unauthorized access.")

    return redirect(request.META.get('HTTP_REFERER', '/'))

class SellTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(StockData, on_delete=models.CASCADE)
    advisor = models.ForeignKey(Advisor, on_delete=models.SET_NULL, null=True)
    broker = models.ForeignKey(Broker, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    selling_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_value = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)

    status = models.CharField(max_length=15, choices=ST_STATUS_LABELS, default='processing')
    STApproved = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='st_approved_sell_transactions'
    )
    
    RM_status = models.CharField(max_length=15, choices=RM_STATUS_LABELS, default='processing')
    RMApproved = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='rm_approved_sell_transactions'
    )
    
    AC_status = models.CharField(max_length=15, choices=AC_STATUS_LABELS, default='processing')
    ACApproved = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='ac_approved_sell_transactions'
    )    

    order_id = models.CharField(max_length=20, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Generate order_id if not present
        if not self.order_id:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]
            self.order_id = f"Ord_S_{timestamp}"

        # Set selling_price from stock.share_price if not manually set
        if self.selling_price is None and self.stock.share_price is not None:
            self.selling_price = Decimal(self.stock.share_price)

        # Calculate total_value
        if self.quantity is not None and self.selling_price is not None:
            self.total_value = self.quantity * self.selling_price

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Sell Order {self.order_id} - {self.stock.company_name} x{self.quantity}"



class SellTransactionOtherAdvisor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(StockData, on_delete=models.CASCADE)
    advisor = models.ForeignKey(Advisor, on_delete=models.SET_NULL, null=True)
    broker = models.ForeignKey(Broker, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    selling_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_value = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)

    status = models.CharField(max_length=15, choices=ST_STATUS_LABELS, default='processing')
    STApproved = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='st_approved_sell_otherAdvisor_transactions'
    )
    
    RM_status = models.CharField(max_length=15, choices=RM_STATUS_LABELS, default='processing')
    RMApproved = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='rm_approved_sell_otherAdvisor_transactions'
    )
    AC_status = models.CharField(max_length=15, choices=AC_STATUS_LABELS, default='processing')
    ACApproved = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='ac_approved_sell_otherAdvisor_transactions'
    )    
    
    order_id = models.CharField(max_length=20, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.order_id:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]
            self.order_id = f"Ord_SO_{timestamp}"

        if self.selling_price is None and self.stock.share_price is not None:
            self.selling_price = Decimal(self.stock.share_price)

        if self.quantity and self.selling_price:
            self.total_value = self.quantity * self.selling_price

        super().save(*args, **kwargs)

    def __str__(self):
        return f"SellOther - {self.order_id} - {self.stock.company_name} x{self.quantity}"
    




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


# app: user_portfolio
# models.py

from django.db import models
from django.conf import settings
from unlisted_stock_marketplace.models import StockData
from site_Manager.models import Advisor, Broker
from django.db.models import Sum, F
from decimal import Decimal
from decimal import Decimal
from django.db.models import Sum, F, Q

# class UserStockInvestmentSummary(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     stock = models.ForeignKey('unlisted_stock_marketplace.StockData', on_delete=models.CASCADE)

#     advisor = models.ForeignKey('site_Manager.Advisor', on_delete=models.SET_NULL, null=True, blank=True)
#     broker = models.ForeignKey('site_Manager.Broker', on_delete=models.SET_NULL, null=True, blank=True)

#     quantity_held = models.PositiveIntegerField(default=0)
#     avg_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)

#     share_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # Current price
#     ltp = models.DecimalField(max_digits=12, decimal_places=2, default=0)          # Previous price
#     previous_day_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)

#     investment_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
#     market_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
#     overall_gain_loss = models.DecimalField(max_digits=15, decimal_places=2, default=0)
#     day_gain_loss = models.DecimalField(max_digits=15, decimal_places=2, default=0)

#     buy_order_count = models.PositiveIntegerField(default=0)
#     buy_order_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)

#     sell_order_count = models.PositiveIntegerField(default=0)
#     sell_order_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)

#     last_updated = models.DateTimeField(auto_now=True)
    
#     def update_from_transactions(self):
#         from user_portfolio.models import BuyTransaction, SellTransaction, BuyTransactionOtherAdvisor
#         from itertools import chain
#         from decimal import Decimal
#         from django.db.models import Sum, F

#         # Combine both BuyTransaction and BuyTransactionOtherAdvisor
#         buy_txns_1 = BuyTransaction.objects.filter(user=self.user, stock=self.stock, status='completed')
#         buy_txns_2 = BuyTransactionOtherAdvisor.objects.filter(user=self.user, stock=self.stock, status='completed')
#         buy_txns = list(chain(buy_txns_1, buy_txns_2))

#         # Sell Transactions
#         sell_txns = SellTransaction.objects.filter(
#             user=self.user,
#             stock=self.stock,
#             status='completed'
#         ).exclude(advisor__advisor_type='Other')

#         # Aggregations from both Buy sources
#         total_bought_qty = sum(txn.quantity for txn in buy_txns)
#         total_bought_cost = sum(txn.quantity * txn.price_per_share for txn in buy_txns)

#         total_sold_qty = sell_txns.aggregate(total=Sum('quantity'))['total'] or 0

#         self.buy_order_count = len(buy_txns)
#         self.buy_order_total = total_bought_cost or Decimal(0)

#         self.sell_order_count = sell_txns.count()
#         self.sell_order_total = sell_txns.aggregate(
#             total=Sum(F('selling_price') * F('quantity'))
#         )['total'] or Decimal(0)

#         self.quantity_held = max(total_bought_qty - total_sold_qty, 0)
#         self.avg_price = (total_bought_cost / total_bought_qty) if total_bought_qty else Decimal(0)

#         # Set price values from Stock
#         self.share_price = self.stock.share_price or Decimal(0)
#         self.ltp = self.stock.ltp or Decimal(0)
#         self.previous_day_price = self.ltp

#         self.investment_amount = self.quantity_held * self.avg_price
#         self.market_value = self.quantity_held * self.share_price
#         self.overall_gain_loss = self.market_value - self.investment_amount
#         self.day_gain_loss = self.quantity_held * (self.share_price - self.previous_day_price)

#         # Set advisor and broker from latest txn
#         latest_txn = sorted(buy_txns, key=lambda x: x.timestamp, reverse=True)[0] if buy_txns else None
#         if latest_txn:
#             self.advisor = getattr(latest_txn, 'advisor', None)
#             self.broker = getattr(latest_txn, 'broker', None)

#     class Meta:
#         unique_together = ('user', 'stock')

#     def __str__(self):
#         return f"{self.user.username} - {self.stock.company_name}"

class UserStockInvestmentSummary(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stock = models.ForeignKey('unlisted_stock_marketplace.StockData', on_delete=models.CASCADE)

    is_other_advisor = models.BooleanField(default=False)  # 👈 NEW FIELD to distinguish buy vs other-buy

    advisor = models.ForeignKey('site_Manager.Advisor', on_delete=models.SET_NULL, null=True, blank=True)
    broker = models.ForeignKey('site_Manager.Broker', on_delete=models.SET_NULL, null=True, blank=True)

    quantity_held = models.PositiveIntegerField(default=0)
    avg_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    share_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ltp = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    previous_day_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    investment_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    market_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    overall_gain_loss = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    day_gain_loss = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    buy_order_count = models.PositiveIntegerField(default=0)
    buy_order_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    sell_order_count = models.PositiveIntegerField(default=0)
    sell_order_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'stock', 'is_other_advisor')  # 👈 ensure separation
    from decimal import Decimal

    def update_from_transactions(self):
        from user_portfolio.models import BuyTransaction, SellTransaction, BuyTransactionOtherAdvisor
        from django.db.models import Sum, F

        total_bought_qty = 0
        total_bought_cost = Decimal(0)

        if self.is_other_advisor:
            buy_txns = BuyTransactionOtherAdvisor.objects.filter(
                user=self.user, stock=self.stock, status='completed'
            )
            total_bought_qty = sum(txn.quantity for txn in buy_txns)
            total_bought_cost = sum(txn.quantity * txn.price_per_share for txn in buy_txns)
            sell_txns = None
        else:
            buy_txns = BuyTransaction.objects.filter(
                user=self.user, stock=self.stock, status='completed'
            )
            total_bought_qty = sum(txn.quantity for txn in buy_txns)
            total_bought_cost = sum(txn.quantity * txn.price_per_share for txn in buy_txns)

            sell_txns = SellTransaction.objects.filter(
                user=self.user, stock=self.stock, status='completed'
            ).exclude(advisor__advisor_type='Other')
            total_sold_qty = sell_txns.aggregate(total=Sum('quantity'))['total'] or 0

        # Common buy data
        self.buy_order_count = len(buy_txns)
        self.buy_order_total = total_bought_cost or Decimal(0)

        # Quantity held
        if self.is_other_advisor:
            self.quantity_held = total_bought_qty
        else:
            self.quantity_held = max(total_bought_qty - total_sold_qty, 0)

        # Avg price (Formula 1)
        self.avg_price = (total_bought_cost / total_bought_qty) if total_bought_qty else Decimal(0)

        # Set market prices from stock
        self.share_price = self.stock.share_price or Decimal(0)
        self.ltp = self.stock.ltp or Decimal(0)
        self.previous_day_price = self.ltp

        # Current Value (Formula 2)
        self.market_value = self.share_price * self.quantity_held

        # Invested
        self.investment_amount = self.quantity_held * self.avg_price

        # Overall Gain ₹ (Formula 3)
        self.overall_gain_loss = self.market_value - self.investment_amount

        # Overall Gain % (Formula 4)
        self.overall_gain_percent = (
            (self.overall_gain_loss / self.investment_amount) * 100 if self.investment_amount else Decimal(0)
        )

        # Day Gain ₹ (Formula 5)
        self.day_gain_loss = (self.share_price - self.previous_day_price) * self.quantity_held

        # Day Gain % (Formula 6)
        self.day_gain_percent = (
            ((self.share_price - self.previous_day_price) / self.previous_day_price) * 100
            if self.previous_day_price else Decimal(0)
        )

        # Sell side (only for non-other advisors)
        if not self.is_other_advisor:
            self.sell_order_count = sell_txns.count()
            self.sell_order_total = sell_txns.aggregate(
                total=Sum(F('selling_price') * F('quantity'))
            )['total'] or Decimal(0)

        # Advisor/broker from latest txn
        latest_txn = sorted(buy_txns, key=lambda x: x.timestamp, reverse=True)[0] if buy_txns else None
        if latest_txn:
            self.advisor = getattr(latest_txn, 'advisor', None)
            self.broker = getattr(latest_txn, 'broker', None)
