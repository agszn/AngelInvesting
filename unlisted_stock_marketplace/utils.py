# utils.py
from datetime import datetime

def parse_user_date(date_str):
    for fmt in ['%d-%m-%Y', '%d/%m/%Y']:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return None  # Return None if parsing fails
