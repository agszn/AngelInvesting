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
                'available_on', 'rofr_require', 'stock_type', 'hide_company_overview'
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



























































# the below code is commented out because it is not used in the current implementation
#  the below code is for managing custom fields and their values in the admin interface
#  it is used to create, edit, and manage custom fields for stocks individually


# @admin.register(TableHeader)
# class TableHeaderAdmin(admin.ModelAdmin):
#     list_display = ['display_title', 'stock_period', 'order']
#     fields = ['title', 'stock_period', 'order']
#     ordering = ['order']
#     search_fields = ['title'] 
#     def display_title(self, obj):
#         return obj.__str__()
#     display_title.short_description = "Title"

# from django.contrib import admin
# from django import forms
# from .models import CustomFieldDefinition, CustomFieldValue, StockPeriod, TableHeader


# # admin.py
# from django.contrib import admin
# from django import forms
# from django.utils.safestring import mark_safe
# from .models import CustomFieldDefinition, CustomFieldValue, TableHeader

# class CustomFieldValueForm(forms.ModelForm):
#     class Meta:
#         model = CustomFieldValue
#         fields = '__all__'

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         # Hide all value fields
#         for ft in ['int', 'dec', 'char', 'date']:
#             self.fields[f"{ft}_value"].widget = forms.HiddenInput()

#         # Show relevant field type
#         field_def = self.initial.get('field_definition') or (self.instance.field_definition if self.instance.pk else None)

#         if field_def:
#             field_type = getattr(field_def, 'field_type', None)
#             if field_type in ['int', 'dec', 'char', 'date']:
#                 self.fields[f"{field_type}_value"].widget = forms.TextInput(attrs={
#                     'class': 'form-control mb-3',
#                     'placeholder': f"Enter {field_type} value"
#                 })

#         # Description styling
#         self.fields['description'].widget.attrs.update({
#             'class': 'form-control mb-3 description-field'
#         })
# from django.utils.html import mark_safe
# from .models import CustomFieldDefinition, CustomFieldValue

# @admin.register(CustomFieldValue)
# class CustomFieldValueAdmin(admin.ModelAdmin):
#     form = CustomFieldValueForm
#     list_display = ['name', 'field_definition', 'display_value', 'parent_field_value']
#     list_filter = ['field_definition', 'table_header']
#     search_fields = ['name', 'char_value']

#     def get_form(self, request, obj=None, **kwargs):
#         form = super().get_form(request, obj, **kwargs)
#         if obj:
#             stock_id = obj.field_definition.stock.id if obj.field_definition and obj.field_definition.stock else None
#             model_type = obj.field_definition.model_type if obj.field_definition else None

#             if stock_id and model_type:
#                 form.base_fields['parent_field_value'].queryset = CustomFieldValue.objects.filter(
#                     field_definition__stock_id=stock_id,
#                     field_definition__model_type=model_type,
#                     parent_field_value__isnull=True
#                 ).exclude(pk=obj.pk)
#             else:
#                 form.base_fields['parent_field_value'].queryset = CustomFieldValue.objects.none()
#         return form

#     def render_change_form(self, request, context, *args, **kwargs):
#         context['adminform'].form.fields['description'].help_text = mark_safe(
#             '<div><label><input type="checkbox" id="toggleDescriptionCheckbox"> Show description</label></div>'
#         )
#         return super().render_change_form(request, context, *args, **kwargs)

#     def save_model(self, request, obj, form, change):
#         super().save_model(request, obj, form, change)

#         # ✅ Automatically parse lines from char_value if field_definition.allows_children is True
#         field_def = obj.field_definition
#         if field_def and field_def.allows_children and obj.char_value:
#             lines = obj.char_value.strip().splitlines()

#             # Avoid duplication: delete old children
#             CustomFieldValue.objects.filter(parent_field_value=obj).delete()

#             for line in lines:
#                 line = line.strip()
#                 if not line:
#                     continue

#                 CustomFieldValue.objects.create(
#                     name=line,
#                     field_definition=field_def,
#                     table_header=obj.table_header,
#                     parent_field_value=obj,
#                     stock=obj.stock,
#                     char_value=line,
#                 )

#     class Media:
#         js = ('js/custom_scroll.js',)


# from django.contrib import admin
# from .models import CustomFieldDefinition, CustomFieldValue
# from .forms import CustomFieldValueForm

# class CustomFieldValueInline(admin.TabularInline):
#     model = CustomFieldValue
#     form = CustomFieldValueForm
#     extra = 25

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










# ======================================================
# ==============================================
# ======================================================
# ==============================================
# ======================================================
# ==============================================









# below is the code for CustomFieldDefinitionAdminForm and CustomFieldValueAdmin
# which are used in the admin interface for managing custom fields and their values.
# This code allows for bulk data entry and dynamic field handling based on the field type.
# It also includes logic to handle parent-child relationships between custom field values.

# from decimal import Decimal
# from django import forms
# from django.contrib import admin
# from .models import CustomFieldDefinition, CustomFieldValue, TableHeader


# def is_number(s):
#     try:
#         float(s)
#         return True
#     except ValueError:
#         return False


# class CustomFieldDefinitionAdminForm(forms.ModelForm):
#     starting_header = forms.ModelChoiceField(
#         queryset=TableHeader.objects.all(),
#         required=False,
#         label="Starting Table Header",
#         help_text="Select the first TableHeader to assign values. Others will auto-increment."
#     )

#     bulk_data = forms.CharField(
#         widget=forms.Textarea(attrs={"rows": 10, "cols": 80}),
#         required=False,
#         help_text="Paste bulk data. First row is parent, next `gap` rows are children."
#     )

#     class Meta:
#         model = CustomFieldDefinition
#         fields = '__all__'

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         # Populate grouped_rows for preview display
#         if self.instance.pk:
#             all_values = CustomFieldValue.objects.filter(
#                 field_definition=self.instance
#             ).select_related('table_header', 'parent_field_value').order_by("id")

#             grouped = {}
#             counter = 1
#             group = []
#             last_parent_id = None

#             for val in all_values:
#                 if val.parent_field_value is None:
#                     if group:
#                         grouped[counter] = group
#                         counter += 1
#                     group = [val]
#                     last_parent_id = val.id
#                 else:
#                     if val.parent_field_value_id == last_parent_id:
#                         group.append(val)
#                     else:
#                         if group:
#                             grouped[counter] = group
#                             counter += 1
#                         group = [val]
#                         last_parent_id = val.parent_field_value_id
#             if group:
#                 grouped[counter] = group

#             self.grouped_rows = grouped

#     def save(self, commit=True):
#         instance = super().save(commit=False)

#         if commit:
#             instance.save()
#             self.save_m2m()

#         bulk_data = self.cleaned_data.get("bulk_data")
#         starting_header = self.cleaned_data.get("starting_header")

#         if bulk_data and starting_header:
#             lines = bulk_data.strip().splitlines()
#             gap = instance.gap or 0
#             table_headers = list(TableHeader.objects.all().order_by("id"))
#             header_start_idx = table_headers.index(starting_header)

#             parent_field_value = None

#             for idx, line in enumerate(lines):
#                 row = line.strip().split()
#                 name_parts = [x for x in row if not is_number(x)]
#                 val_parts = [x for x in row if is_number(x)]

#                 name = ' '.join(name_parts)
#                 values = [Decimal(x) for x in val_parts]
#                 headers = table_headers[header_start_idx:header_start_idx + len(values)]

#                 if idx % (gap + 1) == 0:
#                     parent_field_value = None
#                     for val_idx, value in enumerate(values):
#                         cfv = CustomFieldValue.objects.create(
#                             field_definition=instance,
#                             name=name if val_idx == 0 else None,
#                             dec_value=value,
#                             table_header=headers[val_idx],
#                         )
#                         if val_idx == 0:
#                             parent_field_value = cfv
#                 else:
#                     for val_idx, value in enumerate(values):
#                         CustomFieldValue.objects.create(
#                             field_definition=instance,
#                             name=None,
#                             dec_value=value,
#                             table_header=headers[val_idx],
#                             parent_field_value=parent_field_value
#                         )

#         return instance


# @admin.register(CustomFieldDefinition)
# class CustomFieldDefinitionAdmin(admin.ModelAdmin):
#     form = CustomFieldDefinitionAdminForm
#     list_display = ["stock", "model_type", "field_type", "gap"]
#     fieldsets = (
#         (None, {
#             'fields': ('stock', 'model_type', 'custom_model_name', 'field_type', 'unit', 'gap')
#         }),
#         ('Bulk Entry', {
#             'fields': ('starting_header', 'bulk_data')
#         }),
#     )

#     def render_change_form(self, request, context, *args, **kwargs):
#         if 'adminform' in context and hasattr(context['adminform'].form, 'grouped_rows'):
#             context['grouped_rows'] = context['adminform'].form.grouped_rows
#         return super().render_change_form(request, context, *args, **kwargs)


# @admin.register(CustomFieldValue)
# class CustomFieldValueAdmin(admin.ModelAdmin):
#     list_display = ("name", "dec_value", "table_header", "parent_field_value")
#     list_filter = ("field_definition", "table_header")
#     search_fields = ("name",)

#     def get_form(self, request, obj=None, **kwargs):
#         form = super().get_form(request, obj, **kwargs)
#         if "description" in form.base_fields:
#             form.base_fields["description"].widget = forms.HiddenInput()
#         if "int_value" in form.base_fields:
#             form.base_fields["int_value"].widget = forms.HiddenInput()
#         if "char_value" in form.base_fields:
#             form.base_fields["char_value"].widget = forms.HiddenInput()
#         if "date_value" in form.base_fields:
#             form.base_fields["date_value"].widget = forms.HiddenInput()
#         return form















# the below code is combination of individual and bulk  but single value bulk entry



# from decimal import Decimal
# from django import forms
# from django.contrib import admin
# from django.utils.safestring import mark_safe
# from .models import CustomFieldDefinition, CustomFieldValue, TableHeader


# from django import forms
# from django.utils.safestring import mark_safe
# from django.contrib import admin
# from .models import CustomFieldValue
# from .forms import CustomFieldValueForm


# from django import forms
# from django.utils.safestring import mark_safe
# from django.contrib import admin
# from .models import CustomFieldValue
# from .forms import CustomFieldValueForm


# def is_number(s):
#     try:
#         float(s)
#         return True
#     except ValueError:
#         return False


# # class CustomFieldValueForm(forms.ModelForm):
# #     class Meta:
# #         model = CustomFieldValue
# #         fields = '__all__'

# #     def __init__(self, *args, **kwargs):
# #         super().__init__(*args, **kwargs)

# #         for ft in ['int', 'dec', 'char', 'date']:
# #             self.fields[f"{ft}_value"].widget = forms.HiddenInput()

# #         field_def = self.initial.get('field_definition') or (self.instance.field_definition if self.instance.pk else None)

# #         if field_def:
# #             field_type = getattr(field_def, 'field_type', None)
# #             if field_type in ['int', 'dec', 'char', 'date']:
# #                 self.fields[f"{field_type}_value"].widget = forms.TextInput(attrs={
# #                     'class': 'form-control mb-3',
# #                     'placeholder': f"Enter {field_type} value"
# #                 })

# #         self.fields['description'].widget = forms.HiddenInput()


# class CustomFieldDefinitionAdminForm(forms.ModelForm):
#     starting_header = forms.ModelChoiceField(
#         queryset=TableHeader.objects.all(),
#         required=False,
#         label="Starting Table Header",
#         help_text="Select the first TableHeader to assign values. Others will auto-increment."
#     )

#     bulk_data = forms.CharField(
#         widget=forms.Textarea(attrs={"rows": 10, "cols": 80}),
#         required=False,
#         help_text="Paste bulk data. First row is parent, next `gap` rows are children."
#     )

#     class Meta:
#         model = CustomFieldDefinition
#         fields = '__all__'

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         if self.instance.pk:
#             all_values = CustomFieldValue.objects.filter(
#                 field_definition=self.instance
#             ).select_related('table_header', 'parent_field_value').order_by("id")

#             grouped = {}
#             counter = 1
#             group = []
#             last_parent_id = None

#             for val in all_values:
#                 if val.parent_field_value is None:
#                     if group:
#                         grouped[counter] = group
#                         counter += 1
#                     group = [val]
#                     last_parent_id = val.id
#                 else:
#                     if val.parent_field_value_id == last_parent_id:
#                         group.append(val)
#                     else:
#                         if group:
#                             grouped[counter] = group
#                             counter += 1
#                         group = [val]
#                         last_parent_id = val.parent_field_value_id
#             if group:
#                 grouped[counter] = group

#             self.grouped_rows = grouped

#     def save(self, commit=True):
#         instance = super().save(commit)

#         bulk_data = self.cleaned_data.get("bulk_data")
#         starting_header = self.cleaned_data.get("starting_header")

#         if bulk_data and starting_header:
#             lines = bulk_data.strip().splitlines()
#             gap = instance.gap or 0
#             table_headers = list(TableHeader.objects.all().order_by("id"))
#             header_start_idx = table_headers.index(starting_header)

#             parent_field_value = None

#             for idx, line in enumerate(lines):
#                 row = line.strip().split()
#                 name_parts = [x for x in row if not is_number(x)]
#                 val_parts = [x for x in row if is_number(x)]

#                 name = ' '.join(name_parts)
#                 values = [Decimal(x) for x in val_parts]
#                 headers = table_headers[header_start_idx:header_start_idx + len(values)]

#                 if idx % (gap + 1) == 0:
#                     parent_field_value = None
#                     for val_idx, value in enumerate(values):
#                         cfv = CustomFieldValue.objects.create(
#                             field_definition=instance,
#                             name=name if val_idx == 0 else None,
#                             dec_value=value,
#                             table_header=headers[val_idx],
#                         )
#                         if val_idx == 0:
#                             parent_field_value = cfv
#                 else:
#                     for val_idx, value in enumerate(values):
#                         CustomFieldValue.objects.create(
#                             field_definition=instance,
#                             name=None,
#                             dec_value=value,
#                             table_header=headers[val_idx],
#                             parent_field_value=parent_field_value,
#                         )

#         return instance


# class CustomFieldValueInline(admin.TabularInline):
#     model = CustomFieldValue
#     form = CustomFieldValueForm
#     extra = 1


# @admin.register(CustomFieldDefinition)
# class CustomFieldDefinitionAdmin(admin.ModelAdmin):
#     form = CustomFieldDefinitionAdminForm
#     list_display = ['stock', 'unit', 'model_type', 'get_model_display_name']
#     list_filter = ['stock', 'model_type']
#     search_fields = ['stock__company_name', 'custom_model_name']
#     inlines = [CustomFieldValueInline]
#     save_on_top = True
#     fieldsets = (
#         (None, {
#             'fields': ('stock', 'model_type', 'custom_model_name', 'field_type', 'unit', 'gap')
#         }),
#         ('Bulk Entry', {
#             'fields': ('starting_header', 'bulk_data')
#         }),
#     )

#     class Media:
#         css = {'all': ('css/admin_custom.css',)}

#     def get_model_display_name(self, obj):
#         return obj.get_model_display_name()
#     get_model_display_name.admin_order_field = 'model_type'

#     def render_change_form(self, request, context, *args, **kwargs):
#         if 'adminform' in context and hasattr(context['adminform'].form, 'grouped_rows'):
#             context['grouped_rows'] = context['adminform'].form.grouped_rows
#         return super().render_change_form(request, context, *args, **kwargs)

# @admin.register(CustomFieldValue)
# class CustomFieldValueAdmin(admin.ModelAdmin):
#     form = CustomFieldValueForm
#     list_display = ("name", "dec_value", "table_header", "parent_field_value")
#     list_filter = ['field_definition', 'table_header']
#     search_fields = ['name']
#     save_on_top = True
#     def get_form(self, request, obj=None, **kwargs):
#         form = super().get_form(request, obj, **kwargs)

#         # Parent field filtering logic only
#         if obj:
#             stock_id = obj.field_definition.stock.id if obj.field_definition and obj.field_definition.stock else None
#             model_type = obj.field_definition.model_type if obj.field_definition else None

#             if stock_id and model_type:
#                 form.base_fields['parent_field_value'].queryset = CustomFieldValue.objects.filter(
#                     field_definition__stock_id=stock_id,
#                     field_definition__model_type=model_type,
#                     parent_field_value__isnull=True
#                 ).exclude(pk=obj.pk)
#             else:
#                 form.base_fields['parent_field_value'].queryset = CustomFieldValue.objects.none()

#         return form
#     def render_change_form(self, request, context, *args, **kwargs):
#         context['adminform'].form.fields['description'].help_text = mark_safe(
#             '<div><label><input type="checkbox" id="toggleDescriptionCheckbox"> Show description</label></div>'
#         )
#         return super().render_change_form(request, context, *args, **kwargs)

#     class Media:
#         js = ('js/custom_scroll.js',)

#     def display_value(self, obj):
#         for field in ['int_value', 'dec_value', 'char_value', 'date_value']:
#             val = getattr(obj, field)
#             if val:
#                 return val
#         return ""



# @admin.register(TableHeader)
# class TableHeaderAdmin(admin.ModelAdmin):
#     list_display = ['display_title', 'stock_period', 'order']
#     fields = ['title', 'stock_period', 'order']
#     ordering = ['order']
#     search_fields = ['title']

#     def display_title(self, obj):
#         return obj.__str__()
#     display_title.short_description = "Title"









from decimal import Decimal
from django import forms
from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import CustomFieldDefinition, CustomFieldValue, TableHeader
from .forms import CustomFieldValueForm


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


class CustomFieldDefinitionAdminForm(forms.ModelForm):
    starting_header = forms.ModelChoiceField(
        queryset=TableHeader.objects.all(),
        required=False,
        label="Starting Table Header",
        help_text="Select the first TableHeader to assign values. Others will auto-increment."
    )

    bulk_data = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 10, "cols": 80}),
        required=False,
        help_text="Paste bulk data. Each row will be treated as a new parent and its values as children."
    )

    class Meta:
        model = CustomFieldDefinition
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            all_values = CustomFieldValue.objects.filter(
                field_definition=self.instance
            ).select_related('table_header', 'parent_field_value').order_by("id")

            grouped = {}
            counter = 1
            group = []
            last_parent_id = None

            for val in all_values:
                if val.parent_field_value is None:
                    if group:
                        grouped[counter] = group
                        counter += 1
                    group = [val]
                    last_parent_id = val.id
                else:
                    if val.parent_field_value_id == last_parent_id:
                        group.append(val)
                    else:
                        if group:
                            grouped[counter] = group
                            counter += 1
                        group = [val]
                        last_parent_id = val.parent_field_value_id
            if group:
                grouped[counter] = group

            self.grouped_rows = grouped

    def save(self, commit=True):
        instance = super().save(commit=False)
        bulk_data = self.cleaned_data.get("bulk_data")
        starting_header = self.cleaned_data.get("starting_header")

        if commit:
            instance.save()

        if bulk_data and starting_header:
            lines = bulk_data.strip().splitlines()
            table_headers = list(TableHeader.objects.all().order_by("id"))
            try:
                header_start_idx = table_headers.index(starting_header)
            except ValueError:
                return instance  # invalid header

            for line in lines:
                row = line.strip().split()
                name_parts = [x for x in row if not is_number(x)]
                val_parts = [x for x in row if is_number(x)]

                name = ' '.join(name_parts)
                try:
                    values = [Decimal(x) for x in val_parts]
                except Exception:
                    continue

                headers = table_headers[header_start_idx:header_start_idx + len(values)]

                if not values or len(headers) < len(values):
                    continue

                parent = CustomFieldValue.objects.create(
                    field_definition=instance,
                    name=name,
                    dec_value=values[0],
                    table_header=headers[0],
                )

                for idx in range(1, len(values)):
                    CustomFieldValue.objects.create(
                        field_definition=instance,
                        name=None,
                        dec_value=values[idx],
                        table_header=headers[idx],
                        parent_field_value=parent,
                    )

        return instance


class CustomFieldValueInline(admin.TabularInline):
    model = CustomFieldValue
    form = CustomFieldValueForm
    extra = 1


@admin.register(CustomFieldDefinition)
class CustomFieldDefinitionAdmin(admin.ModelAdmin):
    form = CustomFieldDefinitionAdminForm
    list_display = ['stock', 'unit', 'model_type', 'get_model_display_name']
    list_filter = ['stock', 'model_type']
    search_fields = ['stock__company_name', 'custom_model_name']
    inlines = [CustomFieldValueInline]
    save_on_top = True

    fieldsets = (
        (None, {
            'fields': ('stock', 'model_type', 'custom_model_name', 'field_type', 'unit', 'gap')
        }),
        ('Bulk Entry', {
            'fields': ('starting_header', 'bulk_data')
        }),
    )

    class Media:
        css = {'all': ('css/admin_custom.css',)}

    def get_model_display_name(self, obj):
        return obj.get_model_display_name()
    get_model_display_name.admin_order_field = 'model_type'

    def render_change_form(self, request, context, *args, **kwargs):
        if 'adminform' in context and hasattr(context['adminform'].form, 'grouped_rows'):
            context['grouped_rows'] = context['adminform'].form.grouped_rows
        return super().render_change_form(request, context, *args, **kwargs)


@admin.register(CustomFieldValue)
class CustomFieldValueAdmin(admin.ModelAdmin):
    form = CustomFieldValueForm
    list_display = ("name", "dec_value", "table_header", "parent_field_value")
    list_filter = ['field_definition', 'table_header']
    search_fields = ['name']
    save_on_top = True

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

    class Media:
        js = ('js/custom_scroll.js',)

    def display_value(self, obj):
        for field in ['int_value', 'dec_value', 'char_value', 'date_value']:
            val = getattr(obj, field)
            if val:
                return val
        return ""


@admin.register(TableHeader)
class TableHeaderAdmin(admin.ModelAdmin):
    list_display = ['display_title', 'stock_period', 'order']
    fields = ['title', 'stock_period', 'order']
    ordering = ['order']
    search_fields = ['title']

    def display_title(self, obj):
        return obj.__str__()
    display_title.short_description = "Title"




















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


