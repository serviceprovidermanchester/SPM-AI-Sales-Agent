# REST API reference (v0.1.0)

Base URL: `http://127.0.0.1:8000`  
Interactive browser specification: `/docs` and OpenAPI JSON: `/openapi.json`.

## Authentication model
Login returns a signed HttpOnly cookie and CSRF token in JSON. All private endpoints require the cookie; all private **writes** also require `X-CSRF-Token` header. Normal browser JS sends cookies automatically. API examples below use `curl` with a cookie jar.

```bash
curl -c cookies.txt -H 'Content-Type: application/json' \
  -d '{"password":"REPLACE_WITH_YOUR_LOCAL_PASSWORD"}' \
  http://127.0.0.1:8000/api/auth/login
# Response: {"authenticated":true,"csrf":"..."}
# Save the returned csrf token as $CSRF for protected POST/PATCH/DELETE requests.
```

| HTTP method | Route | Access | Purpose |
| --- | --- | --- | --- |
| GET | `/api/health` | Public | Returns app health and version |
| POST | `/api/auth/login` | Public, rate-limited | Start admin session |
| GET | `/api/auth/me` | Admin | Return auth state, CSRF token and enabled features |
| POST | `/api/auth/logout` | Admin + CSRF | Clear session cookie |
| POST | `/api/public/leads` | Public, if enabled | Submit a demo inquiry |
| GET | `/api/dashboard` | Admin | KPI counts, most recent leads |
| GET | `/api/leads` | Admin | Search and filter leads |
| POST | `/api/leads` | Admin + CSRF | Create/score a lead |
| GET | `/api/leads/export` | Admin | Download CSV (auth required) |
| GET | `/api/leads/{id}` | Admin | Lead details, score factors, activity timeline |
| PATCH | `/api/leads/{id}` | Admin + CSRF | Update status and follow-up |
| POST | `/api/leads/{id}/activities` | Admin + CSRF | Add private note |
| POST | `/api/leads/{id}/draft` | Admin + CSRF | Create local template or opt-in AI draft |
| DELETE | `/api/leads/{id}` | Admin + CSRF | Permanently delete lead and activity |

## Lead creation payload

```json
{
  "company": "Demo Riverside Traders",
  "contact": "Demo Contact",
  "email": "demo-contact@example.com",
  "phone": "",
  "service_interest": "ecommerce",
  "budget_range": "5000-15000",
  "timeline": "30-days",
  "source": "referral",
  "message": "Fictional example enquiry",
  "consent": false
}
```

Enums:
- `service_interest`: `website | ecommerce | seo | paid-ads | ai-automation | crm | other`
- `budget_range`: `unknown | under-1000 | 1000-5000 | 5000-15000 | 15000-plus`
- `timeline`: `researching | 90-days | 30-days | immediate`
- `source`: `website | referral | linkedin | campaign | other`
- `status`: `new | contacted | qualified | proposal | won | lost`

At least one contact method (`email` or `phone`) is required. Consent default is false. `website_url` is a hidden honeypot field used only by the public form.

## List leads
`GET /api/leads?q=traders&status=new&priority=hot&limit=20&offset=0`

Example response:

```json
{"total":1,"items":[{"id":1,"company":"Demo Riverside Traders","contact":"Demo Contact","email":"demo-contact@example.com","phone":"","service_interest":"ecommerce","budget_range":"5000-15000","timeline":"30-days","source":"referral","message":"Fictional example enquiry","consent":false,"status":"new","score":72,"priority":"warm","next_followup_at":null,"created_at":"2026-11-04T00:00:00+00:00","updated_at":"2026-11-04T00:00:00+00:00"}]}
```

**Illustrative result**: example timestamps are not a live response. The score above is calculated as 22 + 21 + 14 + 15 = 72.

## Update a lead

```http
PATCH /api/leads/1
X-CSRF-Token: <token>
Content-Type: application/json

{"status":"contacted","next_followup_at":"2026-11-10T09:00:00+00:00"}
```

`next_followup_at` must include timezone information. A null clears it.

## Draft request

```json
{"tone":"professional","use_ai":false,"confirm_external_processing":false}
```

Set `use_ai=true` and `confirm_external_processing=true` to call the configured AI provider. AI requests are **not** performed otherwise. Returned payload: `{"mode":"template"|"ai","draft":"Subject: ..."}`. Templates work without any API key. A generated draft is not sent.

## HTTP errors
`400` missing AI configuration, `401` unauthenticated, `403` invalid CSRF or disabled public intake, `404` missing lead, `422` invalid input or missing external-processing confirmation, `429` rate-limited, `502` AI provider unavailable, `503` initial setup not completed.

## Privacy/security notes
Do not publish cookie jar files or API secrets. The API is intended for loopback demonstration. See `SECURITY.md` before exposing it publicly.
