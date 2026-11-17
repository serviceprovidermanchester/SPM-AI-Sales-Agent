'use strict';
const $ = (id) => document.getElementById(id);
const state = { csrf: null, offset: 0, limit: 20, current: null, total: 0, aiConfigured: false };
const escapes = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
const safe = (value) => String(value ?? '').replace(/[&<>"']/g, (c) => escapes[c]);
const label = (value) => String(value || '—').replace(/[-_]/g, ' ');
const dateLabel = (value) => value ? new Date(value).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' }) : 'Not scheduled';
let toastTimer;
function toast(message) { $('toast').textContent = message; $('toast').hidden = false; clearTimeout(toastTimer); toastTimer = setTimeout(() => $('toast').hidden = true, 3800); }
async function api(path, options = {}) {
  const method = options.method || 'GET';
  const headers = { ...(options.body ? { 'Content-Type': 'application/json' } : {}), ...(method !== 'GET' && state.csrf ? { 'X-CSRF-Token': state.csrf } : {}) };
  const response = await fetch(path, { credentials: 'same-origin', ...options, headers: { ...headers, ...(options.headers || {}) } });
  let data = null;
  try { data = await response.json(); } catch { /* e.g., empty response */ }
  if (!response.ok) {
    if (response.status === 401 && !path.includes('login')) setLoggedIn(false);
    const detail = data?.detail;
    const message = typeof detail === 'string' ? detail : Array.isArray(detail) ? detail.map((e) => e.msg).join('; ') : `Request failed (${response.status})`;
    throw new Error(message);
  }
  return data;
}
function setLoggedIn(value) { $('workspace').hidden = !value; $('loginView').hidden = value; $('logoutBtn').hidden = !value; if (!value) state.csrf = null; }
async function initialize() { try { const me = await api('/api/auth/me'); state.csrf = me.csrf; state.aiConfigured = me.ai_configured; setLoggedIn(true); await refresh(); } catch { setLoggedIn(false); } }
$('loginForm').addEventListener('submit', async (e) => {
  e.preventDefault(); $('loginError').textContent = '';
  const button = e.target.querySelector('button[type=submit]'); button.disabled = true;
  try { const data = await api('/api/auth/login', { method: 'POST', body: JSON.stringify({ password: $('password').value }) }); state.csrf = data.csrf; $('password').value = ''; setLoggedIn(true); await refresh(); }
  catch (error) { $('loginError').textContent = error.message; } finally { button.disabled = false; }
});
$('logoutBtn').addEventListener('click', async () => { try { await api('/api/auth/logout', { method: 'POST' }); } catch { /* local UI cleanup */ } setLoggedIn(false); });
$('refreshBtn').addEventListener('click', refresh);
async function refresh() { try { const summary = await api('/api/dashboard'); for (const key of ['total', 'hot', 'due', 'won']) $(key).textContent = summary.stats[key]; await listLeads(); } catch (e) { toast(e.message); } }
async function listLeads() {
  const params = new URLSearchParams({ q: $('search').value, status: $('filterStatus').value, priority: $('filterPriority').value, limit: state.limit, offset: state.offset });
  const data = await api('/api/leads?' + params); state.total = data.total;
  $('resultCount').textContent = `${data.total} lead${data.total === 1 ? '' : 's'}`;
  $('leadRows').innerHTML = data.items.length ? data.items.map((l) => `<tr><td><strong>${safe(l.company)}</strong><small>${safe(l.contact)} · ${safe(l.email || l.phone)}</small></td><td>${safe(label(l.service_interest))}</td><td><span class="tag tag-${safe(l.priority)}">${safe(l.score)}/100 · ${safe(l.priority)}</span></td><td><span class="tag tag-status">${safe(l.status)}</span></td><td>${safe(dateLabel(l.next_followup_at))}</td><td><button class="text-btn" data-open-id="${l.id}">View →</button></td></tr>`).join('') : '<tr><td colspan="6" class="empty">No leads found. Add your first lead or clear the filters.</td></tr>';
  $('pager').innerHTML = `<span>${data.total ? state.offset + 1 : 0}–${Math.min(state.offset + state.limit, data.total)} of ${data.total}</span><button id="prevPage" ${state.offset === 0 ? 'disabled' : ''}>← Prev</button><button id="nextPage" ${state.offset + state.limit >= state.total ? 'disabled' : ''}>Next →</button>`;
  $('prevPage').onclick = () => { state.offset = Math.max(0, state.offset - state.limit); listLeads().catch((e) => toast(e.message)); };
  $('nextPage').onclick = () => { state.offset += state.limit; listLeads().catch((e) => toast(e.message)); };
}
$('leadRows').addEventListener('click', (e) => { const id = e.target.closest('[data-open-id]')?.dataset.openId; if (id) openDetail(Number(id)); });
let searchTimer;
$('search').addEventListener('input', () => { clearTimeout(searchTimer); searchTimer = setTimeout(() => { state.offset = 0; listLeads().catch((e) => toast(e.message)); }, 250); });
for (const id of ['filterStatus', 'filterPriority']) $(id).addEventListener('change', () => { state.offset = 0; listLeads().catch((e) => toast(e.message)); });
const toggle = (id, display) => { $(id).hidden = !display; document.body.style.overflow = (!document.querySelector('.overlay:not([hidden])')) ? '' : 'hidden'; };
$('newLeadBtn').onclick = () => toggle('modal', true);
$('closeModal').onclick = $('cancelLead').onclick = () => toggle('modal', false);
$('closeDetail').onclick = () => toggle('detailOverlay', false);
for (const id of ['modal', 'detailOverlay']) $(id).addEventListener('click', (e) => { if (e.target.id === id) toggle(id, false); });
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') for (const id of ['modal', 'detailOverlay']) toggle(id, false); });
$('leadForm').addEventListener('submit', async (e) => {
  e.preventDefault(); $('leadError').textContent = '';
  const form = e.target;
  const raw = Object.fromEntries(new FormData(form).entries());
  const payload = { ...raw, consent: form.elements.consent.checked, website_url: '' };
  if (!payload.email && !payload.phone) { $('leadError').textContent = 'An email or phone number is required.'; return; }
  const button = form.querySelector('[type=submit]'); button.disabled = true;
  try { await api('/api/leads', { method: 'POST', body: JSON.stringify(payload) }); form.reset(); toggle('modal', false); toast('Lead saved and scored.'); await refresh(); }
  catch (error) { $('leadError').textContent = error.message; } finally { button.disabled = false; }
});
async function openDetail(id) {
  try {
    const data = await api(`/api/leads/${id}`);
    state.current = data.lead; const l = data.lead; $('detailTitle').textContent = l.company;
    const fields = [['Contact', l.contact], ['Email', l.email], ['Phone', l.phone], ['Service', label(l.service_interest)], ['Source', label(l.source)], ['Budget (USD, illustrative)', label(l.budget_range)], ['Timeline', label(l.timeline)], ['Consent recorded', l.consent ? 'Yes' : 'No'], ['Lead score', `${l.score}/100 · ${l.priority}`], ['Notes from inquiry', l.message]];
    $('detailBody').innerHTML = `<div class="detail-grid">${fields.map(([k,v]) => `<div class="field"><small>${safe(k)}</small><strong>${safe(v || '—')}</strong></div>`).join('')}</div>
    <div class="detail-section"><h3>Why this score?</h3><p class="muted">${data.score_explanation.map(safe).join(' · ')}</p></div>
    <div class="detail-section"><h3>Pipeline & follow-up</h3><div class="row-controls"><div><label for="detailStatus">Status</label><select id="detailStatus">${['new','contacted','qualified','proposal','won','lost'].map(s => `<option value="${s}" ${l.status === s ? 'selected' : ''}>${label(s)}</option>`).join('')}</select></div><div><label for="followupDate">Follow-up date & time</label><input id="followupDate" type="datetime-local"></div><button id="saveLead" class="btn btn-primary">Save changes</button></div></div>
    <div class="detail-section"><h3>Draft a follow-up (not automatically sent)</h3><div class="row-controls"><div><label for="draftTone">Tone</label><select id="draftTone"><option value="professional">Professional</option><option value="friendly">Friendly</option></select></div><button id="templateBtn" class="btn btn-subtle">Generate template</button><button id="aiBtn" class="btn btn-primary" ${state.aiConfigured ? '' : 'disabled title="Configure OPENAI_API_KEY first"'}>Generate with AI</button></div><label id="aiConsentLabel" class="checkbox" style="margin-top:14px"><input type="checkbox" id="aiConsent"> I approve sending limited company/service context to the configured AI provider.</label><div id="draftResult" class="draft-box" hidden></div><button id="copyDraft" class="btn btn-subtle" hidden>Copy draft</button></div>
    <div class="detail-section"><h3>Activity timeline</h3><label for="activityNote">Add an internal note</label><textarea id="activityNote" rows="2" placeholder="Call summary, next steps…"></textarea><button id="addNote" class="btn btn-subtle">Save note</button><div id="activities">${data.activities.length ? data.activities.map(a => `<div class="activity">${safe(a.note)}<small>${safe(dateLabel(a.created_at))} · ${safe(a.kind)}</small></div>`).join('') : '<p class="muted">No activity yet.</p>'}</div></div><div class="detail-section"><button id="deleteLead" class="btn btn-danger">Delete this lead</button></div>`;
    if (l.next_followup_at) {
      const d = new Date(l.next_followup_at); const local = new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0,16); $('followupDate').value = local;
    }
    $('saveLead').onclick = async () => { try { const input = $('followupDate').value; await api(`/api/leads/${id}`, { method: 'PATCH', body: JSON.stringify({ status: $('detailStatus').value, next_followup_at: input ? new Date(input).toISOString() : null }) }); toast('Pipeline updated.'); await refresh(); await openDetail(id); } catch (e) { toast(e.message); } };
    $('templateBtn').onclick = () => createDraft(id, false);
    $('aiBtn').onclick = () => createDraft(id, true);
    $('addNote').onclick = async () => { const note = $('activityNote').value.trim(); if (!note) { toast('Enter a note first.'); return; } try { await api(`/api/leads/${id}/activities`, { method: 'POST', body: JSON.stringify({ note }) }); toast('Note saved.'); await openDetail(id); } catch (e) { toast(e.message); } };
    $('deleteLead').onclick = async () => { if (!confirm(`Delete the record for ${l.company}? This cannot be undone.`)) return; try { await api(`/api/leads/${id}`, { method: 'DELETE' }); toggle('detailOverlay', false); toast('Lead deleted.'); await refresh(); } catch (e) { toast(e.message); } };
    toggle('detailOverlay', true);
  } catch (e) { toast(e.message); }
}
async function createDraft(id, useAI) {
  if (useAI && !$('aiConsent').checked) { toast('Confirm external AI processing before continuing.'); return; }
  const button = $(useAI ? 'aiBtn' : 'templateBtn'); button.disabled = true;
  try {
    const result = await api(`/api/leads/${id}/draft`, { method: 'POST', body: JSON.stringify({ tone: $('draftTone').value, use_ai: useAI, confirm_external_processing: useAI && $('aiConsent').checked }) });
    $('draftResult').textContent = result.draft; $('draftResult').hidden = false; $('copyDraft').hidden = false;
    $('copyDraft').onclick = async () => { try { await navigator.clipboard.writeText(result.draft); toast('Draft copied. Review it before sending.'); } catch { toast('Clipboard unavailable. Select and copy the draft manually.'); } };
    toast(result.mode === 'ai' ? 'AI draft generated. Review before sending.' : 'Template draft generated.');
  } catch (e) { toast(e.message); } finally { button.disabled = false; }
}
initialize();
