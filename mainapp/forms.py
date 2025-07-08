from django import forms
from.models import Tax

class TaxForm(forms.ModelForm):
    class Meta:
        model = Tax
        fields = ['tax_name', 'tax_percentage']
        widgets = {
            'tax_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Tax Name'}),
            'tax_percentage': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Tax Percentage'}),
        }
        labels = {
            'tax_name': 'Tax Name',
            'tax_percentage': 'Tax Percentage (%)',
        }


from django import forms
from .models import Inventory

class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = [
            'name','brand_name', 'base_product',"value" ,'rate_of_purchase', 'stock'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Product Name',
                'id': 'productName',
                'required': True,
            }),  
            'brand_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Brand Name',
                'id': 'brandName',
                'required': True,
            }),

            'base_product': forms.Select(attrs={
                'class': 'form-select',
                'id': 'baseProduct',
            }),
            'value': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Values like 16gb, 500 SSD (** Optional )',
                'id': 'value',
                
            }),
            'rate_of_purchase': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Rate of Purchase',
                'id': 'rateOfPurchase',
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Stock Quantity',
                'id': 'stockQty',
            }),
        }
