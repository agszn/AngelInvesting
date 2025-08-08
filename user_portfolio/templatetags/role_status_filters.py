from django import template
from user_portfolio.models import RM_STATUS_LABELS, AC_STATUS_LABELS, ST_STATUS_LABELS

register = template.Library()

@register.filter
def rm_status_label(value):
    return RM_STATUS_LABELS.get(value, value)

@register.filter
def ac_status_label(value):
    return AC_STATUS_LABELS.get(value, value)

@register.filter
def st_status_label(value):
    return ST_STATUS_LABELS.get(value, value)
