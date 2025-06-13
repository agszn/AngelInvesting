from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def get_and_clear_popup_message(context):
    request = context['request']
    message = request.session.get('popup_message', '')
    if 'popup_message' in request.session:
        del request.session['popup_message']
    return message
