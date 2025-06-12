# app_name : user_portfolio
# utils.py
from user_portfolio.models import *
from unlisted_stock_marketplace.models import StockData

def update_user_holdings(user):
    stocks = StockData.objects.filter(buytransaction__user=user, buytransaction__status='completed').distinct()

    for stock in stocks:
        summary, _ = UserStockInvestmentSummary.objects.get_or_create(user=user, stock=stock)
        summary.update_from_transactions()
        summary.save()
