"""Environment-driven settings. Never commit your .env file."""
from dataclasses import dataclass
from pathlib import Path
import os
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / '.env')


def yes(value: str) -> bool:
    return value.lower() in ('1', 'true', 'yes', 'on')


@dataclass(frozen=True)
class Settings:
    admin_password: str = os.getenv('ADMIN_PASSWORD', '')
    secret_key: str = os.getenv('SECRET_KEY', '')
    database_path: Path = Path(os.getenv('DATABASE_PATH', str(ROOT / 'data' / 'app.db')))
    cookie_secure: bool = yes(os.getenv('COOKIE_SECURE', 'false'))
    public_form_enabled: bool = yes(os.getenv('PUBLIC_FORM_ENABLED', 'true'))
    openai_api_key: str = os.getenv('OPENAI_API_KEY', '')
    openai_model: str = os.getenv('OPENAI_MODEL', 'gpt-4.1-mini')
    app_name: str = 'SPM AI Sales Agent'
    session_seconds: int = 8 * 60 * 60


settings = Settings()
