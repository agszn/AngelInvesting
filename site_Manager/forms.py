from django import forms
from django.forms import inlineformset_factory
from unlisted_stock_marketplace.models import *

class CustomFieldDefinitionForm(forms.ModelForm):
    class Meta:
        model = CustomFieldDefinition
        fields = ['stock', 'table_title', 'model_type', 'custom_model_name', 'unit']

CustomFieldValueFormSet = inlineformset_factory(
    CustomFieldDefinition,
    CustomFieldValue,
    fields=['name', 'description', 'int_value', 'dec_value', 'char_value', 'date_value', 'text_style', 'table_header', 'parent_field_value'],
    extra=5,
    can_delete=True
)


from django import forms
from .models import Broker, Advisor

from django import forms
from .models import Broker

class BrokerForm(forms.ModelForm):
    class Meta:
        model = Broker
        fields = ['broker_id', 'name', 'pan', 'email', 'contact']
        widgets = {
            'broker_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter unique broker ID (e.g., BRK001)'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter broker name'
            }),
            'pan': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter PAN number (optional)'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email address'
            }),
            'contact': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter contact number'
            }),
        }


from django import forms
from .models import Advisor

class AdvisorForm(forms.ModelForm):
    class Meta:
        model = Advisor
        fields = ['advisor_type']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['advisor_type'].widget.attrs.update({'class': 'form-control'})

# StockData
from django import forms
from django.forms import inlineformset_factory

class StockDataForm(forms.ModelForm):
    class Meta:
        model = StockData
        fields = '__all__'
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'scrip_name': forms.TextInput(attrs={'class': 'form-control'}),
            'isin_no': forms.TextInput(attrs={'class': 'form-control'}),
            'cin': forms.TextInput(attrs={'class': 'form-control'}),
            'sector': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),

            'registration_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'drhp_filed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'available_on': forms.TextInput(attrs={'class': 'form-control'}),
            'rofr_require': forms.CheckboxInput(attrs={'class': 'form-check-input'}),

            'outstanding_shares': forms.NumberInput(attrs={'class': 'form-control'}),
            'face_value': forms.NumberInput(attrs={'class': 'form-control'}),
            'book_value': forms.NumberInput(attrs={'class': 'form-control'}),
            'market_capitalization': forms.NumberInput(attrs={'class': 'form-control'}),
            'profit': forms.NumberInput(attrs={'class': 'form-control'}),
            'profit_percentage': forms.NumberInput(attrs={'class': 'form-control'}),

            'eps': forms.NumberInput(attrs={'class': 'form-control'}),
            'pe_ratio': forms.NumberInput(attrs={'class': 'form-control'}),
            'ps_ratio': forms.NumberInput(attrs={'class': 'form-control'}),
            'pbv': forms.NumberInput(attrs={'class': 'form-control'}),

            'share_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'partner_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'ltp': forms.NumberInput(attrs={'class': 'form-control'}),
            'week_52_high': forms.NumberInput(attrs={'class': 'form-control'}),
            'week_52_low': forms.NumberInput(attrs={'class': 'form-control'}),
            'lifetime_high': forms.NumberInput(attrs={'class': 'form-control'}),
            'lifetime_high_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'lifetime_low': forms.NumberInput(attrs={'class': 'form-control'}),
            'lifetime_low_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'day_high': forms.NumberInput(attrs={'class': 'form-control'}),
            'day_low': forms.NumberInput(attrs={'class': 'form-control'}),

            'lot': forms.NumberInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'conviction_level': forms.Select(attrs={'class': 'form-select'}),

            'number_of_times_searched': forms.NumberInput(attrs={'class': 'form-control'}),

            'pan_no': forms.TextInput(attrs={'class': 'form-control'}),
            'gst_no': forms.TextInput(attrs={'class': 'form-control'}),

            'logo': forms.ClearableFileInput(attrs={'class': 'form-control'}),

            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'company_overview': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'registered_office_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'transfer_agent_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),

            'stock_type': forms.Select(attrs={'class': 'form-select'}),
        }

# ===================== Inline Formsets =====================

ReportFormSet = inlineformset_factory(
    StockData,
    Report,
    fields=('title', 'summary'),
    extra=1,
    can_delete=True,
    widgets={
        'title': forms.TextInput(attrs={'class': 'form-control'}),
        'summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
    }
)

ShareholdingPatternFormSet = inlineformset_factory(
    StockData,
    ShareholdingPattern,
    fields=('shareholder_name', 'number_of_shares', 'percentage_of_total'),
    extra=1,
    can_delete=True,
    widgets={
        'shareholder_name': forms.TextInput(attrs={'class': 'form-control'}),
        'number_of_shares': forms.NumberInput(attrs={'class': 'form-control'}),
        'percentage_of_total': forms.NumberInput(attrs={'class': 'form-control'}),
    }
)

CompanyRelationFormSet = inlineformset_factory(
    StockData,
    CompanyRelation,
    fields=('company_name', 'relation_type', 'percentage_shares_held'),
    extra=1,
    can_delete=True,
    widgets={
        'company_name': forms.TextInput(attrs={'class': 'form-control'}),
        'relation_type': forms.Select(attrs={'class': 'form-select'}),
        'percentage_shares_held': forms.NumberInput(attrs={'class': 'form-control'}),
    }
)

PrincipalBusinessActivityFormSet = inlineformset_factory(
    StockData,
    PrincipalBusinessActivity,
    fields=('product_service_name', 'nic_code', 'turnover_percentage'),
    extra=1,
    can_delete=True,
    widgets={
        'product_service_name': forms.TextInput(attrs={'class': 'form-control'}),
        'nic_code': forms.TextInput(attrs={'class': 'form-control'}),
        'turnover_percentage': forms.NumberInput(attrs={'class': 'form-control'}),
    }
)

from django import forms
from .models import Blog

class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['banner', 'date', 'heading', 'subtitle', 'short_description', 'full_description']
        widgets = {
            'date': forms.DateInput(
                attrs={'type': 'date'},
                format='%Y-%m-%d'  # Ensure correct format for HTML5
            ),
            'short_description': forms.Textarea(attrs={'rows': 3}),
            'full_description': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super(BlogForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.date:
            self.fields['date'].initial = self.instance.date.strftime('%Y-%m-%d')


# stock history
# app/forms.py

class StockHistoryForm(forms.ModelForm):
    class Meta:
        model = StockHistory
        fields = ["stock", "price", "timestamp"]
        widgets = {
            "timestamp": forms.DateInput(attrs={"type": "date"}),
        }

# events forms
from django import forms
from .models import Event

from django import forms
from .models import Event

from django import forms
from .models import Event

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["title", "subtitle", "paragraph", "date_time", "image", "show"]

        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter event title"
            }),
            "subtitle": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter event subtitle"
            }),
            "paragraph": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Enter event details"
            }),
            "date_time": forms.DateTimeInput(attrs={
                "class": "form-control",
                "type": "datetime-local"
            }),
            "image": forms.ClearableFileInput(attrs={
                "class": "form-control"
            }),
            "show": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            }),
        }
