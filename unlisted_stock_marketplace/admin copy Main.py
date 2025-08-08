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

from django.contrib import admin
from django.utils.html import format_html
from .models import *

@admin.register(StockPeriod)
class StockPeriodAdmin(admin.ModelAdmin):
    list_display = ('get_display_period', 'year', 'month', 'day')
    list_filter = ('year', 'month')
    search_fields = ('year',)
    ordering = ('-year', '-month', '-day')


class DirectorInline(admin.TabularInline):
    model = Director
    extra = 1
    classes = ['collapse']


# class StockHistoryInline(admin.TabularInline):
#     model = StockHistory
#     extra = 1
#     readonly_fields = ('price', 'timestamp')
#     can_delete = False
#     show_change_link = False
#     classes = ['collapse']

class StockHistoryInline(admin.TabularInline):
    model = StockHistory
    extra = 1
    fields = ('price', 'timestamp')  # Explicitly include editable fields
    readonly_fields = ()  # Remove read-only status
    can_delete = True  # Allow deleting if needed
    show_change_link = True  # Optional: link to detail view
    classes = ['collapse']

class CompanyRelationInline(admin.TabularInline):
    model = CompanyRelation
    extra = 1
    classes = ['collapse']


class PrincipalBusinessActivityInline(admin.TabularInline):
    model = PrincipalBusinessActivity
    extra = 1
    classes = ['collapse']


class FAQAdmin(admin.TabularInline):
    model = FAQ
    extra = 1
    classes = ['collapse']

class ShareholdingPatternAdmin(admin.TabularInline):
    model = ShareholdingPattern
    extra = 1
    classes = ['collapse']


class ReportAdmin(admin.TabularInline):
    model = Report
    extra = 1



from django.utils.safestring import mark_safe
from .format_utils import render_custom_format

class StockDataAdmin(admin.ModelAdmin):

    list_display = (
        'company_name', 'scrip_name', 'isin_no', 
        'formatted_share_price', 'conviction_level', 'stock_type'
    )
    search_fields = ('company_name', 'scrip_name', 'isin_no', 'sector', 'category', 'cin', 'stock_type')
    list_filter = ('sector', 'conviction_level', 'drhp_filed', 'rofr_require', 'stock_type')
    save_on_top = True

    inlines = [
        DirectorInline,
        CompanyRelationInline,
        PrincipalBusinessActivityInline,
        FAQAdmin,
        ReportAdmin,
        ShareholdingPatternAdmin,
        StockHistoryInline
    ]

    fieldsets = (
        ('📌 Basic Information', {
            'fields': (
                'company_name', 'scrip_name', 'isin_no', 'cin',
                'sector', 'category', 'registration_date', 'drhp_filed',
                'available_on', 'rofr_require', 'stock_type'
            ),
            'description': 'Essential identification and classification of the company.'
        }),
        ('💰 Financial Data', {
            'fields': (
                'outstanding_shares', 'face_value', 'book_value',
                'market_capitalization', 'profit', 'profit_percentage',
                'eps', 'pe_ratio', 'ps_ratio', 'pbv'
            ),
            'description': 'Core financial metrics and ratios.'
        }),
        ('📈 Stock Performance', {
            'fields': (
                'share_price', 'ltp', 'week_52_high', 'week_52_low',
                'lifetime_high', 'lifetime_high_date',
                'lifetime_low', 'lifetime_low_date',
                'day_high', 'day_low'
            ),
            'description': 'Price history and volatility metrics.'
        }),
        ('📦 Stock Configuration', {
            'fields': (
                'lot', 'quantity', 'conviction_level',
                'number_of_times_searched', 'pan_no', 'gst_no'
            ),
            'description': 'Administrative and market positioning settings.'
        }),
        ('🏢 Company Description', {
            'fields': (
                'registered_office_address', 'transfer_agent_address',
                'description', 
                'company_overview',  
                'logo'
            ),
            'description': 'Narrative and visual branding of the company.'
        }),
    )

    def formatted_share_price(self, obj):
        if obj.share_price:
            return format_html('<span style="color: green; font-weight: bold;">₹{}</span>', obj.share_price)
        return "N/A"

    formatted_share_price.admin_order_field = 'share_price'
    formatted_share_price.short_description = "Share Price (₹)"

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
# class CustomFieldValueForm(forms.ModelForm):
#     class Meta:
#         model = CustomFieldValue
#         fields = '__all__'

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         field_def = self.initial.get('field_definition') or \
#                     (self.instance.field_definition if self.instance.pk else None)

#         if field_def:
#             field_type = getattr(field_def, 'field_type', None)
#             if field_type:
#                 for ft in ['int', 'dec', 'char', 'date']:
#                     field_name = f"{ft}_value"
#                     if ft != field_type:
#                         self.fields[field_name].widget = forms.HiddenInput()
#             else:
#                 for ft in ['int', 'dec', 'char', 'date']:
#                     self.fields[f"{ft}_value"].widget = forms.HiddenInput()


# from django.contrib import admin
# from .models import CustomFieldValue

# @admin.register(CustomFieldValue)
# class CustomFieldValueAdmin(admin.ModelAdmin):
#     list_display = ['name', 'field_definition', 'display_value', 'parent_field_value']
#     list_filter = ['field_definition', 'table_header']
#     search_fields = ['name', 'char_value']

#     def formfield_for_foreignkey(self, db_field, request, **kwargs):
#         if db_field.name == "parent_field_value":
#             kwargs["queryset"] = CustomFieldValue.objects.filter(parent_field_value__isnull=True)
#         return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
#     class Media:
#         js = ('js/custom_scroll.js',)




# admin.py
from django.contrib import admin
from django import forms
from django.utils.safestring import mark_safe
from .models import CustomFieldDefinition, CustomFieldValue, TableHeader

class CustomFieldValueForm(forms.ModelForm):
    class Meta:
        model = CustomFieldValue
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Hide all value fields
        for ft in ['int', 'dec', 'char', 'date']:
            self.fields[f"{ft}_value"].widget = forms.HiddenInput()

        # Show relevant field type
        field_def = self.initial.get('field_definition') or (self.instance.field_definition if self.instance.pk else None)

        if field_def:
            field_type = getattr(field_def, 'field_type', None)
            if field_type in ['int', 'dec', 'char', 'date']:
                self.fields[f"{field_type}_value"].widget = forms.TextInput(attrs={
                    'class': 'form-control mb-3',
                    'placeholder': f"Enter {field_type} value"
                })

        # Description styling
        self.fields['description'].widget.attrs.update({
            'class': 'form-control mb-3 description-field'
        })
from django.utils.html import mark_safe
from .models import CustomFieldDefinition, CustomFieldValue

@admin.register(CustomFieldValue)
class CustomFieldValueAdmin(admin.ModelAdmin):
    form = CustomFieldValueForm
    list_display = ['name', 'field_definition', 'display_value', 'parent_field_value']
    list_filter = ['field_definition', 'table_header']
    search_fields = ['name', 'char_value']

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            stock_id = obj.field_definition.stock.id if obj.field_definition and obj.field_definition.stock else None
            model_type = obj.field_definition.model_type if obj.field_definition else None

            if stock_id and model_type:
                form.base_fields['parent_field_value'].queryset = CustomFieldValue.objects.filter(
                    field_definition__stock_id=stock_id,
                    field_definition__model_type=model_type,
                    parent_field_value__isnull=True
                ).exclude(pk=obj.pk)
            else:
                form.base_fields['parent_field_value'].queryset = CustomFieldValue.objects.none()
        return form

    def render_change_form(self, request, context, *args, **kwargs):
        context['adminform'].form.fields['description'].help_text = mark_safe(
            '<div><label><input type="checkbox" id="toggleDescriptionCheckbox"> Show description</label></div>'
        )
        return super().render_change_form(request, context, *args, **kwargs)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        # ✅ Automatically parse lines from char_value if field_definition.allows_children is True
        field_def = obj.field_definition
        if field_def and field_def.allows_children and obj.char_value:
            lines = obj.char_value.strip().splitlines()

            # Avoid duplication: delete old children
            CustomFieldValue.objects.filter(parent_field_value=obj).delete()

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                CustomFieldValue.objects.create(
                    name=line,
                    field_definition=field_def,
                    table_header=obj.table_header,
                    parent_field_value=obj,
                    stock=obj.stock,
                    char_value=line,
                )

    class Media:
        js = ('js/custom_scroll.js',)








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
    extra = 25

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


