from app.scoring import score_lead


def test_scoring_breakdown():
    result = score_lead({'budget_range': '5000-15000', 'timeline': '30-days',
                         'service_interest': 'ecommerce', 'source': 'referral'})
    assert result['score'] == 72
    assert result['priority'] == 'warm'
    assert result['factors'] == ['Budget: +22', 'Timeline: +21', 'Service fit: +14', 'Source: +15']


def test_priority_thresholds_and_upper_bound():
    hot = score_lead({'budget_range': '15000-plus', 'timeline': 'immediate',
                      'service_interest': 'ai-automation', 'source': 'referral'})
    assert hot['score'] == 92
    assert hot['priority'] == 'hot'
    cold = score_lead({'budget_range': 'unknown', 'timeline': 'researching',
                       'service_interest': 'other', 'source': 'other'})
    assert cold == {'score': 15, 'priority': 'cold', 'factors':
                    ['Budget: +0', 'Timeline: +3', 'Service fit: +7', 'Source: +5']}
