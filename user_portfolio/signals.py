# app: user_portfolio
# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from decimal import Decimal
from .models import *
from unlisted_stock_marketplace.models import StockData
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal
from RM_User.models import *
from unlisted_stock_marketplace.models import StockData

@receiver(post_save, sender=BuyTransaction)
def update_portfolio_and_rm_view(sender, instance, created, **kwargs):
    user = instance.user
    summary, _ = UserPortfolioSummary.objects.get_or_create(user=user)

    # Only use completed transactions in summary
    buy_qs = BuyTransaction.objects.filter(user=user, status='completed')

    total_invested = sum(bt.total_amount for bt in buy_qs)
    total_quantity = sum(bt.quantity for bt in buy_qs)

    total_market_value = Decimal(0)
    todays_gain_loss = Decimal(0)

    for bt in buy_qs:
        stock = bt.stock
        if stock and stock.ltp is not None:
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

    # 🟢 Create or update RMUserView if this is a newly created BuyTransaction
    rm_view, _ = RMUserView.objects.update_or_create(
        order_id=instance.order_id,
        defaults={
            'user': instance.user,
            'transaction_type': 'buy',
            'total_amount': instance.total_amount,
            'buy_status': instance.status,
            'stock': instance.stock,
            'buy_quantity': instance.quantity,
            'price_per_share': instance.price_per_share,
            'timestamp': instance.timestamp,
            'order_type': instance.order_type,
            'isin_no': instance.stock.isin_no if instance.stock else None,
        }
    )
    rm_view.auto_populate_from_sources()
    rm_view.save()


