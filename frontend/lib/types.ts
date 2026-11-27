export type Perfil = "conservador" | "moderado" | "agresivo";
export type Moneda = "ARS" | "USD";
export type TipoActivo = "accion" | "cedear" | "bono";
export type TipoOrden = "compra" | "venta";
export type TipoTransferencia = "deposito" | "extraccion";

export interface InversorCrear {
  nombre: string;
  email: string;
  cuit: string;
  perfil_riesgo: Perfil;
}

export interface Inversor extends InversorCrear {
  nombre_cuenta: string;
  fecha_alta: string;
}

export interface Cuenta {
  numero_comitente: string;
  saldo_ars: string;
  saldo_usd: string;
}

export interface PerfilPanel {
  inversor: Inversor;
  cuenta: Cuenta | null;
  favoritos: number[];
}

export interface ActivoCrear {
  ticker: string;
  nombre: string;
  tipo: TipoActivo;
  moneda: Moneda;
  precio_actual: string;
  nivel_riesgo: number;
  activo: boolean;
}

export interface Activo extends ActivoCrear {
  id: number;
}

export interface Posicion {
  activo_id: number;
  cantidad: string;
  precio_promedio: string;
  activo: Activo;
  precio_actual: string;
  valor_actual: string;
  rendimiento_porcentaje: string | null;
}

export type PorMoneda = Record<Moneda, string>;

export interface Cartera {
  cuenta: Cuenta;
  posiciones: Posicion[];
  saldos_disponibles: PorMoneda;
  total_valorizado: PorMoneda;
  composicion_por_tipo: Record<Moneda, Partial<Record<TipoActivo, string>>>;
}

export interface Movimiento {
  id: number;
  tipo: TipoTransferencia | "dividendo";
  moneda: Moneda;
  monto: string;
  fecha: string;
  descripcion: string | null;
}

export interface Operacion {
  id: number;
  activo_id: number;
  tipo: TipoOrden;
  cantidad: string;
  precio_unitario: string;
  comision: string;
  total: string;
  fecha: string;
  estado: string;
  ganancia_realizada: string | null;
}

export interface Historial {
  operaciones: (Operacion & { ticker: string; moneda: Moneda })[];
  total_comisiones: PorMoneda;
}

export interface GananciaAnual {
  anio: number;
  total_por_moneda: PorMoneda;
}

export interface ResultadoMep {
  compra: Operacion;
  venta: Operacion;
  tipo_cambio: string;
  monto_ars_debitado: string;
  monto_usd_acreditado: string;
}

export interface PagoDividendo {
  moneda: Moneda;
  cuentas_acreditadas: number;
  total_pagado: string;
}

export interface Rankings {
  operados: { activo: Activo; unidades: string }[];
  favoritos: { activo: Activo; favoritos: number }[];
}
