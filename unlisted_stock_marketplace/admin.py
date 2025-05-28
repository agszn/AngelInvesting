from django.contrib import admin
from django.utils.html import format_html

from user_auth.forms import *
from user_auth.models import *
from user_auth.utils import *
from user_auth.views import *

from unlisted_stock_marketplace.forms import *
from unlisted_stock_marketplace.models import *
from unlisted_stock_marketplace.utils import *
from unlisted_stock_marketplace.views import *

from user_portfolio.forms import *
from user_portfolio.models import *
from user_portfolio.utils import *
from user_portfolio.views import *

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
    list_display = ('company_name', 'scrip_name', 'isin_no', 'formatted_share_price', 'conviction_level', 'stock_type')
    search_fields = ('company_name', 'scrip_name', 'isin_no', 'sector', 'industry', 'cin', 'stock_type')
    list_filter = ('sector', 'conviction_level', 'drhp_filed', 'rofr_require', 'stock_type')

    inlines = [DirectorInline,CompanyRelationInline, PrincipalBusinessActivityInline,FAQAdmin,ReportAdmin, ShareholdingPatternAdmin, StockHistoryInline, StockTransactionInline]  

    fieldsets = (
        (None, {
            'fields': ('company_name', 'scrip_name', 'isin_no', 'cin', 'sector', 'category', 'registration_date', 'drhp_filed', 'available_on', 'rofr_require', 'stock_type'),
            'description': format_html('<h3 style="color:white;">Basic Information</h3>'),
        }),
        (None, {
            'fields': ('outstanding_shares', 'face_value', 'book_value', 'market_capitalization', 'profit', 'profit_percentage', 'eps', 'pe_ratio', 'ps_ratio', 'pbv'),
            'description': format_html('<h3 style="color:white;">Financial Data</h3>'),
        }),
        (None, {
            'fields': ('share_price', 'ltp', 'week_52_high', 'week_52_low', 'lifetime_high', 'lifetime_high_date', 'lifetime_low', 'lifetime_low_date', 'day_high', 'day_low'),
            'description': format_html('<h3 style="color:white;">Stock Performance</h3>'),
        }),
        (None, {
            'fields': ('lot', 'quantity', 'conviction_level', 'number_of_times_searched', 'pan_no', 'gst_no'),
            'description': format_html('<h3 style="color:white;">Other Information</h3>'),
        }),
        (None, {
            'fields': ('registered_office_address', 'transfer_agent_address', 'description', 'company_overview', 'logo'),
            'description': format_html('<h3 style="color:white;">Company Details</h3>'),
        }),
    )

    def formatted_share_price(self, obj):
        return format_html('<span style="color: green;">₹{}</span>', obj.share_price)

    formatted_share_price.admin_order_field = 'share_price'
    formatted_share_price.short_description = "Share Price (₹)"
    
    # def formatted_registration_date(self, obj):
    #     return obj.registration_date.strftime('%d-%m-%Y') if obj.registration_date else '-'
    # formatted_registration_date.short_description = "Registration Date"

    # def formatted_lifetime_high_date(self, obj):
    #     return obj.lifetime_high_date.strftime('%d-%m-%Y') if obj.lifetime_high_date else '-'
    # formatted_lifetime_high_date.short_description = "Lifetime High Date"

    # def formatted_lifetime_low_date(self, obj):
    #     return obj.lifetime_low_date.strftime('%d-%m-%Y') if obj.lifetime_low_date else '-'
    # formatted_lifetime_low_date.short_description = "Lifetime Low Date"

# part 3


@admin.register(TableHeader)
class TableHeaderAdmin(admin.ModelAdmin):
    list_display = ['display_title', 'stock_period', 'order']
    fields = ['title', 'stock_period', 'order']
    ordering = ['order']
    search_fields = ['title'] 
    def display_title(self, obj):
        return obj.__str__()
    display_title.short_description = "Title"


# @admin.register(CustomFieldDefinition)
# class CustomFieldDefinitionAdmin(admin.ModelAdmin):
#     list_display = ('name', 'field_type', 'unit', 'get_model_name_display', 'table_title', 'description')
#     list_filter = ('field_type', 'unit', 'model_type')
#     search_fields = ('name', 'description', 'custom_model_name', 'table_title')

#     fieldsets = (
#         (None, {
#             'fields': ('name', 'field_type', 'unit', 'description', 'table_title')
#         }),
#         ('Model Binding', {
#             'fields': ('model_type', 'custom_model_name'),
#             'description': 'Select a predefined model or provide a custom model name.'
#         }),
#     )

#     def get_model_name_display(self, obj):
#         return obj.get_model_display_name()
#     get_model_name_display.short_description = 'Model Name'

# # CustomFieldValue Admin
# @admin.register(CustomFieldValue)
# class CustomFieldValueAdmin(admin.ModelAdmin):
#     list_display = (
#         'stock',
#         'stock_period',  # Added
#         'field_definition',
#         'int_value',
#         'dec_value',
#         'char_value',
#         'date_value',
#         'display_value',
#         'table_header',
#         'text_style',
#     )
#     list_filter = (
#         'field_definition__field_type',
#         'field_definition__model_type',
#         'stock_period',  # Optional, if helpful
#         'text_style',
#     )
#     search_fields = (
#         'stock__company_name',
#         'field_definition__name',
#         'field_definition__custom_model_name',
#         'stock_period__period_name',  # Replace with actual field on StockPeriod
#     )
#     readonly_fields = ('display_value',)
#     fields = (
#         'stock',
#         'stock_period',  # Added
#         'field_definition',
#         'int_value',
#         'dec_value',
#         'char_value',
#         'date_value',
#         'display_value',
#         'table_header',
#         'text_style',
#     )

from django.contrib import admin
from django import forms
from .models import CustomFieldDefinition, CustomFieldValue, StockPeriod, TableHeader

# Custom form for the CustomFieldValue model
class CustomFieldValueForm(forms.ModelForm):
    class Meta:
        model = CustomFieldValue
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        field_def = self.initial.get('field_definition') or \
                    (self.instance.field_definition if self.instance.pk else None)

        if field_def:
            field_type = getattr(field_def, 'field_type', None)
            if field_type:
                for ft in ['int', 'dec', 'char', 'date']:
                    field_name = f"{ft}_value"
                    if ft != field_type:
                        self.fields[field_name].widget = forms.HiddenInput()
            else:
                for ft in ['int', 'dec', 'char', 'date']:
                    self.fields[f"{ft}_value"].widget = forms.HiddenInput()

# Inline for CustomFieldValue in CustomFieldDefinition admin
# from django.contrib import admin
# from .models import CustomFieldDefinition, CustomFieldValue
# from .forms import CustomFieldValueForm


# class CustomFieldValueInline(admin.TabularInline):
#     model = CustomFieldValue
#     form = CustomFieldValueForm
#     extra = 1
#     # classes = ['collapse']


# @admin.register(CustomFieldDefinition)
# class CustomFieldDefinitionAdmin(admin.ModelAdmin):
#     list_display = ['stock', 'unit', 'model_type', 'get_model_display_name']
#     list_filter = ['stock', 'model_type']
#     search_fields = ['stock__company_name', 'custom_model_name']
#     inlines = [CustomFieldValueInline]

#     class Media:
#         css = {
#             'all': ('css/admin_custom.css',)
#         }

#     def get_model_display_name(self, obj):
#         return obj.get_model_display_name()
#     get_model_display_name.admin_order_field = 'model_type'


# @admin.register(CustomFieldValue)
# class CustomFieldValueAdmin(admin.ModelAdmin):
#     form = CustomFieldValueForm
#     list_display = ['name', 'field_definition', 'display_value', 'text_style']
#     list_filter = ['field_definition__stock', 'text_style']
#     search_fields = ['name', 'description', 'field_definition__custom_model_name']

#     def display_value(self, obj):
#         return obj.display_value()
#     display_value.admin_order_field = 'char_value'

#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         return qs.select_related('field_definition')

#     class Media:
#         css = {
#             'all': ('css/custom_admin.css',)
#         }
from django.contrib import admin
from .models import CustomFieldDefinition, CustomFieldValue
from .forms import CustomFieldValueForm


class CustomFieldValueInline(admin.TabularInline):
    model = CustomFieldValue
    form = CustomFieldValueForm
    extra = 1
    # classes = ['collapse']

    # Custom field to add multiple entries for the same CustomFieldDefinition
    def get_extra(self, request, obj=None):
        """
        Override the `extra` value to allow adding more rows in the inline.
        """
        return 5  # You can change this number to show more or less rows by default

# Admin for CustomFieldDefinition
@admin.register(CustomFieldDefinition)
class CustomFieldDefinitionAdmin(admin.ModelAdmin):
    list_display = ['stock', 'unit', 'model_type', 'get_model_display_name']
    list_filter = ['stock', 'model_type']
    search_fields = ['stock__company_name', 'custom_model_name']
    inlines = [CustomFieldValueInline]

    class Media:
        css = {
            'all': ('css/admin_custom.css',)
        }

    def get_model_display_name(self, obj):
        return obj.get_model_display_name()
    get_model_display_name.admin_order_field = 'model_type'

from django.db.models import OuterRef, Subquery, Min


# Admin for CustomFieldValue
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode


from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode
from .forms import CustomFieldValueForm  # Adjust according to your project structure

@admin.register(CustomFieldValue)
class CustomFieldValueAdmin(admin.ModelAdmin):
    form = CustomFieldValueForm
    list_display = ['linked_name', 'field_definition', 'display_value', 'text_style', 'parent_field_value_link']
    list_filter = ['field_definition__stock', 'text_style', 'parent_field_value']
    search_fields = ['name', 'description']

    def display_value(self, obj):
        return obj.display_value()
    display_value.admin_order_field = 'dec_value'

    def linked_name(self, obj):
        """Display name as a link to filter all values with that name."""
        url = (
            reverse("admin:unlisted_stock_marketplace_customfieldvalue_changelist")
            + "?" + urlencode({"name": obj.name})
        )
        return format_html('<a href="{}">{}</a>', url, obj.name or "—")
    linked_name.short_description = "Name"

    def parent_field_value_link(self, obj):
        """Display the parent field value as a link to its details."""
        if obj.parent_field_value:
            url = reverse("admin:unlisted_stock_marketplace_customfieldvalue_change", args=[obj.parent_field_value.pk])
            return format_html('<a href="{}">{}</a>', url, obj.parent_field_value.name or "—")
        return "No Parent"
    parent_field_value_link.short_description = "Parent Field Value"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('field_definition', 'parent_field_value')




# daily stock
import csv
from django import forms
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import path
from django.contrib import messages
from .models import StockDailySnapshot, StockData

class CsvImportForm(forms.Form):
    csv_file = forms.FileField()

import csv
from django import forms
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import path
from django.contrib import messages
from .models import StockDailySnapshot, StockData

# CSV Form for file upload
class CsvImportForm(forms.Form):
    csv_file = forms.FileField()

@admin.register(StockDailySnapshot)
class StockDailySnapshotAdmin(admin.ModelAdmin):
    list_display = ('stock', 'date', 'ltp', 'share_price', 'profit', 'profit_percentage', 'conviction_level')
    list_filter = ('conviction_level', 'date', 'stock__company_name')
    search_fields = ('stock__company_name', 'stock__scrip_name')
    change_list_template = "admin/stock_snapshot_changelist.html"  # custom template

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("upload-csv/", self.upload_csv),
        ]
        return custom_urls + urls

    def upload_csv(self, request):
        if request.method == "POST":
            form = CsvImportForm(request.POST, request.FILES)
            if form.is_valid():
                decoded_file = request.FILES['csv_file'].read().decode('utf-8').splitlines()
                reader = csv.DictReader(decoded_file)
                row_count = 0
                for row in reader:
                    try:
                        stock = StockData.objects.get(company_name=row['company_name'].strip())
                        
                        # Convert strings to decimal for ltp and share_price
                        ltp = row['ltp'] and float(row['ltp']) or None
                        share_price = row['share_price'] and float(row['share_price']) or None
                        
                        snapshot, created = StockDailySnapshot.objects.update_or_create(
                            stock=stock,
                            date=row['date'],
                            defaults={
                                'ltp': ltp,
                                'share_price': share_price,
                                'conviction_level': row['conviction_level']
                            }
                        )
                        row_count += 1
                    except StockData.DoesNotExist:
                        messages.warning(request, f"Stock not found: {row['company_name']}")
                self.message_user(request, f"Uploaded {row_count} rows successfully.")
                return HttpResponseRedirect("../")
        else:
            form = CsvImportForm()

        context = {
            "form": form,
            "title": "Upload CSV for Daily Snapshots"
        }
        return render(request, "admin/csv_form.html", context)

# Register models with admin site
admin.site.register(StockData, StockDataAdmin)
admin.site.register(Director)
admin.site.register(StockHistory)
admin.site.register(StockTransaction)

