from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError


CONVICTION_CHOICES = [
    ('Very High', 'Very High'),
    ('High', 'High'),
    ('Medium', 'Medium'),
    ('Low', 'Low'),
]

STOCK_TYPE_CHOICES = [
    ('Unlisted', 'Unlisted'),
    ('Angel', 'Angel'),
    ('Listed', 'Listed'),
]



class StockData(models.Model):
    company_name = models.CharField(max_length=775, blank=True, null=True)
    scrip_name = models.CharField(max_length=775, blank=True, null=True)
    isin_no = models.CharField(max_length=20, unique=True, blank=True, null=True)
    cin = models.CharField(max_length=50, unique=True, blank=True, null=True)
    sector = models.CharField(max_length=100, blank=True, null=True)  # Renamed from industry
    category = models.CharField(max_length=775, blank=True, null=True)  # Category/Sub-Category
    
    registration_date = models.DateField(blank=True, null=True)
    drhp_filed = models.BooleanField(default=False)
    available_on = models.CharField(max_length=50, blank=True, null=True)
    rofr_require = models.BooleanField(default=False)

    outstanding_shares = models.BigIntegerField(blank=True, null=True)
    face_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])  # FV
    book_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # BV
    market_capitalization = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    profit = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    profit_percentage = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    eps = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pe_ratio = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    ps_ratio = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pbv = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    share_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    ltp = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Last traded price
    week_52_high = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    week_52_low = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    lifetime_high = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    lifetime_high_date = models.DateField(blank=True, null=True)
    lifetime_low = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    lifetime_low_date = models.DateField(blank=True, null=True)
    day_high = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    day_low = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    lot = models.PositiveIntegerField(default=1, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=0, blank=True, null=True)
    conviction_level = models.CharField(max_length=50, choices=CONVICTION_CHOICES, default='Very High', blank=True, null=True)

    number_of_times_searched = models.PositiveIntegerField(default=0)
    
    pan_no = models.CharField(max_length=10, unique=True, blank=True, null=True)
    gst_no = models.CharField(max_length=15, unique=True, blank=True, null=True)

    logo = models.ImageField(upload_to='stock_logos/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    company_overview = models.TextField(blank=True, null=True)
    registered_office_address = models.TextField(blank=True, null=True)
    transfer_agent_address = models.TextField(blank=True, null=True)

    stock_type = models.CharField(
        max_length=20,
        choices=STOCK_TYPE_CHOICES,
        default='Unlisted',
        blank=True,
        null=True,
        help_text="Type of stock: Unlisted, Angel, or Listed"
    )
    def formatted_share_price(self):
        return f"₹{self.share_price:,.2f}" if self.share_price else "N/A"

    def save(self, *args, **kwargs):
        """Automatically log price changes to StockHistory before updating"""
        if self.pk:  # Ensure it's an existing instance
            old_stock = StockData.objects.filter(pk=self.pk).first()
            if old_stock and old_stock.share_price != self.share_price and self.share_price is not None:
                StockHistory.objects.create(stock=self, price=self.share_price)
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.company_name} - ₹{self.share_price}" 
    
    def set_custom_field(self, field_name, value):
        field_def, created = CustomFieldDefinition.objects.get_or_create(name=field_name)
        custom_value, created = CustomFieldValue.objects.update_or_create(
            stock=self,
            field_definition=field_def,
            defaults={'value': value}
        )

    def get_custom_field(self, field_name):
        try:
            custom_value = self.custom_field_values.get(field_definition__name=field_name)
            return custom_value.value
        except CustomFieldValue.DoesNotExist:
            return None

from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator

# class StockDailySnapshot(models.Model):
#     stock = models.ForeignKey(StockData, on_delete=models.CASCADE, related_name='daily_snapshots')
#     date = models.DateField(default=timezone.now)
    
#     conviction_level = models.CharField(max_length=50, choices=CONVICTION_CHOICES)
    
#     # Yesterday's close
#     ltp = models.DecimalField("Yesterday's Close (LTP)", max_digits=10, decimal_places=2)

#     # Today's open
#     share_price = models.DecimalField("Today's Opening Price", max_digits=10, decimal_places=2,null=True)

#     # Auto-calculated fields
#     profit = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     profit_percentage = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

#     class Meta:
#         unique_together = ('stock', 'date')

#     def save(self, *args, **kwargs):
#         # Calculate profit and percentage
#         if self.ltp and self.share_price:
#             self.profit = self.share_price - self.ltp
#             if self.ltp != 0:
#                 self.profit_percentage = (self.profit / self.ltp) * 100
#             else:
#                 self.profit_percentage = None
#         else:
#             self.profit = None
#             self.profit_percentage = None

#         # Save snapshot first
#         super().save(*args, **kwargs)

#         # Update main StockData record with today's values
#         self.stock.ltp = self.share_price  # Treat today's open as latest closing for next day
#         self.stock.conviction_level = self.conviction_level
#         self.stock.share_price = self.share_price
#         self.stock.profit = self.profit
#         self.stock.profit_percentage = self.profit_percentage
#         self.stock.save()

#     def __str__(self):
#         return f"{self.stock.company_name} - {self.date} - ₹{self.share_price} - {self.conviction_level}"

from django.db import models
from django.utils import timezone
from decimal import Decimal

from django.db import models
from django.utils import timezone



from django.utils import timezone
from decimal import Decimal
from django.utils.timezone import localtime
class StockDailySnapshot(models.Model):
    stock = models.ForeignKey('StockData', on_delete=models.CASCADE, related_name='daily_snapshots')
    date = models.DateField(default=timezone.now)

    conviction_level = models.CharField(max_length=50, choices=CONVICTION_CHOICES)
    ltp = models.DecimalField("Yesterday's Close (LTP)", max_digits=10, decimal_places=2, null=True, blank=True)
    share_price = models.DecimalField("Today's Opening Price", max_digits=10, decimal_places=2, null=True, blank=True)

    profit = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    profit_percentage = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    sector = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        unique_together = ('stock', 'date')

    def save(self, *args, **kwargs):
        # Check if this is an update or new object
        is_new = self._state.adding

        if not is_new:
            # Fetch original snapshot to detect changes in share_price
            original = StockDailySnapshot.objects.filter(pk=self.pk).first()
            if original and original.share_price != self.share_price:
                # If share_price changed today, set ltp as old share_price
                self.ltp = original.share_price

        # For new snapshots or if ltp is still None
        if self.ltp is None:
            previous_snapshot = (
                StockDailySnapshot.objects
                .filter(stock=self.stock, date__lt=self.date)
                .order_by('-date')
                .first()
            )
            self.ltp = previous_snapshot.share_price if previous_snapshot and previous_snapshot.share_price is not None else Decimal('0.00')

        # Calculate profit and profit percentage
        if self.ltp is not None and self.share_price is not None:
            self.profit = self.share_price - self.ltp
            self.profit_percentage = (self.profit / self.ltp * 100) if self.ltp != 0 else Decimal('0.00')
        else:
            self.profit = Decimal('0.00')
            self.profit_percentage = Decimal('0.00')

        # Sync sector if missing or changed
        if not self.sector:
            self.sector = self.stock.sector
        elif self.stock.sector != self.sector:
            self.stock.sector = self.sector
            self.stock.save()

        # Save snapshot first
        super().save(*args, **kwargs)

        # Sync calculated fields to StockData - IMPORTANT!
        self.stock.ltp = self.ltp  # <-- use snapshot's ltp, NOT share_price
        self.stock.share_price = self.share_price
        self.stock.profit = self.profit
        self.stock.profit_percentage = self.profit_percentage
        self.stock.conviction_level = self.conviction_level
        self.stock.save()

    def __str__(self):
        return f"{self.stock.company_name} - {self.date} - ₹{self.share_price} - {self.conviction_level}"

# class StockDailySnapshot(models.Model):
#     stock = models.ForeignKey(StockData, on_delete=models.CASCADE, related_name='daily_snapshots')
#     date = models.DateField(default=timezone.now)
    
#     conviction_level = models.CharField(max_length=50, choices=CONVICTION_CHOICES)
    
#     # Yesterday's close
#     ltp = models.DecimalField("Yesterday's Close (LTP)", max_digits=10, decimal_places=2)

#     # Today's open
#     share_price = models.DecimalField("Today's Opening Price", max_digits=10, decimal_places=2, null=True)

#     # Auto-calculated fields
#     profit = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     profit_percentage = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

#     class Meta:
#         unique_together = ('stock', 'date')

#     def save(self, *args, **kwargs):
#         # Calculate profit and percentage
#         if self.ltp and self.share_price:
#             self.profit = self.share_price - self.ltp
#             if self.ltp != 0:
#                 self.profit_percentage = (self.profit / self.ltp) * 100
#             else:
#                 self.profit_percentage = None
#         else:
#             self.profit = None
#             self.profit_percentage = None

#         # Save the snapshot first
#         super().save(*args, **kwargs)

#         # Update the main StockData record
#         self.stock.ltp = self.ltp  # Yesterday's closing price
#         self.stock.share_price = self.share_price  # Today's opening price
#         self.stock.profit = self.profit  # Calculate profit
#         self.stock.profit_percentage = self.profit_percentage  # Calculate profit percentage
        
#         # Save the updated StockData instance
#         self.stock.save()

#     def __str__(self):
#         return f"{self.stock.company_name} - {self.date} - ₹{self.share_price} - {self.conviction_level}"


class Director(models.Model):
    stock = models.ForeignKey(StockData, on_delete=models.CASCADE, related_name="directors", blank=True, null=True)
    name = models.CharField(max_length=775, blank=True, null=True)
    position = models.CharField(max_length=775, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.position})" if self.name and self.position else "Unnamed Director"

class StockHistory(models.Model):
    stock = models.ForeignKey(StockData, on_delete=models.CASCADE, related_name='history')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.stock.company_name} - ₹{self.price} ({self.timestamp.strftime('%Y-%m-%d %H:%M:%S')})"

class StockPeriod(models.Model):
    # Separate fields for date components
    year = models.PositiveIntegerField(blank=True, null=True)
    month = models.PositiveIntegerField(blank=True, null=True)
    day = models.PositiveIntegerField(blank=True, null=True)

    def clean(self):
        # Ensure year is always provided
        if not self.year:
            raise ValidationError("Year is required.")
        
        if self.month is not None and (self.month < 1 or self.month > 12):
            raise ValidationError("Month must be between 1 and 12.")
        
        if self.day is not None:
            if self.month is None:
                raise ValidationError("Cannot specify day without a month.")
            try:
                import datetime
                datetime.date(self.year, self.month, self.day)
            except ValueError:
                raise ValidationError("Invalid day for the given month and year.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def get_display_period(self):
        if self.year and self.month and self.day:
            return f"{self.day:02d}-{self.month:02d}-{self.year}"
        elif self.year and self.month:
            import calendar
            month_name = calendar.month_name[self.month]
            return f"{month_name} {self.year}"
        elif self.year:
            return str(self.year)
        return "N/A"

    def __str__(self):
        return self.get_display_period()

# class BalanceSheet(models.Model):
#     stock_period = models.ForeignKey(StockPeriod, on_delete=models.CASCADE, related_name='balance_sheets')
    
#     # Non-current assets
#     property_plant_equipment = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     capital_work_in_progress = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     goodwill = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     other_intangible_assets = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     other_non_current_financial_assets = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     other_non_current_assets = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    
#     # Current assets
#     inventories = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     current_investments = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     trade_receivables_current = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     cash_and_cash_equivalents = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     bank_balance_other_than_cash = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     loans_current = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     other_current_financial_assets = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     other_current_assets = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    
#     total_assets = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    
#     # Equity
#     equity_share_capital = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     other_equity = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     non_controlling_interest = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    
#     # Non-current liabilities
#     borrowings_non_current = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     other_non_current_financial_liabilities = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     provisions_non_current = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     other_non_current_liabilities = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    
#     # Current liabilities
#     borrowings_current = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     trade_payable_current = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     other_current_financial_liabilities = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     other_current_liabilities = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     provisions_current = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    
#     total_equity_and_liabilities = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    
#     def __str__(self):
#         return f"Balance Sheet ({self.stock_period.get_display_period()})"

#     @property
#     def display_period(self):
#         return self.stock_period.get_display_period()

# class ProfitLossStatement(models.Model):
#     stock_period = models.ForeignKey(StockPeriod, on_delete=models.CASCADE, related_name='profit_loss_statements')
    
#     # Income
#     revenue_from_operations = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
#     other_income = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
#     total_income = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    
#     # Expenses
#     purchases_of_stock_in_trade = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
#     changes_in_inventories = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
#     employee_benefit_expenses = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
#     finance_costs = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
#     depreciation_amortisation_expense = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
#     other_expenses = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
#     total_expenses = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    
#     # Profit and Tax
#     total_profit_before_tax = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
#     total_tax_expense = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
#     total_profit_loss_from_continuing_operations = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
#     total_profit_loss_for_period = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    
#     # Attributable profits
#     profit_loss_attributable_to_owners = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
#     profit_loss_attributable_to_non_controlling_interests = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    
#     # Comprehensive income
#     oci_components_net_of_tax = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
#     other_comprehensive_income_net_of_tax = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
#     total_other_comprehensive_income = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
#     total_comprehensive_income = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
#     comprehensive_income_attributable_to_owners = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
#     comprehensive_income_attributable_to_non_controlling_interests = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    
#     # Earnings per share
#     basic_earnings_per_share = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
#     diluted_earnings_per_share = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
#     def __str__(self):
#         return f"Profit & Loss Statement ({self.stock_period.get_display_period()})"

#     @property
#     def display_period(self):
#         return self.stock_period.get_display_period()

# class CashFlow(models.Model):
#     stock_period = models.ForeignKey(StockPeriod, on_delete=models.CASCADE, related_name='cash_flows')
    
#     profit_before_tax = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    
#     # Adjustments for various items
#     finance_costs_adjustment = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     decrease_in_inventories = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     decrease_in_trade_receivables = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     decrease_in_other_non_current_assets = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     other_non_current_financial_assets = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     other_current_financial_assets = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     increase_in_trade_payables = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     depreciation_and_amortization_expense = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     provisions_current = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     other_current_financial_liabilities = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     interest_income = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     share_based_payments = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     other_non_cash_adjustments = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)

#     total_adjustments = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     net_cash_flows_from_operations = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    
#     # Income tax details
#     income_taxes_paid_refund = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     net_cash_flows_from_operating_activities = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    
#     # Investing Activities
#     proceeds_from_sale_of_ppe = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     purchase_of_ppe = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     proceeds_from_sale_of_other_long_term_assets = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     purchase_of_other_long_term_assets = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     cash_advances_and_loans_made = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     cash_receipts_from_repayment_of_advances = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     interest_received = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     other_inflows_outflows_of_cash = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)

#     net_cash_flows_from_investing_activities = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)

#     # Financing Activities
#     proceeds_from_issuing_other_equity = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     payments_to_acquire_or_redeem_shares = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     proceeds_from_borrowings = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     repayments_of_borrowings = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     payments_of_lease_liabilities = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     interest_paid = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)

#     net_cash_flows_from_financing_activities = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)

#     # Cash Flow Summary
#     net_increase_in_cash_before_exchange_rate_changes = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     net_increase_in_cash_and_equivalents = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     cash_and_cash_equivalents_at_end_of_period = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    
#     cash_flow_statement_summary = models.TextField(blank=True, null=True)

#     def __str__(self):
#         return f"Cash Flow Statement ({self.stock_period.get_display_period()})"

#     @property
#     def display_period(self):
#         return self.stock_period.get_display_period()

#     def save(self, *args, **kwargs):
#         if self.net_increase_in_cash_and_equivalents is not None:
#             try:
#                 beginning_balance = (
#                     self.cash_and_cash_equivalents_at_end_of_period or 0
#                 ) - self.net_increase_in_cash_and_equivalents
#                 self.net_increase_in_cash_before_exchange_rate_changes = beginning_balance
#             except:
#                 pass
#         super().save(*args, **kwargs)

# add 
class TableHeader(models.Model):
    title = models.CharField(
        max_length=775,
        unique=True,
        blank=True,
        help_text="Leave blank if stock period is used as title"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Order in the table display"
    )
    stock_period = models.ForeignKey(
        'StockPeriod',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='table_headers',
        help_text="If provided, will override the title"
    )

    class Meta:
        ordering = ['order']

    def __str__(self):
        if self.stock_period:
            return self.stock_period.get_display_period()
        return self.title or "Untitled Header"

    def clean(self):
        # Ensure either title or stock_period is provided
        if not self.stock_period and not self.title:
            raise ValidationError("Either title or stock_period must be provided.")

    def save(self, *args, **kwargs):
        # Automatically set the title to stock_period's display if title is blank
        if self.stock_period and not self.title:
            self.title = self.stock_period.get_display_period()
        self.full_clean()  # Run model validations
        super().save(*args, **kwargs)

# custom Fields
# class CustomFieldDefinition(models.Model):
#     FIELD_TYPES = [
#         ('char', 'Text'),
#         ('int', 'Integer'),
#         ('dec', 'Decimal'),
#         ('date', 'Date'),
#     ]

#     UNIT_CHOICES = [
#         ('', 'None'),
#         ('₹', 'Rupee (₹)'),
#         ('$', 'Dollar ($)'),
#         ('€', 'Euro (€)'),
#         ('%', 'Percentage (%)'),
#         ('bps', 'Basis Points (bps)'),
#         ('x', 'Multiplier (x)'),
#         ('Cr', 'Crore (Cr)'),
#         ('L', 'Lakh (L)'),
#         ('M', 'Million (M)'),
#         ('B', 'Billion (B)'),
#         ('Units', 'Units'),
#     ]

#     MODEL_TYPE_CHOICES = [
#         ('FinancialRatios', 'Financial Ratios'),
#         ('BalanceSheet', 'Balance Sheet'),
#         ('ProfitLossStatement', 'Profit & Loss Statement'),
#         ('CashFlow', 'Cash Flow'),
#     ]

#     stock = models.ForeignKey(
#         'StockData',
#         on_delete=models.CASCADE,
#         related_name='custom_field_definitions',
#         help_text="Associate this field with a specific stock"
#     )

#     name = models.CharField(max_length=775)
#     table_title = models.CharField(max_length=775, blank=True, null=True, 
#     help_text="Friendly section title for UI (e.g., 'Operating Metrics')")
    
#     # Users can choose from dropdown OR enter a custom model name
#     model_type = models.CharField(max_length=50, choices=MODEL_TYPE_CHOICES, blank=True, null=True)
#     custom_model_name = models.CharField(max_length=100, blank=True, null=True, help_text="Optional custom model name (e.g., 'CustomRatios')")

#     field_type = models.CharField(max_length=10, choices=FIELD_TYPES,default='int')
#     unit = models.CharField(max_length=10, choices=UNIT_CHOICES, blank=True, null=True)
#     description = models.TextField(blank=True, null=True)

#     def clean(self):
#         from django.core.exceptions import ValidationError
#         if not self.model_type and not self.custom_model_name:
#             raise ValidationError("Either 'model_type' or 'custom_model_name' must be provided.")

#     def get_model_display_name(self):
#         return self.get_model_type_display() if self.model_type else self.custom_model_name or "Unknown"

#     def __str__(self):
#         stock_name = f" [{self.stock.company_name}]" if self.stock and self.stock.company_name else ""
#         return f"{self.name} ({self.get_model_display_name()}){stock_name}"



# TEXT_STYLE_CHOICES = [
#     ('normal', 'Normal'),
#     ('bold', 'Bold'),
#     ('italic', 'Italic'),
#     ('underline', 'Underline'),
#     ('bold_italic', 'Bold & Italic'),
#     ('bold_underline', 'Bold & Underline'),
#     ('italic_underline', 'Italic & Underline'),
#     ('all', 'Bold, Italic & Underline'),
# ]

# class CustomFieldValue(models.Model):
#     stock = models.ForeignKey('StockData', on_delete=models.CASCADE, related_name='custom_field_values')
#     stock_period = models.ForeignKey('StockPeriod', on_delete=models.CASCADE, related_name='custom_field_values', null=True, blank=True)

#     field_definition = models.ForeignKey(CustomFieldDefinition, on_delete=models.CASCADE)

#     # Raw values for processing
#     int_value = models.IntegerField(null=True, blank=True)
#     dec_value = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
#     char_value = models.TextField(blank=True, null=True)
#     date_value = models.DateField(null=True, blank=True)

#     table_header = models.ForeignKey(
#         TableHeader,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name='custom_field_values',
#     )

#     text_style = models.CharField(max_length=30, choices=TEXT_STYLE_CHOICES, default='normal')

#     class Meta:
#         unique_together = ('stock', 'stock_period', 'field_definition')

#     def __str__(self):
#         return self.display_value()

#     def display_value(self):
#         """Return the formatted display value with unit/symbol"""
#         if self.field_definition.field_type == 'int':
#             return f"{self.int_value}{self.field_definition.unit or ''}"
#         elif self.field_definition.field_type == 'dec':
#             return f"{self.dec_value}{self.field_definition.unit or ''}"
#         elif self.field_definition.field_type == 'date':
#             return self.date_value.strftime('%Y-%m-%d') if self.date_value else ''
#         else:
#             return self.char_value or ''

#     def get_raw_value(self):
#         """Return the raw numeric value for calculations"""
#         if self.field_definition.field_type == 'int':
#             return self.int_value
#         elif self.field_definition.field_type == 'dec':
#             return self.dec_value
#         return None

#     def clean(self):
#         """Ensure that the correct type of value is set based on the field_definition"""
#         field_type = self.field_definition.field_type
#         if field_type == 'int' and self.int_value is None:
#             raise ValidationError(f"{self.field_definition.name} requires an integer value.")
#         elif field_type == 'dec' and self.dec_value is None:
#             raise ValidationError(f"{self.field_definition.name} requires a decimal value.")
#         elif field_type == 'char' and not self.char_value:
#             raise ValidationError(f"{self.field_definition.name} requires a text value.")
#         elif field_type == 'date' and self.date_value is None:
#             raise ValidationError(f"{self.field_definition.name} requires a date value.")

#     def save(self, *args, **kwargs):
#         self.full_clean()
#         super().save(*args, **kwargs)
from django.db import models
from django.core.exceptions import ValidationError

TEXT_STYLE_CHOICES = [
    ('normal', 'Normal'),
    ('bold', 'Bold'),
    ('italic', 'Italic'),
    ('underline', 'Underline'),
    ('bold_italic', 'Bold & Italic'),
    ('bold_underline', 'Bold & Underline'),
    ('italic_underline', 'Italic & Underline'),
    ('all', 'Bold, Italic & Underline'),
]

UNIT_CHOICES = [
    ('', 'None'),
    ('₹', 'Rupee (₹)'),
    ('$', 'Dollar ($)'),
    ('€', 'Euro (€)'),
    ('%', 'Percentage (%)'),
    ('bps', 'Basis Points (bps)'),
    ('x', 'Multiplier (x)'),
    ('Cr', 'Crore (Cr)'),
    ('L', 'Lakh (L)'),
    ('M', 'Million (M)'),
    ('B', 'Billion (B)'),
    ('Units', 'Units'),
]

MODEL_TYPE_CHOICES = [
    ('FinancialRatios', 'Financial Ratios'),
    ('BalanceSheet', 'Balance Sheet'),
    ('ProfitLossStatement', 'Profit & Loss Statement'),
    ('CashFlow', 'Cash Flow'),
    ('DividendHistory', 'Dividend History'),
]

class CustomFieldDefinition(models.Model):
    stock = models.ForeignKey(
        'StockData',
        on_delete=models.CASCADE,
        related_name='custom_field_definitions',
        help_text="Associate this field with a specific stock", blank=True, null=True
    )
    table_title = models.CharField(max_length=775, blank=True, null=True, help_text="Friendly section title for UI (e.g., 'Non-current assets')")
    
    model_type = models.CharField(max_length=50, choices=MODEL_TYPE_CHOICES, blank=True, null=True)
    custom_model_name = models.CharField(max_length=100, blank=True, null=True, help_text="Optional custom model name (e.g., 'CustomRatios')")

    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, blank=True, null=True)

    def clean(self):
        if not self.model_type and not self.custom_model_name:
            raise ValidationError("Either 'model_type' or 'custom_model_name' must be provided.")

    def get_model_display_name(self):
        return self.get_model_type_display() if self.model_type else self.custom_model_name or "Unknown"

    def __str__(self):
        stock_name = f" [{self.stock.company_name}]" if self.stock and self.stock.company_name else ""
        return f"{self.get_model_display_name()}{stock_name}"


    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.model_type and not self.custom_model_name:
            raise ValidationError("Either 'model_type' or 'custom_model_name' must be provided.")

    def get_model_display_name(self):
        return self.get_model_type_display() if self.model_type else self.custom_model_name or "Unknown"

    def __str__(self):
        stock_name = f" [{self.stock.company_name}]" if self.stock and self.stock.company_name else ""
        return f"{self.get_model_display_name()}{stock_name}"
    
# class CustomFieldValue(models.Model):
#     field_definition = models.ForeignKey(CustomFieldDefinition, on_delete=models.CASCADE)

#     name = models.CharField(max_length=775,blank=True, null=True)
#     description = models.TextField(max_length=775,blank=True, null=True)

#     int_value = models.IntegerField(null=True, blank=True)
#     dec_value = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
#     char_value = models.TextField(blank=True, null=True)
#     date_value = models.DateField(null=True, blank=True)

#     table_header = models.ForeignKey(
#         TableHeader,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name='custom_field_values',
#     )

#     text_style = models.CharField(max_length=30, choices=TEXT_STYLE_CHOICES, default='normal')

#     class Meta:
#         verbose_name = "Custom Field Value"
#         verbose_name_plural = "Custom Field Values"

#     def __str__(self):
#         return self.display_value()

#     def display_value(self):
#         if self.int_value is not None:
#             return f"{self.int_value}{self.field_definition.unit or ''}"
#         elif self.dec_value is not None:
#             return f"{self.dec_value}{self.field_definition.unit or ''}"
#         elif self.date_value is not None:
#             return self.date_value.strftime('%Y-%m-%d')
#         elif self.char_value:
#             return self.char_value
#         return ''

#     def get_raw_value(self):
#         if self.int_value is not None:
#             return self.int_value
#         elif self.dec_value is not None:
#             return self.dec_value
#         return None

#     def clean(self):
#         if any([self.int_value, self.dec_value, self.char_value, self.date_value]):
#             return
#         raise ValidationError("At least one value must be set (int, decimal, char, or date).")

#     def save(self, *args, **kwargs):
#         self.full_clean()
#         super().save(*args, **kwargs)
# class CustomFieldValue(models.Model):
#     field_definition = models.ForeignKey(CustomFieldDefinition, on_delete=models.CASCADE)
    
#     name = models.CharField(max_length=775, blank=True, null=True)
#     description = models.TextField(max_length=775, blank=True, null=True)

#     int_value = models.IntegerField(null=True, blank=True)
#     dec_value = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
#     char_value = models.TextField(blank=True, null=True)
#     date_value = models.DateField(null=True, blank=True)

#     table_header = models.ForeignKey(
#         TableHeader,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name='custom_field_values',
#     )

#     text_style = models.CharField(max_length=30, choices=TEXT_STYLE_CHOICES, default='normal')

#     class Meta:
#         verbose_name = "Custom Field Value"
#         verbose_name_plural = "Custom Field Values"

#     def __str__(self):
#         return self.display_value()

#     def display_value(self):
#         """Return the formatted display value with unit/symbol"""
#         if self.int_value is not None:
#             return f"{self.int_value}{self.field_definition.unit or ''}"
#         elif self.dec_value is not None:
#             return f"{self.dec_value}{self.field_definition.unit or ''}"
#         elif self.date_value is not None:
#             return self.date_value.strftime('%Y-%m-%d')
#         elif self.char_value:
#             return self.char_value
#         return ''

#     def get_raw_value(self):
#         """Return the raw numeric value for calculations"""
#         if self.int_value is not None:
#             return self.int_value
#         elif self.dec_value is not None:
#             return self.dec_value
#         return None

#     def clean(self):
#         """Ensure that one and only one value field is set"""
#         if any([self.int_value, self.dec_value, self.char_value, self.date_value]):
#             return
#         raise ValidationError("At least one value must be set (int, decimal, char, or date).")

#     def save(self, *args, **kwargs):
#         self.full_clean()
#         super().save(*args, **kwargs)
from django.db import models
from django.core.exceptions import ValidationError
from datetime import date

TEXT_STYLE_CHOICES = [
    ('normal', 'Normal'),
    ('bold', 'Bold'),
    ('italic', 'Italic'),
    ('underline', 'Underline'),
]

from django.db import models
from django.core.exceptions import ValidationError

class CustomFieldValue(models.Model):
    field_definition = models.ForeignKey(
        'CustomFieldDefinition', 
        on_delete=models.CASCADE
    )

    name = models.CharField(max_length=775, blank=True, null=True)
    description = models.TextField(max_length=775, blank=True, null=True)

    int_value = models.IntegerField(null=True, blank=True)
    dec_value = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
    char_value = models.TextField(blank=True, null=True)
    date_value = models.DateField(null=True, blank=True)

    table_header = models.ForeignKey(
        'TableHeader',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='custom_field_values',
    )

    text_style = models.CharField(
        max_length=30,
        choices=TEXT_STYLE_CHOICES,
        default='normal'
    )

    parent_field_value = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='sub_field_values'
    )

    class Meta:
        verbose_name = "Custom Field Value"
        verbose_name_plural = "Custom Field Values"

    def __str__(self):
        return self.name or f"Value #{self.pk}"

    def display_value(self):
        """Return the formatted display value with unit/symbol"""
        if self.int_value is not None:
            return f"{self.int_value}{self.field_definition.unit or ''}"
        elif self.dec_value is not None:
            return f"{self.dec_value}{self.field_definition.unit or ''}"
        elif self.date_value is not None:
            return self.date_value.strftime('%Y-%m-%d')
        elif self.char_value:
            return self.char_value
        return self.name or ''

    def get_raw_value(self):
        """Return the raw numeric value for calculations"""
        if self.int_value is not None:
            return self.int_value
        elif self.dec_value is not None:
            return self.dec_value
        return None

    def clean(self):
        """Validation to allow values in both parent and sub-values"""
        has_value = any([
            self.int_value is not None,
            self.dec_value is not None,
            self.char_value,
            self.date_value is not None
        ])

        if not self.parent_field_value and not self.name:
            raise ValidationError("Parent values must have a name.")
        
        # if not has_value:
        #     raise ValidationError("At least one value must be provided (int, dec, char, or date).")


        def save(self, *args, **kwargs):
            """Auto-fill sub-value names and reset value fields for sub-values"""
            if self.parent_field_value:
                if not self.name:
                    self.name = f"{self.parent_field_value.name} (Sub-value)"
                # Sub-values should not store actual values
                self.int_value = None
                self.dec_value = None
                self.char_value = None
                self.date_value = None
            super().save(*args, **kwargs)


# 
# 
# 
# 
# Subsidary and assiciate companies
from django.db import models

class CompanyRelation(models.Model):
    RELATION_TYPE_CHOICES = [
        ('subsidiary', 'Subsidiary'),
        ('associate', 'Associate'),
        ('WhollyOwnedSubsidiary', 'Wholly Owned Subsidiary'),
        ('StepDownSubsidiary', 'Step Down Subsidiary'),
        ('JointVenture','Joint Venture'),
    ]

    company_name = models.CharField(max_length=775,blank=True, null=True)
    stock = models.ForeignKey('StockData', on_delete=models.CASCADE, related_name='related_companies')
    relation_type = models.CharField(max_length=30, choices=RELATION_TYPE_CHOICES,blank=True, null=True)
    percentage_shares_held = models.DecimalField(
        max_digits=7,  # allows up to 999.9999
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Enter percentage (e.g., 75.00)"
    )


    def __str__(self):
        return f"{self.company_name} - {self.get_relation_type_display()} ({self.percentage_shares_held}%)"

# stock
class ShareholdingPattern(models.Model):
    stock = models.ForeignKey('StockData', on_delete=models.CASCADE, related_name='shareholdings')
    shareholder_name = models.CharField(max_length=775,blank=True, null=True)
    number_of_shares = models.BigIntegerField(blank=True, null=True)
    percentage_of_total = models.DecimalField(max_digits=7, decimal_places=4,blank=True, null=True)  # Now manually editable
    
    def __str__(self):
        return f"{self.shareholder_name} - {self.percentage_of_total:.2f}% of {self.stock.company_name}"

# Report
class Report(models.Model):
    title = models.CharField(max_length=775,blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    stock = models.ForeignKey('StockData', on_delete=models.CASCADE, related_name='reports',)

    def __str__(self):
        return self.title
    
# FAQ
class FAQ(models.Model):
    stock = models.ForeignKey('StockData', on_delete=models.CASCADE, related_name='faqs')
    question = models.TextField(help_text="Enter the FAQ question. Symbols like ₹, %, etc. are supported.", blank=True, null=True)
    answer = models.TextField(help_text="Provide a clear, concise answer.", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"FAQ for {self.stock.company_name}: {self.question[:50]}"

# PrincipalBusinessActivity
class PrincipalBusinessActivity(models.Model):
    stock = models.ForeignKey('StockData', on_delete=models.CASCADE, related_name='business_activities')
    product_service_name = models.CharField("Name and Description of main products/services", max_length=775,blank=True, null=True)
    nic_code = models.CharField("NIC Code of the product/service", max_length=20, blank=True,null=True)
    turnover_percentage = models.DecimalField("% to total turnover of the Company", max_digits=5, decimal_places=2,blank=True, null=True)

    def __str__(self):
        return f"{self.product_service_name} ({self.nic_code})"
    
# stockTransaction

from django.conf import settings


# wishlist
class WishlistGroup(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist_groups')
    name = models.CharField(max_length=100, editable=False)  # Auto-assigned, not user-editable
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'name')

    def __str__(self):
        return f"{self.user.username} - List {self.name}"

    def stock_count(self):
        return self.wishlist_items.count()

    def save(self, *args, **kwargs):
        if not self.pk:
            # Auto-assign name as the next number for this user
            last_number = (
                WishlistGroup.objects.filter(user=self.user)
                .annotate(num=models.functions.Cast('name', models.IntegerField()))
                .order_by('-num')
                .first()
            )
            next_number = 1
            if last_number:
                try:
                    next_number = int(last_number.name) + 1
                except ValueError:
                    pass  # fallback to 1 if name is not an integer

            self.name = str(next_number)

        super().save(*args, **kwargs)


class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist_items')
    group = models.ForeignKey(WishlistGroup, on_delete=models.CASCADE, related_name='wishlist_items', null = True, blank=True)
    stock = models.ForeignKey(StockData, on_delete=models.CASCADE, related_name='wishlisted_by')
    added_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'stock')  # Prevent duplicate wishlist entries

    def __str__(self):
        return f"{self.user.username} - {self.stock.company_name} ({self.group.name})"

    @property
    def share_price(self):
        return self.stock.share_price

    @property
    def ltp(self):
        return self.stock.ltp

    @property
    def profit(self):
        return self.stock.profit

    @property
    def profit_percentage(self):
        return self.stock.profit_percentage



from user_auth.models import Broker
class StockTransaction(models.Model): 
    TRANSACTION_TYPE_CHOICES = [('Purchase', 'Purchase'), ('Sale', 'Sale')]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stock = models.ForeignKey(StockData, on_delete=models.CASCADE)
    broker = models.ForeignKey(Broker, on_delete=models.SET_NULL, null=True, blank=True)  
    
    closing_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    price_difference = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    price_difference_percentage = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)


    share_name = models.CharField(max_length=775)
    date_bought = models.DateField()
    price_bought = models.DecimalField(max_digits=10, decimal_places=2)
    number_of_shares = models.PositiveIntegerField(default=1)
    
    price_sold = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    date_sold = models.DateField(blank=True, null=True)

    current_status = models.CharField(max_length=50, choices=[('Holding', 'Holding'), ('Sold', 'Sold')], default='Holding')
    
    invested_value = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    market_value = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    avg_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    profit = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    profit_percentage = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    overall_gain = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    overall_gain_percentage = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    days_gain_loss = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # optional historical logic
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES, default='Purchase')
    quantity = models.PositiveIntegerField(default=1)


    def save(self, *args, **kwargs):
        self.invested_value = self.price_bought * self.number_of_shares
        self.avg_price = self.price_bought

        if self.stock and self.stock.ltp:
            self.market_value = self.stock.ltp * self.number_of_shares
            self.overall_gain = self.market_value - self.invested_value
            if self.invested_value > 0:
                self.overall_gain_percentage = (self.overall_gain / self.invested_value) * 100

            # Auto update closing_price and calculate difference
            if self.stock.previous_close:
                self.closing_price = self.stock.previous_close
                self.price_difference = self.stock.ltp - self.stock.previous_close
                if self.stock.previous_close > 0:
                    self.price_difference_percentage = (self.price_difference / self.stock.previous_close) * 100
            else:
                self.closing_price = None
                self.price_difference = None
                self.price_difference_percentage = None

        else:
            self.market_value = None
            self.overall_gain = None
            self.overall_gain_percentage = None
            self.closing_price = None
            self.price_difference = None
            self.price_difference_percentage = None

        if self.price_sold:
            self.profit = (self.price_sold - self.price_bought) * self.number_of_shares
            if self.price_bought > 0:
                self.profit_percentage = ((self.price_sold - self.price_bought) / self.price_bought) * 100
        else:
            self.profit = None
            self.profit_percentage = None

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.share_name} ({self.current_status})"

