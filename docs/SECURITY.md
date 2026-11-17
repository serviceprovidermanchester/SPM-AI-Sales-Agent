# Security, privacy and responsible demo usage

**Security status: portfolio prototype. Not security audited or ready for live internet customer data.**

## Controls included
- Local bootstrap generates a random admin password and signing secret into ignored `.env`.
- Signed HttpOnly session cookie, SameSite=Strict, configurable `COOKIE_SECURE`.
- CSRF token required for protected writes.
- Input validation with explicit string bounds and email validation.
- Parameterized SQL and foreign-key enforcement.
- Per-process rate limits for login and public submissions; basic honeypot.
- CSV data escaped for likely spreadsheet formula prefixes.
- Browser UI escapes untrusted strings to avoid HTML injection.
- AI drafts are triggered manually; direct identifiers excluded from provider prompts.
- `.gitignore` excludes secrets, environments and local database files.

## Known risks and limitations
1. **One password, plaintext local configuration:** acceptable for local demo; replace with production identity controls, hashed stored credentials, rotation and MFA for real deployments.
2. **No distributed abuse control:** in-memory rate limiting resets on restart and does not work across processes. Use reverse-proxy/WAF limits and spam protection for any internet-facing capture form.
3. **Public intake by default:** disable with `PUBLIC_FORM_ENABLED=false` until proper spam prevention, privacy notice and consent handling are deployed.
4. **No tenant isolation or granular permissions:** never deploy as a multi-customer hosted CRM without redesigning authorization and data isolation.
5. **Transport safety:** production exposure needs HTTPS, trusted reverse proxy, `COOKIE_SECURE=true`, HSTS and secret management.
6. **No automated backup/restore or retention controls:** implement encrypted backups, restore drills, retention and erasure workflow before handling sensitive data.
7. **AI output uncertainty:** generated text may be wrong or misleading. Explicit confirmation is required for external processing, but customer consent/legal basis must be managed separately. Human review before sending is compulsory.
8. **No compliance certification:** this code does not claim GDPR, UK GDPR, PECR, ISO 27001, SOC 2 or HIPAA compliance.
9. **Proxy headers and client identity:** rate limits read the request client address; do not assume that it is a reliable source when behind an improperly configured proxy.
10. **Exported data:** CSV files leave app controls; protect them with access restrictions and appropriate retention.

## Priorities before production
Security review, threat modeling, MFA/SSO, secrets vault, TLS reverse proxy, robust audit logs, CSRF/xss review, centralized throttling, webhook verification, testable backups, monitoring, least-privilege DB, data retention and a lawful privacy notice.

## Safe GitHub publishing checklist
- Inspect `git status` for `.env`, `.db`, personal records and secret tokens before pushing.
- Never paste API keys into issues, screenshots or README examples.
- Leave public demo screenshots populated only with fictional `example.com` data.
- Run tests; use dependency scanning and secret scanning in the remote repository.
- If credentials are accidentally published, revoke/rotate them; deleting a commit alone is not sufficient.
