from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db import models

from user_auth.models import *
from user_portfolio.models import *
from unlisted_stock_marketplace.models import *
from site_Manager.models import *

import csv
from django.http import HttpResponse

def baseStructure(request):
    return render(request, 'baseStructureRM.html')

@login_required
def unlistedSharesRM(request):
    query = request.GET.get('q', '')  # Search query

    # Filter stocks by company_name or sector case-insensitive contains
    stocks = StockData.objects.all()
    if query:
        stocks = stocks.filter(
            models.Q(company_name__icontains=query) | models.Q(sector__icontains=query)
        )

    # CSV download logic
    if 'download' in request.GET:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="angel_invest_stocks.csv"'

        writer = csv.writer(response)
        writer.writerow(['Company Name', 'Industry', 'Conviction Level', "Today's Price", "Yesterday's Price", 'Lot Size'])

        for stock in stocks:
            writer.writerow([
                stock.company_name,
                stock.sector,
                stock.conviction_level,
                stock.share_price,
                stock.ltp,
                stock.lot,
            ])

        return response

    return render(request, 'unlistedSharesRM.html', {'stocks': stocks, 'query': query})

@login_required
def buyorderRM(request):
    rm_user = request.user

    # Get users assigned to this RM
    assigned_users = CustomUser.objects.filter(assigned_rm=rm_user)

    # Fetch BuyTransactions of those users
    buy_orders = BuyTransaction.objects.filter(user__in=assigned_users).order_by('-timestamp')

    return render(request, 'buyorderRM.html', {'buy_orders': buy_orders})


from .models import *

from .models import RMUserView, RMPaymentRecord

# app: RM_User
# models.py
@login_required
def buyordersummeryRM(request, order_id):
    # Get the buy transaction
    order = BuyTransaction.objects.filter(order_id=order_id).first()

    user_profile = order.user.profile
    cmr = CMRCopy.objects.filter(user_profile=user_profile).first()
    bank_accounts = BankAccount.objects.filter(user_profile=user_profile)

    # ✅ Correct way to fetch RMUserView using order_id
    rm_view = RMUserView.objects.filter(order_id=order_id).first()
    TransactionDetails = BuyTransaction.objects.all()
    context = {
        'order': order,
        'cmr': cmr,
        'bank_accounts': bank_accounts,
        'rm_view': rm_view,
        'TransactionDetails':TransactionDetails,
    }
    return render(request, 'buyordersummeryRM.html', context)


from django.views.decorators.csrf import csrf_exempt
from .models import RMPaymentRecord

from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import RMUserView, RMPaymentRecord
from user_portfolio.models import BuyTransaction  # adjust if import differs

from django.utils import timezone
from django.http import HttpResponseBadRequest

@csrf_exempt
@login_required
def add_or_edit_payment(request, order_id=None, payment_id=None):
    if request.method == 'POST':
        if payment_id:  # Edit flow
            payment = get_object_or_404(RMPaymentRecord, id=payment_id)
        else:  # Add flow
            order = get_object_or_404(BuyTransaction, order_id=order_id)
            rm_view = get_object_or_404(RMUserView, order_id=order_id)
            payment = RMPaymentRecord(rm_user_view=rm_view, date=timezone.now().date(), time=timezone.now().time())

        # Shared logic
        payment.bank_name = request.POST.get('bank_name')
        payment.amount = request.POST.get('amount')
        payment.remaining_amount = request.POST.get('remaining_amount')
        payment.remark = request.POST.get('remark')
        payment.payment_status = request.POST.get('payment_status', 'pending')

        if request.FILES.get('screenshot'):
            payment.screenshot = request.FILES['screenshot']

        payment.save()
        return redirect('RM_User:buyordersummery', order_id=payment.rm_user_view.order_id)

    return HttpResponseBadRequest("Invalid request method")

@login_required
def delete_payment(request, payment_id):
    payment = get_object_or_404(RMPaymentRecord, id=payment_id)
    order_id = payment.rm_user_view.order_id
    payment.delete()
    return redirect('RM_User:buyordersummery', order_id=order_id)



@login_required
def clientRM(request):
    current_rm = request.user 
    clients = current_rm.assigned_users.all()  
    context = {
        'clients': clients
    }
    return render(request, 'clientRM.html', context)




# 
# 
# ---------------------------------------------------------------------
# ------------------ Dashboard -------------
# ------------------------------------------------------------------
# 
# 
# views.py

from django.utils import timezone
from django.db.models import Sum, Count
from django.shortcuts import render
from datetime import timedelta
from .models import RMUserView, RMPaymentRecord

def dashboardRM(request):
    today = timezone.now().date()
    ten_days_ago = today - timedelta(days=10)
    start_of_month = today.replace(day=1)

    # Transaction Metrics
    total_transactions = RMUserView.objects.count()
    total_buys = RMUserView.objects.filter(transaction_type='buy').count()
    total_sells = RMUserView.objects.filter(transaction_type='sell').count()

    # Total invested amount (sum of all buy total_amounts)
    total_invested = RMUserView.objects.filter(transaction_type='buy').aggregate(
        total=Sum('total_amount'))['total'] or 0

    # Payment Aggregates
    total_collected_today = RMPaymentRecord.objects.filter(date=today).aggregate(
        total=Sum('amount'))['total'] or 0
    total_collected_10_days = RMPaymentRecord.objects.filter(date__gte=ten_days_ago).aggregate(
        total=Sum('amount'))['total'] or 0
    total_collected_month = RMPaymentRecord.objects.filter(date__gte=start_of_month).aggregate(
        total=Sum('amount'))['total'] or 0

    # Graph Data (date vs amount)
    payments_by_day = RMPaymentRecord.objects.filter(
        date__gte=ten_days_ago
    ).values('date').annotate(
        total_amount=Sum('amount')
    ).order_by('date')

    chart_labels = [entry['date'].strftime('%d-%b') for entry in payments_by_day]
    chart_data = [float(entry['total_amount']) for entry in payments_by_day]

    context = {
        'total_transactions': total_transactions,
        'total_buys': total_buys,
        'total_sells': total_sells,
        'total_invested': total_invested,
        'total_collected_today': total_collected_today,
        'total_collected_10_days': total_collected_10_days,
        'total_collected_month': total_collected_month,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
    }

    return render(request, 'dashboardRM.html', context)


def ordersRM(request):
    return render(request, 'ordersRM.html')

def sellorderRM(request):
    return render(request, 'sellorderRM.html')

def ShareListRM(request):
    return render(request, 'ShareListRM.html')

def selldersummeryRM(request):
    return render(request, 'selldersummeryRM.html')


def angelInvestRM(request):
    return render(request, 'angelInvestRM.html')



# 
# 
# ---------------------------------------------------------------------
# ------------------ Edit Delete Transactions -------------
# ------------------------------------------------------------------
# 
# 
# views.py
from django.shortcuts import render, get_object_or_404, redirect
from user_portfolio.models import BuyTransaction
from user_portfolio.forms import BuyTransactionEditForm
from django.contrib.auth.decorators import login_required

@login_required
def edit_buy_transaction(request, pk):
    transaction = get_object_or_404(BuyTransaction, pk=pk)
    order_id = transaction.order_id  # Get order_id to redirect back

    if request.method == 'POST':
        form = BuyTransactionEditForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            return redirect('RM_User:buyordersummery', order_id=order_id)  # Redirect to same page
    else:
        form = BuyTransactionEditForm(instance=transaction)

    return render(request, 'transaction/edit_transaction.html', {'form': form})


# views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

@login_required
def delete_buy_transaction(request, pk):
    transaction = get_object_or_404(BuyTransaction, pk=pk)
    order_id = transaction.order_id  # Capture before deleting
    transaction.delete()
    return redirect('RM_User:buyordersummery', order_id=order_id)  # Change as per your URL name
