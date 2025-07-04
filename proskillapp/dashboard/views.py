# myapp/views.py
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from .models import Stock, DeliveryTicket, OgaRequest, StockTransaction
from .forms import StockForm, DeliveryTicketForm, OgaRequestForm, CustomDeliveryTicketForm
from django.utils import timezone
from dashboard.gmail_utils import send_gmail_api_mail

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
    # Only show not approved OGA requests
    oga_requests = OgaRequest.objects.filter(approved=False).order_by('-submitted_at')
    # Calculate total and available for each type
    total_mehandi = sum(stock.added_quantity for stock in Stock.objects.filter(stock_type='mehandi'))
    total_resin = sum(stock.added_quantity for stock in Stock.objects.filter(stock_type='resin'))
    available_mehandi = sum(stock.quantity for stock in Stock.objects.filter(stock_type='mehandi'))
    available_resin = sum(stock.quantity for stock in Stock.objects.filter(stock_type='resin'))

    # Handle OgaRequest approval
    if request.method == 'POST' and 'approve_oga' in request.POST:
        oga_id = request.POST.get('oga_id')
        oga = OgaRequest.objects.get(pk=oga_id)
        if not oga.approved:
            # Find stock of the correct type
            stock = Stock.objects.filter(stock_type=oga.stock_type, quantity__gt=0).first()
            if stock:
                oga.approved = True
                oga.approved_at = timezone.now()
                oga.save()
                stock.quantity -= 1
                stock.save()
                # Create StockTransaction for selling
                StockTransaction.objects.create(
                    stock_type=stock.stock_type,
                    quantity=1,
                    transaction_type='sell',
                    related_oga=oga
                )
                DeliveryTicket.objects.create(
                    stock=stock,
                    delivery_to=f"{oga.oga_name}, {oga.phone}, {oga.email}, {oga.address}, {oga.pincode}",
                    email=oga.email
                )
        return redirect('accounts_dashboard')

    # --- Sales stats for dashboard ---
    from datetime import datetime, timedelta
    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    week_start = now - timedelta(days=now.weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    sold_mehandi_month = StockTransaction.objects.filter(stock_type='mehandi', transaction_type='sell', created_at__gte=month_start).count()
    sold_resin_month = StockTransaction.objects.filter(stock_type='resin', transaction_type='sell', created_at__gte=month_start).count()
    sold_mehandi_week = StockTransaction.objects.filter(stock_type='mehandi', transaction_type='sell', created_at__gte=week_start).count()
    sold_resin_week = StockTransaction.objects.filter(stock_type='resin', transaction_type='sell', created_at__gte=week_start).count()
    sold_mehandi_all = StockTransaction.objects.filter(stock_type='mehandi', transaction_type='sell').count()
    sold_resin_all = StockTransaction.objects.filter(stock_type='resin', transaction_type='sell').count()

    # Annotate each OgaRequest with can_approve property
    for oga in oga_requests:
        if not oga.approved:
            if oga.stock_type == 'mehandi':
                oga.can_approve = available_mehandi > 0
            elif oga.stock_type == 'resin':
                oga.can_approve = available_resin > 0
            else:
                oga.can_approve = False
        else:
            oga.can_approve = False

    return render(request, 'accounts/dashboard.html', {
        'stocks': stocks,
        'oga_requests': oga_requests,
        'total_mehandi': total_mehandi,
        'available_mehandi': available_mehandi,
        'total_resin': total_resin,
        'available_resin': available_resin,
        'sold_mehandi_month': sold_mehandi_month,
        'sold_resin_month': sold_resin_month,
        'sold_mehandi_week': sold_mehandi_week,
        'sold_resin_week': sold_resin_week,
        'sold_mehandi_all': sold_mehandi_all,
        'sold_resin_all': sold_resin_all,
    })

# Stock CRUD
@login_required
@user_passes_test(is_accounts)
def stock_add(request):
    if request.method == 'POST':
        form = StockForm(request.POST)
        if form.is_valid():
            stock = form.save(commit=False)
            # No name field anymore, just save
            stock.save()
            # Add StockTransaction for stock addition
            from .models import StockTransaction
            StockTransaction.objects.create(
                stock_type=stock.stock_type,
                quantity=stock.added_quantity,
                transaction_type='add',
                related_oga=None
            )
            return redirect('accounts_dashboard')
    else:
        form = StockForm()
    return render(request, 'accounts/stock_form.html', {'form': form, 'action': 'Add Stock'})

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
    sort = request.GET.get('sort', 'unshipped')
    tickets = DeliveryTicket.objects.all()
    if sort == 'unshipped':
        tickets = tickets.order_by('is_delivered', '-created_at')
    elif sort == 'date':
        tickets = tickets.order_by('-created_at')
    elif sort == 'done':
        tickets = tickets.order_by('-is_delivered', '-created_at')
    else:
        tickets = tickets.order_by('-created_at')

    if request.method == 'POST':
        ticket_id = request.POST.get('ticket_id')
        status = request.POST.get('status')
        tracking_id = request.POST.get('tracking_id', '').strip()
        if ticket_id and status:
            try:
                ticket = DeliveryTicket.objects.get(pk=ticket_id)
                if status == 'done':
                    if not tracking_id:
                        from django.contrib import messages
                        messages.error(request, 'Tracking ID required to mark as done.')
                    else:
                        ticket.is_delivered = True
                        ticket.tracking_id = tracking_id
                        ticket.save()
                        # Send email to customer
                        customer_email = ticket.email
                        print(f"DEBUG: Attempting to send shipment email to {customer_email}")  # Debug print
                        if customer_email:
                            stock_type = ticket.stock.get_stock_type_display()
                            subject = f"Your {stock_type} is shipped!"
                            message = f"Hey, greetings from Proskill! Your {stock_type} is shipped to {ticket.delivery_to}. You can track it with Tracking ID: {tracking_id}"
                            try:
                                send_gmail_api_mail(
                                    subject,
                                    message,
                                    customer_email,
                                    from_email='delivery@proskilledu.com'
                                )
                            except Exception as e:
                                print(f"EMAIL ERROR: {e}")
                elif status == 'pending':
                    ticket.is_delivered = False
                    ticket.tracking_id = ''
                    ticket.save()
            except DeliveryTicket.DoesNotExist:
                pass
    return render(request, 'delivery/tickets.html', {'tickets': tickets, 'sort': sort})


# DeliveryTicket CRUD (Accounts only)
@login_required
@user_passes_test(is_accounts)
def ticket_add(request):
    if request.method == 'POST':
        form = OgaRequestForm(request.POST, request.FILES)
        if form.is_valid():
            oga = form.save(commit=False)
            oga.approved = True
            oga.save()
            # Reduce stock by 1 (from the first available stock item)
            stock = None
            for s in Stock.objects.all():
                if s.quantity > 0:
                    stock = s
                    s.quantity -= 1
                    s.save()
                    break
            if stock:
                DeliveryTicket.objects.create(
                    stock=stock,
                    delivery_to=f"{oga.oga_name}, {oga.phone}, {oga.email}, {oga.address}, {oga.pincode}",
                    email=oga.email
                )
            if request.user.groups.filter(name='accounts').exists():
                return redirect('accounts_dashboard')
            else:
                return redirect('delivery_dashboard')
    else:
        form = OgaRequestForm()
    return render(request, 'delivery/ticket_form.html', {'form': form, 'action': 'Add'})

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

# OgaRequestForm view
def ogaform_view(request):
    if request.method == 'POST':
        form = OgaRequestForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return render(request, 'ogaform_success.html')
    else:
        form = OgaRequestForm()
    return render(request, 'ogaform.html', {'form': form})

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
