# Create your models here.

# myapp/models.py
from django.db import models


class Stock(models.Model):
    STOCK_TYPE_CHOICES = [
        ('mehandi', 'Mehandi'),
        ('resin', 'Resin'),
    ]
    stock_type = models.CharField(max_length=20, choices=STOCK_TYPE_CHOICES)
    quantity = models.IntegerField()
    added_quantity = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.get_stock_type_display()} - {self.quantity}"

class DeliveryTicket(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    delivery_to = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)  # New field for direct customer email storage
    created_at = models.DateTimeField(auto_now_add=True)
    is_delivered = models.BooleanField(default=False)
    tracking_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.stock.name}  {self.delivery_to}"

class OgaRequest(models.Model):
    STOCK_TYPE_CHOICES = [
        ('resin', 'Resin'),
        ('mehandi', 'Mehandi'),
        
    ]
    stock_type = models.CharField(max_length=20, choices=STOCK_TYPE_CHOICES, default='resin')
    oga_name = models.CharField(max_length=100)
    customer_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()
    pincode = models.CharField(max_length=10)
    landmark = models.CharField(max_length=100, blank=True)
    screenshot = models.ImageField(upload_to='oga_screenshots/')
    full_payment = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.oga_name} ({self.phone})"

class StockTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('add', 'Add'),
        ('sell', 'Sell'),
    ]
    stock_type = models.CharField(max_length=20, choices=Stock.STOCK_TYPE_CHOICES)
    quantity = models.IntegerField()
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    related_oga = models.ForeignKey('OgaRequest', null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_transaction_type_display()} {self.quantity} {self.get_stock_type_display()} on {self.created_at:%Y-%m-%d}"
