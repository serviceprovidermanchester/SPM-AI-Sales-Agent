# Run, package and deployment notes

## Supported demonstration methods
**Local Python:** recommended for portfolio viewing. `start.bat` / `start.sh` bind on `127.0.0.1:8000` by default.

**Docker Compose:** if Docker Desktop or Docker Engine is installed:

```bash
python scripts/bootstrap.py  # once, creates ignored .env
# optional: python scripts/seed_demo.py (requires local Python dependencies)
docker compose up --build
```

The compose file binds to **127.0.0.1:8000**, not all network interfaces. SQLite is stored via the mounted `./data:/workspace/data` volume. Stop with `docker compose down`; the local `data/` folder persists.

**Manual command:**

```bash
python -m pip install -r requirements.txt
python scripts/bootstrap.py
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## Configuration variables
| Variable | Meaning | Default |
|---|---|---|
| `ADMIN_PASSWORD` | Unique local administrator credential | blank; bootstrap generates |
| `SECRET_KEY` | Cookie-signing secret | blank; bootstrap generates |
| `DATABASE_PATH` | SQLite file path | `data/app.db` |
| `COOKIE_SECURE` | Restrict cookies to HTTPS connections | `false` for loopback |
| `PUBLIC_FORM_ENABLED` | Allow public form submissions | `true` for local demo |
| `OPENAI_API_KEY` | Optional paid AI service key | blank |
| `OPENAI_MODEL` | AI model ID accessible on account | `gpt-4.1-mini` |

**Important:** `.env.example` is a template only. Run bootstrap, not `cp .env.example .env`, to avoid placeholder secrets.

## Hosting restrictions
Many shared hosting packages do not support a continuously running FastAPI application; verify Python/ASGI support first. A VPS, a container host or a Python-compatible platform is required for hosted deployment. No remote deployment has been tested or completed for this demonstration.

## Production hardening checklist
- Add HTTPS / TLS termination and set `COOKIE_SECURE=true`.
- Replace demo password model with secure identity management and role access.
- Protect or disable the public capture form; add rate limiting at the edge and bot protection.
- Add monitoring, structured logs, backup, recovery, failover and data retention.
- Use a managed relational database and schema migrations when concurrent traffic grows.
- Validate full data-privacy and marketing consent requirements for the target jurisdiction.
- Penetration test and load test before asserting production readiness.

## Backup / restore (demo only)
Stop the server, then copy `data/app.db` to a safe private location. Restore while stopped by replacing the DB file. This is not a substitute for managed production backup automation.
