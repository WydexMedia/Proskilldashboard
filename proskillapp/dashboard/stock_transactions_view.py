from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import StockTransaction
from django.utils import timezone
from datetime import timedelta

def is_accounts(user):
    return user.groups.filter(name='accounts').exists()

@login_required
@user_passes_test(is_accounts)
def stock_transactions(request):
    filter_type = request.GET.get('filter', 'all')
    now = timezone.now()
    if filter_type == 'monthly':
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        transactions = StockTransaction.objects.filter(created_at__gte=start)
    elif filter_type == 'yearly':
        start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        transactions = StockTransaction.objects.filter(created_at__gte=start)
    elif filter_type == 'weekly':
        start = now - timedelta(days=now.weekday())
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        transactions = StockTransaction.objects.filter(created_at__gte=start)
    else:
        transactions = StockTransaction.objects.all()
    transactions = transactions.order_by('-created_at')
    return render(request, 'accounts/stock_transactions.html', {
        'transactions': transactions,
        'filter_type': filter_type,
    })
