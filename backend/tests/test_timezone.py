from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from app.core.timezone import get_now_jakarta, get_today_jakarta, JAKARTA_TZ


def test_timezone_is_asia_jakarta():
    now_jkt = get_now_jakarta()
    assert now_jkt.tzinfo == JAKARTA_TZ
    # Asia/Jakarta is UTC+7
    offset = now_jkt.utcoffset()
    assert offset == timedelta(hours=7)


def test_today_jakarta_date():
    today = get_today_jakarta()
    expected = datetime.now(JAKARTA_TZ).date()
    assert today == expected
