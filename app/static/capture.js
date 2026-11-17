'use strict';
const form = document.querySelector('#captureForm');
const result = document.querySelector('#formResult');
form.addEventListener('submit', async (event) => {
  event.preventDefault();
  result.textContent = '';
  const button = form.querySelector('button[type=submit]');
  button.disabled = true;
  const raw = Object.fromEntries(new FormData(form).entries());
  const payload = { ...raw, consent: Boolean(form.elements.consent.checked) };
  try {
    const response = await fetch('/api/public/leads', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const body = await response.json();
    if (!response.ok) throw new Error(typeof body.detail === 'string' ? body.detail : 'Please review the fields and try again.');
    result.style.color = '#91ebcd';
    result.textContent = `Inquiry saved for this demo. Reference #${body.reference ?? 'received'}. No automatic email was sent.`;
    form.reset();
  } catch (error) {
    result.style.color = '#ffa4ad';
    result.textContent = error.message;
  } finally { button.disabled = false; }
});
