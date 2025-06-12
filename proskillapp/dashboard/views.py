# myapp/views.py
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from .models import Stock, DeliveryTicket
from .forms import StockForm, DeliveryTicketForm

# Role checks
def is_accounts(user):
    return user.groups.filter(name='accounts').exists()

def is_delivery(user):
    return user.groups.filter(name='delivery partners').exists()

# DeliveryTicket edit view (Accounts only)
@login_required
@user_passes_test(is_accounts)
def ticket_edit(request, pk):
    ticket = get_object_or_404(DeliveryTicket, pk=pk)
    if request.method == 'POST':
        form = DeliveryTicketForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            return redirect('delivery_dashboard')
    else:
        form = DeliveryTicketForm(instance=ticket)
    return render(request, 'delivery/ticket_form.html', {'form': form, 'action': 'Edit'})
# myapp/views.py
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from .models import Stock, DeliveryTicket
from .forms import StockForm, DeliveryTicketForm

# Role checks
def is_accounts(user):
    return user.groups.filter(name='accounts').exists()

def is_delivery(user):
    return user.groups.filter(name='delivery partners').exists()

# Dashboards
@login_required
@user_passes_test(is_accounts)
def accounts_dashboard(request):
    stocks = Stock.objects.all()
    return render(request, 'accounts/dashboard.html', {'stocks': stocks})

# Stock CRUD
@login_required
@user_passes_test(is_accounts)
def stock_add(request):
    if request.method == 'POST':
        form = StockForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('accounts_dashboard')
    else:
        form = StockForm()
    return render(request, 'accounts/stock_form.html', {'form': form, 'action': 'Add'})

@login_required
@user_passes_test(is_accounts)
def stock_edit(request, pk):
    stock = get_object_or_404(Stock, pk=pk)
    if request.method == 'POST':
        form = StockForm(request.POST, instance=stock)
        if form.is_valid():
            form.save()
            return redirect('accounts_dashboard')
    else:
        form = StockForm(instance=stock)
    return render(request, 'accounts/stock_form.html', {'form': form, 'action': 'Edit'})

@login_required
@user_passes_test(is_accounts)
def stock_delete(request, pk):
    stock = get_object_or_404(Stock, pk=pk)
    if request.method == 'POST':
        stock.delete()
        return redirect('accounts_dashboard')
    return render(request, 'accounts/stock_confirm_delete.html', {'stock': stock})

@login_required
@user_passes_test(is_delivery)
def delivery_tickets(request):
    tickets = DeliveryTicket.objects.all()
    if request.method == 'POST':
        ticket_id = request.POST.get('ticket_id')
        status = request.POST.get('status')
        if ticket_id and status:
            try:
                ticket = DeliveryTicket.objects.get(pk=ticket_id)
                if status == 'pending':
                    ticket.is_delivered = False
                elif status == 'done':
                    ticket.is_delivered = True
                ticket.save()
            except DeliveryTicket.DoesNotExist:
                pass
    return render(request, 'delivery/tickets.html', {'tickets': tickets})


# DeliveryTicket CRUD (Accounts only)
@login_required
@user_passes_test(is_accounts)
def ticket_add(request):
    if request.method == 'POST':
        form = DeliveryTicketForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('delivery_dashboard')  # Redirect to delivery dashboard
    else:
        form = DeliveryTicketForm()
    return render(request, 'delivery/ticket_form.html', {'form': form, 'action': 'Add'})

@login_required
@user_passes_test(is_accounts)
def ticket_delete(request, pk):
    ticket = get_object_or_404(DeliveryTicket, pk=pk)
    if request.method == 'POST':
        ticket.delete()
        return redirect('delivery_dashboard')  # Redirect to delivery dashboard
    return render(request, 'delivery/ticket_confirm_delete.html', {'ticket': ticket})

# Print delivery slip (for both roles)
@login_required
def print_ticket(request, pk):
    ticket = get_object_or_404(DeliveryTicket, pk=pk)
    return render(request, 'delivery/ticket_slip.html', {'ticket': ticket})

# Redirect after login based on group
@login_required
def role_redirect(request):
    user = request.user
    if user.groups.filter(name='accounts').exists():
        print('Redirecting to accounts/dashboard.html')
        return redirect('accounts_dashboard')
    elif user.groups.filter(name='delivery partners').exists():
        print('Redirecting to delivery/tickets.html')
        return redirect('delivery_dashboard')
    else:
        print('User not in any group, showing error')
        from django.http import HttpResponse
        return HttpResponse("You do not have access to any dashboard. Please contact admin.", status=403)

# Custom login view
class CustomLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True
