from datetime import datetime, timedelta, timezone
from hashlib import sha256
from secrets import token_urlsafe

from passlib.hash import pbkdf2_sha256
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from src.db.models.inversor_model import Inversor
from src.db.models.sesion_inversor_model import SesionInversor
from src.utils.errors import AppError, UnauthorizedError


COOKIE_SESION = "zeno_sesion"
DURACION_SESION = timedelta(hours=8)
HASH = pbkdf2_sha256.using(rounds=600_000)
HASH_SIN_CUENTA = HASH.hash(token_urlsafe(32))


class PasswordInvalida(AppError):
    status_code = 422
    message = "La contraseña debe tener entre 8 y 128 caracteres."


def hash_password_inversor(password: str) -> str:
    if not 8 <= len(password) <= 128:
        raise PasswordInvalida()
    return HASH.hash(password)


def _hash_token(token: str) -> str:
    return sha256(token.encode()).hexdigest()


def autenticar(db: Session, nombre_cuenta: str, password: str) -> Inversor:
    if not 8 <= len(password) <= 128:
        raise UnauthorizedError("Nombre de cuenta o contraseña incorrectos.")
    inversor = db.scalar(select(Inversor).where(Inversor.nombre_cuenta == nombre_cuenta.lower()))
    password_hash = inversor.password_hash if inversor else None
    valido = HASH.verify(password, password_hash or HASH_SIN_CUENTA)
    if not valido or not password_hash or inversor is None:
        raise UnauthorizedError("Nombre de cuenta o contraseña incorrectos.")
    return inversor


def crear_sesion(db: Session, inversor_id: int, anterior: str | None) -> str:
    ahora = datetime.now(timezone.utc)
    db.execute(delete(SesionInversor).where(SesionInversor.vence <= ahora))
    if anterior:
        cerrar_sesion(db, anterior)
    token = token_urlsafe(32)
    db.add(SesionInversor(token_hash=_hash_token(token), inversor_id=inversor_id, vence=ahora + DURACION_SESION))
    return token


def cerrar_sesion(db: Session, token: str) -> None:
    db.execute(delete(SesionInversor).where(SesionInversor.token_hash == _hash_token(token)))


def inversor_de_sesion(db: Session, token: str | None) -> Inversor:
    if token:
        inversor = db.scalar(
            select(Inversor).join(SesionInversor, SesionInversor.inversor_id == Inversor.id)
            .where(SesionInversor.token_hash == _hash_token(token),
                   SesionInversor.vence > datetime.now(timezone.utc), Inversor.password_hash.is_not(None))
        )
        if inversor:
            return inversor
    raise UnauthorizedError("Iniciá sesión para continuar.")
