from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

try:
    HORA_ARGENTINA = ZoneInfo("America/Argentina/Buenos_Aires")
except ZoneInfoNotFoundError:
    HORA_ARGENTINA = timezone(timedelta(hours=-3))

def ahora_mercado() -> datetime:
    return datetime.now(HORA_ARGENTINA)
