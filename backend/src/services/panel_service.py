from datetime import date, datetime, time, timedelta
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP, localcontext
from typing import Literal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.db.models.activo_model import Activo
from src.db.models.cuenta_model import Cuenta
from src.db.models.dividendo_model import Dividendo
from src.db.models.favorito_model import Favorito
from src.db.models.inversor_model import Inversor
from src.db.models.movimiento_model import Movimiento
from src.db.models.operacion_model import Operacion
from src.db.models.tenencia_model import Tenencia
from src.dtos.dividendo_dto import CreateDividendoDTO
from src.dtos.inversor_dto import CreateInversorDTO
from src.dtos.panel_dto import (
    ActividadPanelDTO, ActivoFavoritoPanelDTO, ActivoOperadoPanelDTO, CarteraPanelDTO,
    GananciaAnualDTO, HistorialOperacionesDTO, MepPanelDTO, OrdenHistorialDTO,
    PagoPanelDTO, PerfilPanelDTO, PosicionPanelDTO, RankingsPanelDTO,
)
from src.mappers.activo_mapper import to_activo_response
from src.mappers.cuenta_mapper import to_cuenta_response
from src.mappers.dividendo_mapper import to_dividendo_response
from src.mappers.inversor_mapper import to_inversor_response
from src.mappers.movimiento_mapper import to_movimiento_response
from src.mappers.operacion_mapper import to_operacion_response
from src.mappers.tenencia_mapper import to_tenencia_response
from src.utils.errors import AppError, ConflictError, NotFoundError
from src.utils.horario_mercado import HORA_ARGENTINA, ahora_mercado, comprobar_horario


COMISION = Decimal("0.005")
UNIDAD = Decimal("0.00000001")
RIESGO_MAXIMO = {"conservador": 2, "moderado": 4, "agresivo": 5}
SALDOS = {"ARS": "saldo_ars", "USD": "saldo_usd"}


def redondear(valor: Decimal) -> Decimal:
    return valor.quantize(UNIDAD, rounding=ROUND_HALF_UP)


class FiltroOperacionesError(AppError):
    status_code = 422


def liquidacion(importe: Decimal, tipo: Literal["compra", "venta"]) -> tuple[Decimal, Decimal]:
    comision = redondear(importe * COMISION)
    total = redondear(importe + comision if tipo == "compra" else importe - comision)
    if total <= 0:
        raise ConflictError("El importe es demasiado chico para ejecutar la orden.")
    return comision, total


class PanelService:
    def __init__(self, db: Session):
        self.db = db

    def _cuenta(self, cuenta_id: int, *, bloqueo: bool = False) -> Cuenta:
        cuenta = self.db.get(Cuenta, cuenta_id, with_for_update=bloqueo)
        if cuenta is None:
            raise NotFoundError("Cuenta comitente no encontrada.")
        return cuenta

    def _inversor(self, inversor_id: int, *, bloqueo: bool = False) -> Inversor:
        inversor = self.db.get(Inversor, inversor_id, with_for_update=bloqueo)
        if inversor is None:
            raise NotFoundError("Inversor no encontrado.")
        return inversor

    def _activo(self, activo_id: int) -> Activo:
        activo = self.db.get(Activo, activo_id, with_for_update=True)
        if activo is None:
            raise NotFoundError("Activo no encontrado.")
        return activo

    def _cuenta_del_inversor(self, inversor_id: int) -> Cuenta | None:
        return self.db.scalars(
            select(Cuenta).where(Cuenta.inversor_id == inversor_id).order_by(Cuenta.id).limit(1)
        ).first()

    def _abrir_cuenta(self, inversor_id: int) -> Cuenta:
        cuenta = Cuenta(inversor_id=inversor_id, numero_comitente=f"COM-{inversor_id:08d}")
        self.db.add(cuenta)
        self.db.flush()
        return cuenta

    def _perfil(self, inversor: Inversor, cuenta: Cuenta | None) -> PerfilPanelDTO:
        ids = self.db.scalars(
            select(Favorito.activo_id).where(Favorito.inversor_id == inversor.id).order_by(Favorito.activo_id)
        ).all()
        return PerfilPanelDTO(
            inversor=to_inversor_response(inversor),
            cuenta=to_cuenta_response(cuenta) if cuenta else None,
            favoritos=list(ids),
        )

    def perfil(self, inversor_id: int) -> PerfilPanelDTO:
        return self._perfil(self._inversor(inversor_id), self._cuenta_del_inversor(inversor_id))

    def alta(self, dto: CreateInversorDTO) -> PerfilPanelDTO:
        with self.db.begin():
            inversor = Inversor(**dto.model_dump())
            self.db.add(inversor)
            self.db.flush()
            return self._perfil(inversor, self._abrir_cuenta(inversor.id))

    def abrir_cuenta(self, inversor_id: int) -> PerfilPanelDTO:
        with self.db.begin():
            inversor = self._inversor(inversor_id, bloqueo=True)
            cuenta = self._cuenta_del_inversor(inversor_id) or self._abrir_cuenta(inversor_id)
            return self._perfil(inversor, cuenta)

    def activos(self, tipo: str | None = None, moneda: str | None = None):
        consulta = select(Activo).order_by(Activo.ticker)
        if tipo is not None:
            consulta = consulta.where(Activo.tipo == tipo)
        if moneda is not None:
            consulta = consulta.where(Activo.moneda == moneda)
        return [to_activo_response(activo) for activo in self.db.scalars(consulta)]

    def cartera(self, cuenta_id: int) -> CarteraPanelDTO:
        cuenta = self._cuenta(cuenta_id)
        posiciones = self.db.execute(
            select(Tenencia, Activo).join(Activo, Tenencia.activo_id == Activo.id)
            .where(Tenencia.cuenta_id == cuenta_id).order_by(Activo.ticker)
        )
        with localcontext() as contexto:
            contexto.prec = 60
            valorizadas = []
            totales = {moneda: Decimal(0) for moneda in SALDOS}
            por_tipo: dict[str, dict[str, Decimal]] = {moneda: {} for moneda in SALDOS}
            for tenencia, activo in posiciones:
                valor = redondear(tenencia.cantidad * activo.precio_actual)
                promedio = tenencia.precio_promedio
                rendimiento = redondear((activo.precio_actual / promedio - 1) * 100) if promedio else None
                valorizadas.append(PosicionPanelDTO(
                    **to_tenencia_response(tenencia).model_dump(), activo=to_activo_response(activo),
                    precio_actual=activo.precio_actual, valor_actual=valor, rendimiento_porcentaje=rendimiento,
                ))
                totales[activo.moneda] += valor
                grupos = por_tipo[activo.moneda]
                grupos[activo.tipo] = grupos.get(activo.tipo, Decimal(0)) + valor

            composicion = {
                moneda: {tipo: redondear(valor * 100 / totales[moneda]) for tipo, valor in grupos.items()}
                if totales[moneda] else {}
                for moneda, grupos in por_tipo.items()
            }
            return CarteraPanelDTO(
                cuenta=to_cuenta_response(cuenta), posiciones=valorizadas,
                saldos_disponibles={moneda: getattr(cuenta, campo) for moneda, campo in SALDOS.items()},
                total_valorizado=totales, composicion_por_tipo=composicion,
            )

    def actividad(self, cuenta_id: int) -> ActividadPanelDTO:
        operaciones = self.db.scalars(
            select(Operacion).where(Operacion.cuenta_id == cuenta_id).order_by(Operacion.fecha.desc(), Operacion.id.desc())
        ).all()
        return ActividadPanelDTO(
            operaciones=[to_operacion_response(operacion) for operacion in operaciones],
            movimientos=self.movimientos(cuenta_id),
        )

    def movimientos(self, cuenta_id: int):
        self._cuenta(cuenta_id)
        movimientos = self.db.scalars(
            select(Movimiento).where(Movimiento.cuenta_id == cuenta_id).order_by(Movimiento.fecha.desc(), Movimiento.id.desc())
        )
        return [to_movimiento_response(movimiento) for movimiento in movimientos]

    def historial(self, cuenta_id: int, desde: date | None = None, hasta: date | None = None,
                  tipo: str | None = None, ticker: str | None = None) -> HistorialOperacionesDTO:
        self._cuenta(cuenta_id)
        if desde and hasta and desde > hasta:
            raise FiltroOperacionesError("La fecha desde debe ser anterior o igual a la fecha hasta.")
        consulta = (
            select(Operacion, Activo.ticker, Activo.moneda).join(Activo, Activo.id == Operacion.activo_id)
            .where(Operacion.cuenta_id == cuenta_id).order_by(Operacion.fecha.desc(), Operacion.id.desc())
        )
        if desde:
            consulta = consulta.where(Operacion.fecha >= datetime.combine(desde, time.min, HORA_ARGENTINA))
        if hasta and hasta < date.max:
            fin = datetime.combine(hasta + timedelta(days=1), time.min, HORA_ARGENTINA)
            consulta = consulta.where(Operacion.fecha < fin)
        if tipo:
            consulta = consulta.where(Operacion.tipo == tipo)
        if ticker and ticker.strip():
            consulta = consulta.where(func.upper(Activo.ticker) == ticker.strip().upper())

        operaciones = []
        comisiones = {moneda: Decimal(0) for moneda in SALDOS}
        with localcontext() as contexto:
            contexto.prec = 60
            for operacion, nombre, moneda in self.db.execute(consulta):
                operaciones.append(OrdenHistorialDTO(
                    **to_operacion_response(operacion).model_dump(), ticker=nombre, moneda=moneda,
                ))
                comisiones[moneda] += operacion.comision
        return HistorialOperacionesDTO(operaciones=operaciones, total_comisiones=comisiones)

    def ganancias(self, cuenta_id: int) -> list[GananciaAnualDTO]:
        self._cuenta(cuenta_id)
        anio = func.extract("year", func.timezone("America/Argentina/Buenos_Aires", Operacion.fecha))
        filas = self.db.execute(
            select(anio, Activo.moneda, func.sum(Operacion.ganancia_realizada))
            .join(Activo, Activo.id == Operacion.activo_id)
            .where(Operacion.cuenta_id == cuenta_id, Operacion.tipo == "venta",
                   Operacion.estado == "ejecutada", Operacion.ganancia_realizada.is_not(None))
            .group_by(anio, Activo.moneda).order_by(anio.desc())
        )
        totales: dict[int, dict[str, Decimal]] = {}
        for ejercicio, moneda, valor in filas:
            totales.setdefault(int(ejercicio), {moneda: Decimal(0) for moneda in SALDOS})[moneda] = valor
        return [GananciaAnualDTO(anio=ejercicio, total_por_moneda=valores) for ejercicio, valores in totales.items()]

    def transferir(self, cuenta_id: int, tipo: Literal["deposito", "extraccion"], moneda: str,
                   monto: Decimal, descripcion: str | None = None):
        with self.db.begin(), localcontext() as contexto:
            contexto.prec = 60
            cuenta = self._cuenta(cuenta_id, bloqueo=True)
            campo = SALDOS[moneda]
            nuevo_saldo = getattr(cuenta, campo) + (monto if tipo == "deposito" else -monto)
            if nuevo_saldo < 0:
                raise ConflictError("Saldo insuficiente para la extracción.")
            setattr(cuenta, campo, nuevo_saldo)
            movimiento = Movimiento(
                cuenta_id=cuenta_id, tipo=tipo, moneda=moneda, monto=monto,
                descripcion=descripcion or ("Depósito" if tipo == "deposito" else "Extracción"),
            )
            self.db.add(movimiento)
            self.db.flush()
            return to_movimiento_response(movimiento)

    def _validar_riesgo(self, cuenta: Cuenta, activo: Activo) -> None:
        inversor = self._inversor(cuenta.inversor_id)
        if activo.nivel_riesgo > RIESGO_MAXIMO[inversor.perfil_riesgo]:
            raise ConflictError("El riesgo del activo supera el límite de tu perfil.")

    def _registrar_operacion(
        self, cuenta: Cuenta, activo: Activo, tipo: Literal["compra", "venta"], cantidad: Decimal,
        comision: Decimal, total: Decimal, fecha: datetime, ganancia: Decimal | None = None,
    ) -> Operacion:
        operacion = Operacion(
            cuenta_id=cuenta.id, activo_id=activo.id, tipo=tipo, cantidad=cantidad,
            precio_unitario=activo.precio_actual, comision=comision, total=total,
            estado="ejecutada", fecha=fecha, ganancia_realizada=ganancia,
        )
        self.db.add(operacion)
        self.db.flush()
        return operacion

    def operar(self, cuenta_id: int, activo_id: int, tipo: Literal["compra", "venta"], cantidad: Decimal):
        with self.db.begin(), localcontext() as contexto:
            contexto.prec = 60
            activo = self._activo(activo_id)
            cuenta = self._cuenta(cuenta_id, bloqueo=True)
            ahora = ahora_mercado()
            comprobar_horario(ahora)
            if not activo.activo:
                raise ConflictError("El activo está suspendido.")
            campo = SALDOS.get(activo.moneda)
            if campo is None:
                raise ConflictError("La moneda de este activo no está habilitada.")
            tenencia = self.db.get(Tenencia, (cuenta_id, activo_id), with_for_update=True)
            importe = cantidad * activo.precio_actual
            comision, total = liquidacion(importe, tipo)

            saldo = getattr(cuenta, campo)
            ganancia = None
            if tipo == "compra":
                self._validar_riesgo(cuenta, activo)
                if saldo < total:
                    raise ConflictError("Saldo insuficiente para la compra.")
                if tenencia is None:
                    self.db.add(Tenencia(cuenta_id=cuenta_id, activo_id=activo_id, cantidad=cantidad,
                                         precio_promedio=activo.precio_actual))
                else:
                    unidades = tenencia.cantidad + cantidad
                    tenencia.precio_promedio = redondear(
                        (tenencia.cantidad * tenencia.precio_promedio + importe) / unidades
                    )
                    tenencia.cantidad = unidades
                setattr(cuenta, campo, saldo - total)
            else:
                if tenencia is None or tenencia.cantidad < cantidad:
                    raise ConflictError("No tenés suficientes unidades para vender.")
                ganancia = redondear(total - cantidad * tenencia.precio_promedio)
                tenencia.cantidad -= cantidad
                if tenencia.cantidad == 0:
                    self.db.delete(tenencia)
                setattr(cuenta, campo, saldo + total)

            return to_operacion_response(
                self._registrar_operacion(cuenta, activo, tipo, cantidad, comision, total, ahora, ganancia)
            )

    def mep(self, cuenta_id: int, monto_ars: Decimal) -> MepPanelDTO:
        with self.db.begin(), localcontext() as contexto:
            contexto.prec = 60
            bonos = {bono.ticker.upper(): bono for bono in self.db.scalars(
                select(Activo).where(func.upper(Activo.ticker).in_(("AL30", "AL30D")))
                .order_by(Activo.id).with_for_update()
            )}
            al30 = bonos.get("AL30")
            al30d = bonos.get("AL30D")
            if (al30 is None or al30d is None or al30.tipo != "bono" or al30d.tipo != "bono"
                    or al30.moneda != "ARS" or al30d.moneda != "USD"):
                raise ConflictError("El catálogo debe incluir AL30 en pesos y AL30D en dólares.")
            cuenta = self._cuenta(cuenta_id, bloqueo=True)
            ahora = ahora_mercado()
            comprobar_horario(ahora)
            if not al30.activo or not al30d.activo:
                raise ConflictError("AL30 y AL30D deben estar habilitados para operar.")
            self._validar_riesgo(cuenta, al30)
            if cuenta.saldo_ars < monto_ars:
                raise ConflictError("Saldo en pesos insuficiente para el monto solicitado.")

            cantidad = (monto_ars / (al30.precio_actual * (1 + COMISION))).quantize(UNIDAD, rounding=ROUND_DOWN)
            if not cantidad:
                raise ConflictError("El monto no alcanza para comprar la cantidad mínima.")
            comision_ars, debito = liquidacion(cantidad * al30.precio_actual, "compra")
            if debito > monto_ars:
                cantidad -= UNIDAD
                comision_ars, debito = liquidacion(cantidad * al30.precio_actual, "compra")
            comision_usd, credito = liquidacion(cantidad * al30d.precio_actual, "venta")

            cuenta.saldo_ars -= debito
            cuenta.saldo_usd += credito
            compra = self._registrar_operacion(cuenta, al30, "compra", cantidad, comision_ars, debito, ahora)
            venta = self._registrar_operacion(cuenta, al30d, "venta", cantidad, comision_usd, credito, ahora)
            return MepPanelDTO(
                compra=to_operacion_response(compra), venta=to_operacion_response(venta),
                tipo_cambio=redondear(al30.precio_actual / al30d.precio_actual),
                monto_ars_debitado=debito, monto_usd_acreditado=credito,
            )

    def pagar_dividendo(self, dto: CreateDividendoDTO) -> PagoPanelDTO:
        with self.db.begin(), localcontext() as contexto:
            contexto.prec = 60
            activo = self._activo(dto.activo_id)
            if activo.tipo not in ("accion", "cedear") or activo.moneda not in SALDOS:
                raise ConflictError("El activo no admite dividendos.")
            registrado = self.db.scalar(
                select(Dividendo.id).where(Dividendo.activo_id == activo.id, Dividendo.fecha_pago == dto.fecha_pago).limit(1)
            )
            if registrado is not None:
                raise ConflictError("Ya hay un dividendo registrado para este activo y fecha.")
            dividendo = Dividendo(**dto.model_dump())
            self.db.add(dividendo)
            cuentas = self.db.execute(
                select(Cuenta, Tenencia.cantidad).join(Tenencia, Tenencia.cuenta_id == Cuenta.id)
                .where(Tenencia.activo_id == activo.id).order_by(Cuenta.id).with_for_update(of=Cuenta)
            )
            total = Decimal("0")
            acreditadas = 0
            campo = SALDOS[activo.moneda]
            for cuenta, cantidad in cuentas:
                monto = redondear(cantidad * dto.monto_por_unidad)
                if monto <= 0:
                    continue
                setattr(cuenta, campo, getattr(cuenta, campo) + monto)
                self.db.add(Movimiento(cuenta_id=cuenta.id, tipo="dividendo", moneda=activo.moneda, monto=monto,
                                       descripcion=f"Dividendo de {activo.ticker} ({dto.fecha_pago})"))
                total += monto
                acreditadas += 1
            self.db.flush()
            return PagoPanelDTO(dividendo=to_dividendo_response(dividendo), moneda=activo.moneda,
                                cuentas_acreditadas=acreditadas, total_pagado=total)

    def mas_operados(self) -> list[ActivoOperadoPanelDTO]:
        ahora = ahora_mercado()
        desde = ahora - timedelta(days=7)
        unidades = func.sum(Operacion.cantidad)
        operados = self.db.execute(
            select(Activo, unidades).join(Operacion, Operacion.activo_id == Activo.id)
            .where(Operacion.fecha.between(desde, ahora), Operacion.estado == "ejecutada").group_by(Activo.id)
            .order_by(unidades.desc(), Activo.ticker).limit(10)
        )
        return [ActivoOperadoPanelDTO(activo=to_activo_response(activo), unidades=n) for activo, n in operados]

    def mas_favoritos(self) -> list[ActivoFavoritoPanelDTO]:
        cantidad = func.count(Favorito.activo_id)
        favoritos = self.db.execute(
            select(Activo, cantidad).join(Favorito, Favorito.activo_id == Activo.id)
            .group_by(Activo.id).order_by(cantidad.desc(), Activo.ticker).limit(10)
        )
        return [ActivoFavoritoPanelDTO(activo=to_activo_response(activo), favoritos=n) for activo, n in favoritos]

    def rankings(self) -> RankingsPanelDTO:
        return RankingsPanelDTO(
            operados=self.mas_operados(), favoritos=self.mas_favoritos(),
        )
