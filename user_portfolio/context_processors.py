# user_portfolio/context_processors.py
import json
from site_Manager.models import Advisor, Broker

def buy_sell_context(request):
    advisors = [{'id': a.id, 'name': a.advisor_type} for a in Advisor.objects.all()]
    brokers = list(Broker.objects.values('id', 'name'))

    return {
        'advisors_json': json.dumps(advisors),
        'brokers_json': json.dumps(brokers),
    }
