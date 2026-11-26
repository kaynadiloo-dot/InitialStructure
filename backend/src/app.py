from fastapi import FastAPI
from sqlalchemy.exc import IntegrityError

from src.middlewares.error_middleware import app_error_handler
from src.middlewares.inversiones_middleware import inversiones_integrity_handler
from src.routers import (
    activo_router,
    auth_router,
    conductores_router,
    cuenta_router,
    dividendo_router,
    favorito_router,
    inversor_router,
    movimiento_router,
    operacion_router,
    panel_router,
    pasajero_router,
    tenencia_router,
    user_router,
)
from src.utils.errors import AppError

app = FastAPI(title="Initial Structure API")

app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(IntegrityError, inversiones_integrity_handler)

app.include_router(user_router.router, prefix="/api")
app.include_router(auth_router.router, prefix="/api")
app.include_router(pasajero_router.router, prefix="/api")
app.include_router(conductores_router.router, prefix="/api")
app.include_router(inversor_router.router, prefix="/api")
app.include_router(cuenta_router.router, prefix="/api")
app.include_router(activo_router.router, prefix="/api")
app.include_router(operacion_router.router, prefix="/api")
app.include_router(movimiento_router.router, prefix="/api")
app.include_router(dividendo_router.router, prefix="/api")
app.include_router(tenencia_router.router, prefix="/api")
app.include_router(favorito_router.router, prefix="/api")
app.include_router(panel_router.router, prefix="/api")
# TODO: registrar product_router cuando se implemente
# app.include_router(product_router.router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}
