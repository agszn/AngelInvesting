# forms.py
from django import forms
from .models import BuyTransaction, SellTransaction

class BuyTransactionEditForm(forms.ModelForm):
    class Meta:
        model = BuyTransaction
        fields = ['price_per_share', 'order_type', 'quantity', 'total_amount', 'RM_status', 'AC_status', 'status']
        widgets = {
            'price_per_share': forms.NumberInput(attrs={'class': 'form-control'}),
            'order_type': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'RM_status': forms.Select(attrs={'class': 'form-control'}),
            'AC_status': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'status': 'ST Status',  
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        editable_fields = []

        if user:
            if user.user_type == 'RM':
                editable_fields = ['price_per_share', 'order_type', 'quantity', 'total_amount', 'RM_status']
            elif user.user_type == 'AC':
                editable_fields = ['AC_status']
            elif user.user_type == 'ST':
                editable_fields = ['status']

        # Disable or remove fields not allowed
        for field in self.fields:
            if field not in editable_fields:
                self.fields[field].disabled = True

class SellTransactionEditForm(forms.ModelForm):
    class Meta:
        model = SellTransaction
        fields = ['selling_price', 'RM_status', 'AC_status', 'status']
        widgets = {
            'selling_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'RM_status': forms.Select(attrs={'class': 'form-control'}),
            'AC_status': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'status': 'ST Status',  
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        editable_fields = []

        if user:
            if user.user_type == 'RM':
                editable_fields = ['selling_price', 'RM_status']
            elif user.user_type == 'AC':
                editable_fields = ['AC_status']
            elif user.user_type == 'ST':
                editable_fields = ['status']

        for field in self.fields:
            if field not in editable_fields:
                self.fields[field].disabled = True
