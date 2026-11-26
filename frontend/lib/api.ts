import type {
  Activo, ActivoCrear, Cartera, GananciaAnual, Historial, Inversor, InversorCrear, Mercado, Moneda,
  Movimiento, Operacion, PagoDividendo, Perfil, PerfilPanel, Rankings, ResultadoMep, TipoOrden, TipoTransferencia,
} from "./types";

export class ApiError extends Error {
  constructor(message: string, public status: number) {
    super(message);
  }
}

async function request<T>(path: string, method = "GET", body?: unknown): Promise<T> {
  let res: Response;
  try {
    res = await fetch("/api" + path, {
      method,
      cache: "no-store",
      headers: body === undefined ? undefined : { "Content-Type": "application/json" },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch {
    throw new ApiError("No se pudo conectar con la API de inversiones.", 0);
  }
  if (res.status === 204) return undefined as T;
  const datos = await res.json().catch(() => null);
  if (!res.ok) {
    const detalle = datos?.detail;
    const campos = Array.isArray(detalle)
      ? detalle.map(({ loc, msg }) => [loc.slice(1).join("."), msg].filter(Boolean).join(" · ")).join(". ")
      : detalle;
    throw new ApiError(datos?.message || campos || `La API respondió con un error (${res.status}).`, res.status);
  }
  return datos as T;
}

function query(filtros: Record<string, string>) {
  const parametros = new URLSearchParams(Object.entries(filtros).filter(([, valor]) => valor.trim()));
  return parametros.size ? `?${parametros}` : "";
}

export const api = {
  perfil: (id: number) => request<PerfilPanel>(`/panel/inversores/${id}`),
  alta: (datos: InversorCrear) => request<PerfilPanel>("/panel/inversores", "POST", datos),
  abrirCuenta: (id: number) => request<PerfilPanel>(`/panel/inversores/${id}/cuenta`, "POST"),
  cambiarPerfil: (id: number, perfil_riesgo: Perfil) => request<Inversor>(`/inversores/${id}/perfil`, "PATCH", { perfil_riesgo }),
  mercado: () => request<Mercado>("/panel/mercado"),
  activos: (filtros: Record<string, string> = {}) => request<Activo[]>("/activos" + query(filtros)),
  activo: (id: number) => request<Activo>(`/activos/${id}`),
  crearActivo: (datos: ActivoCrear) => request<Activo>("/activos", "POST", datos),
  cambiarPrecio: (id: number, precio: string) => request<Activo>(`/activos/${id}/precio`, "PATCH", { precio }),
  actualizarActivo: ({ id, ...datos }: Activo) => request<Activo>(`/activos/${id}`, "PUT", datos),
  marcarFavorito: (inversor_id: number, activo_id: number) =>
    request("/favoritos", "POST", { inversor_id, activo_id }),
  quitarFavorito: (inversorId: number, activoId: number) =>
    request<void>(`/favoritos/${inversorId}/${activoId}`, "DELETE"),
  cartera: (id: number) => request<Cartera>(`/cuentas/${id}/cartera`),
  movimientos: (id: number) => request<Movimiento[]>(`/cuentas/${id}/movimientos`),
  historial: (id: number, filtros: Record<string, string>) => request<Historial>(`/cuentas/${id}/operaciones` + query(filtros)),
  ganancias: (id: number) => request<GananciaAnual[]>(`/cuentas/${id}/ganancias-realizadas`),
  transferir: (id: number, tipo: TipoTransferencia, moneda: Moneda, monto: string) =>
    request<Movimiento>(`/cuentas/${id}/${tipo === "deposito" ? "depositos" : "extracciones"}`, "POST", { moneda, monto }),
  operar: (id: number, activo_id: number, tipo: TipoOrden, cantidad: string) =>
    request<Operacion>(`/cuentas/${id}/${tipo === "compra" ? "compras" : "ventas"}`, "POST", { activo_id, cantidad }),
  mep: (id: number, monto_ars: string) => request<ResultadoMep>(`/cuentas/${id}/mep`, "POST", { monto_ars }),
  pagarDividendo: (activo_id: number, monto_por_unidad: string, fecha_pago: string) =>
    request<PagoDividendo>("/panel/dividendos", "POST", { activo_id, monto_por_unidad, fecha_pago }),
  rankings: () => request<Rankings>("/panel/rankings"),
};
