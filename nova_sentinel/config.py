from __future__ import annotations

from dataclasses import dataclass
import os
from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    poll_minutes: int = 10
    min_alert_score: int = 45
    max_galactic_latitude: float = 20.0
    max_alert_magnitude: float = 18.0
    database_path: str = "nova_sentinel.db"
    jsonl_path: str = "alerts.jsonl"
    atom_path: str = "feed.xml"
    timeout: float = 30.0
    user_agent: str = "NovaSentinel/0.1"
    tns_bot_id: str = ""
    tns_bot_name: str = ""
    tns_api_key: str = ""
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    webhook_url: str = ""

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        return cls(
            poll_minutes=int(os.getenv("POLL_MINUTES", "10")),
            min_alert_score=int(os.getenv("MIN_ALERT_SCORE", "45")),
            max_galactic_latitude=float(os.getenv("MAX_GALACTIC_LATITUDE", "20")),
            max_alert_magnitude=float(os.getenv("MAX_ALERT_MAGNITUDE", "18")),
            database_path=os.getenv("DATABASE_PATH", "nova_sentinel.db"),
            jsonl_path=os.getenv("JSONL_PATH", "alerts.jsonl"),
            atom_path=os.getenv("ATOM_PATH", "feed.xml"),
            timeout=float(os.getenv("HTTP_TIMEOUT_SECONDS", "30")),
            user_agent=os.getenv("USER_AGENT", "NovaSentinel/0.1"),
            tns_bot_id=os.getenv("TNS_BOT_ID", ""),
            tns_bot_name=os.getenv("TNS_BOT_NAME", ""),
            tns_api_key=os.getenv("TNS_API_KEY", ""),
            telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
            telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID", ""),
            webhook_url=os.getenv("WEBHOOK_URL", ""),
        )
