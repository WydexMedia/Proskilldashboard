from django import forms
from .models import Stock, DeliveryTicket, OgaRequest

class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['stock_type', 'quantity']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['stock_type'].label = 'Stock Type'
        self.fields['stock_type'].choices = [
            ('mehandi', 'Mehandi'),
            ('resin', 'Resin'),
        ]
        self.fields['stock_type'].initial = 'resin'  # Set Resin as default
        self.fields['quantity'].label = 'Number of Stock'

class DeliveryTicketForm(forms.ModelForm):
    class Meta:
        model = DeliveryTicket
        fields = ['stock', 'delivery_to', 'is_delivered']

class OgaRequestForm(forms.ModelForm):
    class Meta:
        model = OgaRequest
        fields = ['stock_type', 'oga_name', 'phone', 'email', 'address', 'pincode', 'landmark', 'screenshot', 'full_payment']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['stock_type'].required = True
        self.fields['oga_name'].required = True
        self.fields['phone'].required = True
        self.fields['email'].required = True
        self.fields['address'].required = True
        self.fields['pincode'].required = True
        self.fields['screenshot'].required = True
        self.fields['full_payment'].required = False
        self.fields['landmark'].required = False

class CustomDeliveryTicketForm(forms.Form):
    stock = forms.ModelChoiceField(queryset=Stock.objects.all())
    name = forms.CharField(max_length=100)
    phone = forms.CharField(max_length=20)
    email = forms.EmailField()
    address = forms.CharField(widget=forms.Textarea)
    pincode = forms.CharField(max_length=10)
    is_delivered = forms.BooleanField(required=False)
