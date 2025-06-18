# user_portfolio/constants/order_status.py

RM_STATUS_CHOICES = [
    ('pending_rm_approval', 'Pending RM Approval'),
    ('on_hold', 'On Hold'),
    ('cancelled', 'Cancelled'),
]

ACCOUNTS_STATUS_CHOICES = [
    ('pending_accounts_verification', 'Pending Accounts Verification'),
    ('on_hold', 'On Hold'),
    ('cancelled', 'Cancelled'),
]

STOCK_MANAGER_STATUS_CHOICES = [
    ('processing', 'Processing'),
    ('completed', 'Completed'),
    ('on_hold', 'On Hold'),
    ('cancelled', 'Cancelled'),
]


def get_status_choices_for_user(user):
    user_type = getattr(user, 'user_type', None)

    if user_type == 'RM':
        return RM_STATUS_CHOICES
    elif user_type == 'AC':
        return ACCOUNTS_STATUS_CHOICES
    elif user_type == 'ST':
        return STOCK_MANAGER_STATUS_CHOICES
    else:
        return []  # Default: no access or view-only
