"""Add explicitly fictional sample leads; never real customer data."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.database import initialize, connect
from app.main import LeadInput, insert_lead

SAMPLES = [
    ('Demo Northstar Retail', 'Demo Contact A', 'ecommerce', '5000-15000', '30-days', 'referral'),
    ('Demo Vertex Estates', 'Demo Contact B', 'website', '15000-plus', 'immediate', 'linkedin'),
    ('Demo Metro Call Center', 'Demo Contact C', 'ai-automation', '5000-15000', 'immediate', 'website'),
    ('Demo Evergreen Clinic', 'Demo Contact D', 'seo', '1000-5000', '90-days', 'campaign'),
    ('Demo Skyline Traders', 'Demo Contact E', 'crm', 'under-1000', 'researching', 'website'),
    ('Demo Meridian Foods', 'Demo Contact F', 'paid-ads', '15000-plus', '30-days', 'referral'),
]
initialize()
with connect() as db:
    count = db.execute('SELECT COUNT(*) FROM leads').fetchone()[0]
if count:
    print('There are already leads in the database. Demo seed skipped to avoid mixing data.')
    raise SystemExit(0)
for index, (company, contact, service, budget, timeline, source) in enumerate(SAMPLES, 1):
    item = LeadInput(company=company, contact=contact,
                     email=f'demo{index}@example.com', service_interest=service,
                     budget_range=budget, timeline=timeline, source=source,
                     message='Fictional portfolio demonstration record.', consent=False)
    insert_lead(item)
print(f'Added {len(SAMPLES)} fictional leads. None are genuine client records.')
