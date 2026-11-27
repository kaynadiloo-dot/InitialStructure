from fastapi import Depends, Request, Response
from fastapi.concurrency import run_in_threadpool
from pydantic import TypeAdapter, ValidationError
from sqlalchemy import select

from src.db.connection import SessionLocal
from src.db.models.cuenta_model import Cuenta
from src.db.models.inversor_model import Inversor
from src.db.models.movimiento_model import Movimiento
from src.db.models.operacion_model import Operacion
from src.schemas.inversiones_tipos import IdPositivo
from src.services.sesion_inversor_service import COOKIE_SESION, inversor_de_sesion
from src.utils.errors import ForbiddenError, NotFoundError


def comprobar_origen(request: Request) -> None:
    if request.method not in ("GET", "HEAD", "OPTIONS") and request.headers.get("sec-fetch-site") in ("cross-site", "same-site"):
        raise ForbiddenError("La solicitud debe salir del panel de Zeno.")


def cargar_inversor(request: Request) -> Inversor:
    with SessionLocal() as db:
        return inversor_de_sesion(db, request.cookies.get(COOKIE_SESION))


def inversor_actual(request: Request, response: Response, _: None = Depends(comprobar_origen)) -> Inversor:
    response.headers["Cache-Control"] = "no-store"
    return cargar_inversor(request)


def verificar_inversor(inversor_id: int, usuario: Inversor) -> None:
    if inversor_id != usuario.id:
        raise NotFoundError("Inversor no encontrado.")


def verificar_cuenta(cuenta_id: int, usuario: Inversor) -> None:
    with SessionLocal() as db:
        propietario = db.scalar(select(Cuenta.inversor_id).where(Cuenta.id == cuenta_id))
    if propietario != usuario.id:
        raise NotFoundError("Cuenta comitente no encontrada.")


def cuenta_actual(usuario: Inversor = Depends(inversor_actual)) -> int:
    with SessionLocal() as db:
        cuenta_id = db.scalar(
            select(Cuenta.id).where(Cuenta.inversor_id == usuario.id).order_by(Cuenta.id).limit(1)
        )
    if cuenta_id is None:
        raise NotFoundError("Cuenta comitente no encontrada.")
    return cuenta_id


def verificar_registro(modelo, registro_id: int, usuario: Inversor) -> None:
    with SessionLocal() as db:
        propietario = db.scalar(
            select(Cuenta.inversor_id).join(modelo, modelo.cuenta_id == Cuenta.id).where(modelo.id == registro_id)
        )
    if propietario != usuario.id:
        raise NotFoundError("Registro no encontrado.")


as_id = TypeAdapter(IdPositivo)


def _verificar_recurso(request: Request, datos: dict) -> None:
    usuario = cargar_inversor(request)
    claves = request.path_params
    controles = {"inversor_id": verificar_inversor, "cuenta_id": verificar_cuenta}
    for clave, comprobar in controles.items():
        if clave in claves:
            try:
                identificador = as_id.validate_python(claves[clave])
            except ValidationError:
                continue  # FastAPI informa el error de formato.
            comprobar(identificador, usuario)

    for clave, modelo in (("movimiento_id", Movimiento), ("operacion_id", Operacion)):
        if clave in claves:
            try:
                identificador = as_id.validate_python(claves[clave])
            except ValidationError:
                continue
            verificar_registro(modelo, identificador, usuario)

    for clave, comprobar in controles.items():
        if clave in datos:
            try:
                identificador = as_id.validate_python(datos[clave])
            except ValidationError:
                continue
            comprobar(identificador, usuario)


async def autorizar_ruta_inversiones(request: Request, response: Response) -> None:
    """Protege las rutas de inversiones que reciben identificadores explícitos."""
    comprobar_origen(request)
    recurso = request.url.path.rstrip("/")
    if request.method == "POST" and recurso == "/api/inversores":
        return
    if request.method in ("GET", "HEAD") and (recurso == "/api/activos" or recurso.startswith("/api/activos/")):
        return

    datos = {}
    if request.method in ("POST", "PUT", "PATCH") and await request.body():
        try:
            cuerpo = await request.json()
            if isinstance(cuerpo, dict):
                datos = cuerpo
        except ValueError:
            pass  # FastAPI valida el cuerpo del endpoint.
    await run_in_threadpool(_verificar_recurso, request, datos)
    response.headers["Cache-Control"] = "no-store"
