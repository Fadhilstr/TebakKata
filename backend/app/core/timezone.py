from datetime import datetime, date
from zoneinfo import ZoneInfo
from app.core.config import settings

JAKARTA_TZ = ZoneInfo(settings.TIMEZONE)


def get_now_jakarta() -> datetime:
    """Returns current datetime in Asia/Jakarta timezone."""
    return datetime.now(JAKARTA_TZ)


def get_today_jakarta() -> date:
    """Returns current date in Asia/Jakarta timezone."""
    return get_now_jakarta().date()
