from django import forms
from.models import Tax,Purchase, Vendor, PaymentTransaction
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


from django.utils import timezone

class PurchaseForm(forms.ModelForm):
    
    class Meta:
        model = Purchase
        fields = [
            'purchase_type', 'supplier', 'payment_terms', 'due_date', 'place_of_supply',
            'purchase_item', 'quantity', 'purchase_price', 'discount', 'unit', 
            'amount', 'paid_amount', 'balance_amount', 'payment_status', 'shipping_cost', 'received_date'
        ]
        labels = {
            'purchase_price':'Purchase Unit Price',
            "recived_date":'received Date'
        }
        widgets = {
            'purchase_type': forms.Select(attrs={'class': 'form-control', 'id': 'purchase_type'}),
            'supplier': forms.Select(attrs={'class': 'form-control', 'id': 'supplier'}),
            'payment_terms': forms.TextInput(attrs={'class': 'form-control', 'id': 'payment_terms'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'id': 'due_date', 'type': 'date'}),
            'place_of_supply': forms.TextInput(attrs={'class': 'form-control', 'id': 'place_of_supply'}),
            'purchase_item': forms.Select(attrs={'class': 'form-control', 'id': 'purchase_item'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'id': 'quantity', 'min': 0}),
            'purchase_price': forms.NumberInput(attrs={'class': 'form-control', 'id': 'purchase_price', 'step': '0.01', 'min': 0}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'id': 'discount', 'step': '0.01', 'min': 0}),
            'unit': forms.Select(attrs={'class': 'form-control', 'id': 'unit'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'id': 'amount', 'step': '0.01', 'min': 0}),
            'paid_amount': forms.NumberInput(attrs={'class': 'form-control', 'id': 'paid_amount', 'step': '0.01', 'min': 0}),
            'balance_amount': forms.NumberInput(attrs={'class': 'form-control', 'id': 'balance_amount', 'step': '0.01', 'min': 0}),
            'payment_status': forms.Select(attrs={'class': 'form-control', 'id': 'payment_status'}),
            'shipping_cost': forms.NumberInput(attrs={'class': 'form-control', 'id': 'shipping_cost', 'step': '0.01', 'min': 0}),
            'recived_date': forms.DateInput(attrs={'class': 'form-control', 'id': 'recived_date', 'type': 'date','max': timezone.now().date()}),
        }

class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ['name', 'email', 'phone_number', 'city', 'state', 'country', 'pincode', 'contact_info', 'supply_product']
        labels = {
            "pincode":"Location Url"
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'id': 'vendor_name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'id': 'vendor_email'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'id': 'vendor_phone_number'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'id': 'vendor_city'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'id': 'vendor_state'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'id': 'vendor_country'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control', 'id': 'vendor_pincode',"type":"url"}),
            'contact_info': forms.Textarea(attrs={'class': 'form-control', 'id': 'vendor_contact_info', 'rows': 3}),
            'supply_product': forms.TextInput(attrs={'class': 'form-control', 'id': 'vendor_supply_product'}),
        }


class PaymentForm(forms.ModelForm):
    class Meta:
        model = PaymentTransaction
        fields = ['amount', 'payment_date', 'payment_method', 'reference_number', 'notes']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'reference_number': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.purchase = kwargs.pop('purchase', None)
        super().__init__(*args, **kwargs)
        
        if self.purchase:
            self.fields['amount'].widget.attrs['max'] = self.purchase.balance_amount

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if self.purchase and amount > self.purchase.balance_amount:
            raise forms.ValidationError('Payment amount cannot exceed the balance amount.')
        if amount <= 0:
            raise forms.ValidationError('Payment amount must be greater than zero.')
        return amount
