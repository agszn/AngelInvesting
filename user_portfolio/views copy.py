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




# testing

# 
# 
# ---------------------------------------------------------------------
# ------------------ Buy stocks -------------
# ------------------------------------------------------------------
# 
# 
# user_portfolio/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import BuyTransaction, SellTransaction
from unlisted_stock_marketplace.models import *
from site_Manager.models import *
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from decimal import Decimal

from .models import BuyTransaction
from site_Manager.models import Broker, Advisor
from unlisted_stock_marketplace.models import StockData


# user_portfolio/views.py
@require_POST
def buy_stock(request, stock_id):
    stock = get_object_or_404(StockData, id=stock_id)
    try:
        advisor_id = request.POST.get('advisor')
        broker_id = request.POST.get('broker')
        quantity = int(request.POST.get('quantity'))
        price_per_share = Decimal(request.POST.get('price_per_share'))
        order_type = request.POST.get('order_type')

        total_amount = quantity * price_per_share

        advisor = get_object_or_404(Advisor, id=advisor_id)
        broker = get_object_or_404(Broker, id=broker_id)

        BuyTransaction.objects.create(
            user=request.user,
            stock=stock,
            advisor=advisor,
            broker=broker,
            quantity=quantity,
            price_per_share=price_per_share,
            order_type=order_type,
            total_amount=total_amount,
        )

        messages.success(request, f"Buy order placed for {stock.company_name} successfully.")
    except Exception as e:
        messages.error(request, f"Buy order failed: {str(e)}")

    return redirect(request.META.get('HTTP_REFERER', '/'))


# 
# 
# ---------------------------------------------------------------------
# ------------------ Sell stocks -------------
# ------------------------------------------------------------------
# 
# 

@require_POST
def sell_stock(request, stock_id):
    stock = get_object_or_404(StockData, id=stock_id)

    try:
        advisor_id = request.POST.get('advisor')
        broker_id = request.POST.get('broker')
        quantity = int(request.POST.get('quantity'))

        advisor = get_object_or_404(Advisor, id=advisor_id)
        broker = get_object_or_404(Broker, id=broker_id)

        SellTransaction.objects.create(
            user=request.user,  
            advisor=advisor,
            broker=broker,
            stock=stock,
            quantity=quantity,
        )

        messages.success(request, f"Sell order placed for {stock.company_name}  {quantity}")
    except Exception as e:
        messages.error(request, f"Failed to place sell order: {str(e)}")

    return redirect(request.META.get('HTTP_REFERER', '/'))