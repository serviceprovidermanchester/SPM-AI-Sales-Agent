# Publish this as a truthful professional GitHub portfolio demo

## Repository details
- **Name:** `spm-ai-sales-agent`
- **Suggested description:** `Local-first AI-assisted sales CRM demo: lead capture, scoring, pipeline, follow-ups, API and optional AI drafts. FastAPI + SQLite.`
- **Website:** `https://spmanchester.com`
- **Topics:** `fastapi`, `python`, `sqlite`, `crm`, `sales-automation`, `lead-scoring`, `ai-assistant`, `portfolio-project`, `business-software`
- **Visibility:** Public if you want prospects to inspect the code.

## Before publishing
1. Run app locally and verify login, create/view lead and draft flow.
2. Run `python -m pytest -q`; do not claim tests passed unless they do.
3. If desired, add **real screenshots of your running demo** with fictional data. Never invent performance charts or present company logos as actual clients.
4. Check `.gitignore` excludes `.env`, `.venv/`, `data/`, `*.db`.
5. Keep the `Portfolio transparency` notice in README.

## Git commands (new repository)

```bash
cd spm-ai-sales-agent
git init
git add .
git status                        # inspect carefully for credentials/data
git commit -m "Initial SPM AI Sales Agent portfolio demo"
git branch -M main
# Create a NEW empty public repo with the name spm-ai-sales-agent on GitHub.
git remote add origin https://github.com/YOUR_USERNAME/spm-ai-sales-agent.git
git push -u origin main
```

**Replace** `YOUR_USERNAME` with your own GitHub account/organization; do not paste placeholder URLs as if they exist. On GitHub, allow Actions to run, and describe this as an original portfolio **demo**, not a finished client deliverable.

## Suggested portfolio case-study wording
> SPManchester Private Limited created a working proof-of-concept for qualifying B2B leads and organizing sales follow-ups. The prototype includes a responsive admin dashboard, explainable scoring, a REST API, SQLite persistence and optional AI-assisted drafting. It is a demonstration build, not a deployed customer project.

## What to demonstrate live
- Open admin dashboard with fictional leads.
- Show how lead priority changes based on selected budget/timeline.
- Update a lead and schedule a follow-up.
- Generate and review a template response without using a paid API.
- Point a technical client to `/docs`, architecture and tests.
