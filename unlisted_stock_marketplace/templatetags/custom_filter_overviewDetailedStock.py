# your_app/templatetags/custom_filters.py
from django import template
register = template.Library()

@register.filter
def get_itemTest(dictionary, key):
    return dictionary.get(key, '')


