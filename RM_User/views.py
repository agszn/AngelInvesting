from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db import models

import csv
from decimal import Decimal
from django.db.models import Sum

from django.http import HttpResponse, HttpResponseBadRequest
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model

from django.views.decorators.csrf import csrf_exempt

from datetime import timedelta
from django.utils import timezone
from datetime import datetime

from .models import *
from user_portfolio.models import *
from user_auth.models import *
from site_Manager.models import *
from unlisted_stock_marketplace.models import *

from django.http import JsonResponse
from django.template.loader import render_to_string


CustomUser = get_user_model()

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



def _attach_activity_and_payments(orders_qs):
    """
    Returns:
      orders_list: list of orders with .latest_payment_at and ._last_activity set
      payments_by_order: {order_id: [RMPaymentRecord, ...]}
      payment_stats_by_order: {order_id: {...summary...}}
    """
    orders_list = list(orders_qs)
    order_ids = [o.order_id for o in orders_list if o.order_id]

    # payments (latest edit/add first)
    payments = (
        RMPaymentRecord.objects
        .filter(rm_user_view__order_id__in=order_ids)
        .select_related('rm_user_view')
        .order_by('-modified_at')
    )

    payments_by_order = {}
    latest_payment_at_by_order = {}
    for p in payments:
        oid = p.rm_user_view.order_id
        payments_by_order.setdefault(oid, []).append(p)
        if oid not in latest_payment_at_by_order:
            latest_payment_at_by_order[oid] = p.modified_at

    # quick stats per order_id
    payment_stats_by_order = {}
    for oid, plist in payments_by_order.items():
        latest = plist[0] if plist else None
        payment_stats_by_order[oid] = {
            'count': len(plist),
            'total_paid': sum(p.amount for p in plist),
            'latest_remaining': latest.remaining_amount if latest else None,
            'last_payment_date': latest.date if latest else None,
            'last_payment_time': latest.time if latest else None,
        }

    # attach last_activity for sorting
    for o in orders_list:
        latest_payment_at = latest_payment_at_by_order.get(o.order_id)
        o.latest_payment_at = latest_payment_at
        upd = o.updated_at
        if timezone.is_naive(upd):
            upd = timezone.make_aware(upd, timezone.get_current_timezone())
        o._last_activity = max(upd, latest_payment_at) if latest_payment_at else upd

    # most recent activity first
    orders_list.sort(key=lambda o: (o._last_activity, o.updated_at, o.timestamp), reverse=True)

    return orders_list, payments_by_order, payment_stats_by_order


@login_required
def ReportRM(request):
    # Current RM and all users assigned to this RM
    rm_user = request.user
    assigned_users = (
        CustomUser.objects
        .filter(assigned_rm=rm_user)
        .select_related('profile')
    )

    # Base completed/cancelled sets, scoped to assigned users
    buy_qs_base = (
        BuyTransaction.objects
        .filter(RM_status__in=['completed', 'cancelled'], user__in=assigned_users)
        .select_related('user', 'stock', 'user__profile')
    )
    sell_qs_base = (
        SellTransaction.objects
        .filter(RM_status__in=['completed', 'cancelled'], user__in=assigned_users)
        .select_related('user', 'stock', 'user__profile')
    )

    # --- Dropdown options (built BEFORE user filters) ---
    # Order IDs from these scoped orders
    buy_oids = buy_qs_base.values_list('order_id', flat=True)
    sell_oids = sell_qs_base.values_list('order_id', flat=True)
    order_id_options = sorted({oid for oid in buy_oids if oid} | {oid for oid in sell_oids if oid})

    # Usernames from ALL users assigned to this RM (even if no orders)
    username_options = []
    for u in assigned_users:
        # Prefer profile.full_name() if it exists / returns text; else fallback
        try:
            full_name = u.profile.full_name() or u.get_full_name() or u.username
        except Exception:
            full_name = u.get_full_name() or u.username
        username_options.append((u.username, full_name))
    # sort by label then username
    username_options.sort(key=lambda t: (t[1] or t[0], t[0]))

    # --- Filters from querystring ---
    date_filter = (request.GET.get('date_filter') or '').strip() or None
    order_id = (request.GET.get('order_id') or '').strip() or None
    username = (request.GET.get('username') or '').strip() or None

    buy_qs = buy_qs_base
    sell_qs = sell_qs_base

    if date_filter:
        buy_qs = buy_qs.filter(timestamp__date=date_filter)
        sell_qs = sell_qs.filter(timestamp__date=date_filter)

    # From dropdowns, so exact matches make sense; keep icontains if you prefer partials
    if order_id:
        buy_qs = buy_qs.filter(order_id=order_id)
        sell_qs = sell_qs.filter(order_id=order_id)

    if username:
        buy_qs = buy_qs.filter(user__username=username)
        sell_qs = sell_qs.filter(user__username=username)

    # Compute activity + payments
    buy_list, buy_payments_by_order, buy_payment_stats = _attach_activity_and_payments(buy_qs)
    sell_list, sell_payments_by_order, sell_payment_stats = _attach_activity_and_payments(sell_qs)

    # Paginate
    buy_paginator = Paginator(buy_list, 10)
    sell_paginator = Paginator(sell_list, 10)
    buy_page_number = request.GET.get('buy_page') or 1
    sell_page_number = request.GET.get('sell_page') or 1
    buy_orders_ReportsRM = buy_paginator.get_page(buy_page_number)
    sell_orders_ReportsRM = sell_paginator.get_page(sell_page_number)

    return render(request, 'ReportRM.html', {
        'buy_orders_ReportsRM': buy_orders_ReportsRM,
        'sell_orders_ReportsRM': sell_orders_ReportsRM,

        # payments + stats dicts (cover all visible order_ids)
        'buy_payments_by_order': buy_payments_by_order,
        'buy_payment_stats_by_order': buy_payment_stats,
        'sell_payments_by_order': sell_payments_by_order,
        'sell_payment_stats_by_order': sell_payment_stats,

        # filters and dropdown options
        'date_filter': date_filter,
        'order_id': order_id,
        'username': username,
        'order_id_options': order_id_options,
        'username_options': username_options,  # list of (username, full_name)
    })


def _combine_aware(d, t):
    """Combine date + time and make timezone-aware if needed."""
    dt = datetime.combine(d, t)
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.get_current_timezone())
    return dt


@login_required
def buyorderRM(request):
    rm_user = request.user

    # Users assigned to this RM
    assigned_users = CustomUser.objects.filter(assigned_rm=rm_user)

    # Base queryset (we'll sort in Python)
    buy_qs = (
        BuyTransaction.objects
        .filter(user__in=assigned_users)
        .exclude(RM_status__in=['completed', 'cancelled'])
        .select_related('user', 'stock', 'advisor', 'broker')
    )

    # Gather payments for these orders, latest EDITS first
    order_ids = list(buy_qs.values_list('order_id', flat=True))
    payments = (
        RMPaymentRecord.objects
        .filter(rm_user_view__order_id__in=order_ids)
        .select_related('rm_user_view')
        .order_by('-modified_at')   # <-- key change
    )

    # Group + compute latest_payment_at per order from modified_at
    payments_by_order = {}
    payment_stats_by_order = {}
    latest_payment_at_by_order = {}

    for p in payments:
        oid = p.rm_user_view.order_id
        payments_by_order.setdefault(oid, []).append(p)
        # first seen is the latest because of order_by('-modified_at')
        if oid not in latest_payment_at_by_order:
            latest_payment_at_by_order[oid] = p.modified_at  # <-- use modified_at

    # Stats (you can keep using date/time for display)
    for oid, plist in payments_by_order.items():
        latest = plist[0] if plist else None
        payment_stats_by_order[oid] = {
            'total_paid': sum(p.amount for p in plist),
            'latest_remaining': latest.remaining_amount if latest else None,
            'last_payment_date': latest.date if latest else None,
            'last_payment_time': latest.time if latest else None,
            'count': len(plist),
        }

    # Attach latest_payment_at and compute last_activity
    buy_orders = []
    for order in buy_qs:
        latest_payment_at = latest_payment_at_by_order.get(order.order_id)
        order.latest_payment_at = latest_payment_at  # for template if you show it

        updated_at = order.updated_at
        if timezone.is_naive(updated_at):
            updated_at = timezone.make_aware(updated_at, timezone.get_current_timezone())

        last_activity = max(updated_at, latest_payment_at) if latest_payment_at else updated_at
        order._last_activity = last_activity
        buy_orders.append(order)

    # Sort by last activity desc (then updated_at, then timestamp)
    buy_orders.sort(key=lambda o: (o._last_activity, o.updated_at, o.timestamp), reverse=True)

    context = {
        'buy_orders': buy_orders,
        'payments_by_order': payments_by_order,
        'payment_stats_by_order': payment_stats_by_order,
    }
    return render(request, 'buyorderRM.html', context)

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

    # Step 3.5: Sort transactions by latest first
    transactions = transactions.order_by('-timestamp')

    # Step 4: Fetch related payment records
    payment_records = RMPaymentRecord.objects.filter(
        rm_user_view__order_id__in=transactions.values_list('order_id', flat=True)
    )

    # Organize payment records by order_id for easy lookup in template
    payments_by_order = {}
    for record in payment_records:
        payments_by_order.setdefault(record.rm_user_view.order_id, []).append(record)

    # Step 5: Limit dropdowns to assigned users' data
    company_names = transactions.values_list('stock__company_name', flat=True).distinct()
    order_ids = transactions.values_list('order_id', flat=True).distinct()

    context = {
        'TransactionDetails': transactions,
        'users': users,
        'advisors': Advisor.objects.all(),
        'brokers': Broker.objects.all(),
        'company_names': company_names,
        'order_ids': order_ids,
        'payments_by_order': payments_by_order,  # <-- add this to template
    }
    if request.user.user_type == "AC":
        template = "AllbuyTransactionSummary_ac.html"
    elif request.user.user_type == "ST":
        template = "AllbuyTransactionSummary_st.html"
    else:
        template = "AllbuyTransactionSummary.html"  

    return render(request, template, context)



@login_required
def AllsellTransactionSummary(request):
    # Step 1: Restrict users to those assigned to the logged-in RM
    if request.user.user_type == 'RM':
        users = CustomUser.objects.filter(assigned_rm=request.user)
    else:
        users = CustomUser.objects.all()

    # Step 2: Restrict transactions to only those users
    transactions = (
        SellTransaction.objects
        .filter(user__in=users)
        .select_related('user', 'broker', 'stock', 'advisor')  # perf
    )

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

    # Latest first
    transactions = transactions.order_by('-timestamp')

    # Step 4: Fetch related payment records (match by order_id)
    order_ids_qs = transactions.values_list('order_id', flat=True)
    payment_records = RMPaymentRecord.objects.filter(
        rm_user_view__order_id__in=order_ids_qs
    )

    # Group payments by order_id for easy template lookup
    payments_by_order = {}
    for pr in payment_records:
        payments_by_order.setdefault(pr.rm_user_view.order_id, []).append(pr)

    # Step 5: Limit dropdowns to assigned users' data (based on filtered set)
    company_names = transactions.values_list('stock__company_name', flat=True).distinct()
    order_ids = transactions.values_list('order_id', flat=True).distinct()

    context = {
        'TransactionDetails': transactions,
        'users': users,
        'advisors': Advisor.objects.all(),
        'brokers': Broker.objects.all(),
        'company_names': company_names,
        'order_ids': order_ids,
        'payments_by_order': payments_by_order,  # <-- ADD
    }

    if request.user.user_type == "AC":
        template = "AllsellTransactionSummary_ac.html"
    elif request.user.user_type == "ST":
        template = "AllsellTransactionSummary_st.html"
    else:
        template = "AllsellTransactionSummary.html"  

    return render(request, template, context)


@csrf_exempt
@login_required
def add_or_edit_payment(request, order_id=None, payment_id=None):
    if request.method != 'POST':
        return HttpResponseBadRequest("Invalid request method")

    # locate / build record
    if payment_id:
        payment = get_object_or_404(RMPaymentRecord, id=payment_id)
        rm_view = payment.rm_user_view
    else:
        order = get_object_or_404(BuyTransaction, order_id=order_id)
        rm_view = get_object_or_404(RMUserView, order_id=order_id)
        payment = RMPaymentRecord(
            rm_user_view=rm_view,
            date=timezone.now().date(),
            time=timezone.now().time()
        )

    # posted fields
    payment.bank_name = request.POST.get('bank_name')
    posted_status = request.POST.get('payment_status', 'pending')
    payment.payment_status = posted_status
    payment.remark = request.POST.get('remark') or None

    # ---- Parse datetime-local -> timezone-aware datetime ----
    # Accepts 'YYYY-MM-DDTHH:MM' or 'YYYY-MM-DDTHH:MM:SS'
    dt_str = request.POST.get('payment_transaction_date')
    if dt_str:
        from datetime import datetime
        try:
            try:
                dt = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M")
            except ValueError:
                dt = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S")
            # Make timezone-aware in current timezone if naive
            if timezone.is_naive(dt):
                dt = timezone.make_aware(dt, timezone.get_current_timezone())
            payment.payment_transaction_date = dt
        except ValueError:
            return HttpResponseBadRequest("Invalid date/time for transaction date.")
    else:
        payment.payment_transaction_date = None
    # --------------------------------------------------------

    payment.paymentConfirmationMessage = request.POST.get('paymentConfirmationMessage') or None

    if request.FILES.get('screenshot'):
        payment.screenshot = request.FILES['screenshot']

    # compute remaining BEFORE applying this payment
    from decimal import Decimal
    from django.db.models import Sum

    total_expected = rm_view.total_amount  # comes from RMUserView auto-populated total_amount
    previous_total = RMPaymentRecord.objects.filter(
        rm_user_view=rm_view
    ).exclude(id=payment.id).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    remaining_before = (total_expected or Decimal('0')) - previous_total

    # STATUS RULES
    # 2) pending => block submission
    if posted_status == 'pending':
        return HttpResponseBadRequest("Cannot submit while status is Pending. Please choose Partial or Payment Received.")

    # 3) approved => take all remaining, lock amount
    if posted_status == 'approved':
        payment.amount = max(remaining_before, Decimal('0'))
        payment.remaining_amount = max(total_expected - (previous_total + payment.amount), Decimal('0'))
        payment.save()
        return redirect('RM_User:buyordersummery', order_id=rm_view.order_id)

    # 5) rejected ("cancelled") => zero effect, lock everything
    if posted_status == 'rejected':
        payment.amount = Decimal('0')
        payment.remaining_amount = remaining_before
        payment.save()
        return redirect('RM_User:buyordersummery', order_id=rm_view.order_id)

    # 3) partial => amount must be >0 and <= remaining_before
    if posted_status == 'partial':
        try:
            amt = Decimal(request.POST.get('amount') or '0')
        except Exception:
            return HttpResponseBadRequest("Invalid amount.")
        if amt <= 0:
            return HttpResponseBadRequest("Amount must be greater than 0 for Partial Payment.")
        if amt > remaining_before:
            return HttpResponseBadRequest("Amount cannot exceed remaining.")
        payment.amount = amt
        payment.remaining_amount = max(total_expected - (previous_total + amt), Decimal('0'))
        payment.save()
        return redirect('RM_User:buyordersummery', order_id=rm_view.order_id)

    # Fallback
    return HttpResponseBadRequest("Unsupported payment status.")

@login_required
def delete_payment(request, payment_id):
    payment = get_object_or_404(RMPaymentRecord, id=payment_id)
    rm_view = payment.rm_user_view
    payment.delete()

    # 🧮 Recalculate remaining amounts after deletion
    all_payments = RMPaymentRecord.objects.filter(
        rm_user_view=rm_view
    ).order_by('date', 'time', 'id')

    total_expected = rm_view.total_amount
    cumulative_paid = Decimal('0')

    for p in all_payments:
        cumulative_paid += p.amount
        p.remaining_amount = max(total_expected - cumulative_paid, Decimal('0'))
        p.save(update_fields=['remaining_amount'])

    return redirect('RM_User:buyordersummery', order_id=rm_view.order_id)



@login_required
def clientRM(request):
    current_rm = request.user 
    clients = current_rm.assigned_users.all()  
    context = {
        'clients': clients
    }
    return render(request, 'clientRM.html', context)


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


@login_required
def sellorderRM(request):
    rm_user = request.user
    assigned_users = CustomUser.objects.filter(assigned_rm=rm_user)

    # Base querysets (don’t order here; we’ll sort after computing last_activity)
    sell_main_qs = (
        SellTransaction.objects
        .filter(user__in=assigned_users)
        .exclude(RM_status__in=['completed', 'cancelled'])
        .select_related('user', 'stock', 'advisor', 'broker')
    )

    # Build list we’ll sort
    sell_qs = list(sell_main_qs)
    # sell_qs = list(chain(sell_main_qs, sell_other_qs))

    # Collect order_ids for payment lookup
    order_ids = [s.order_id for s in sell_qs if s.order_id]

    # Pull payments (latest edits first)
    payments = (
        RMPaymentRecord.objects
        .filter(rm_user_view__order_id__in=order_ids)
        .select_related('rm_user_view')
        .order_by('-modified_at')   
    )

    payments_by_order = {}
    payment_stats_by_order = {}
    latest_payment_at_by_order = {}

    for p in payments:
        oid = p.rm_user_view.order_id
        payments_by_order.setdefault(oid, []).append(p)
        if oid not in latest_payment_at_by_order:
            latest_payment_at_by_order[oid] = p.modified_at  
            
    for oid, plist in payments_by_order.items():
        latest = plist[0] if plist else None
        payment_stats_by_order[oid] = {
            'total_paid': sum(p.amount for p in plist),
            'latest_remaining': latest.remaining_amount if latest else None,
            'last_payment_date': latest.date if latest else None,
            'last_payment_time': latest.time if latest else None,
            'count': len(plist),
        }

    sell_orders = []
    for s in sell_qs:
        latest_payment_at = latest_payment_at_by_order.get(s.order_id)
        s.latest_payment_at = latest_payment_at  

        updated_at = s.updated_at
        if timezone.is_naive(updated_at):
            updated_at = timezone.make_aware(updated_at, timezone.get_current_timezone())

        last_activity = max(updated_at, latest_payment_at) if latest_payment_at else updated_at
        s._last_activity = last_activity
        sell_orders.append(s)

    sell_orders.sort(key=lambda o: (o._last_activity, o.updated_at, o.timestamp), reverse=True)

    return render(request, 'sellorderRM.html', {
        'sell_orders': sell_orders,
        'payments_by_order': payments_by_order,
        'payment_stats_by_order': payment_stats_by_order,
    })

@login_required
def ShareListRM(request):
    return render(request, 'ShareListRM.html')

@login_required
def selldersummeryRM(request, order_id):
    # Get the base transaction from SellTransaction only
    base_transaction = get_object_or_404(SellTransaction, order_id=order_id)
    
    user_profile = base_transaction.user.profile

    # Related data
    cmr = CMRCopy.objects.filter(user_profile=user_profile).first()
    bank_accounts = BankAccount.objects.filter(user_profile=user_profile)
    rm_view = RMUserView.objects.filter(order_id=order_id).first()

    sell_txns = SellTransaction.objects.filter(order_id=order_id)

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


@login_required
@csrf_exempt
def ajax_transaction_handler(request, pk):
    transaction = get_object_or_404(BuyTransaction, pk=pk)
    order_id = transaction.order_id

    if request.method == 'GET':
        form = BuyTransactionEditForm(instance=transaction, user=request.user)
        return render(request, 'partials/transaction_edit_form.html', {'form': form, 'transaction': transaction})

    elif request.method == 'POST':
        form = BuyTransactionEditForm(request.POST, instance=transaction, user=request.user)
        if form.is_valid():
            tx = form.save(commit=False)

            # ✅ Recalculate total_amount
            try:
                tx.total_amount = tx.price_per_share * tx.quantity
            except Exception as e:
                print("Error calculating total amount:", e)

            print("Before Save:")
            print("Qty:", tx.quantity)
            print("Price:", tx.price_per_share)
            print("Total Amount:", tx.total_amount)
            print("RM Status:", tx.RM_status)

            user_type = getattr(request.user, 'user_type', None)
            if user_type == 'RM' and transaction.RM_status != 'completed' and tx.RM_status == 'completed':
                tx.RMApproved = request.user
            elif user_type == 'AC' and transaction.AC_status != 'completed' and tx.AC_status == 'completed':
                tx.ACApproved = request.user
            elif user_type == 'ST' and transaction.status != 'completed' and tx.status == 'completed':
                tx.STApproved = request.user

            tx.save()

            print("After Save:")
            print("Qty:", tx.quantity)
            print("Price:", tx.price_per_share)
            print("Total Amount:", tx.total_amount)
            print("RM Status:", tx.RM_status)

            # ✅ If this is via AJAX, use JsonResponse. If redirecting, client must handle it.
            # return JsonResponse({'success': True})
            # Or use redirect only if you're not in modal AJAX:
            return redirect('RM_User:buyordersummery', order_id=order_id)

        else:
            html = render_to_string('partials/transaction_edit_form.html', {'form': form, 'transaction': transaction})
            return JsonResponse({'success': False, 'html': html})


# sell Handeler
@login_required
@csrf_exempt
def ajax_sell_transaction_handler(request, pk):
    transaction = get_object_or_404(SellTransaction, pk=pk)
    order_id = transaction.order_id

    if request.method == 'GET':
        form = SellTransactionEditForm(instance=transaction, user=request.user)
        return render(request, 'partials/sell_transaction_edit_form.html', {
            'form': form,
            'transaction': transaction,
            'is_sell': True  # optional flag for template
        })

    elif request.method == 'POST':
        form = SellTransactionEditForm(request.POST, instance=transaction, user=request.user)
        if form.is_valid():
            tx = form.save(commit=False)

            user_type = getattr(request.user, 'user_type', None)
            if user_type == 'RM' and transaction.RM_status != 'completed' and tx.RM_status == 'completed':
                tx.RMApproved = request.user
            elif user_type == 'AC' and transaction.AC_status != 'completed' and tx.AC_status == 'completed':
                tx.ACApproved = request.user
            elif user_type == 'ST' and transaction.status != 'completed' and tx.status == 'completed':
                tx.STApproved = request.user

            tx.save()
            return redirect('RM_User:selldersummeryRM', order_id=order_id)

        else:
            html = render_to_string('partials/sell_transaction_edit_form.html', {
                'form': form,
                'transaction': transaction,
                'is_sell': True
            })
            return JsonResponse({'success': False, 'html': html})



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
# RM_User/views.py
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
