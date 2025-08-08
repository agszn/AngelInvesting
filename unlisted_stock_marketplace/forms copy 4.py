




from django import forms
from .models import CustomFieldValue, CustomFieldDefinition, TableHeader

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
            'name': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter one name per line or comma-separated for bulk insert...'
            }),
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

        instance = kwargs.get('instance')
        field_def = self.initial.get('field_definition') or getattr(self.instance, 'field_definition', None)

        # Set parent_field_value queryset based on field_definition context
        if instance and field_def:
            stock_id = field_def.stock_id
            model_type = field_def.model_type
            self.fields['parent_field_value'].queryset = CustomFieldValue.objects.filter(
                field_definition__stock_id=stock_id,
                field_definition__model_type=model_type,
                parent_field_value__isnull=True
            ).exclude(pk=instance.pk)
        else:
            self.fields['parent_field_value'].queryset = CustomFieldValue.objects.none()

        # Default hide value input fields
        for ft in ['int', 'dec', 'char', 'date']:
            self.fields[f"{ft}_value"].widget.attrs['style'] = 'display: none;'
            self.fields[f"{ft}_value"].label = ''

        self.fields['description'].widget.attrs['style'] = 'display: none;'
        self.fields['description'].label = ''

        # Determine which value field to show based on field_type
        field_type = getattr(field_def, 'field_type', 'dec') if field_def else 'dec'
        if field_type in ['int', 'dec', 'char', 'date']:
            self.fields[f"{field_type}_value"].widget.attrs['style'] = 'display: block;'
            self.fields[f"{field_type}_value"].label = f"{field_type.capitalize()} Value"

    def clean(self):
        cleaned_data = super().clean()
        raw_name_input = cleaned_data.get("name", "")
        gap = self.instance.field_definition.gap if self.instance and self.instance.field_definition else 1

        # Parse names from comma-separated or multi-line text
        lines = raw_name_input.replace(',', '\n').splitlines()
        parsed_names = [line.strip() for line in lines if line.strip()]

        cleaned_data['parsed_names'] = parsed_names
        cleaned_data['gap'] = gap

        return cleaned_data

# forms.py
from django import forms
from .models import CustomFieldDefinition

class CustomFieldDefinitionAdminForm(forms.ModelForm):
    bulk_data = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 8, 'cols': 80}),
        required=False,
        help_text="Paste custom field values here (rows separated by newline)",
        label="Bulk Field Values"
    )

    class Meta:
        model = CustomFieldDefinition
        fields = '__all__'
