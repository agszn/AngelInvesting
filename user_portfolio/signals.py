from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from decimal import Decimal
from .models import BuyTransaction, UserPortfolioSummary
from unlisted_stock_marketplace.models import StockData

@receiver(post_save, sender=BuyTransaction)
def update_portfolio_summary(sender, instance, **kwargs):
    user = instance.user
    summary, _ = UserPortfolioSummary.objects.get_or_create(user=user)

    buy_qs = BuyTransaction.objects.filter(user=user, status='completed')

    total_invested = sum([bt.total_amount for bt in buy_qs])
    total_quantity = sum([bt.quantity for bt in buy_qs])

    # Market value and today's gain/loss
    total_market_value = Decimal(0)
    todays_gain_loss = Decimal(0)
    
    for bt in buy_qs:
        stock = bt.stock
        if stock.ltp:  # live traded price must exist
            market_value = Decimal(bt.quantity) * stock.ltp
            total_market_value += market_value
            gain_today = (stock.ltp - stock.share_price) * bt.quantity
            todays_gain_loss += gain_today

    summary.total_invested = total_invested
    summary.total_quantity = total_quantity
    summary.total_market_value = total_market_value
    summary.overall_gain_loss = total_market_value - total_invested
    summary.todays_gain_loss = todays_gain_loss
    summary.save()
