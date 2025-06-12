

# Create your models here.

# myapp/models.py
from django.db import models


class Stock(models.Model):
    STOCK_TYPE_CHOICES = [
        ('raw', 'Raw Material'),
        ('finished', 'Finished Product'),
        ('other', 'Other'),
    ]
    name = models.CharField(max_length=100)
    stock_type = models.CharField(max_length=20, choices=STOCK_TYPE_CHOICES, default='raw')
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class DeliveryTicket(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    delivery_to = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    is_delivered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.stock.name} → {self.delivery_to}"
