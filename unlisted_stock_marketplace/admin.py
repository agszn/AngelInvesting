from django.contrib import admin
from django.utils.html import format_html
from .models import *
from django.contrib.auth.models import Group

# Unregister default Group model from Django Admin
admin.site.unregister(Group)

# Custom Admin Site
class MyAdminSite(admin.AdminSite):
    site_header = "My Custom Admin Dashboard"
    site_title = "Admin Panel"
    index_title = "Welcome to the Dashboard"

    class Media:
        css = {
            'all': ('css/admin_custom.css',)
        }

# Create an instance of the custom admin site
admin_site = MyAdminSite(name='myadmin')

@admin.register(StockPeriod)
class StockPeriodAdmin(admin.ModelAdmin):
    list_display = ('get_display_period', 'year', 'month', 'day')
    list_filter = ('year', 'month')
    search_fields = ('year',)

    # Optional: order by latest period first
    ordering = ('-year', '-month', '-day')

class DirectorInline(admin.TabularInline):
    model = Director
    extra = 1  # Allows adding new directors directly

class StockHistoryInline(admin.TabularInline):
    model = StockHistory
    extra = 1
    readonly_fields = ('price', 'timestamp')

class StockTransactionInline(admin.TabularInline):
    model = StockTransaction
    extra = 1
    readonly_fields = ('user', 'share_name', 'date_bought', 'price_bought', 'price_sold', 'date_sold', 'current_status', 'profit', 'profit_percentage')

class CompanyRelationInline(admin.TabularInline):
    model = CompanyRelation
    extra = 1


class PrincipalBusinessActivityInline(admin.TabularInline):  # or admin.StackedInline
    model = PrincipalBusinessActivity
    extra = 1  # Number of empty forms shown

class FAQAdmin(admin.TabularInline):
    model = FAQ
    extra = 1

class ReportAdmin(admin.TabularInline):
    model = Report
    extra = 1

class ShareholdingPatternAdmin(admin.TabularInline):
    model = ShareholdingPattern
    extra = 1


class StockDataAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'scrip_name', 'isin_no', 'formatted_share_price', 'conviction_level')
    search_fields = ('company_name', 'scrip_name', 'isin_no', 'sector', 'industry', 'cin')
    list_filter = ('sector', 'conviction_level', 'drhp_filed', 'rofr_require')

    inlines = [DirectorInline,CompanyRelationInline, PrincipalBusinessActivityInline,FAQAdmin,ReportAdmin, ShareholdingPatternAdmin, StockHistoryInline, StockTransactionInline]  

    fieldsets = (
        (None, {
            'fields': ('company_name', 'scrip_name', 'isin_no', 'cin', 'sector', 'category', 'registration_date', 'drhp_filed', 'available_on', 'rofr_require'),
            'description': format_html('<h3 style="color:navy;">Basic Information</h3>'),
        }),
        (None, {
            'fields': ('outstanding_shares', 'face_value', 'book_value', 'market_capitalization', 'profit', 'profit_percentage', 'eps', 'pe_ratio', 'ps_ratio', 'pbv'),
            'description': format_html('<h3 style="color:navy;">Financial Data</h3>'),
        }),
        (None, {
            'fields': ('share_price', 'ltp', 'week_52_high', 'week_52_low', 'lifetime_high', 'lifetime_high_date', 'lifetime_low', 'lifetime_low_date', 'day_high', 'day_low'),
            'description': format_html('<h3 style="color:navy;">Stock Performance</h3>'),
        }),
        (None, {
            'fields': ('lot', 'quantity', 'conviction_level', 'number_of_times_searched', 'pan_no', 'gst_no'),
            'description': format_html('<h3 style="color:navy;">Other Information</h3>'),
        }),
        (None, {
            'fields': ('registered_office_address', 'transfer_agent_address', 'description', 'company_overview', 'logo'),
            'description': format_html('<h3 style="color:navy;">Company Details</h3>'),
        }),
    )

    def formatted_share_price(self, obj):
        return format_html('<span style="color: green;">₹{}</span>', obj.share_price)

    formatted_share_price.admin_order_field = 'share_price'
    formatted_share_price.short_description = "Share Price (₹)"

# part 3


@admin.register(TableHeader)
class TableHeaderAdmin(admin.ModelAdmin):
    list_display = ['display_title', 'stock_period', 'order']
    fields = ['title', 'stock_period', 'order']
    ordering = ['order']

    def display_title(self, obj):
        return obj.__str__()
    display_title.short_description = "Title"


@admin.register(CustomFieldDefinition)
class CustomFieldDefinitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'field_type', 'unit', 'get_model_name_display', 'table_title', 'description')
    list_filter = ('field_type', 'unit', 'model_type')
    search_fields = ('name', 'description', 'custom_model_name', 'table_title')

    fieldsets = (
        (None, {
            'fields': ('name', 'field_type', 'unit', 'description', 'table_title')
        }),
        ('Model Binding', {
            'fields': ('model_type', 'custom_model_name'),
            'description': 'Select a predefined model or provide a custom model name.'
        }),
    )

    def get_model_name_display(self, obj):
        return obj.get_model_display_name()
    get_model_name_display.short_description = 'Model Name'

# CustomFieldValue Admin
@admin.register(CustomFieldValue)
class CustomFieldValueAdmin(admin.ModelAdmin):
    list_display = (
        'stock',
        'stock_period',  # Added
        'field_definition',
        'int_value',
        'dec_value',
        'char_value',
        'date_value',
        'display_value',
        'table_header',
        'text_style',
    )
    list_filter = (
        'field_definition__field_type',
        'field_definition__model_type',
        'stock_period',  # Optional, if helpful
        'text_style',
    )
    search_fields = (
        'stock__company_name',
        'field_definition__name',
        'field_definition__custom_model_name',
        'stock_period__period_name',  # Replace with actual field on StockPeriod
    )
    readonly_fields = ('display_value',)
    fields = (
        'stock',
        'stock_period',  # Added
        'field_definition',
        'int_value',
        'dec_value',
        'char_value',
        'date_value',
        'display_value',
        'table_header',
        'text_style',
    )




# Register models with admin site
admin.site.register(StockData, StockDataAdmin)
admin.site.register(Director)
admin.site.register(StockHistory)
admin.site.register(StockTransaction)

