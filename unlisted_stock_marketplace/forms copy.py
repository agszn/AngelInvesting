# unlisted_stock_marketplace/forms.py
from django import forms
from .models import CustomFieldValue

class CustomFieldValueForm(forms.ModelForm):
    class Meta:
        model = CustomFieldValue
        fields = [
            'field_definition',
            'name',
            'description',
            'int_value',
            'dec_value',
            'char_value',
            'date_value',
            'table_header',
            'text_style',
            'parent_field_value',  # Add parent field value here
        ]
        widgets = {
            'field_definition': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter field name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Optional description'
            }),
            'int_value': forms.NumberInput(attrs={'class': 'form-control'}),
            'dec_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'char_value': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Enter text value'
            }),
            'date_value': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'table_header': forms.Select(attrs={'class': 'form-control'}),
            'text_style': forms.Select(attrs={'class': 'form-control'}),
            'parent_field_value': forms.Select(attrs={'class': 'form-control'}),  # Widget for parent field value
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parent_field_value'].queryset = CustomFieldValue.objects.order_by('-id')


