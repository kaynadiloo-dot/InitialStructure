import type {
  Activo, ActivoCrear, Cartera, GananciaAnual, Historial, Inversor, InversorCrear, Moneda,
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
    if (res.status === 401 && path !== "/panel/mi/perfil" && typeof window !== "undefined"
      && window.location.pathname !== "/login") {
      window.location.replace("/login");
    }
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
  perfil: () => request<PerfilPanel>("/panel/mi/perfil"),
  ingresar: (nombre_cuenta: string, password: string) => request<PerfilPanel>("/panel/sesion", "POST", { nombre_cuenta, password }),
  salir: () => request<void>("/panel/sesion", "DELETE"),
  alta: (datos: InversorCrear & { nombre_cuenta: string; password: string }) =>
    request<PerfilPanel>("/panel/inversores", "POST", datos),
  abrirCuenta: () => request<PerfilPanel>("/panel/mi/cuenta", "POST"),
  cambiarPerfil: (perfil_riesgo: Perfil) => request<Inversor>("/panel/mi/perfil", "PATCH", { perfil_riesgo }),
  activos: (filtros: Record<string, string> = {}) => request<Activo[]>("/activos" + query(filtros)),
  activo: (id: number) => request<Activo>(`/activos/${id}`),
  crearActivo: (datos: ActivoCrear) => request<Activo>("/activos", "POST", datos),
  cambiarPrecio: (id: number, precio: string) => request<Activo>(`/activos/${id}/precio`, "PATCH", { precio }),
  actualizarActivo: ({ id, ...datos }: Activo) => request<Activo>(`/activos/${id}`, "PUT", datos),
  marcarFavorito: (activoId: number) => request<void>(`/panel/mi/favoritos/${activoId}`, "POST"),
  quitarFavorito: (activoId: number) => request<void>(`/panel/mi/favoritos/${activoId}`, "DELETE"),
  cartera: () => request<Cartera>("/panel/mi/cartera"),
  movimientos: () => request<Movimiento[]>("/panel/mi/movimientos"),
  historial: (filtros: Record<string, string>) => request<Historial>("/panel/mi/operaciones" + query(filtros)),
  ganancias: () => request<GananciaAnual[]>("/panel/mi/ganancias-realizadas"),
  transferir: (tipo: TipoTransferencia, moneda: Moneda, monto: string) =>
    request<Movimiento>("/panel/mi/movimientos", "POST", { tipo, moneda, monto }),
  operar: (activo_id: number, tipo: TipoOrden, cantidad: string) =>
    request<Operacion>("/panel/mi/operaciones", "POST", { tipo, activo_id, cantidad }),
  mep: (monto_ars: string) => request<ResultadoMep>("/panel/mi/mep", "POST", { monto_ars }),
  pagarDividendo: (activo_id: number, monto_por_unidad: string, fecha_pago: string) =>
    request<PagoDividendo>("/panel/dividendos", "POST", { activo_id, monto_por_unidad, fecha_pago }),
  rankings: () => request<Rankings>("/panel/rankings"),
};
