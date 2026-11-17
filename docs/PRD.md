# Product Requirements Document (PRD)

**Product:** SPM AI Sales Agent  
**Organization:** SPManchester Private Limited  
**Release:** 0.1.0 — portfolio demo  
**Product type:** Single-team, local-first sales lead qualification system

## 1. Problem and opportunity
For digital agencies, call centres, real-estate agencies and small service businesses, new leads arrive via website, social platforms, referrals and inbound calls. Without a lightweight process, enquiries go untracked, follow-ups are inconsistent and teams struggle to prioritize genuinely promising deals.

## 2. Goal
Demonstrate a clear workflow from lead intake through prioritization, status management, a scheduled follow-up, and a human-reviewed written response. Provide real software rather than empty screenshots or marketing claims.

## 3. Target users
- **Agency owner / sales lead:** wants a concise pipeline view and priority ranking.
- **Business-development representative:** wants lead details, follow-up dates, notes and writing assistance.
- **Prospective client:** submits project details in a simple form.

## 4. Scope and acceptance criteria
| ID | Requirement | Acceptance criterion | Status |
|---|---|---|---|
| FR-01 | Admin sign-in | Unique password generated locally; incorrect password rejected | Implemented |
| FR-02 | Public inquiry intake | Required company/contact/contact method validated; persists in SQLite | Implemented |
| FR-03 | Manual lead capture | Authenticated admin can add a lead | Implemented |
| FR-04 | Scoring | Deterministic score 0–100 with factors shown | Implemented |
| FR-05 | Lead list | Search, filter, sort, 20-row UI pagination | Implemented |
| FR-06 | Pipeline progression | Update any of six pipeline states | Implemented |
| FR-07 | Follow-up planner | Store time-zone-aware date; dashboard counts due items | Implemented |
| FR-08 | Notes / activity | Add dated note; status change appears in timeline | Implemented |
| FR-09 | Draft generation | Local template works without external service | Implemented |
| FR-10 | Optional AI draft | Only when configured and with explicit user confirmation | Implemented |
| FR-11 | Export | Authenticated CSV export with spreadsheet formula injection mitigation | Implemented |
| FR-12 | Removal | Delete a lead and associated activity records | Implemented |
| FR-13 | Responsive UI | Usable at desktop/mobile widths | Implemented (manual visual QA advised) |

## 5. Non-goals (this release)
No bulk outreach, automated dispatch, native WhatsApp integration, multi-user role management, billing, tenant isolation, email verification, live ads performance integrations or predictive ML outcomes. Adding these without a real specification would misrepresent the software.

## 6. Key flows
**Lead:** enter project request → validate → store → auto-score → mark status → schedule follow-up → draft response → human reviews/copies → manually contacts prospect.

**Admin:** log in → inspect hot and due counts → search lead → review notes → update status/date → log activity.

## 7. Business rules
- Priority thresholds: `hot >= 75`, `warm >= 45`, otherwise `cold`.
- Scores combine budget (0–30), timeline (3–30), service fit (7–17), source (5–15), capped at 100.
- A follow-up is due when its UTC timestamp is in the past and status is neither `won` nor `lost`.
- Consent indicator is a user-entered record, **not** proof of a verified opt-in process.
- No message is ever sent by this demo.

## 8. Success measures for a future pilot
Track percent of captured enquiries, time to first human review, follow-up completion rate, pipeline progression, qualified-lead share and time saved drafting. The demo does **not** claim to have achieved these metrics.

## 9. Assumptions & constraints
One administrator; local SQLite; one application process; no high-availability guarantee. Currency bands in the interface are illustrative USD labels, not live exchange rates or a pricing policy. The admin password is stored in a local `.env` file, not a production identity provider.

## 10. Release criteria
Automated API tests pass, login blocks unauthenticated lead access, default config creates no external AI requests, fictional seed works, no credentials committed, and the README clearly identifies prototype status.
