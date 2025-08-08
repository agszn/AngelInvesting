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

# @receiver(post_save, sender=BuyTransaction)
# def update_portfolio_and_rm_view(sender, instance, created, **kwargs):
#     user = instance.user
#     summary, _ = UserPortfolioSummary.objects.get_or_create(user=user)

#     # Only use completed transactions in summary
#     buy_qs = BuyTransaction.objects.filter(user=user, status='completed')

#     total_invested = sum(bt.total_amount for bt in buy_qs)
#     total_quantity = sum(bt.quantity for bt in buy_qs)

#     total_market_value = Decimal(0)
#     todays_gain_loss = Decimal(0)

#     for bt in buy_qs:
#         stock = bt.stock
#         if stock and stock.ltp is not None:
#             market_value = Decimal(bt.quantity) * stock.ltp
#             total_market_value += market_value
#             gain_today = (stock.ltp - stock.share_price) * bt.quantity
#             todays_gain_loss += gain_today

#     summary.total_invested = total_invested
#     summary.total_quantity = total_quantity
#     summary.total_market_value = total_market_value
#     summary.overall_gain_loss = total_market_value - total_invested
#     summary.todays_gain_loss = todays_gain_loss
#     summary.save()

#     # 🟢 Create or update RMUserView if this is a newly created BuyTransaction
#     rm_view, _ = RMUserView.objects.update_or_create(
#         order_id=instance.order_id,
#         defaults={
#             'user': instance.user,
#             'transaction_type': 'buy',
#             'total_amount': instance.total_amount,
#             'buy_status': instance.status,
#             'stock': instance.stock,
#             'buy_quantity': instance.quantity,
#             'price_per_share': instance.price_per_share,
#             'timestamp': instance.timestamp,
#             'order_type': instance.order_type,
#             'isin_no': instance.stock.isin_no if instance.stock else None,
#         }
#     )
#     rm_view.auto_populate_from_sources()
#     rm_view.save()



@receiver(post_save, sender=BuyTransaction)
def update_portfolio_and_rm_view(sender, instance, created, **kwargs):
    user = instance.user
    summary, _ = UserPortfolioSummary.objects.get_or_create(user=user)

    # Filter only completed transactions
    buy_qs = BuyTransaction.objects.filter(user=user, status='completed')
    sell_qs = SellTransaction.objects.filter(
        user=user,
        status='completed',
    ).exclude(advisor__advisor_type='Other')  # 🛑 Exclude "Other" advisors

    total_invested = Decimal(0)
    total_quantity = 0
    total_market_value = Decimal(0)
    todays_gain_loss = Decimal(0)

    # Grouped by stock
    stock_ids = buy_qs.values_list('stock_id', flat=True).distinct()

    for stock_id in stock_ids:
        stock = StockData.objects.filter(id=stock_id).first()
        if not stock:
            continue

        # Total bought
        buys = buy_qs.filter(stock_id=stock_id)
        buy_qty = buys.aggregate(qty=Sum('quantity'))['qty'] or 0
        buy_amt = buys.aggregate(total=Sum(F('quantity') * F('price_per_share')))['total'] or Decimal(0)

        # Total sold
        sells = sell_qs.filter(stock_id=stock_id)
        sold_qty = sells.aggregate(qty=Sum('quantity'))['qty'] or 0

        # Net quantity held
        quantity_held = max(buy_qty - sold_qty, 0)

        # Only consider held quantity
        if quantity_held > 0:
            avg_price = (buy_amt / buy_qty) if buy_qty else Decimal(0)
            invested_amt = quantity_held * avg_price
            market_val = quantity_held * (stock.ltp or Decimal(0))
            gain_today = quantity_held * ((stock.share_price or 0) - (stock.ltp or 0))

            total_quantity += quantity_held
            total_invested += invested_amt
            total_market_value += market_val
            todays_gain_loss += gain_today

    summary.total_quantity = total_quantity
    summary.total_invested = total_invested
    summary.total_market_value = total_market_value
    summary.overall_gain_loss = total_market_value - total_invested
    summary.todays_gain_loss = todays_gain_loss
    summary.save()

    # 🔄 Update RMUserView for this BuyTransaction
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


# auto update the ither advisor stock price automatically
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal
from unlisted_stock_marketplace.models import StockData
from user_portfolio.models import BuyTransactionOtherAdvisor

@receiver(post_save, sender=StockData)
def update_transactions_on_stock_change(sender, instance, **kwargs):
    related_transactions = BuyTransactionOtherAdvisor.objects.filter(stock=instance)

    for txn in related_transactions:
        txn.market_value = Decimal(txn.quantity) * instance.share_price
        txn.overall_gain_loss = txn.market_value - txn.total_amount

        if instance.ltp:
            change_per_share = instance.share_price - instance.ltp
            txn.todays_gain_loss = Decimal(txn.quantity) * change_per_share
        else:
            txn.todays_gain_loss = Decimal('0.00')

        txn.save(update_fields=['market_value', 'overall_gain_loss', 'todays_gain_loss'])
