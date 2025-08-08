# unlisted_stock_marketplace/forms.py
from django import forms
from django.forms.widgets import Select
from .models import CustomFieldValue

class CustomFieldValueForm(forms.ModelForm):
    class Meta:
        model = CustomFieldValue
        fields = [
            'field_definition',
            'name',
            # 'description',
            # 'int_value',
            'dec_value',
            # 'char_value',
            # 'date_value',
            'table_header',
            'text_style',
            'parent_field_value',
        ]
        widgets = {
            'field_definition': Select(attrs={
                'class': 'form-select mb-3',
                'placeholder': 'Select field definition'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control mb-3',
                'placeholder': 'Enter field name'
            }),
            'dec_value': forms.NumberInput(attrs={
                'class': 'form-control mb-3',
                'step': '0.0001',
                'placeholder': 'Enter decimal value'
            }),
            'table_header': Select(attrs={
                'class': 'form-select mb-3',
                'placeholder': 'Select table header'
            }),
            'text_style': Select(attrs={
                'class': 'form-select mb-3',
                'placeholder': 'Select text style'
            }),
            'parent_field_value': Select(attrs={
                'class': 'form-select mb-3',
                'placeholder': 'Select parent field (optional)'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parent_field_value'].queryset = CustomFieldValue.objects.order_by('-id')

        # Remove all admin-related icons (add, change, delete, view)
        for field_name in ['field_definition', 'table_header', 'text_style', 'parent_field_value']:
            widget = self.fields[field_name].widget
            widget.can_add_related = False
            widget.can_change_related = False
            widget.can_delete_related = False
            widget.can_view_related = False  # 👁️ disables the "view" eye icon




# if u want "Add another", "Change", and "Delete" icons that appear next to dropdowns (ForeignKey fields) in Django admin or forms

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['parent_field_value'].queryset = CustomFieldValue.objects.order_by('-id')
