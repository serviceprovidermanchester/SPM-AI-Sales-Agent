"""Isolated tests; temporary SQLite database; no real external AI requests."""
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ['ADMIN_PASSWORD'] = 'test-admin-password-strong-12345'
os.environ['SECRET_KEY'] = 'test-only-secret-at-least-32-characters-long-123456789'
os.environ['OPENAI_API_KEY'] = ''
os.environ['PUBLIC_FORM_ENABLED'] = 'true'

import pytest
from fastapi.testclient import TestClient
from app.config import settings
from app.main import app, login_failures, public_submissions


@pytest.fixture
def client(tmp_path):
    old_path = settings.database_path
    old_key = settings.openai_api_key
    old_public = settings.public_form_enabled
    object.__setattr__(settings, 'database_path', tmp_path / 'db.sqlite')
    object.__setattr__(settings, 'openai_api_key', '')
    object.__setattr__(settings, 'public_form_enabled', True)
    login_failures.clear()
    public_submissions.clear()
    with TestClient(app) as tc:
        yield tc
    object.__setattr__(settings, 'database_path', old_path)
    object.__setattr__(settings, 'openai_api_key', old_key)
    object.__setattr__(settings, 'public_form_enabled', old_public)


@pytest.fixture
def authenticated(client):
    response = client.post('/api/auth/login', json={'password': os.environ['ADMIN_PASSWORD']})
    assert response.status_code == 200, response.text
    return client, {'X-CSRF-Token': response.json()['csrf']}


@pytest.fixture
def sample_lead():
    return {
        'company': 'Demo Riverside Traders',
        'contact': 'Demo Contact',
        'email': 'demo@example.com',
        'phone': '',
        'service_interest': 'ecommerce',
        'budget_range': '5000-15000',
        'timeline': '30-days',
        'source': 'referral',
        'message': 'Demo use only',
        'consent': False
    }
