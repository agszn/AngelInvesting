from django import template

register = template.Library()

@register.simple_tag
def get_label(queryset, selected_id):
    try:
        selected_id = int(selected_id)
        return queryset.get(id=selected_id).name
    except:
        return ""
