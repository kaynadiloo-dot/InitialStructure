from getpass import getpass

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.db.connection import SessionLocal
from src.db.models.inversor_model import Inversor
from src.schemas.inversor_schema import CredencialesInversorSchema
from src.services.sesion_inversor_service import PasswordInvalida, hash_password_inversor


def activar() -> None:
    email = input("Correo del inversor existente: ").strip().lower()
    nombre_cuenta = input("Nuevo nombre de cuenta: ")
    password = getpass("Nueva contraseña (no se muestra al escribir): ")
    if password != getpass("Repetí la contraseña (no se muestra al escribir): "):
        raise SystemExit("Las contraseñas no coinciden.")
    try:
        datos = CredencialesInversorSchema(nombre_cuenta=nombre_cuenta, password=password)
        clave = hash_password_inversor(datos.password.get_secret_value())
    except ValidationError:
        raise SystemExit("Nombre de cuenta inválido. Usá entre 3 y 32 letras, números, puntos, guiones o guiones bajos.")
    except PasswordInvalida as exc:
        raise SystemExit(exc.message)

    try:
        with SessionLocal.begin() as db:
            inversor = db.scalar(select(Inversor).where(Inversor.email == email).with_for_update())
            if inversor is None:
                raise SystemExit("No se encontró un inversor con ese correo.")
            if inversor.password_hash:
                raise SystemExit("Ese inversor ya tiene credenciales.")
            inversor.nombre_cuenta = datos.nombre_cuenta
            inversor.password_hash = clave
    except IntegrityError:
        raise SystemExit("El nombre de cuenta ya está en uso.")
    print("Credenciales asignadas.")


if __name__ == "__main__":
    activar()
