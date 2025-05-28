from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from django.views.decorators.csrf import csrf_exempt

from django.utils.timezone import localtime
from django.utils import timezone

from decimal import Decimal
from django.db.models import Q

from django.core.paginator import Paginator
from django.contrib import messages
from django.http import JsonResponse

import json
from collections import defaultdict

from .forms import *
from .models import *
from .utils import *
from .views import *

from unlisted_stock_marketplace.models import *

def profile_overview(request):
    return render(request, 'portfolio/overview.html')

def unlisted_view(request):
    return render(request, 'portfolio/unlistedOverview.html')

def angel_invest(request):
    return render(request, 'portfolio/angelOverview.html')

def portfolio_view(request):
    return render(request, 'portfolio/PortfolioList.html')

def buy_orders(request):
    return render(request, 'portfolio/BuyOrdersList.html')

def sell_orders(request):
    return render(request, 'portfolio/SellOrdersList.html')



# 
# 
# ---------------------------------------------------------------------
# ------------------ Buy stocks -------------
# ------------------------------------------------------------------
# 
# 
@login_required
def buy_stock(request, stock_id):
    stock = get_object_or_404(StockData, id=stock_id)
    brokers = Broker.objects.all()
    
    query = request.GET.get('q', '').strip()
    stock_type = request.GET.get('stock_type', '')
    
    transactions = StockTransaction.objects.filter(user=request.user)
    
    if request.method == 'POST':
        number_of_shares = int(request.POST.get('number_of_shares', 1))
        order_type = request.POST.get('order_type')
        limit_price_raw = request.POST.get('limit_price')
        broker_id = request.POST.get('broker_id')

        broker = get_object_or_404(Broker, id=broker_id)

        # Use Decimal to prevent type mismatch
        price = Decimal(limit_price_raw) if order_type == 'Limit' and limit_price_raw else stock.ltp

        transactions = StockTransaction.objects.create(
            user=request.user,
            stock=stock,
            share_name=stock.company_name,
            date_bought=timezone.now().date(),
            price_bought=price,
            number_of_shares=number_of_shares,
            current_status='Holding',
            transaction_type='Purchase',
            quantity=number_of_shares,
            broker=broker
        )

        if query:
            transactions = transactions.filter(share_name__icontains=query)

        if stock_type:
            transactions = transactions.filter(stock__stock_type=stock_type)
            
        messages.success(request, f'You have successfully purchased {number_of_shares} shares of {stock.company_name} at ₹{price}.')
        return redirect('unlisted_stock_marketplace:stock_detail', stock_id=stock.id)



    return render(request, 'User_portfolio/buy.html', {
        'stock': stock,
        'brokers': brokers,
        'stock_transactions': transactions,
        'selected_stock_type': stock_type,
        'search_query': query,
    })


# 
# 
# ---------------------------------------------------------------------
# ------------------ Sell stocks -------------
# ------------------------------------------------------------------
# 
# 
@login_required
def sell_stock(request, transaction_id):
    transaction = get_object_or_404(StockTransaction, id=transaction_id, user=request.user)

    query = request.GET.get('q', '').strip()
    stock_type = request.GET.get('stock_type', '')
    
    transactions = StockTransaction.objects.filter(user=request.user)
    

    if query:
        transactions = transactions.filter(share_name__icontains=query)

    if stock_type:
        transactions = transactions.filter(stock__stock_type=stock_type)

    if transaction.current_status == 'Sold':
        messages.warning(request, 'This stock has already been sold.')
        return redirect('user_portfolio:portfolio')  # or wherever your portfolio view is

    if request.method == 'POST':
        number_of_shares_to_sell = int(request.POST.get('number_of_shares', 1))
        order_type = request.POST.get('order_type')
        limit_price_raw = request.POST.get('limit_price')

        if number_of_shares_to_sell > transaction.number_of_shares:
            messages.error(request, f'You only own {transaction.number_of_shares} shares.')
            return redirect('user_portfolio:sell_stock', transaction_id=transaction.id)

        price_sold = Decimal(limit_price_raw) if order_type == 'Limit' and limit_price_raw else transaction.stock.ltp

        transaction.price_sold = price_sold
        transaction.date_sold = timezone.now().date()
        transaction.current_status = 'Sold'
        transaction.transaction_type = 'Sale'
        transaction.quantity = number_of_shares_to_sell
        transaction.save()

        messages.success(request, f'You have successfully sold {number_of_shares_to_sell} shares of {transaction.share_name} at ₹{price_sold}.')
        return redirect('user_portfolio:portfolio')

    return render(request, 'User_portfolio/sell.html', {
        'transaction': transaction,
        'stock': transaction.stock,
        'stock_transactions': transactions,
        'selected_stock_type': stock_type,
        'search_query': query,
    })
