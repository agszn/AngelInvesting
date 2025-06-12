# templatetags/custom_filters.py
from django import template
register = template.Library()

@register.filter
def get_current_label(queryset, selected_id):
    try:
        return queryset.get(id=selected_id).name
    except:
        return ""
