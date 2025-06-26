from django.contrib import admin
from .models import Stock, DeliveryTicket, OgaRequest, StockTransaction

admin.site.register(Stock)
admin.site.register(DeliveryTicket)
admin.site.register(OgaRequest)
admin.site.register(StockTransaction)
