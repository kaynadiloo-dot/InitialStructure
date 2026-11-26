from fastapi import FastAPI
from sqlalchemy.exc import IntegrityError

from src.db.connection import Base, engine
from src.db.models.inversor_model import Inversor
from src.db.models.cuenta_model import Cuenta
from src.db.models.activo_model import Activo
from src.db.models.operacion_model import Operacion
from src.db.models.movimiento_model import Movimiento
from src.db.models.dividendo_model import Dividendo
from src.db.models.tenencia_model import Tenencia
from src.db.models.favorito_model import Favorito
from src.middlewares.error_middleware import app_error_handler
from src.middlewares.inversiones_middleware import inversiones_integrity_handler
from src.routers import (
    inversor_router,
    cuenta_router,
    activo_router,
    operacion_router,
    movimiento_router,
    dividendo_router,
    tenencia_router,
    favorito_router,
    panel_router,
)
from src.utils.errors import AppError

app = FastAPI(title="API de Inversiones")
app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(IntegrityError, inversiones_integrity_handler)

for modulo in (
    inversor_router,
    cuenta_router,
    activo_router,
    operacion_router,
    movimiento_router,
    dividendo_router,
    tenencia_router,
    favorito_router,
    panel_router,
):
    app.include_router(modulo.router, prefix="/api")


def crear_tablas() -> None:
    modelos = (Inversor, Cuenta, Activo, Operacion, Movimiento, Dividendo, Tenencia, Favorito)
    with engine.begin() as conexion:
        Base.metadata.create_all(conexion, tables=[modelo.__table__ for modelo in modelos])
        conexion.exec_driver_sql(
            "ALTER TABLE operaciones ADD COLUMN IF NOT EXISTS ganancia_realizada NUMERIC(32, 8)"
        )


if __name__ == "__main__":
    crear_tablas()
    print("Tablas de inversiones listas.")
