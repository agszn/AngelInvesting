# user_portfolio/context_processors.py
import json
from site_Manager.models import Advisor, Broker

def buy_sell_context(request):
    advisors = [{'id': a.id, 'name': a.advisor_type} for a in Advisor.objects.all()]
    brokers = list(Broker.objects.values('id', 'name'))

    return {
        'advisors_json': json.dumps(advisors),
        'brokers_json': json.dumps(brokers),
    }

from django.shortcuts import render, get_object_or_404, redirect
from unlisted_stock_marketplace.models import *

def stock_detail(request, stock_id):
    stock = get_object_or_404(StockData, id=stock_id)
    context = {
        'stock': stock,
        'advisors': Advisor.objects.all(),
        'brokers': Broker.objects.all(),
    }
    return render(request, 'user_portfolio/sell_stock.html', context)
