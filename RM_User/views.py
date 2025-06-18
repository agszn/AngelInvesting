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
from django.db.models import Sum

# @login_required
# def buyordersummeryRM(request, order_id):
#     order = BuyTransaction.objects.filter(order_id=order_id).first()
#     user_profile = order.user.profile
#     cmr = CMRCopy.objects.filter(user_profile=user_profile).first()
#     bank_accounts = BankAccount.objects.filter(user_profile=user_profile)

#     rm_view = RMUserView.objects.filter(order_id=order_id).first()
#     TransactionDetails = BuyTransaction.objects.all()

#     # ✅ Calculate total paid
#     total_paid = rm_view.payment_records.aggregate(Sum('amount'))['amount__sum'] or 0
#     remaining_amount = order.total_amount - total_paid

#     context = {
#         'order': order,
#         'cmr': cmr,
#         'bank_accounts': bank_accounts,
#         'rm_view': rm_view,
#         'TransactionDetails': TransactionDetails,
#         'remaining_amount': remaining_amount,
#     }
#     return render(request, 'buyordersummeryRM.html', context)


@login_required
def buyordersummeryRM(request, order_id):
    # Get the BuyTransaction
    order = get_object_or_404(BuyTransaction, order_id=order_id)
    user_profile = order.user.profile

    # Get associated data
    cmr = CMRCopy.objects.filter(user_profile=user_profile).first()
    bank_accounts = BankAccount.objects.filter(user_profile=user_profile)
    rm_view = RMUserView.objects.filter(order_id=order_id).first()

    # Total amount paid so far for this order
    total_paid = rm_view.payment_records.aggregate(Sum('amount'))['amount__sum'] or 0

    # Calculate remaining amount
    remaining_amount = order.total_amount - total_paid

    context = {
        'order': order,
        'cmr': cmr,
        'bank_accounts': bank_accounts,
        'rm_view': rm_view,
        'TransactionDetails': BuyTransaction.objects.filter(order_id=order_id),
        'remaining_amount': remaining_amount,
    }
    return render(request, 'buyordersummeryRM.html', context)

# displays of all users
# def AllbuyTransactionSummary(request):
#     transactions = BuyTransaction.objects.all()

#     # Filter: Only show users assigned to this RM
#     if request.user.user_type == 'RM':
#         users = User.objects.filter(assigned_rm=request.user)
#     else:
#         users = User.objects.all()

#     # Filters from request
#     user_id = request.GET.get('user')
#     company_name = request.GET.get('company_name')
#     advisor_id = request.GET.get('advisor')
#     broker_id = request.GET.get('broker')
#     order_type = request.GET.get('order_type')
#     status = request.GET.get('status')
#     order_id = request.GET.get('order_id')
#     timestamp = request.GET.get('timestamp')

#     # Apply filters
#     if user_id:
#         transactions = transactions.filter(user__id=user_id)
#     if company_name:
#         transactions = transactions.filter(stock__company_name__icontains=company_name)
#     if advisor_id:
#         transactions = transactions.filter(advisor__id=advisor_id)
#     if broker_id:
#         transactions = transactions.filter(broker__id=broker_id)
#     if order_type:
#         transactions = transactions.filter(order_type=order_type)
#     if status:
#         transactions = transactions.filter(status=status)
#     if order_id:
#         transactions = transactions.filter(order_id__icontains=order_id)
#     if timestamp:
#         transactions = transactions.filter(timestamp__date=timestamp)

#     # Distinct dropdown lists
#     company_names = BuyTransaction.objects.values_list('stock__company_name', flat=True).distinct()
#     order_ids = BuyTransaction.objects.values_list('order_id', flat=True).distinct()

#     context = {
#         'TransactionDetails': transactions,
#         'users': users,
#         'advisors': Advisor.objects.all(),
#         'brokers': Broker.objects.all(),
#         'company_names': company_names,
#         'order_ids': order_ids,
#     }
#     return render(request, 'AllbuyTransactionSummary.html', context)


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from user_portfolio.models import BuyTransaction
from user_auth.models import CustomUser
from site_Manager.models import Advisor, Broker

@login_required
def AllbuyTransactionSummary(request):
    # Step 1: Restrict users to those assigned to the logged-in RM
    if request.user.user_type == 'RM':
        users = CustomUser.objects.filter(assigned_rm=request.user)
    else:
        users = CustomUser.objects.all()

    # Step 2: Restrict transactions to only those users
    transactions = BuyTransaction.objects.filter(user__in=users)

    # Step 3: Filters from request
    user_id = request.GET.get('user')
    company_name = request.GET.get('company_name')
    advisor_id = request.GET.get('advisor')
    broker_id = request.GET.get('broker')
    order_type = request.GET.get('order_type')
    status = request.GET.get('status')
    order_id = request.GET.get('order_id')
    timestamp = request.GET.get('timestamp')

    if user_id:
        transactions = transactions.filter(user__id=user_id)
    if company_name:
        transactions = transactions.filter(stock__company_name__icontains=company_name)
    if advisor_id:
        transactions = transactions.filter(advisor__id=advisor_id)
    if broker_id:
        transactions = transactions.filter(broker__id=broker_id)
    if order_type:
        transactions = transactions.filter(order_type=order_type)
    if status:
        transactions = transactions.filter(status=status)
    if order_id:
        transactions = transactions.filter(order_id__icontains=order_id)
    if timestamp:
        transactions = transactions.filter(timestamp__date=timestamp)

    # Step 4: Limit dropdowns to assigned users' data
    company_names = transactions.values_list('stock__company_name', flat=True).distinct()
    order_ids = transactions.values_list('order_id', flat=True).distinct()

    context = {
        'TransactionDetails': transactions,
        'users': users,
        'advisors': Advisor.objects.all(),
        'brokers': Broker.objects.all(),
        'company_names': company_names,
        'order_ids': order_ids,
    }
    return render(request, 'AllbuyTransactionSummary.html', context)



from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from user_auth.models import CustomUser
from user_portfolio.models import SellTransaction
from site_Manager.models import Advisor, Broker

@login_required
def AllsellTransactionSummary(request):
    # Step 1: Restrict users to those assigned to the logged-in RM
    if request.user.user_type == 'RM':
        users = CustomUser.objects.filter(assigned_rm=request.user)
    else:
        users = CustomUser.objects.all()

    # Step 2: Restrict transactions to only those users
    transactions = SellTransaction.objects.filter(user__in=users)

    # Step 3: Filters from request
    user_id = request.GET.get('user')
    company_name = request.GET.get('company_name')
    advisor_id = request.GET.get('advisor')
    broker_id = request.GET.get('broker')
    order_type = request.GET.get('order_type')
    status = request.GET.get('status')
    order_id = request.GET.get('order_id')
    timestamp = request.GET.get('timestamp')

    if user_id:
        transactions = transactions.filter(user__id=user_id)
    if company_name:
        transactions = transactions.filter(stock__company_name__icontains=company_name)
    if advisor_id:
        transactions = transactions.filter(advisor__id=advisor_id)
    if broker_id:
        transactions = transactions.filter(broker__id=broker_id)
    if order_type:
        transactions = transactions.filter(order_type=order_type)
    if status:
        transactions = transactions.filter(status=status)
    if order_id:
        transactions = transactions.filter(order_id__icontains=order_id)
    if timestamp:
        transactions = transactions.filter(timestamp__date=timestamp)

    # Step 4: Limit dropdowns to assigned users' data
    company_names = transactions.values_list('stock__company_name', flat=True).distinct()
    order_ids = transactions.values_list('order_id', flat=True).distinct()

    context = {
        'TransactionDetails': transactions,
        'users': users,
        'advisors': Advisor.objects.all(),
        'brokers': Broker.objects.all(),
        'company_names': company_names,
        'order_ids': order_ids,
    }

    return render(request, 'AllsellTransactionSummary.html', context)

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

from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from user_portfolio.models import BuyTransaction  # Adjust import if needed
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseBadRequest
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import RMPaymentRecord, BuyTransaction, RMUserView

# @csrf_exempt
# @login_required
# def add_or_edit_payment(request, order_id=None, payment_id=None):
#     if request.method == 'POST':
#         if payment_id:  # Edit flow
#             payment = get_object_or_404(RMPaymentRecord, id=payment_id)
#         else:  # Add flow
#             order = get_object_or_404(BuyTransaction, order_id=order_id)
#             rm_view = get_object_or_404(RMUserView, order_id=order_id)
#             payment = RMPaymentRecord(
#                 rm_user_view=rm_view,
#                 date=timezone.now().date(),
#                 time=timezone.now().time()
#             )

#         # Process form fields safely
#         payment.bank_name = request.POST.get('bank_name')
#         payment.amount = Decimal(request.POST.get('amount') or '0')
#         payment.remaining_amount = Decimal(request.POST.get('remaining_amount') or '0')
#         payment.remark = request.POST.get('remark')
#         payment.payment_status = request.POST.get('payment_status', 'pending')

#         if request.FILES.get('screenshot'):
#             payment.screenshot = request.FILES['screenshot']

#         payment.save()
#         return redirect('RM_User:buyordersummery', order_id=payment.rm_user_view.order_id)

#     return HttpResponseBadRequest("Invalid request method")


from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseBadRequest
from decimal import Decimal

from .models import RMPaymentRecord, RMUserView, BuyTransaction

@csrf_exempt
@login_required
def add_or_edit_payment(request, order_id=None, payment_id=None):
    if request.method == 'POST':
        if payment_id:  # Edit flow
            payment = get_object_or_404(RMPaymentRecord, id=payment_id)
        else:  # Add flow
            order = get_object_or_404(BuyTransaction, order_id=order_id)
            rm_view = get_object_or_404(RMUserView, order_id=order_id)
            payment = RMPaymentRecord(
                rm_user_view=rm_view,
                date=timezone.now().date(),
                time=timezone.now().time()
            )

        # Input values
        payment.bank_name = request.POST.get('bank_name')
        entered_amount = Decimal(request.POST.get('amount') or '0')
        payment.amount = entered_amount
        payment.remark = request.POST.get('remark')
        payment.payment_status = request.POST.get('payment_status', 'pending')

        if request.FILES.get('screenshot'):
            payment.screenshot = request.FILES['screenshot']

        # Auto-calculate remaining amount
        rm_view = payment.rm_user_view
        total_expected_amount = rm_view.total_amount  # <-- Assumes `total_amount` exists on RMUserView

        # Sum of all other payments for this rm_view (excluding current one if editing)
        previous_payments = RMPaymentRecord.objects.filter(rm_user_view=rm_view).exclude(id=payment.id)
        total_paid_before = previous_payments.aggregate(total=models.Sum('amount'))['total'] or Decimal('0')

        # Remaining = Total expected - (Previous paid + Current amount)
        payment.remaining_amount = total_expected_amount - (total_paid_before + entered_amount)

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

# @login_required
# def dashboardRM(request):
#     today = timezone.now().date()
#     ten_days_ago = today - timedelta(days=10)
#     start_of_month = today.replace(day=1)

#     # Transaction Metrics
#     total_transactions = RMUserView.objects.count()
#     total_buys = RMUserView.objects.filter(transaction_type='buy').count()
#     total_sells = RMUserView.objects.filter(transaction_type='sell').count()

#     # Total invested amount (sum of all buy total_amounts)
#     total_invested = RMUserView.objects.filter(transaction_type='buy').aggregate(
#         total=Sum('total_amount'))['total'] or 0

#     # Payment Aggregates
#     total_collected_today = RMPaymentRecord.objects.filter(date=today).aggregate(
#         total=Sum('amount'))['total'] or 0
#     total_collected_10_days = RMPaymentRecord.objects.filter(date__gte=ten_days_ago).aggregate(
#         total=Sum('amount'))['total'] or 0
#     total_collected_month = RMPaymentRecord.objects.filter(date__gte=start_of_month).aggregate(
#         total=Sum('amount'))['total'] or 0

#     # Graph Data (date vs amount)
#     payments_by_day = RMPaymentRecord.objects.filter(
#         date__gte=ten_days_ago
#     ).values('date').annotate(
#         total_amount=Sum('amount')
#     ).order_by('date')

#     chart_labels = [entry['date'].strftime('%d-%b') for entry in payments_by_day]
#     chart_data = [float(entry['total_amount']) for entry in payments_by_day]

#     context = {
#         'total_transactions': total_transactions,
#         'total_buys': total_buys,
#         'total_sells': total_sells,
#         'total_invested': total_invested,
#         'total_collected_today': total_collected_today,
#         'total_collected_10_days': total_collected_10_days,
#         'total_collected_month': total_collected_month,
#         'chart_labels': chart_labels,
#         'chart_data': chart_data,
#     }

#     return render(request, 'dashboardRM.html', context)


from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from RM_User.models import RMUserView, RMPaymentRecord

@login_required
def dashboardRM(request):
    user = request.user
    today = timezone.now().date()
    ten_days_ago = today - timedelta(days=10)
    start_of_month = today.replace(day=1)

    # Transaction Metrics (filtered by assigned_rm)
    user_views = RMUserView.objects.filter(assigned_rm=user)
    total_transactions = user_views.count()
    total_buys = user_views.filter(transaction_type='buy').count()
    total_sells = user_views.filter(transaction_type='sell').count()

    # Total invested amount (sum of all buy total_amounts)
    total_invested = user_views.filter(transaction_type='buy').aggregate(
        total=Sum('total_amount'))['total'] or 0

    # Related payment records for this RM only
    rm_payment_records = RMPaymentRecord.objects.filter(rm_user_view__assigned_rm=user)

    # Payment Aggregates
    total_collected_today = rm_payment_records.filter(date=today).aggregate(
        total=Sum('amount'))['total'] or 0
    total_collected_10_days = rm_payment_records.filter(date__gte=ten_days_ago).aggregate(
        total=Sum('amount'))['total'] or 0
    total_collected_month = rm_payment_records.filter(date__gte=start_of_month).aggregate(
        total=Sum('amount'))['total'] or 0

    # Graph Data (date vs amount)
    payments_by_day = rm_payment_records.filter(
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


@login_required
def ordersRM(request):
    return render(request, 'ordersRM.html')

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from itertools import chain
from operator import attrgetter

@login_required
def sellorderRM(request):
    rm_user = request.user
    assigned_users = CustomUser.objects.filter(assigned_rm=rm_user)

    # Fetch both types of sell transactions
    sell_orders_main = SellTransaction.objects.filter(user__in=assigned_users).order_by('-timestamp')
    # sell_orders_other = SellTransactionOtherAdvisor.objects.filter(user__in=assigned_users)

    # Combine and sort them by timestamp (most recent first)
    # combined_sell_orders = sorted(
    #     chain(sell_orders_main, sell_orders_other),
    #     key=attrgetter('timestamp'),
    #     reverse=True
    # )

    return render(request, 'sellorderRM.html', {'sell_orders': sell_orders_main})


@login_required
def ShareListRM(request):
    return render(request, 'ShareListRM.html')

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from user_portfolio.models import SellTransaction
from user_auth.models import UserProfile, CMRCopy, BankAccount

# @login_required
# def selldersummeryRM(request):
#     order_id = request.GET.get('order_id')

#     if not order_id:
#         return render(request, 'selldersummeryRM.html', {'order': None})

#     # Get the sell transaction
#     order = get_object_or_404(SellTransaction, order_id=order_id)

#     # Get the user's profile
#     try:
#         profile = order.user.profile
#     except UserProfile.DoesNotExist:
#         profile = None

#     # Get the CMR copy for this user (assuming latest or first)
#     cmr = CMRCopy.objects.filter(user_profile=profile).first() if profile else None

#     # Get all bank accounts for this user
#     bank_accounts = BankAccount.objects.filter(user_profile=profile) if profile else None

#     context = {
#         'order': order,
#         'cmr': cmr,
#         'bank_accounts': bank_accounts,
#     }

#     return render(request, 'selldersummeryRM.html', context)






















# @login_required
# def selldersummeryRM(request, order_id):
#     # Get the base transaction from either model
#     base_transaction = (
#         SellTransaction.objects.filter(order_id=order_id).first() or
#         SellTransactionOtherAdvisor.objects.filter(order_id=order_id).first()
#     )
#     if not base_transaction:
#         return render(request, "not_found.html", {"message": "Sell order not found."})

#     user_profile = base_transaction.user.profile

#     cmr = CMRCopy.objects.filter(user_profile=user_profile).first()
#     bank_accounts = BankAccount.objects.filter(user_profile=user_profile)
#     rm_view = RMUserView.objects.filter(order_id=order_id).first()

#     # Get matching transactions from both models
#     sell_txns_main = SellTransaction.objects.filter(order_id=order_id)
#     sell_txns_other = SellTransactionOtherAdvisor.objects.filter(order_id=order_id)

#     # Merge and annotate with model_name for template logic
#     all_transactions = []
#     for txn in chain(sell_txns_main, sell_txns_other):
#         txn.model_name = txn.__class__.__name__
#         all_transactions.append(txn)

#     # Payment calculation
#     total_paid = rm_view.payment_records.aggregate(Sum('amount'))['amount__sum'] if rm_view and rm_view.payment_records.exists() else 0
#     total_order_value = sum([txn.total_value or 0 for txn in all_transactions])
#     remaining_amount = total_order_value - total_paid

#     context = {
#         'order': base_transaction,
#         'cmr': cmr,
#         'bank_accounts': bank_accounts,
#         'rm_view': rm_view,
#         'TransactionDetails': all_transactions,
#         'remaining_amount': remaining_amount,
#     }

#     return render(request, 'selldersummeryRM.html', context)









from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.db.models import Sum
from itertools import chain  # Optional now, but can be removed
from .models import SellTransaction, CMRCopy, BankAccount, RMUserView

@login_required
def selldersummeryRM(request, order_id):
    # Get the base transaction from SellTransaction only
    base_transaction = get_object_or_404(SellTransaction, order_id=order_id)
    
    user_profile = base_transaction.user.profile

    # Related data
    cmr = CMRCopy.objects.filter(user_profile=user_profile).first()
    bank_accounts = BankAccount.objects.filter(user_profile=user_profile)
    rm_view = RMUserView.objects.filter(order_id=order_id).first()

    # Get all transactions with this order_id (if multiples exist)
    sell_txns = SellTransaction.objects.filter(order_id=order_id)

    # Annotate each with model name (optional, if used in template logic)
    for txn in sell_txns:
        txn.model_name = "SellTransaction"

    # Calculate total paid and remaining
    total_paid = rm_view.payment_records.aggregate(Sum('amount'))['amount__sum'] if rm_view and rm_view.payment_records.exists() else 0
    total_order_value = sum([txn.total_value or 0 for txn in sell_txns])
    remaining_amount = total_order_value - total_paid

    context = {
        'order': base_transaction,
        'cmr': cmr,
        'bank_accounts': bank_accounts,
        'rm_view': rm_view,
        'TransactionDetails': sell_txns,
        'remaining_amount': remaining_amount,
    }

    return render(request, 'selldersummeryRM.html', context)














@login_required
def angelInvestRM(request):
    return render(request, 'angelInvestRM.html')



# 
# 
# ---------------------------------------------------------------------
# ------------------ Edit Delete  BUY Transactions -------------
# ------------------------------------------------------------------
# 
# 
# views.py
from django.shortcuts import render, get_object_or_404, redirect
from user_portfolio.models import *
from user_portfolio.forms import *
from django.contrib.auth.decorators import login_required

# @login_required
# def edit_buy_transaction(request, pk):
#     transaction = get_object_or_404(BuyTransaction, pk=pk)
#     order_id = transaction.order_id

#     if request.method == 'POST':
#         form = BuyTransactionEditForm(request.POST, instance=transaction, user=request.user)
#         if form.is_valid():
#             form.save()
#             return redirect('RM_User:buyordersummery', order_id=order_id)
#     else:
#         form = BuyTransactionEditForm(instance=transaction, user=request.user)

#     return render(request, 'transaction/edit_transaction.html', {'form': form})

@login_required
def edit_buy_transaction(request, pk):
    transaction = get_object_or_404(BuyTransaction, pk=pk)
    order_id = transaction.order_id

    old_rm_status = transaction.RM_status
    old_ac_status = transaction.AC_status
    old_status = transaction.status

    if request.method == 'POST':
        form = BuyTransactionEditForm(request.POST, instance=transaction, user=request.user)
        if form.is_valid():
            tx = form.save(commit=False)

            user_type = getattr(request.user, 'user_type', None)

            # Check if status changed to "completed" and assign approver accordingly
            if user_type == 'RM' and old_rm_status != 'completed' and tx.RM_status == 'completed':
                tx.RMApproved = request.user
            elif user_type == 'AC' and old_ac_status != 'completed' and tx.AC_status == 'completed':
                tx.ACApproved = request.user
            elif user_type == 'ST' and old_status != 'completed' and tx.status == 'completed':
                tx.STApproved = request.user

            tx.save()
            return redirect('RM_User:buyordersummery', order_id=order_id)
    else:
        form = BuyTransactionEditForm(instance=transaction, user=request.user)

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


# 
# 
# ---------------------------------------------------------------------
# ------------------ Edit Delete  SELL Transactions -------------
# ------------------------------------------------------------------
# 
# 
# views.py

@login_required
def edit_sell_transaction(request, pk):
    transaction = get_object_or_404(SellTransaction, pk=pk)
    order_id = transaction.order_id

    old_rm_status = transaction.RM_status
    old_ac_status = transaction.AC_status
    old_status = transaction.status

    if request.method == 'POST':
        form = SellTransactionEditForm(request.POST, instance=transaction, user=request.user)
        if form.is_valid():
            tx = form.save(commit=False)

            user_type = getattr(request.user, 'user_type', None)

            if user_type == 'RM' and old_rm_status != 'completed' and tx.RM_status == 'completed':
                tx.RMApproved = request.user
            elif user_type == 'AC' and old_ac_status != 'completed' and tx.AC_status == 'completed':
                tx.ACApproved = request.user
            elif user_type == 'ST' and old_status != 'completed' and tx.status == 'completed':
                tx.STApproved = request.user

            tx.save()
            return redirect('RM_User:selldersummeryRM', order_id=order_id)
    else:
        form = SellTransactionEditForm(instance=transaction, user=request.user)

    return render(request, 'transaction/edit_sell_transaction.html', {
        'form': form,
        'transaction': transaction,
    })
