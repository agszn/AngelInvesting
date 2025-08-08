# app: unlisted_stock_marketplace
# models.py

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
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
    _disable_history = False
    def formatted_share_price(self):
        return f"₹{self.share_price:,.2f}" if self.share_price else "N/A"

    # def save(self, *args, **kwargs):
    #     """Automatically log price changes to StockHistory before updating"""
    #     if self.pk:  # Ensure it's an existing instance
    #         old_stock = StockData.objects.filter(pk=self.pk).first()
    #         if old_stock and old_stock.share_price != self.share_price and self.share_price is not None:
    #             StockHistory.objects.create(stock=self, price=self.share_price)
    #     super().save(*args, **kwargs)

    def save(self, *args, **kwargs):
        if self.pk and not getattr(self, '_disable_history', False):
            old_stock = StockData.objects.filter(pk=self.pk).first()
            if old_stock and old_stock.share_price != self.share_price and self.share_price is not None:
                from unlisted_stock_marketplace.models import StockHistory
                StockHistory.objects.create(
                    stock=self,
                    price=self.share_price,
                    timestamp=timezone.now()
                )
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


from decimal import Decimal, InvalidOperation


class StockDailySnapshot(models.Model):
    stock = models.ForeignKey('StockData', on_delete=models.CASCADE, related_name='daily_snapshots')
    date = models.DateField(default=timezone.now)

    conviction_level = models.CharField(max_length=50, choices=CONVICTION_CHOICES)
    ltp = models.DecimalField("Yesterdays Close (LTP)", max_digits=10, decimal_places=2, null=True, blank=True)
    share_price = models.DecimalField("Today's Opening Price", max_digits=10, decimal_places=2, null=True, blank=True)

    profit = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    profit_percentage = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    sector = models.CharField(max_length=100, blank=True, null=True)

    lot = models.PositiveIntegerField(default=100, blank=True, null=True)
    class Meta:
        unique_together = ('stock', 'date')
    # def save(self, *args, update_stockdata=False, **kwargs):
    #     from decimal import Decimal, InvalidOperation

    #     # ✅ Always get previous snapshot for ltp
    #     previous_snapshot = (
    #         StockDailySnapshot.objects
    #         .filter(stock=self.stock, date__lt=self.date)
    #         .order_by('-date')
    #         .first()
    #     )
    #     self.ltp = (
    #         previous_snapshot.share_price
    #         if previous_snapshot and previous_snapshot.share_price is not None
    #         else Decimal('0.00')
    #     )

    #     # Ensure ltp and share_price are Decimal
    #     try:
    #         self.ltp = Decimal(self.ltp) if self.ltp is not None else Decimal('0.00')
    #     except InvalidOperation:
    #         self.ltp = Decimal('0.00')

    #     try:
    #         self.share_price = Decimal(self.share_price) if self.share_price is not None else Decimal('0.00')
    #     except InvalidOperation:
    #         self.share_price = Decimal('0.00')

    #     # Calculate profit
    #     try:
    #         self.profit = self.share_price - self.ltp
    #         self.profit_percentage = (self.profit / self.ltp * 100) if self.ltp != 0 else Decimal('0.00')
    #     except Exception:
    #         self.profit = Decimal('0.00')
    #         self.profit_percentage = Decimal('0.00')

    #     # Sync sector
    #     if not self.sector:
    #         self.sector = self.stock.sector
    #     elif self.stock.sector != self.sector:
    #         self.stock.sector = self.sector
    #         self.stock.save()

    #     super().save(*args, **kwargs)

    #     # ✅ Sync back to StockData
    #     self.stock.ltp = self.ltp
    #     self.stock.share_price = self.share_price
    #     self.stock.profit = self.profit
    #     self.stock.profit_percentage = self.profit_percentage
    #     if self.conviction_level:
    #         self.stock.conviction_level = self.conviction_level
    #     self.stock.save()
    
    # save directly to StockHistory
    def save(self, *args, update_stockdata=False, **kwargs):
        from decimal import Decimal, InvalidOperation
        from unlisted_stock_marketplace.models import StockHistory

        is_new = self._state.adding  # to detect if this is a new snapshot

        # ✅ Always get previous snapshot for LTP
        previous_snapshot = (
            StockDailySnapshot.objects
            .filter(stock=self.stock, date__lt=self.date)
            .order_by('-date')
            .first()
        )
        self.ltp = (
            previous_snapshot.share_price
            if previous_snapshot and previous_snapshot.share_price is not None
            else Decimal('0.00')
        )

        # Ensure ltp and share_price are Decimal
        try:
            self.ltp = Decimal(self.ltp) if self.ltp is not None else Decimal('0.00')
        except InvalidOperation:
            self.ltp = Decimal('0.00')

        try:
            self.share_price = Decimal(self.share_price) if self.share_price is not None else Decimal('0.00')
        except InvalidOperation:
            self.share_price = Decimal('0.00')

        # Calculate profit
        try:
            self.profit = self.share_price - self.ltp
            self.profit_percentage = (self.profit / self.ltp * 100) if self.ltp != 0 else Decimal('0.00')
        except Exception:
            self.profit = Decimal('0.00')
            self.profit_percentage = Decimal('0.00')

        # Sync sector
        if not self.sector:
            self.sector = self.stock.sector
        elif self.stock.sector != self.sector:
            self.stock.sector = self.sector
            self.stock.save()

        # Save snapshot first
        super().save(*args, **kwargs)

        from decimal import Decimal, InvalidOperation
        from datetime import datetime
        from django.utils.timezone import make_aware
        from unlisted_stock_marketplace.models import StockHistory
        # Sync to StockData
        previous_price = self.stock.share_price
        self.stock.ltp = self.ltp
        self.stock.share_price = self.share_price
        self.stock.profit = self.profit
        self.stock.profit_percentage = self.profit_percentage
        if self.conviction_level:
            self.stock.conviction_level = self.conviction_level

        # ✅ Skip StockData history logging here
        self.stock._disable_history = True
        self.stock.save()
        self.stock._disable_history = False

        # ✅ Log history (once) if changed
        if previous_price != self.share_price:
            aware_timestamp = make_aware(datetime.combine(self.date, datetime.min.time()))
            StockHistory.objects.update_or_create(
                stock=self.stock,
                timestamp=aware_timestamp,
                defaults={'price': self.share_price}
            )

    def __str__(self):
        return f"{self.stock.company_name} - {self.date} - ₹{self.share_price} - {self.conviction_level}"



class Director(models.Model):
    stock = models.ForeignKey(StockData, on_delete=models.CASCADE, related_name="directors", blank=True, null=True)
    name = models.CharField(max_length=775, blank=True, null=True)
    position = models.CharField(max_length=775, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.position})" if self.name and self.position else "Unnamed Director"

class StockHistory(models.Model):
    stock = models.ForeignKey(StockData, on_delete=models.CASCADE, related_name='history')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateField()  

    def __str__(self):
        return f"{self.stock.company_name} - ₹{self.price} ({self.timestamp.strftime('%Y-%m-%d')})"


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


# 
# ---------------------
# -----------------------

# -------------------------
# -------------------------------

# -------------------------
# -----------------------

















# models.py admin add custom values
# from django.db import models
# from django.core.exceptions import ValidationError

# TEXT_STYLE_CHOICES = [
#     ('normal', 'Normal'),
#     ('bold', 'Bold'),
#     ('italic', 'Italic'),
# ]

# UNIT_CHOICES = [
#     ('', 'None'),
#     ('₹', 'Rupee (₹)'),
#     ('$', 'Dollar ($)'),
#     ('€', 'Euro (€)'),
#     ('%', 'Percentage (%)'),
#     ('bps', 'Basis Points (bps)'),
#     ('x', 'Multiplier (x)'),
#     ('Cr', 'Crore (Cr)'),
#     ('L', 'Lakh (L)'),
#     ('M', 'Million (M)'),
#     ('B', 'Billion (B)'),
#     ('Units', 'Units'),
# ]

# MODEL_TYPE_CHOICES = [
#     ('FinancialRatios', 'Financial Ratios'),
#     ('BalanceSheet', 'Balance Sheet'),
#     ('ProfitLossStatement', 'Profit & Loss Statement'),
#     ('CashFlow', 'Cash Flow'),
#     ('DividendHistory', 'Dividend History'),
# ]


# class CustomFieldDefinition(models.Model):
#     stock = models.ForeignKey(
#         'StockData',
#         on_delete=models.CASCADE,
#         related_name='custom_field_definitions',
#         blank=True,
#         null=True,
#         help_text="Associate this field with a specific stock"
#     )
#     table_title = models.CharField(
#         max_length=775,
#         blank=True,
#         null=True,
#         help_text="Friendly section title for UI (e.g., 'Non-current assets')"
#     )
#     model_type = models.CharField(max_length=50, choices=MODEL_TYPE_CHOICES, blank=True, null=True)
#     custom_model_name = models.CharField(max_length=100, blank=True, null=True)
#     unit = models.CharField(max_length=10, choices=UNIT_CHOICES, blank=True, null=True)

#     def clean(self):
#         if not self.model_type and not self.custom_model_name:
#             raise ValidationError("Either 'model_type' or 'custom_model_name' must be provided.")

#     def get_model_display_name(self):
#         return self.get_model_type_display() if self.model_type else self.custom_model_name or "Unknown"

#     def __str__(self):
#         stock_name = f" [{self.stock.company_name}]" if self.stock and self.stock.company_name else ""
#         return f"{self.get_model_display_name()}{stock_name}"

# from django.db import models
# from django.core.exceptions import ValidationError

# TEXT_STYLE_CHOICES = [
#     ('normal', 'Normal'),
#     ('bold', 'Bold'),
#     ('italic', 'Italic'),
#     ('underline', 'Underline'),
# ]

# class CustomFieldValue(models.Model):
#     field_definition = models.ForeignKey(
#         'CustomFieldDefinition', 
#         on_delete=models.CASCADE,
#         related_name='custom_values'
#     )

#     name = models.CharField(max_length=775, blank=True, null=True)
#     description = models.TextField(max_length=775, blank=True, null=True)

#     int_value = models.IntegerField(blank=True, null=True)
#     dec_value = models.DecimalField(max_digits=20, decimal_places=4, blank=True, null=True)
#     char_value = models.TextField(blank=True, null=True)
#     date_value = models.DateField(blank=True, null=True)

#     table_header = models.ForeignKey(
#         'TableHeader',
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name='custom_field_values'
#     )

#     text_style = models.CharField(
#         max_length=30,
#         choices=TEXT_STYLE_CHOICES,
#         default='normal'
#     )

#     parent_field_value = models.ForeignKey(
#         'self',
#         on_delete=models.CASCADE,
#         null=True,
#         blank=True,
#         related_name='sub_field_values'
#     )

#     class Meta:
#         verbose_name = "Custom Field Value"
#         verbose_name_plural = "Custom Field Values"
#         indexes = [
#             models.Index(fields=['field_definition']),
#             models.Index(fields=['parent_field_value']),
#             models.Index(fields=['table_header']),
#         ]

#     def __str__(self):
#         return self.name or f"Value #{self.pk}"

#     def display_value(self):
#         """
#         Returns a human-readable representation of the value.
#         Optimized to avoid extra DB hits when used with select_related('field_definition').
#         """
#         unit = getattr(self.field_definition, 'unit', '') or ''
        
#         if self.int_value is not None:
#             return f"{self.int_value}{unit}"
#         elif self.dec_value is not None:
#             return f"{self.dec_value}{unit}"
#         elif self.date_value is not None:
#             return self.date_value.strftime('%Y-%m-%d')
#         elif self.char_value:
#             return self.char_value
#         return self.name or ''

#     def get_raw_value(self):
#         """
#         Returns raw numeric value for computation, if available.
#         """
#         return self.int_value if self.int_value is not None else self.dec_value

#     # def clean(self):
#     #     """
#     #     Validates the model instance before saving.
#     #     Ensures that either int, dec, char, or date value is set.
#     #     Requires 'name' for top-level parent values.
#     #     """
#     #     if not self.parent_field_value and not self.name:
#     #         raise ValidationError("Parent values must have a name.")

#         # if self.int_value is None and self.dec_value is None and not self.char_value and self.date_value is None:
#         #     raise ValidationError("At least one value must be provided (int, dec, char, or date).")




from django.db import models
from django.core.exceptions import ValidationError

TEXT_STYLE_CHOICES = [
    ('normal', 'Normal'),
    ('bold', 'Bold'),
    ('italic', 'Italic'),
    ('underline', 'Underline'),
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

FIELD_TYPE_CHOICES = [
    ('int', 'Integer'),
    ('dec', 'Decimal'),
    ('char', 'Text'),
    ('date', 'Date'),
]


class CustomFieldDefinition(models.Model):
    stock = models.ForeignKey(
        'StockData',
        on_delete=models.CASCADE,
        related_name='custom_field_definitions',
        blank=True,
        null=True
    )
    table_title = models.CharField(max_length=775, blank=True, null=True)
    model_type = models.CharField(max_length=50, choices=MODEL_TYPE_CHOICES, blank=True, null=True)
    custom_model_name = models.CharField(max_length=100, blank=True, null=True)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, blank=True, null=True)
    field_type = models.CharField(max_length=10, choices=FIELD_TYPE_CHOICES, 
    default='dec', help_text="Determines which input type to show in admin")

    def clean(self):
        if not self.model_type and not self.custom_model_name:
            raise ValidationError("Either 'model_type' or 'custom_model_name' must be provided.")

    def get_model_display_name(self):
        return self.get_model_type_display() if self.model_type else self.custom_model_name or "Unknown"

    def __str__(self):
        stock_name = f" [{self.stock.company_name}]" if self.stock and self.stock.company_name else ""
        return f"{self.get_model_display_name()}{stock_name}"


class CustomFieldValue(models.Model):
    field_definition = models.ForeignKey(
        'CustomFieldDefinition', 
        on_delete=models.CASCADE,
        related_name='custom_values'
    )

    name = models.CharField(max_length=775, blank=True, null=True)
    description = models.TextField(max_length=775, blank=True, null=True)

    int_value = models.IntegerField(blank=True, null=True)
    dec_value = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    char_value = models.TextField(blank=True, null=True)
    date_value = models.DateField(blank=True, null=True)

    table_header = models.ForeignKey(
        'TableHeader',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='custom_field_values'
    )

    text_style = models.CharField(max_length=30, choices=TEXT_STYLE_CHOICES, default='normal')

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
        indexes = [
            models.Index(fields=['field_definition']),
            models.Index(fields=['parent_field_value']),
            models.Index(fields=['table_header']),
        ]

    def __str__(self):
        return self.name or self.char_value or str(self.dec_value) or f"Value #{self.pk}"

    def display_value(self):
        unit = getattr(self.field_definition, 'unit', '') or ''
        if self.int_value is not None:
            return f"{self.int_value}{unit}"
        elif self.dec_value is not None:
            return f"{self.dec_value}{unit}"
        elif self.date_value is not None:
            return self.date_value.strftime('%Y-%m-%d')
        elif self.char_value:
            return self.char_value
        return self.name or ''

    def get_raw_value(self):
        return self.int_value if self.int_value is not None else self.dec_value



















# 
# ---------------------
# -----------------------

# -------------------------
# -------------------------------

# -------------------------
# -----------------------


# models.py admin add custom values

# 
# 
# 
# 
# Subsidary and assiciate companies

class CompanyRelation(models.Model):
    RELATION_TYPE_CHOICES = [
        ('subsidiary', 'Subsidiary'),
        ('associate', 'Associate'),
        ('WhollyOwnedSubsidiary', 'Wholly Owned Subsidiary'),
        ('StepDownSubsidiary', 'Step Down Subsidiary'),
        ('JointVenture','Joint Venture'),
        ('Holding','Holding'),
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
    

# unlisted_stock_marketplace/models.py
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

