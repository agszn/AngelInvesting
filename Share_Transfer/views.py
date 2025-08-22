from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db import models

from user_auth.models import *
from user_portfolio.models import *
from unlisted_stock_marketplace.models import *
from site_Manager.models import *

from RM_User.models import RMUserView, RMPaymentRecord

from django.contrib import messages

@login_required
def dashboardST(request):
    all_deals = DealLetterRecord.objects.all()

    # Distinct values for dropdowns
    user_options = DealLetterRecord.objects.values_list('user__username', flat=True).distinct()
    stock_options = DealLetterRecord.objects.values_list('stock_name', flat=True).distinct()
    date_options = DealLetterRecord.objects.dates('generated_on', 'day')

    # Filters
    type_filter = request.GET.get('deal_type')
    user_filter = request.GET.get('user')
    stock_filter = request.GET.get('stock')
    date_from = request.GET.get('from')
    date_to = request.GET.get('to')
    sort_by = request.GET.get('sort', '-generated_on')

    query = all_deals
    if type_filter:
        query = query.filter(deal_type=type_filter)
    if user_filter:
        query = query.filter(user__username=user_filter)
    if stock_filter:
        query = query.filter(stock_name=stock_filter)
    if date_from:
        query = query.filter(generated_on__date__gte=date_from)
    if date_to:
        query = query.filter(generated_on__date__lte=date_to)

    query = query.order_by(sort_by)

    return render(request, 'dashboardST.html', {
        'records': query,
        'user_options': user_options,
        'stock_options': stock_options,
        'date_options': date_options,
    })



from django.core.paginator import Paginator
from django.shortcuts import render
from django.utils.dateparse import parse_date
from django.contrib.auth.decorators import login_required
from datetime import datetime
from RM_User.models import BuyTransaction, SellTransaction
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def ReportsST(request):
    buy_orders_qs = BuyTransaction.objects.filter(status__in=['completed', 'cancelled']).order_by('-timestamp')
    sell_orders_qs = SellTransaction.objects.filter(status__in=['completed', 'cancelled']).order_by('-timestamp')

    date_filter = request.GET.get('date_filter')
    order_id = request.GET.get('order_id')
    username = request.GET.get('username')

    if date_filter in [None, '', 'None']:
        date_filter = None
    if order_id in [None, '', 'None']:
        order_id = None
    if username in [None, '', 'None']:
        username = None

    if date_filter:
        buy_orders_qs = buy_orders_qs.filter(timestamp__date=date_filter)
        sell_orders_qs = sell_orders_qs.filter(timestamp__date=date_filter)

    if order_id:
        buy_orders_qs = buy_orders_qs.filter(order_id__icontains=order_id)
        sell_orders_qs = sell_orders_qs.filter(order_id__icontains=order_id)

    if username:
        buy_orders_qs = buy_orders_qs.filter(user__username__icontains=username)
        sell_orders_qs = sell_orders_qs.filter(user__username__icontains=username)

    buy_paginator = Paginator(buy_orders_qs, 10)
    sell_paginator = Paginator(sell_orders_qs, 10)

    buy_page_number = request.GET.get('buy_page')
    sell_page_number = request.GET.get('sell_page')

    buy_orders_ReportsST = buy_paginator.get_page(buy_page_number)
    sell_orders_ReportsST = sell_paginator.get_page(sell_page_number)

    return render(request, 'ReportsST.html', {
        'buy_orders_ReportsST': buy_orders_ReportsST,
        'sell_orders_ReportsST': sell_orders_ReportsST,
        'date_filter': date_filter,
        'order_id': order_id,
        'username': username,
    })


@login_required
def buyorderST(request):
    # Show only non-completed BuyTransactions
    buy_orders = BuyTransaction.objects.exclude(status__in=['completed', 'cancelled']).order_by('-timestamp')
    
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
        'st_status_choices': [(k, ST_STATUS_LABELS[k]) for k, _ in BuyTransaction._meta.get_field('status').choices],
    }

    return render(request, 'buyOrderSummaryST.html', context)


# @login_required
# def edit_transaction_st_status(request, transaction_id):
#     if request.method == 'POST':
#         transaction = get_object_or_404(BuyTransaction, id=transaction_id)
#         if request.user.user_type == 'ST':
#             transaction.status = request.POST.get('status')
#             transaction.save()
#             messages.success(request, "Share Transfer Status updated successfully.")
#         else:
#             messages.error(request, "Unauthorized access.")
#     return redirect(request.META.get('HTTP_REFERER', '/'))
# ST buy
@login_required
def edit_transaction_st_status(request, transaction_id):
    if request.method == 'POST':
        transaction = get_object_or_404(BuyTransaction, id=transaction_id)
        
        if request.user.user_type == 'ST':
            new_status = request.POST.get('status')
            transaction.status = new_status
            
            if new_status == 'completed':
                transaction.STApproved = request.user
            
            transaction.save()
            messages.success(request, "Share Transfer Status updated successfully.")
        else:
            messages.error(request, "Unauthorized access.")
            
    return redirect(request.META.get('HTTP_REFERER', '/'))


# ST sell
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

@csrf_exempt
@login_required
def edit_sell_transaction_st_status(request, transaction_id):
    if request.method == 'POST':
        transaction = get_object_or_404(SellTransaction, id=transaction_id)

        if request.user.user_type == 'ST':
            new_status = request.POST.get('status')
            transaction.status = new_status

            if new_status == 'completed':
                transaction.STApproved = request.user

            transaction.save()
            messages.success(request, "Sell Transaction Share Transfer Status updated successfully.")
        else:
            messages.error(request, "Unauthorized access.")

    return redirect(request.META.get('HTTP_REFERER', '/'))


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





from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def sellorderST(request):
    # Exclude both 'completed' and 'cancelled' statuses
    sell_orders = SellTransaction.objects.exclude(status__in=['completed', 'cancelled']).order_by('-timestamp')
    
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
        'st_status_choices': [(k, ST_STATUS_LABELS[k]) for k, _ in BuyTransaction._meta.get_field('status').choices],
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



# 
# 
# 
# ---------------------------------------------------------------------
# ------------------ DealLetters Start -------------
# ------------------------------------------------------------------
# 
# 


def sellDealLetterrST(request):
    return render(request, 'sellDealLetterST.html')

def buyDealLetterrST(request):
    return render(request, 'buyDealLetterrST.html')

# views.py
import base64
import os
import tempfile
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.contrib import messages
from django.conf import settings
from weasyprint import HTML

def generate_invoice_no(prefix, order_id):
    return f"INV-{prefix}-{order_id[-6:]}"


def get_client_details(user):
    profile = getattr(user, 'profile', None)
    cmr = CMRCopy.objects.filter(user_profile=profile).first()
    return {
        'full_name': profile.full_name() if profile else user.get_full_name(),
        'pan_number': profile.pan_number if profile else '-',
        'email': user.email,
        'phone': profile.mobile_number if profile else '-',
        'client_id': cmr.client_id_input if cmr else '-',
    }


def render_to_pdf(request, template_src, context_dict, filename):
    html_string = render_to_string(template_src, context_dict)
    html = HTML(string=html_string)
    result = tempfile.NamedTemporaryFile(delete=True)
    html.write_pdf(target=result.name)

    with open(result.name, 'rb') as pdf:
        response = HttpResponse(pdf.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


def get_logo_base64():
    logo_path = os.path.join(settings.BASE_DIR, 'static/images/logo2.png')
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    return ""


# @login_required
# def buyDealLetterrST(request):
#     order_id = request.GET.get('order_id')
#     if not order_id:
#         messages.error(request, "Order ID is missing.")
#         return redirect("ST_User:dashboard")

#     transaction = get_object_or_404(BuyTransaction, order_id=order_id)
#     invoice_no = generate_invoice_no("BUY", order_id)

#     buyer = get_client_details(transaction.user)
#     seller = {
#         'full_name': 'AngelInvesting.com',
#         'pan_number': 'NA',
#         'email': 'support@angelinvesting.com',
#         'phone': '+91-XXXXXXXXXX',
#         'client_id': 'NA',
#     }

#     context = {
#         'invoice_no': invoice_no,
#         'transaction_date': transaction.timestamp,
#         'to_user': transaction.user.get_full_name(),
#         'transaction': transaction,
#         'stock': transaction.stock,
#         'buyer': buyer,
#         'seller': seller,
#         'mode_of_delivery': 'Demat',
#         'logo_base64': get_logo_base64(),
#     }

#     if request.GET.get('download') == 'pdf':
#         return render_to_pdf(request, 'buyDealLetterrST.html', context, f'{invoice_no}.pdf')

#     return render(request, 'buyDealLetterrST.html', context)


# @login_required
# def sellDealLetterrST(request):
#     order_id = request.GET.get("order_id")
#     if not order_id:
#         messages.error(request, "Order ID is missing.")
#         return redirect("ST_User:dashboard")

#     transaction = get_object_or_404(SellTransaction, order_id=order_id)
#     stock = transaction.stock

#     seller = get_client_details(transaction.user)

#     # Simulate AngelInvesting.com as buyer
#     buyer = {
#         'full_name': 'AngelInvesting.com',
#         'pan_number': 'NA',
#         'email': 'support@angelinvesting.com',
#         'phone': '+91-XXXXXXXXXX',
#         'client_id': 'NA',
#     }

#     context = {
#         'invoice_no': generate_invoice_no("SELL", order_id),
#         'transaction_date': transaction.timestamp,
#         'transaction': transaction,
#         'stock': stock,
#         'buyer': buyer,
#         'seller': seller,
#         'mode_of_delivery': "Demat",
#         'logo_base64': get_logo_base64(),
#     }

#     if request.GET.get("download") == "pdf":
#         return render_to_pdf(request, "sellDealLetterST.html", context, f"{context['invoice_no']}.pdf")

#     return render(request, "sellDealLetterST.html", context)

from .models import DealLetterRecord  # Import

@login_required
def buyDealLetterrST(request):
    order_id = request.GET.get('order_id')
    # print(order_id)
    if not order_id:
        messages.error(request, "Order ID is missing.")
        return redirect("ST_User:dashboardST")

    transaction = get_object_or_404(BuyTransaction, order_id=order_id)
    invoice_no = generate_invoice_no("BUY", order_id)

    buyer = get_client_details(transaction.user)
    seller = {
        'full_name': 'theangelinvesting.com',
        'pan_number': 'NA',
        'email': 'info@theangelinvesting.com',
        'phone': '+91-9945164369',
        'client_id': 'NA',
    }

    # Save deal letter record if not exists
    DealLetterRecord.objects.get_or_create(
        user=transaction.user,
        transaction_id=order_id,
        deal_type='BUY',
        defaults={
            'invoice_no': invoice_no,
            'stock_name': transaction.stock.company_name,
            'quantity': transaction.quantity,
            'price_per_share': transaction.price_per_share,
            'total_amount': transaction.total_amount
        }
    )

    context = {
        'invoice_no': invoice_no,
        'transaction_date': transaction.timestamp,
        'to_user': transaction.user.get_full_name(),
        'transaction': transaction,
        'stock': transaction.stock,
        'buyer': buyer,
        'seller': seller,
        'mode_of_delivery': 'Demat',
        'logo_base64': get_logo_base64(),
    }

    if request.GET.get('download') == 'pdf':
        return render_to_pdf(request, 'buyDealLetterrST.html', context, f'{invoice_no}.pdf')

    return render(request, 'buyDealLetterrST.html', context)


@login_required
def sellDealLetterrST(request):
    order_id = request.GET.get("order_id")
    if not order_id:
        messages.error(request, "Order ID is missing.")
        return redirect("ST_User:dashboardST")

    transaction = get_object_or_404(SellTransaction, order_id=order_id)
    stock = transaction.stock
    seller = get_client_details(transaction.user)

    buyer = {
        'full_name': 'theangelinvesting.com',
        'pan_number': 'NA',
        'email': 'info@theangelinvesting.com',
        'phone': '+91-9945164369',
        'client_id': 'NA',
    }

    invoice_no = generate_invoice_no("SELL", order_id)

    # Save deal letter record if not exists
    DealLetterRecord.objects.get_or_create(
        user=transaction.user,
        transaction_id=order_id,
        deal_type='SELL',
        defaults={
            'invoice_no': invoice_no,
            'stock_name': transaction.stock.company_name,
            'quantity': transaction.quantity,
            'price_per_share': transaction.selling_price,
            'total_amount': transaction.total_value  
        }
    )

    context = {
        'invoice_no': invoice_no,
        'transaction_date': transaction.timestamp,
        'transaction': transaction,
        'stock': stock,
        'buyer': buyer,
        'seller': seller,
        'mode_of_delivery': "Demat",
        'logo_base64': get_logo_base64(),
    }

    if request.GET.get("download") == "pdf":
        return render_to_pdf(request, "sellDealLetterST.html", context, f"{invoice_no}.pdf")

    return render(request, "sellDealLetterST.html", context)


# 
# 
# 
# ---------------------------------------------------------------------
# ------------------ DealLetters End -------------
# ------------------------------------------------------------------
# 
# 

def clientST(request):
    return render(request, 'clientST.html')

