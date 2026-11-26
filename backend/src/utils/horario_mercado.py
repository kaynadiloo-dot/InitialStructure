from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from src.utils.errors import ConflictError

try:
    HORA_ARGENTINA = ZoneInfo("America/Argentina/Buenos_Aires")
except ZoneInfoNotFoundError:
    HORA_ARGENTINA = timezone(timedelta(hours=-3))

HORARIO = "Lunes a viernes de 11:00 a 17:00 (Argentina)"


def ahora_mercado() -> datetime:
    return datetime.now(HORA_ARGENTINA)


def mercado_abierto(ahora: datetime) -> bool:
    local = ahora.astimezone(HORA_ARGENTINA)
    return local.weekday() < 5 and time(11) <= local.time() < time(17)


def comprobar_horario(ahora: datetime) -> None:
    if not mercado_abierto(ahora):
        raise ConflictError(f"Mercado cerrado. Horario: {HORARIO}.")
