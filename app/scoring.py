"""Explainable, deterministic lead scoring; no AI subscription required."""
BUDGET = {'unknown': 0, 'under-1000': 4, '1000-5000': 12,
          '5000-15000': 22, '15000-plus': 30}
TIMELINE = {'researching': 3, '90-days': 10, '30-days': 21, 'immediate': 30}
SERVICE = {'website': 9, 'ecommerce': 14, 'seo': 11, 'paid-ads': 12,
           'ai-automation': 17, 'crm': 15, 'other': 7}
SOURCE = {'website': 8, 'referral': 15, 'linkedin': 11, 'campaign': 7,
          'other': 5}


def score_lead(data):
    budget = BUDGET.get(data.get('budget_range', 'unknown'), 0)
    timeline = TIMELINE.get(data.get('timeline', 'researching'), 0)
    service = SERVICE.get(data.get('service_interest', 'other'), 0)
    source = SOURCE.get(data.get('source', 'other'), 0)
    score = min(100, budget + timeline + service + source)
    priority = 'hot' if score >= 75 else 'warm' if score >= 45 else 'cold'
    factors = [f'Budget: +{budget}', f'Timeline: +{timeline}',
               f'Service fit: +{service}', f'Source: +{source}']
    return {'score': score, 'priority': priority, 'factors': factors}
