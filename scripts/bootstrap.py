"""Generate local-only, strong credentials without placing secrets in the Git repo."""
from pathlib import Path
import secrets

ROOT = Path(__file__).resolve().parents[1]
target = ROOT / '.env'
if target.exists():
    print('Configuration already exists at .env; nothing overwritten.')
    raise SystemExit(0)
password = secrets.token_urlsafe(18)
secret = secrets.token_urlsafe(48)
content = (f'ADMIN_PASSWORD={password}\nSECRET_KEY={secret}\n'
           'DATABASE_PATH=data/app.db\nCOOKIE_SECURE=false\n'
           'PUBLIC_FORM_ENABLED=true\nOPENAI_API_KEY=\nOPENAI_MODEL=gpt-4.1-mini\n')
with target.open('x', encoding='utf-8') as f:
    f.write(content)
try:
    target.chmod(0o600)
except OSError:
    pass
print('\n=== SPManchester Sales Agent - Local Setup ===')
print(f'Admin password: {password}')
print('Save this password securely. It is also stored in your local, git-ignored .env.')
print('Next step: run start.bat (Windows) or ./start.sh (Mac/Linux).')
