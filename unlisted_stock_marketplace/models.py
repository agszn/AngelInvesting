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

class StockData(models.Model):
    company_name = models.CharField(max_length=255, blank=True, null=True)
    scrip_name = models.CharField(max_length=255, blank=True, null=True)
    isin_no = models.CharField(max_length=20, unique=True, blank=True, null=True)
    cin = models.CharField(max_length=50, unique=True, blank=True, null=True)
    sector = models.CharField(max_length=100, blank=True, null=True)  # Renamed from industry
    category = models.CharField(max_length=255, blank=True, null=True)  # Category/Sub-Category
    
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

class Director(models.Model):
    stock = models.ForeignKey(StockData, on_delete=models.CASCADE, related_name="directors", blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    position = models.CharField(max_length=255, blank=True, null=True)

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
        max_length=255,
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
class CustomFieldDefinition(models.Model):
    FIELD_TYPES = [
        ('char', 'Text'),
        ('int', 'Integer'),
        ('dec', 'Decimal'),
        ('date', 'Date'),
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
    ]

    name = models.CharField(max_length=255, unique=True)
    table_title = models.CharField(max_length=255, blank=True, null=True, 
    help_text="Friendly section title for UI (e.g., 'Operating Metrics')")
    
    # Users can choose from dropdown OR enter a custom model name
    model_type = models.CharField(max_length=50, choices=MODEL_TYPE_CHOICES, blank=True, null=True)
    custom_model_name = models.CharField(max_length=100, blank=True, null=True, help_text="Optional custom model name (e.g., 'CustomRatios')")

    field_type = models.CharField(max_length=10, choices=FIELD_TYPES)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.model_type and not self.custom_model_name:
            raise ValidationError("Either 'model_type' or 'custom_model_name' must be provided.")

    def get_model_display_name(self):
        return self.get_model_type_display() if self.model_type else self.custom_model_name or "Unknown"

    def __str__(self):
        return f"{self.name} ({self.get_model_display_name()})"


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

class CustomFieldValue(models.Model):
    stock = models.ForeignKey('StockData', on_delete=models.CASCADE, related_name='custom_field_values')
    stock_period = models.ForeignKey('StockPeriod', on_delete=models.CASCADE, related_name='custom_field_values', null=True, blank=True)

    field_definition = models.ForeignKey(CustomFieldDefinition, on_delete=models.CASCADE)

    # Raw values for processing
    int_value = models.IntegerField(null=True, blank=True)
    dec_value = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
    char_value = models.TextField(blank=True, null=True)
    date_value = models.DateField(null=True, blank=True)

    table_header = models.ForeignKey(
        TableHeader,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='custom_field_values',
    )

    text_style = models.CharField(max_length=30, choices=TEXT_STYLE_CHOICES, default='normal')

    class Meta:
        unique_together = ('stock', 'stock_period', 'field_definition')

    def __str__(self):
        return self.display_value()

    def display_value(self):
        """Return the formatted display value with unit/symbol"""
        if self.field_definition.field_type == 'int':
            return f"{self.int_value}{self.field_definition.unit or ''}"
        elif self.field_definition.field_type == 'dec':
            return f"{self.dec_value}{self.field_definition.unit or ''}"
        elif self.field_definition.field_type == 'date':
            return self.date_value.strftime('%Y-%m-%d') if self.date_value else ''
        else:
            return self.char_value or ''

    def get_raw_value(self):
        """Return the raw numeric value for calculations"""
        if self.field_definition.field_type == 'int':
            return self.int_value
        elif self.field_definition.field_type == 'dec':
            return self.dec_value
        return None

    def clean(self):
        """Ensure that the correct type of value is set based on the field_definition"""
        field_type = self.field_definition.field_type
        if field_type == 'int' and self.int_value is None:
            raise ValidationError(f"{self.field_definition.name} requires an integer value.")
        elif field_type == 'dec' and self.dec_value is None:
            raise ValidationError(f"{self.field_definition.name} requires a decimal value.")
        elif field_type == 'char' and not self.char_value:
            raise ValidationError(f"{self.field_definition.name} requires a text value.")
        elif field_type == 'date' and self.date_value is None:
            raise ValidationError(f"{self.field_definition.name} requires a date value.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

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

    company_name = models.CharField(max_length=255)
    stock = models.ForeignKey('StockData', on_delete=models.CASCADE, related_name='related_companies')
    relation_type = models.CharField(max_length=30, choices=RELATION_TYPE_CHOICES)
    percentage_shares_held = models.DecimalField(max_digits=5, null= True,blank= True,decimal_places=2, help_text="Enter percentage (e.g., 75.00)")

    def __str__(self):
        return f"{self.company_name} - {self.get_relation_type_display()} ({self.percentage_shares_held}%)"

# stock
class ShareholdingPattern(models.Model):
    stock = models.ForeignKey('StockData', on_delete=models.CASCADE, related_name='shareholdings')
    shareholder_name = models.CharField(max_length=255)
    number_of_shares = models.BigIntegerField()
    percentage_of_total = models.DecimalField(max_digits=6, decimal_places=2)  # Now manually editable

    def __str__(self):
        return f"{self.shareholder_name} - {self.percentage_of_total:.2f}% of {self.stock.company_name}"

# Report
class Report(models.Model):
    title = models.CharField(max_length=255)
    summary = models.TextField()
    stock = models.ForeignKey('StockData', on_delete=models.CASCADE, related_name='reports')

    def __str__(self):
        return self.title
    
# FAQ
class FAQ(models.Model):
    stock = models.ForeignKey('StockData', on_delete=models.CASCADE, related_name='faqs')
    question = models.TextField(help_text="Enter the FAQ question. Symbols like ₹, %, etc. are supported.")
    answer = models.TextField(help_text="Provide a clear, concise answer.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"FAQ for {self.stock.company_name}: {self.question[:50]}"

# PrincipalBusinessActivity
class PrincipalBusinessActivity(models.Model):
    stock = models.ForeignKey('StockData', on_delete=models.CASCADE, related_name='business_activities')
    product_service_name = models.CharField("Name and Description of main products/services", max_length=255)
    nic_code = models.CharField("NIC Code of the product/service", max_length=20, blank=True,null=True)
    turnover_percentage = models.DecimalField("% to total turnover of the Company", max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.product_service_name} ({self.nic_code})"
    
# stockTransaction
class StockTransaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stock = models.ForeignKey(StockData, on_delete=models.CASCADE)
    share_name = models.CharField(max_length=255)
    date_bought = models.DateField()
    price_bought = models.DecimalField(max_digits=10, decimal_places=2)
    price_sold = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    date_sold = models.DateField(blank=True, null=True)
    current_status = models.CharField(max_length=50, choices=[('Holding', 'Holding'), ('Sold', 'Sold')], default='Holding')
    profit = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    profit_percentage = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.share_name} ({self.current_status})"

