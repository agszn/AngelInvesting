from django import template
from unlisted_stock_marketplace.models import StockData, CustomFieldValue


register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, None)

from django import template

register = template.Library()

@register.filter
def percentage_change(ltp, share_price):
    """Calculates the percentage change between LTP and Share Price."""
    if share_price and ltp:
        return ((ltp - share_price) / share_price) * 100
    return 0  # Default to 0% if any value is missing



@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


from django import template

register = template.Library()

@register.filter
def dict_key(d, key):
    return d.get(key)
