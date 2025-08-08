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

        # Hide all value fields by default
        for ft in ['int', 'dec', 'char', 'date']:
            self.fields[f"{ft}_value"].widget.attrs['style'] = 'display: none;'
            self.fields[f"{ft}_value"].label = ''

        self.fields['description'].widget.attrs['style'] = 'display: none;'
        self.fields['description'].label = ''

        # SAFELY get field_definition from instance or initial
        field_def = getattr(self.instance, 'field_definition', None)
        if not field_def:
            field_def_id = self.initial.get('field_definition') or self.data.get('field_definition')
            if field_def_id:
                from .models import CustomFieldDefinition
                try:
                    field_def = CustomFieldDefinition.objects.get(pk=field_def_id)
                except CustomFieldDefinition.DoesNotExist:
                    pass

        field_type = getattr(field_def, 'field_type', 'dec') if field_def else 'dec'

        if field_type in ['int', 'dec', 'char', 'date']:
            self.fields[f"{field_type}_value"].widget.attrs['style'] = 'display: block;'
            self.fields[f"{field_type}_value"].label = f"{field_type.capitalize()} Value"
