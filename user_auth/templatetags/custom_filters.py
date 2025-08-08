from django import template

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


@register.filter(name='get_value')
def get_value(custom_values, args):
    field_id, period_id = map(int, args.split(','))
    for val in custom_values:
        if (val.field_definition_id == field_id and 
            val.stock_period_id == period_id):
            return val.display_value()
    return '-'