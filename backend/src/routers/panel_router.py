from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session

from src.db.connection import get_db
from src.db.models.inversor_model import Inversor
from src.dtos.activo_dto import ActivoResponseDTO
from src.dtos.dividendo_dto import CreateDividendoDTO
from src.dtos.inversor_dto import CreateInversorDTO
from src.dtos.favorito_dto import CreateFavoritoDTO
from src.dtos.movimiento_dto import MovimientoResponseDTO
from src.dtos.operacion_dto import OperacionResponseDTO
from src.dtos.panel_dto import (
    ActividadPanelDTO, CarteraPanelDTO, GananciaAnualDTO, HistorialOperacionesDTO,
    MercadoPanelDTO, MepPanelDTO, PagoPanelDTO, PerfilPanelDTO, RankingsPanelDTO,
)
from src.dtos.sesion_inversor_dto import InversorSesionDTO, PerfilSesionDTO
from src.middlewares.sesion_inversor_middleware import autorizar_ruta_inversiones, comprobar_origen, cuenta_actual, inversor_actual
from src.schemas.dividendo_schema import CreateDividendoSchema
from src.schemas.inversiones_tipos import IdPositivo
from src.schemas.inversor_schema import CredencialesInversorSchema, PerfilRiesgoSchema, RegistroInversorSchema
from src.schemas.panel_schema import FiltroOperacionesSchema, MepPanelSchema, OrdenPanelSchema, TransferenciaPanelSchema
from src.services.favorito_service import FavoritoService
from src.services.inversor_service import InversorService
from src.services.panel_service import PanelService
from src.services.sesion_inversor_service import (
    COOKIE_SESION, DURACION_SESION, autenticar, cerrar_sesion, crear_sesion, hash_password_inversor,
)
from src.utils.horario_mercado import ahora_mercado

router = APIRouter(prefix="/panel", tags=["panel de inversiones"])


@router.get("/mercado", response_model=MercadoPanelDTO)
def estado_mercado():
    return MercadoPanelDTO(abierto=True, hora_argentina=ahora_mercado(), horario="Abierto las 24 horas, todos los días")


def _guardar_cookie(request: Request, response: Response, token: str) -> None:
    response.headers["Cache-Control"] = "no-store"
    response.set_cookie(
        COOKIE_SESION, token, httponly=True, secure=request.url.scheme == "https", samesite="strict",
        path="/api", max_age=int(DURACION_SESION.total_seconds()),
    )


@router.post("/inversores", status_code=status.HTTP_201_CREATED, dependencies=[Depends(comprobar_origen)])
def alta(payload: RegistroInversorSchema, request: Request, response: Response, db: Session = Depends(get_db)) -> PerfilSesionDTO:
    clave = hash_password_inversor(payload.password.get_secret_value())
    dto = CreateInversorDTO(**payload.model_dump(exclude={"password", "nombre_cuenta"}))
    datos = PanelService(db).alta(dto, payload.nombre_cuenta, clave)
    with db.begin():
        token = crear_sesion(db, datos.inversor.id, request.cookies.get(COOKIE_SESION))
    _guardar_cookie(request, response, token)
    return PerfilSesionDTO.desde_perfil(datos, payload.nombre_cuenta)


@router.post("/sesion", dependencies=[Depends(comprobar_origen)])
def ingresar(payload: CredencialesInversorSchema, request: Request, response: Response, db: Session = Depends(get_db)) -> PerfilSesionDTO:
    with db.begin():
        usuario = autenticar(db, payload.nombre_cuenta, payload.password.get_secret_value())
        datos = PanelService(db).perfil(usuario.id)
        perfil = PerfilSesionDTO.desde_perfil(datos, usuario.nombre_cuenta)
        token = crear_sesion(db, usuario.id, request.cookies.get(COOKIE_SESION))
    _guardar_cookie(request, response, token)
    return perfil


@router.delete("/sesion", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(comprobar_origen)])
def salir(request: Request, response: Response, db: Session = Depends(get_db)):
    if token := request.cookies.get(COOKIE_SESION):
        with db.begin():
            cerrar_sesion(db, token)
    response.delete_cookie(COOKIE_SESION, path="/api", httponly=True, samesite="strict")


@router.get("/mi/perfil")
def perfil(usuario: Inversor = Depends(inversor_actual), db: Session = Depends(get_db)) -> PerfilSesionDTO:
    return PerfilSesionDTO.desde_perfil(PanelService(db).perfil(usuario.id), usuario.nombre_cuenta)


@router.patch("/mi/perfil")
def cambiar_perfil(payload: PerfilRiesgoSchema, usuario: Inversor = Depends(inversor_actual),
                    db: Session = Depends(get_db)) -> InversorSesionDTO:
    datos = InversorService(db).cambiar_perfil(usuario.id, payload.perfil_riesgo)
    return InversorSesionDTO(nombre_cuenta=usuario.nombre_cuenta, **datos.model_dump(exclude={"id"}))


@router.post("/mi/cuenta")
def abrir_cuenta(usuario: Inversor = Depends(inversor_actual), db: Session = Depends(get_db)) -> PerfilSesionDTO:
    return PerfilSesionDTO.desde_perfil(PanelService(db).abrir_cuenta(usuario.id), usuario.nombre_cuenta)


@router.post("/mi/favoritos/{activo_id}", status_code=status.HTTP_204_NO_CONTENT)
def marcar_favorito(activo_id: IdPositivo, usuario: Inversor = Depends(inversor_actual), db: Session = Depends(get_db)):
    FavoritoService(db).create(CreateFavoritoDTO(inversor_id=usuario.id, activo_id=activo_id))


@router.delete("/mi/favoritos/{activo_id}", status_code=status.HTTP_204_NO_CONTENT)
def quitar_favorito(activo_id: IdPositivo, usuario: Inversor = Depends(inversor_actual), db: Session = Depends(get_db)):
    FavoritoService(db).delete(usuario.id, activo_id)


@router.get("/activos", response_model=list[ActivoResponseDTO])
def activos(db: Session = Depends(get_db)):
    return PanelService(db).activos()


@router.get("/mi/cartera", response_model=CarteraPanelDTO, response_model_exclude={
    "cuenta": {"id", "inversor_id"}, "posiciones": {"__all__": {"cuenta_id"}},
})
def cartera(cuenta_id: int = Depends(cuenta_actual), db: Session = Depends(get_db)):
    return PanelService(db).cartera(cuenta_id)


@router.get("/mi/movimientos", response_model=list[MovimientoResponseDTO],
            response_model_exclude={"__all__": {"cuenta_id"}})
def movimientos(cuenta_id: int = Depends(cuenta_actual), db: Session = Depends(get_db)):
    return PanelService(db).movimientos(cuenta_id)


@router.post("/mi/movimientos", response_model=MovimientoResponseDTO, response_model_exclude={"cuenta_id"},
             status_code=status.HTTP_201_CREATED)
def transferir(payload: TransferenciaPanelSchema, cuenta_id: int = Depends(cuenta_actual), db: Session = Depends(get_db)):
    return PanelService(db).transferir(cuenta_id, payload.tipo, payload.moneda, payload.monto, payload.descripcion)


@router.get("/mi/operaciones", response_model=HistorialOperacionesDTO,
            response_model_exclude={"operaciones": {"__all__": {"cuenta_id"}}})
def historial(filtros: FiltroOperacionesSchema = Depends(), cuenta_id: int = Depends(cuenta_actual), db: Session = Depends(get_db)):
    return PanelService(db).historial(cuenta_id, **filtros.model_dump())


@router.post("/mi/operaciones", response_model=OperacionResponseDTO, response_model_exclude={"cuenta_id"},
             status_code=status.HTTP_201_CREATED)
def operar(payload: OrdenPanelSchema, cuenta_id: int = Depends(cuenta_actual), db: Session = Depends(get_db)):
    return PanelService(db).operar(cuenta_id, payload.activo_id, payload.tipo, payload.cantidad)


@router.get("/mi/ganancias-realizadas", response_model=list[GananciaAnualDTO])
def ganancias(cuenta_id: int = Depends(cuenta_actual), db: Session = Depends(get_db)):
    return PanelService(db).ganancias(cuenta_id)


@router.post("/mi/mep", response_model=MepPanelDTO, status_code=status.HTTP_201_CREATED,
             response_model_exclude={"compra": {"cuenta_id"}, "venta": {"cuenta_id"}})
def mep(payload: MepPanelSchema, cuenta_id: int = Depends(cuenta_actual), db: Session = Depends(get_db)):
    return PanelService(db).mep(cuenta_id, payload.monto_ars)


@router.post("/dividendos", response_model=PagoPanelDTO, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(inversor_actual)])
def pagar_dividendo(payload: CreateDividendoSchema, db: Session = Depends(get_db)):
    return PanelService(db).pagar_dividendo(CreateDividendoDTO(**payload.model_dump()))


@router.get("/rankings", response_model=RankingsPanelDTO)
def rankings(db: Session = Depends(get_db)):
    return PanelService(db).rankings()


# Conserva las rutas anteriores para clientes que ya conocen sus identificadores.
rutas_anteriores = APIRouter(dependencies=[Depends(autorizar_ruta_inversiones)], include_in_schema=False)


@rutas_anteriores.get("/inversores/{inversor_id}", response_model=PerfilPanelDTO)
def perfil_por_id(inversor_id: IdPositivo, db: Session = Depends(get_db)):
    return PanelService(db).perfil(inversor_id)


@rutas_anteriores.post("/inversores/{inversor_id}/cuenta", response_model=PerfilPanelDTO)
def abrir_cuenta_por_id(inversor_id: IdPositivo, db: Session = Depends(get_db)):
    return PanelService(db).abrir_cuenta(inversor_id)


@rutas_anteriores.get("/cuentas/{cuenta_id}/cartera", response_model=CarteraPanelDTO)
def cartera_por_id(cuenta_id: IdPositivo, db: Session = Depends(get_db)):
    return PanelService(db).cartera(cuenta_id)


@rutas_anteriores.get("/cuentas/{cuenta_id}/actividad", response_model=ActividadPanelDTO)
def actividad_por_id(cuenta_id: IdPositivo, db: Session = Depends(get_db)):
    return PanelService(db).actividad(cuenta_id)


@rutas_anteriores.post("/cuentas/{cuenta_id}/movimientos", response_model=MovimientoResponseDTO,
                       status_code=status.HTTP_201_CREATED)
def transferir_por_id(cuenta_id: IdPositivo, payload: TransferenciaPanelSchema, db: Session = Depends(get_db)):
    return PanelService(db).transferir(cuenta_id, payload.tipo, payload.moneda, payload.monto, payload.descripcion)


@rutas_anteriores.post("/cuentas/{cuenta_id}/operaciones", response_model=OperacionResponseDTO,
                       status_code=status.HTTP_201_CREATED)
def operar_por_id(cuenta_id: IdPositivo, payload: OrdenPanelSchema, db: Session = Depends(get_db)):
    return PanelService(db).operar(cuenta_id, payload.activo_id, payload.tipo, payload.cantidad)


router.include_router(rutas_anteriores)
