# site_Manager/utils/helpers.py
from unlisted_stock_marketplace.models import CustomFieldValue
from django.db.models import Max, F

def assign_next_order(field_definition):
    """
    Returns the next order value for a given CustomFieldDefinition.
    """
    max_order = CustomFieldValue.objects.filter(
        field_definition=field_definition
    ).aggregate(Max('order'))['order__max']
    return (max_order or 0) + 1


def shift_order_if_needed(field_definition, new_order, exclude_id=None):
    """
    Shifts values with order >= new_order by +1.
    If `exclude_id` is provided, it skips that object (helpful during updates).
    """
    qs = CustomFieldValue.objects.filter(
        field_definition=field_definition,
        order__gte=new_order
    )
    if exclude_id:
        qs = qs.exclude(id=exclude_id)
    qs.update(order=F('order') + 1)

def normalize_orders(field_definition):
    """
    Normalizes the order field for all values of a given field_definition.
    Ensures values are ordered as 1, 2, 3, ... without gaps or duplicates.
    """
    values = CustomFieldValue.objects.filter(
        field_definition=field_definition
    ).order_by('order', 'id')  # Add tie-breaker to ensure consistency

    for i, val in enumerate(values, start=1):
        if val.order != i:
            val.order = i
            val.save(update_fields=['order'])
