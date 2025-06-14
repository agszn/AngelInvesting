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

            'registration_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'},format='%Y-%m-%d'),
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
            'ltp': forms.NumberInput(attrs={'class': 'form-control'}),
            'week_52_high': forms.NumberInput(attrs={'class': 'form-control'}),
            'week_52_low': forms.NumberInput(attrs={'class': 'form-control'}),
            'lifetime_high': forms.NumberInput(attrs={'class': 'form-control'}),
            'lifetime_high_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'},format='%Y-%m-%d'),
            'lifetime_low': forms.NumberInput(attrs={'class': 'form-control'}),
            'lifetime_low_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'},format='%Y-%m-%d'),
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
