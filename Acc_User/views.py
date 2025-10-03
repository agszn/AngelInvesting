from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db import models

from user_auth.models import *
from user_portfolio.models import *
from unlisted_stock_marketplace.models import *
from site_Manager.models import *
from RM_User.models import RMUserView, RMPaymentRecord

import csv
from django.http import HttpResponse
from django.contrib.auth import get_user_model

from django.db.models import Sum
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib import messages

from user_portfolio.forms import *
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator


User = get_user_model()

@login_required
def dashboardAcc(request):
    rms = User.objects.filter(user_type='RM')
    selected_rm_id = request.GET.get('filter_rm')

    if selected_rm_id:
        users = User.objects.filter(assigned_rm_id=selected_rm_id)
    else:
        users = User.objects.exclude(user_type='RM')

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        rm_id = request.POST.get('rm_id')
        try:
            user = User.objects.get(id=user_id)
            rm = User.objects.get(id=rm_id, user_type='RM')
            user.assigned_rm = rm
            user.save()
        except User.DoesNotExist:
            pass

        return redirect('Acc_User:dashboardAcc')  

    context = {
        'rms': rms,
        'users': users,
        'selected_rm_id': selected_rm_id,
    }
    return render(request, 'dashboardAcc.html', context)

@login_required
def ordersAcc(request):
    buy_orders = BuyTransaction.objects.filter(RM_status='completed')
    sell_orders = SellTransaction.objects.filter(RM_status='completed')
    sell_other_orders = SellTransactionOtherAdvisor.objects.filter(RM_status='completed')

    all_orders = []

    for order in buy_orders:
        all_orders.append({
            'type': 'Buy',
            'order_id': order.order_id,
            'user': order.user.username,
            'stock': order.stock.company_name,
            'quantity': order.quantity,
            'price': order.price_per_share,
            'total': order.total_amount,
            'timestamp': order.timestamp,
        })

    for order in sell_orders:
        all_orders.append({
            'type': 'Sell',
            'order_id': order.order_id,
            'user': order.user.username,
            'stock': order.stock.company_name,
            'quantity': order.quantity,
            'price': order.selling_price,
            'total': order.total_value,
            'timestamp': order.timestamp,
        })

    for order in sell_other_orders:
        all_orders.append({
            'type': 'Sell (Other Advisor)',
            'order_id': order.order_id,
            'user': order.user.username,
            'stock': order.stock.company_name,
            'quantity': order.quantity,
            'price': order.selling_price,
            'total': order.total_value,
            'timestamp': order.timestamp,
        })

    # Sort all by timestamp descending
    all_orders.sort(key=lambda x: x['timestamp'], reverse=True)

    return render(request, 'ordersAcc.html', {'orders': all_orders})


@login_required
def buyorderAcc(request):
    # Fetch BuyTransactions of those users
    buy_ordersAcc = BuyTransaction.objects.exclude(AC_status__in=['completed', 'cancelled']).order_by('-timestamp')
    return render(request, 'buyorderAcc.html', {'buy_orders': buy_ordersAcc})


@login_required
def buyOrderSummaryAcc(request, order_id):
    order = get_object_or_404(BuyTransaction, order_id=order_id)
    user_profile = order.user.profile
    user_type = request.user.user_type  
    if user_type == 'RM':
        pass  
    elif user_type == 'AC':
        if order.RM_status != 'completed':
            messages.warning(request, "This order has not been approved by the Relationship Manager yet.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

    elif user_type == 'ST':
        if order.RM_status != 'completed' or order.AC_status != 'completed':
            messages.warning(request, "This order has not been approved by both RM and Accounts yet.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

    elif not request.user.is_superuser:
        messages.error(request, "You do not have permission to view this order.")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    
    # Retrieve related data
    rm_view = RMUserView.objects.filter(order_id=order_id).first()
    cmr = CMRCopy.objects.filter(user_profile=user_profile).first()
    bank_accounts = BankAccount.objects.filter(user_profile=user_profile)
    total_paid = rm_view.payment_records.aggregate(Sum('amount'))['amount__sum'] if rm_view else 0
    total_paid = total_paid or 0
    remaining_amount = order.total_amount - total_paid

    context = {
        'order': order,
        'cmr': cmr,
        'bank_accounts': bank_accounts,
        'rm_view': rm_view,
        'TransactionDetails': BuyTransaction.objects.filter(order_id=order_id),
        'remaining_amount': remaining_amount,
        'user_type': user_type,
        'ac_payment_choices': RMPaymentRecord._meta.get_field('AC_Payment_Status').choices,
        'ac_status_choices': [(k, AC_STATUS_LABELS[k]) for k in dict(BuyTransaction._meta.get_field('AC_status').choices)],

    }

    return render(request, 'buyOrderSummaryAcc.html', context)



# this is main start
@require_POST
@login_required
def edit_payment_ac_status(request, payment_id):
    payment = get_object_or_404(RMPaymentRecord, id=payment_id)

    # Ensure only AC or superuser can edit
    if request.user.user_type != 'AC' and not request.user.is_superuser:
        messages.error(request, "You do not have permission to update this.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    # Get values from form
    payment.AC_Payment_Status = request.POST.get('AC_Payment_Status')
    payment.payment_transaction_date = request.POST.get('payment_transaction_date') or None
    payment.payment_transaction_id = request.POST.get('payment_transaction_id') or ''

    payment.save()

    messages.success(request, "Payment status and transaction details updated.")
    return redirect(request.META.get('HTTP_REFERER', '/'))
# this is main end

from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages


@csrf_exempt
@login_required
def edit_transaction_ac_status(request, transaction_id):
    if request.method == 'POST':
        transaction = get_object_or_404(BuyTransaction, id=transaction_id)
        
        if request.user.user_type == 'AC':
            new_status = request.POST.get('AC_status')
            transaction.AC_status = new_status
            
            if new_status == 'completed':
                transaction.ACApproved = request.user
            
            transaction.save()
            messages.success(request, "Accounts Approval Status updated successfully.")
        else:
            messages.error(request, "Unauthorized access.")
            
    return redirect(request.META.get('HTTP_REFERER', '/'))


@csrf_exempt
@login_required
def edit_sell_transaction_ac_status(request, transaction_id):
    if request.method == 'POST':
        transaction = get_object_or_404(SellTransaction, id=transaction_id)

        if request.user.user_type == 'AC':
            new_status = request.POST.get('AC_status')
            transaction.AC_status = new_status

            if new_status == 'completed':
                transaction.ACApproved = request.user

            transaction.save()
            messages.success(request, "Accounts Approval Status updated successfully.")
        else:
            messages.error(request, "Unauthorized access.")

    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def edit_buy_transactionAcc(request, pk):
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
            return redirect('Acc_User:buyOrderSummaryAcc', order_id=order_id)
    else:
        form = BuyTransactionEditForm(instance=transaction, user=request.user)

    return render(request, 'transaction/edit_transactionAcc.html', {'form': form})


# 
# 
# ---------------------------------------------------------------------
# ------------------ Edit Delete  SELL Transactions -------------
# ------------------------------------------------------------------
# 
# 
# views.py

@login_required
def edit_sell_transactionAcc(request, pk):
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
            return redirect('Acc_User:SellerSummaryAcc', order_id=order_id)
    else:
        form = SellTransactionEditForm(instance=transaction, user=request.user)

    return render(request, 'transaction/edit_sell_transactionAcc.html', {
        'form': form,
        'transaction': transaction,
    })


def sellorderAcc(request):

    # Fetch both types of sell transactions
    sell_ordersAcc = SellTransaction.objects.exclude(AC_status__in=['completed', 'cancelled']).order_by('-timestamp')

    return render(request, 'sellorderAcc.html', {'sell_orders': sell_ordersAcc})

def unlistedSharesAcc(request):
    return render(request, 'unlistedSharesAcc.html')

def ShareListAcc(request):
    return render(request, 'ShareListAcc.html')

def clientAcc(request):
    return render(request, 'clientAcc.html')

def reportsAcc(request):
    buy_orders_qs = BuyTransaction.objects.filter(AC_status__in=['completed', 'cancelled']).order_by('-timestamp')
    sell_orders_qs = SellTransaction.objects.filter(AC_status__in=['completed', 'cancelled']).order_by('-timestamp')

    # Get the filters
    date_filter = request.GET.get('date_filter')
    order_id = request.GET.get('order_id')
    username = request.GET.get('username')

    # Sanitize inputs
    if date_filter in [None, '', 'None']:
        date_filter = None
    if order_id in [None, '', 'None']:
        order_id = None
    if username in [None, '', 'None']:
        username = None

    # Apply date filtering
    if date_filter:
        buy_orders_qs = buy_orders_qs.filter(timestamp__date=date_filter)
        sell_orders_qs = sell_orders_qs.filter(timestamp__date=date_filter)

    # Apply order ID filtering
    if order_id:
        buy_orders_qs = buy_orders_qs.filter(order_id__icontains=order_id)
        sell_orders_qs = sell_orders_qs.filter(order_id__icontains=order_id)

    # Apply username filtering (assuming related user has a `username` field)
    if username:
        buy_orders_qs = buy_orders_qs.filter(user__username__icontains=username)
        sell_orders_qs = sell_orders_qs.filter(user__username__icontains=username)

    # PAGINATION
    buy_paginator = Paginator(buy_orders_qs, 10)
    sell_paginator = Paginator(sell_orders_qs, 10)

    buy_page_number = request.GET.get('buy_page')
    sell_page_number = request.GET.get('sell_page')

    buy_orders_ReportsAcc = buy_paginator.get_page(buy_page_number)
    sell_orders_ReportsAcc = sell_paginator.get_page(sell_page_number)

    return render(request, 'reportsAcc.html', {
        'buy_orders_ReportsAcc': buy_orders_ReportsAcc,
        'sell_orders_ReportsAcc': sell_orders_ReportsAcc,
        'date_filter': date_filter,
        'order_id': order_id,
        'username': username,
    })


@login_required
def SellerSummaryAcc(request, order_id):
    # Get the base sell transaction
    order = get_object_or_404(SellTransaction, order_id=order_id)
    user_profile = order.user.profile
    user_type = request.user.user_type  # Or from request.user.profile.user_type if stored in profile

    # ✅ Access Control Logic
    if user_type == 'RM':
        pass  # RM always has access

    elif user_type == 'AC':
        if order.RM_status != 'completed':
            messages.warning(request, "This order has not been approved by the Relationship Manager yet.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

    elif user_type == 'ST':
        if order.RM_status != 'completed' or order.AC_status != 'completed':
            messages.warning(request, "This order has not been approved by both RM and Accounts yet.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

    elif not request.user.is_superuser:
        messages.error(request, "You do not have permission to view this order.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    # ✅ Related data
    rm_view = RMUserView.objects.filter(order_id=order_id).first()
    cmr = CMRCopy.objects.filter(user_profile=user_profile).first()
    bank_accounts = BankAccount.objects.filter(user_profile=user_profile)

    # ✅ Transactions under same order
    sell_txns = SellTransaction.objects.filter(order_id=order_id)

    # ✅ Add model name (optional for template)
    for txn in sell_txns:
        txn.model_name = "SellTransaction"

    # ✅ Payment and remaining amount
    total_paid = rm_view.payment_records.aggregate(Sum('amount'))['amount__sum'] if rm_view else 0
    total_paid = total_paid or 0
    total_order_value = sum([txn.total_value or 0 for txn in sell_txns])
    remaining_amount = total_order_value - total_paid

    context = {
        'order': order,
        'cmr': cmr,
        'bank_accounts': bank_accounts,
        'rm_view': rm_view,
        'TransactionDetails': sell_txns,
        'remaining_amount': remaining_amount,
        'user_type': user_type,
        'ac_status_choices': [(k, AC_STATUS_LABELS[k]) for k in dict(BuyTransaction._meta.get_field('AC_status').choices)],
    }

    return render(request, 'SellSummaryAcc.html', context)


def AngelInvestAcc(request):
    return render(request, 'AngelInvest.html')
