# Quick start — zero-to-dashboard walkthrough

## Prerequisites
- Windows 10/11, macOS or Linux; Python 3.11+; internet access for initial package installation.
- Local browser (Chrome, Firefox, Edge, etc.). No paid SaaS account is required for template mode.

## Windows: simplest way
1. Extract ZIP into a normal folder, for example `Desktop/spm-ai-sales-agent`.
2. Open `start.bat` from inside the extracted folder.
3. The script creates `.venv/`, installs the Python packages and, if missing, generates `.env` with a strong random admin password. **Copy that password** from the console; don't share it.
4. Keep the console running. Open `http://127.0.0.1:8000`.
5. Log in with the password. Add a lead with the `+ Add lead` button.
6. Open that lead, adjust its status, schedule a follow-up and generate a *template* response draft.
7. Stop the local server with **Ctrl+C** in the console.

## macOS / Linux
```bash
chmod +x start.sh
./start.sh
```
If your OS cannot create a virtual environment, install the system's `python3-venv` package first.

## Sample records
Open a second terminal in the project directory and execute:

```bash
# Windows
.venv\Scripts\python.exe scripts\seed_demo.py

# macOS / Linux
.venv/bin/python scripts/seed_demo.py
```

Refresh the dashboard. The script only runs when the lead table is empty, so real and fictional data won't be mixed by accidental repeated runs. Sample records use `example.com` email addresses and names clearly marked Demo.

## View the public lead form
Go to `http://127.0.0.1:8000/capture`. The public form is enabled in the local demo. It accepts an inquiry and writes it to local SQLite. It is **not** connected to a sales inbox. To disable it, change `.env` to `PUBLIC_FORM_ENABLED=false` and restart.

## Troubleshooting
| Symptom | Likely fix |
| --- | --- |
| `python` not found | Install Python 3.11+ and enable PATH; restart terminal. |
| `No module named fastapi` | Run `python -m pip install -r requirements.txt` using the same interpreter used to launch the server. |
| Port 8000 in use | Stop the other process or run `python -m uvicorn app.main:app --port 8001`. |
| `503 Setup needed` when logging in | Run `python scripts/bootstrap.py`. Remove placeholder values in `.env` if they were added manually. |
| Forgot admin password | Stop server, back up your local `.env`, then change `ADMIN_PASSWORD` to a new long unique password and restart. Do not upload `.env`. |
| Empty dashboard | Add a manual lead or run the optional seed script. |
| AI button disabled | Set a valid `OPENAI_API_KEY` in local `.env`, restart, then explicitly confirm outbound processing before AI generation. |
| AI error | Check model access, API billing and network. Template drafting remains available. |
| Existing leads disappeared | Check `DATABASE_PATH` in `.env` and ensure you start from the project root. |

## Safety notes
- This runs on loopback (`127.0.0.1`) by default, not publicly accessible to the internet.
- `.env` and `data/` are excluded from Git; verify before publishing.
- The public form is deliberately simple and not suitable for internet exposure without extra anti-abuse controls.
