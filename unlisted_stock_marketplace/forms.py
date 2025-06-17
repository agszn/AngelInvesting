# forms.py
from django import forms
from .models import CustomFieldValue

class CustomFieldValueForm(forms.ModelForm):
    class Meta:
        model = CustomFieldValue
        fields = [
            'field_definition', 'name', 'description',
            'int_value', 'dec_value', 'char_value', 'date_value',
            'table_header', 'text_style', 'parent_field_value'
        ]
        widgets = {
            'field_definition': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control description-field',
                'rows': 2,
                'placeholder': 'Optional description',
                'style': 'display: none;'
            }),
            'int_value': forms.NumberInput(attrs={'class': 'form-control value-field int-field', 'style': 'display: none;'}),
            'dec_value': forms.NumberInput(attrs={'class': 'form-control value-field dec-field', 'step': '0.0001', 'style': 'display: none;'}),
            'char_value': forms.Textarea(attrs={'class': 'form-control value-field char-field', 'rows': 2, 'style': 'display: none;'}),
            'date_value': forms.DateInput(attrs={'class': 'form-control value-field date-field', 'type': 'date', 'style': 'display: none;'}),
            'table_header': forms.Select(attrs={'class': 'form-control'}),
            'text_style': forms.Select(attrs={'class': 'form-control'}),
            'parent_field_value': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Only show relevant parent values
        instance = kwargs.get('instance')
        if instance and instance.field_definition:
            stock_id = instance.field_definition.stock_id
            model_type = instance.field_definition.model_type
            self.fields['parent_field_value'].queryset = CustomFieldValue.objects.filter(
                field_definition__stock_id=stock_id,
                field_definition__model_type=model_type,
                parent_field_value__isnull=True
            ).exclude(pk=instance.pk)
        else:
            self.fields['parent_field_value'].queryset = CustomFieldValue.objects.none()

        for ft in ['int', 'dec', 'char', 'date']:
            self.fields[f"{ft}_value"].widget.attrs['style'] = 'display: none;'
            self.fields[f"{ft}_value"].label = ''

        self.fields['description'].widget.attrs['style'] = 'display: none;'
        self.fields['description'].label = ''

        field_def = self.initial.get('field_definition') or getattr(self.instance, 'field_definition', None)
        field_type = getattr(field_def, 'field_type', 'dec') if field_def else 'dec'

        if field_type in ['int', 'dec', 'char', 'date']:
            self.fields[f"{field_type}_value"].widget.attrs['style'] = 'display: block;'
            self.fields[f"{field_type}_value"].label = f"{field_type.capitalize()} Value"