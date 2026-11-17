"""SPM AI Sales Agent: single-team, local-first portfolio demo."""
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
import csv
import hmac
import secrets
import time
from collections import defaultdict, deque

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator, model_validator
from typing import Literal

from app.ai import generate_ai_draft, template_draft
from app.config import ROOT, settings
from app.database import connect, initialize, lead_dict, now
from app.scoring import score_lead

STATIC = ROOT / 'app' / 'static'
STATUS = Literal['new', 'contacted', 'qualified', 'proposal', 'won', 'lost']
SERVICE = Literal['website', 'ecommerce', 'seo', 'paid-ads', 'ai-automation', 'crm', 'other']
BUDGET = Literal['unknown', 'under-1000', '1000-5000', '5000-15000', '15000-plus']
TIMELINE = Literal['researching', '90-days', '30-days', 'immediate']
SOURCE = Literal['website', 'referral', 'linkedin', 'campaign', 'other']


class Login(BaseModel):
    password: str = Field(min_length=1, max_length=300)


class LeadInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    company: str = Field(min_length=2, max_length=120)
    contact: str = Field(min_length=2, max_length=100)
    email: EmailStr | None = None
    phone: str = Field(default='', max_length=40)
    service_interest: SERVICE
    budget_range: BUDGET = 'unknown'
    timeline: TIMELINE = 'researching'
    source: SOURCE = 'website'
    message: str = Field(default='', max_length=1500)
    consent: bool = False
    # Honeypot: humans leave blank, naïve bots may populate.
    website_url: str = Field(default='', max_length=200)

    @field_validator('email', mode='before')
    @classmethod
    def normalize_optional_email(cls, value):
        return None if value == '' else value

    @model_validator(mode='after')
    def validate_contact_method(self):
        if not self.email and not self.phone:
            raise ValueError('An email address or phone number is required.')
        return self


class LeadUpdate(BaseModel):
    status: STATUS
    next_followup_at: datetime | None = None

    @model_validator(mode='after')
    def tz_aware(self):
        if self.next_followup_at and self.next_followup_at.tzinfo is None:
            raise ValueError('Follow-up timestamp must include a time zone.')
        return self


class ActivityInput(BaseModel):
    note: str = Field(min_length=1, max_length=1200)


class DraftInput(BaseModel):
    tone: Literal['professional', 'friendly'] = 'professional'
    use_ai: bool = False
    confirm_external_processing: bool = False


@asynccontextmanager
async def lifespan(_app):
    initialize()
    yield


app = FastAPI(title='SPM AI Sales Agent', version='0.1.0', lifespan=lifespan)
app.mount('/static', StaticFiles(directory=STATIC), name='static')
serializer = URLSafeTimedSerializer(settings.secret_key or 'NOT-CONFIGURED', salt='spm-sales-agent-v1')
login_failures = defaultdict(deque)
public_submissions = defaultdict(deque)


def rate_limit(store, key, threshold, window):
    current = time.monotonic()
    q = store[key]
    while q and current - q[0] > window:
        q.popleft()
    if len(q) >= threshold:
        raise HTTPException(429, 'Too many requests. Try again later.')
    q.append(current)


def session_data(request: Request):
    raw = request.cookies.get('spm_session')
    if not raw:
        return None
    try:
        data = serializer.loads(raw, max_age=settings.session_seconds)
        if data.get('sub') == 'admin':
            return data
    except (BadSignature, SignatureExpired):
        pass
    return None


def require_auth(request: Request):
    data = session_data(request)
    if data is None:
        raise HTTPException(401, 'Please log in.')
    return data


def require_write(request: Request, session=Depends(require_auth)):
    supplied = request.headers.get('X-CSRF-Token', '')
    if not supplied or not hmac.compare_digest(supplied, session.get('csrf', '')):
        raise HTTPException(403, 'Missing or invalid CSRF token.')
    return session


def get_lead(lead_id: int):
    with connect() as db:
        row = db.execute('SELECT * FROM leads WHERE id = ?', (lead_id,)).fetchone()
    if not row:
        raise HTTPException(404, 'Lead not found.')
    return lead_dict(row)


def insert_lead(data: LeadInput):
    clean = data.model_dump(exclude={'website_url'})
    clean['email'] = str(clean.get('email') or '')
    scoring = score_lead(clean)
    created = now()
    with connect() as db:
        cur = db.execute('''INSERT INTO leads
            (company, contact, email, phone, service_interest, budget_range, timeline,
             source, message, consent, status, score, priority, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'new', ?, ?, ?, ?)''', (
                clean['company'], clean['contact'], clean['email'], clean['phone'],
                clean['service_interest'], clean['budget_range'], clean['timeline'],
                clean['source'], clean['message'], int(clean['consent']),
                scoring['score'], scoring['priority'], created, created))
        lead_id = cur.lastrowid
        db.execute('INSERT INTO activities (lead_id, kind, note, created_at) VALUES (?, ?, ?, ?)',
                   (lead_id, 'created', 'Lead added to the pipeline', created))
    return {'id': lead_id, **scoring}


@app.get('/', include_in_schema=False)
def root():
    return FileResponse(STATIC / 'index.html')


@app.get('/capture', include_in_schema=False)
def capture():
    return FileResponse(STATIC / 'capture.html')


@app.get('/api/health')
def health():
    return {'status': 'ok', 'app': settings.app_name, 'version': '0.1.0'}


@app.post('/api/auth/login')
def login(payload: Login, request: Request, response: Response):
    if len(settings.secret_key) < 32 or len(settings.admin_password) < 12:
        raise HTTPException(503, 'Setup needed: run python scripts/bootstrap.py')
    ip = request.client.host if request.client else 'unknown'
    rate_limit(login_failures, ip, threshold=10, window=900)
    if not hmac.compare_digest(payload.password, settings.admin_password):
        raise HTTPException(401, 'Invalid credentials.')
    login_failures.pop(ip, None)
    csrf = secrets.token_urlsafe(32)
    token = serializer.dumps({'sub': 'admin', 'csrf': csrf})
    response.set_cookie('spm_session', token, max_age=settings.session_seconds,
                        httponly=True, secure=settings.cookie_secure, samesite='strict', path='/')
    return {'authenticated': True, 'csrf': csrf}


@app.get('/api/auth/me')
def me(session=Depends(require_auth)):
    return {'authenticated': True, 'csrf': session['csrf'],
            'ai_configured': bool(settings.openai_api_key),
            'public_form_enabled': settings.public_form_enabled}


@app.post('/api/auth/logout')
def logout(response: Response, _=Depends(require_write)):
    response.delete_cookie('spm_session', path='/')
    return {'ok': True}


@app.post('/api/public/leads', status_code=201)
def public_lead(payload: LeadInput, request: Request):
    if not settings.public_form_enabled:
        raise HTTPException(403, 'The public form is disabled.')
    ip = request.client.host if request.client else 'unknown'
    rate_limit(public_submissions, ip, threshold=5, window=3600)
    if payload.website_url:
        return {'accepted': True}  # avoid revealing spam filtering rules
    result = insert_lead(payload)
    return {'accepted': True, 'reference': result['id']}


@app.post('/api/leads', status_code=201)
def create_lead(payload: LeadInput, _=Depends(require_write)):
    if payload.website_url:
        raise HTTPException(422, 'Invalid input.')
    result = insert_lead(payload)
    return {'ok': True, **result}


@app.get('/api/leads')
def list_leads(q: str = '', status: str = '', priority: str = '',
               limit: int = 100, offset: int = 0, _=Depends(require_auth)):
    if len(q) > 120 or limit < 1 or limit > 500 or offset < 0:
        raise HTTPException(422, 'Invalid filter or pagination.')
    if status and status not in ('new', 'contacted', 'qualified', 'proposal', 'won', 'lost'):
        raise HTTPException(422, 'Invalid status.')
    if priority and priority not in ('hot', 'warm', 'cold'):
        raise HTTPException(422, 'Invalid priority.')
    conditions = []
    params = []
    if q:
        conditions.append('(company LIKE ? OR contact LIKE ? OR email LIKE ?)')
        params.extend([f'%{q}%'] * 3)
    if status:
        conditions.append('status = ?')
        params.append(status)
    if priority:
        conditions.append('priority = ?')
        params.append(priority)
    where = ' WHERE ' + ' AND '.join(conditions) if conditions else ''
    with connect() as db:
        total = db.execute('SELECT COUNT(*) FROM leads' + where, params).fetchone()[0]
        rows = db.execute('SELECT * FROM leads' + where +
                          ' ORDER BY score DESC, created_at DESC LIMIT ? OFFSET ?',
                          (*params, limit, offset)).fetchall()
    return {'total': total, 'items': [lead_dict(row) for row in rows]}


def csv_safe(value):
    text = '' if value is None else str(value)
    return "'" + text if text.lstrip().startswith(('=', '+', '-', '@', '\t', '\r')) else text


@app.get('/api/leads/export')
def export_leads(_=Depends(require_auth)):
    with connect() as db:
        items = db.execute('SELECT * FROM leads ORDER BY created_at DESC').fetchall()
    field_names = ['id', 'company', 'contact', 'email', 'phone', 'service_interest',
                   'budget_range', 'timeline', 'source', 'status', 'score', 'priority',
                   'consent', 'next_followup_at', 'created_at']
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(field_names)
    for item in items:
        writer.writerow([csv_safe(item[k]) for k in field_names])
    output.seek(0)
    return StreamingResponse(iter([output.getvalue()]), media_type='text/csv; charset=utf-8',
                             headers={'Content-Disposition': 'attachment; filename="spm-leads.csv"',
                                      'Cache-Control': 'no-store'})


@app.get('/api/dashboard')
def dashboard(_=Depends(require_auth)):
    with connect() as db:
        lead_stats = db.execute('''SELECT COUNT(*) AS total,
            SUM(CASE WHEN priority='hot' THEN 1 ELSE 0 END) AS hot,
            SUM(CASE WHEN priority='warm' THEN 1 ELSE 0 END) AS warm,
            SUM(CASE WHEN status='new' THEN 1 ELSE 0 END) AS new,
            SUM(CASE WHEN status='won' THEN 1 ELSE 0 END) AS won
            FROM leads''').fetchone()
        due = db.execute('''SELECT COUNT(*) FROM leads
            WHERE next_followup_at IS NOT NULL AND next_followup_at <= ?
            AND status NOT IN ('won', 'lost')''', (now(),)).fetchone()[0]
        recent = db.execute('SELECT * FROM leads ORDER BY created_at DESC LIMIT 6').fetchall()
    return {'stats': {**{k: lead_stats[k] or 0 for k in lead_stats.keys()}, 'due': due},
            'recent': [lead_dict(r) for r in recent]}


@app.get('/api/leads/{lead_id}')
def lead_details(lead_id: int, _=Depends(require_auth)):
    lead = get_lead(lead_id)
    with connect() as db:
        acts = db.execute('SELECT * FROM activities WHERE lead_id=? ORDER BY id DESC',
                          (lead_id,)).fetchall()
    return {'lead': lead, 'score_explanation': score_lead(lead)['factors'],
            'activities': [dict(a) for a in acts]}


@app.patch('/api/leads/{lead_id}')
def update_lead(lead_id: int, payload: LeadUpdate, _=Depends(require_write)):
    old = get_lead(lead_id)
    followup = (payload.next_followup_at.astimezone(timezone.utc).isoformat(timespec='seconds')
                if payload.next_followup_at else None)
    with connect() as db:
        db.execute('UPDATE leads SET status=?, next_followup_at=?, updated_at=? WHERE id=?',
                   (payload.status, followup, now(), lead_id))
        notes = []
        if old['status'] != payload.status:
            notes.append(f"Status: {old['status']} → {payload.status}")
        if old['next_followup_at'] != followup:
            notes.append('Follow-up schedule changed')
        for note in notes:
            db.execute('INSERT INTO activities (lead_id, kind, note, created_at) VALUES (?, ?, ?, ?)',
                       (lead_id, 'updated', note, now()))
    return {'ok': True}


@app.post('/api/leads/{lead_id}/activities', status_code=201)
def add_activity(lead_id: int, payload: ActivityInput, _=Depends(require_write)):
    get_lead(lead_id)
    with connect() as db:
        db.execute('INSERT INTO activities (lead_id, kind, note, created_at) VALUES (?, ?, ?, ?)',
                   (lead_id, 'note', payload.note, now()))
    return {'ok': True}


@app.post('/api/leads/{lead_id}/draft')
async def draft(lead_id: int, payload: DraftInput, _=Depends(require_write)):
    lead = get_lead(lead_id)
    if payload.use_ai:
        if not payload.confirm_external_processing:
            raise HTTPException(422, 'Confirm external AI processing before generating a draft.')
        try:
            result = await generate_ai_draft(lead, payload.tone)
            return {'mode': 'ai', 'draft': result}
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from exc
        except Exception as exc:
            # Avoid leaking provider credentials/responses to clients.
            raise HTTPException(502, 'AI service unavailable. Please use Template Draft.') from exc
    return {'mode': 'template', 'draft': template_draft(lead, payload.tone)}


@app.delete('/api/leads/{lead_id}')
def delete_lead(lead_id: int, _=Depends(require_write)):
    get_lead(lead_id)
    with connect() as db:
        db.execute('DELETE FROM leads WHERE id=?', (lead_id,))
    return {'ok': True}
