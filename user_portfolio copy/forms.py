from django import forms
from .models import BuyTransaction

class BuyTransactionEditForm(forms.ModelForm):
    class Meta:
        model = BuyTransaction
        fields = ['price_per_share', 'order_type', 'quantity', 'total_amount', 'status']

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
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
