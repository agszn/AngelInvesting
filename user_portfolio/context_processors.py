# user_portfolio/context_processors.py
from site_Manager.models import Broker, Advisor
from unlisted_stock_marketplace.models import StockData

def buy_sell_context(request):
    return {
        'global_brokers': Broker.objects.all(),
        'global_advisors': Advisor.objects.all(),
        'global_stocks': StockData.objects.all()
    }
