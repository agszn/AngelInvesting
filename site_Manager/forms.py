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
