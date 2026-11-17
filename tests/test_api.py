from datetime import datetime, timedelta, timezone
from app.config import settings
from app.database import connect


def test_health_ui_and_openapi(client):
    assert client.get('/api/health').json()['status'] == 'ok'
    assert 'SPManchester' in client.get('/').text
    assert 'Tell us about your project' in client.get('/capture').text
    assert client.get('/openapi.json').status_code == 200


def test_auth_and_csrf(client, sample_lead):
    assert client.get('/api/leads').status_code == 401
    assert client.post('/api/auth/login', json={'password': 'bad'}).status_code == 401
    login = client.post('/api/auth/login', json={'password': 'test-admin-password-strong-12345'})
    assert login.status_code == 200
    assert 'httponly' in login.headers['set-cookie'].lower()
    assert client.get('/api/auth/me').json()['authenticated'] is True
    assert client.post('/api/leads', json=sample_lead).status_code == 403
    csrf = {'X-CSRF-Token': login.json()['csrf']}
    assert client.post('/api/leads', json=sample_lead, headers=csrf).status_code == 201
    assert client.post('/api/auth/logout', headers=csrf).status_code == 200
    assert client.get('/api/leads').status_code == 401


def test_crud_pipeline_notes_dashboard(authenticated, sample_lead):
    client, headers = authenticated
    created = client.post('/api/leads', json=sample_lead, headers=headers)
    assert created.status_code == 201, created.text
    data = created.json()
    assert data['score'] == 72
    lead_id = data['id']
    assert client.get('/api/dashboard').json()['stats']['total'] == 1
    assert client.get('/api/leads?priority=warm').json()['total'] == 1
    assert client.get('/api/leads?status=qualified').json()['total'] == 0
    assert client.get('/api/leads?q=riverside').json()['total'] == 1
    detail = client.get(f'/api/leads/{lead_id}').json()
    assert len(detail['activities']) == 1
    past = (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat()
    updated = client.patch(f'/api/leads/{lead_id}', json={'status': 'contacted', 'next_followup_at': past}, headers=headers)
    assert updated.status_code == 200, updated.text
    assert client.get('/api/dashboard').json()['stats']['due'] == 1
    assert client.post(f'/api/leads/{lead_id}/activities', json={'note': 'Follow-up planned'}, headers=headers).status_code == 201
    assert len(client.get(f'/api/leads/{lead_id}').json()['activities']) == 4
    assert client.get('/api/leads?status=contacted').json()['total'] == 1
    assert client.delete(f'/api/leads/{lead_id}', headers=headers).status_code == 200
    assert client.get(f'/api/leads/{lead_id}').status_code == 404
    assert client.get('/api/dashboard').json()['stats']['total'] == 0
    with connect() as db:
        assert db.execute('SELECT COUNT(*) FROM activities').fetchone()[0] == 0


def test_validation(authenticated, sample_lead):
    client, headers = authenticated
    invalid = {**sample_lead, 'email': '', 'phone': ''}
    assert client.post('/api/leads', json=invalid, headers=headers).status_code == 422
    invalid = {**sample_lead, 'email': 'not-email'}
    assert client.post('/api/leads', json=invalid, headers=headers).status_code == 422
    phone_only = {**sample_lead, 'email': '', 'phone': '+44 123456789'}
    assert client.post('/api/leads', json=phone_only, headers=headers).status_code == 201
    invalid = {**sample_lead, 'timeline': 'next-century'}
    assert client.post('/api/leads', json=invalid, headers=headers).status_code == 422
    assert client.get('/api/leads?limit=900').status_code == 422
    assert client.get('/api/leads?priority=urgent').status_code == 422
    assert client.patch('/api/leads/123', json={'status': 'new', 'next_followup_at': '2026-11-04T11:00:00'}, headers=headers).status_code == 422


def test_public_form_and_honeypot(client, sample_lead):
    result = client.post('/api/public/leads', json=sample_lead)
    assert result.status_code == 201, result.text
    assert result.json()['accepted'] is True
    fake_bot = client.post('/api/public/leads', json={**sample_lead, 'website_url': 'https://spam.example'})
    assert fake_bot.status_code == 201
    with connect() as db:
        assert db.execute('SELECT COUNT(*) FROM leads').fetchone()[0] == 1
    old = settings.public_form_enabled
    object.__setattr__(settings, 'public_form_enabled', False)
    try:
        assert client.post('/api/public/leads', json=sample_lead).status_code == 403
    finally:
        object.__setattr__(settings, 'public_form_enabled', old)


def test_csv_formula_escape(authenticated, sample_lead):
    client, headers = authenticated
    lead = {**sample_lead, 'company': '=HYPERLINK("evil")'}
    assert client.post('/api/leads', json=lead, headers=headers).status_code == 201
    response = client.get('/api/leads/export')
    assert response.status_code == 200
    assert "'=HYPERLINK" in response.text
    assert 'spm-leads.csv' in response.headers['content-disposition']


def test_draft_modes_and_no_dispatched_message(authenticated, sample_lead):
    client, headers = authenticated
    lead_id = client.post('/api/leads', json=sample_lead, headers=headers).json()['id']
    route = f'/api/leads/{lead_id}/draft'
    local = client.post(route, json={'tone': 'friendly', 'use_ai': False}, headers=headers)
    assert local.status_code == 200
    assert local.json()['mode'] == 'template'
    assert 'Subject:' in local.json()['draft']
    assert 'SPManchester' in local.json()['draft']
    assert client.post(route, json={'tone': 'professional', 'use_ai': True}, headers=headers).status_code == 422
    no_key = client.post(route, json={'use_ai': True, 'confirm_external_processing': True}, headers=headers)
    assert no_key.status_code == 400
    with connect() as db:
        assert db.execute('SELECT COUNT(*) FROM activities WHERE kind="sent"').fetchone()[0] == 0
