from django.db import models

class StockData(models.Model):
    company_name = models.CharField(max_length=255, blank=True, null=True)
    scrip_name = models.CharField(max_length=255, blank=True, null=True)
    isin_no = models.CharField(max_length=20, unique=True, blank=True, null=True)
    cin = models.CharField(max_length=50, unique=True, blank=True, null=True)
    sector = models.CharField(max_length=100, blank=True, null=True)
    industry = models.CharField(max_length=100, blank=True, null=True)

    registration_date = models.DateField(blank=True, null=True)
    drhp_filed = models.BooleanField(default=False)
    available_on = models.CharField(max_length=50, blank=True, null=True)
    rofr_require = models.BooleanField(default=False)

    outstanding_shares = models.BigIntegerField(blank=True, null=True)
    face_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    market_cap = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)

    eps = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pe_ratio = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    ps_ratio = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    book_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pbv = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    share_price = models.DecimalField(max_digits=10, decimal_places=2, default=1900.00, blank=True, null=True)
    week_52_high = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    week_52_low = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    lifetime_high = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    lifetime_low = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    day_high = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    day_low = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    lot = models.PositiveIntegerField(default=1, blank=True, null=True)
    qty = models.PositiveIntegerField(default=0, blank=True, null=True)
    conviction_level = models.CharField(max_length=50, default='Very High', blank=True, null=True)

    pan_no = models.CharField(max_length=10, unique=True, blank=True, null=True)

    logo = models.ImageField(upload_to='stock_logos/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    company_overview = models.TextField(blank=True, null=True)
    registered_office_address = models.TextField(blank=True, null=True)
    transfer_agent_address = models.TextField(blank=True, null=True)

    def formatted_share_price(self):
        return f"₹{self.share_price:,.2f}" if self.share_price else "N/A"

    def save(self, *args, **kwargs):
        """Automatically log price changes to StockHistory before updating"""
        if self.pk:  # Ensure it's an existing record
            old_stock = StockData.objects.filter(pk=self.pk).first()
            if old_stock and old_stock.share_price != self.share_price:
                StockHistory.objects.create(stock=self, price=old_stock.share_price)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.company_name} - ₹{self.share_price}"

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
