from django import forms
from .models import BuyTransaction

class BuyTransactionEditForm(forms.ModelForm):
    class Meta:
        model = BuyTransaction
        fields = '__all__'  # Keep all, trim logic is in __init__
        widgets = {
            'price_per_share': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter price per share'
            }),
            'order_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter quantity'
            }),
            'total_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Total amount will be auto-calculated'
            }),
            'RM_status': forms.Select(attrs={'class': 'form-control'}),
            'AC_status': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Fields normally editable
        editable_fields = ['price_per_share', 'order_type', 'quantity', 'total_amount']

        if user and hasattr(user, 'user_type'):
            if user.user_type == 'RM':
                editable_fields.append('RM_status')  # RM can edit everything
            elif user.user_type == 'AC':
                editable_fields.append('AC_status')
                for field in self.fields:
                    if field not in ['AC_status']:
                        self.fields[field].disabled = True  # Make others read-only
            elif user.user_type == 'ST':
                editable_fields.append('status')
                for field in self.fields:
                    if field not in ['status']:
                        self.fields[field].disabled = True
        else:
            # If no user, disable everything for safety
            for field in self.fields:
                self.fields[field].disabled = True

        # Now remove all unrelated fields (to avoid displaying extra things)
        for field_name in list(self.fields.keys()):
            if field_name not in editable_fields:
                self.fields.pop(field_name)
