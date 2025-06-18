from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db import models

from user_auth.models import *
from user_portfolio.models import *
from unlisted_stock_marketplace.models import *
from site_Manager.models import *

from RM_User.models import RMUserView, RMPaymentRecord

from django.contrib import messages
def dashboardST(request):
    return render(request, 'dashboardST.html')

@login_required
def buyorderST(request):
    # Fetch BuyTransactions of those users
    buy_orders = BuyTransaction.objects.filter(RM_status='completed').order_by('-timestamp')
    
    return render(request, 'buyorderST.html', {'buy_orders': buy_orders})

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.db.models import Sum
from django.shortcuts import render, get_object_or_404

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.db.models import Sum
from django.shortcuts import render, get_object_or_404
from user_portfolio.models import BuyTransaction
from user_auth.models import UserProfile, CMRCopy, BankAccount


@login_required
def buyOrderSummaryST(request, order_id):
    order = get_object_or_404(BuyTransaction, order_id=order_id)
    user_profile = order.user.profile
    user_type = request.user.user_type  # Or from profile if needed

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
    }

    return render(request, 'buyOrderSummaryST.html', context)



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
#             return redirect('ST_User:buyOrderSummaryST', order_id=order_id)
#     else:
#         form = BuyTransactionEditForm(instance=transaction, user=request.user)

#     return render(request, 'transaction/edit_transaction.html', {'form': form})


@login_required
def edit_buy_transactionST(request, pk):
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
            return redirect('ST_User:buyOrderSummaryST', order_id=order_id)
    else:
        form = BuyTransactionEditForm(instance=transaction, user=request.user)

    return render(request, 'transactionST/edit_transactionST.html', {'form': form})



def buyDealLetterrST(request):
    return render(request, 'buyDealLetterrST.html')

@login_required
def sellorderST(request):
    sell_orders = SellTransaction.objects.all().order_by('-timestamp')
    return render(request, 'sellorderST.html', {'sell_orders': sell_orders})

def SellerSummaryST(request, order_id):
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
    }

    return render(request, 'SellSummaryST.html', context)


# ---------------------------------------------------------------------
# ------------------ Edit Delete  SELL Transactions -------------
# ------------------------------------------------------------------
# 
# 
# views.py

@login_required
def edit_sell_transactionST(request, pk):
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
            return redirect('ST_User:SellerSummaryST', order_id=order_id)
    else:
        form = SellTransactionEditForm(instance=transaction, user=request.user)

    return render(request, 'transactionST/edit_sell_transactionST.html', {
        'form': form,
        'transaction': transaction,
    })


def sellDealLetterrST(request):
    return render(request, 'sellDealLetterST.html')

def clientST(request):
    return render(request, 'clientST.html')

