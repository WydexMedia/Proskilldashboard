from django import forms
from .models import Stock, DeliveryTicket

class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['name', 'stock_type', 'quantity', 'price']

class DeliveryTicketForm(forms.ModelForm):
    class Meta:
        model = DeliveryTicket
        fields = ['stock', 'delivery_to', 'is_delivered']
