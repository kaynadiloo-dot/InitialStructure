import type { Moneda, TipoActivo } from "./types";

export const tipos: Record<TipoActivo, string> = { accion: "Acción", cedear: "CEDEAR", bono: "Bono" };
export const colores: Record<TipoActivo, string> = { accion: "#3F86C8", cedear: "#8CC4EE", bono: "#C9A227" };
export const perfiles = ["conservador", "moderado", "agresivo"] as const;
export const monedas = ["ARS", "USD"] as const;
export const comision = 0.005;
const monto = new Intl.NumberFormat("es-AR", { minimumFractionDigits: 2, maximumFractionDigits: 8 });
const unidades = new Intl.NumberFormat("es-AR", { maximumFractionDigits: 8 });
const dia = new Intl.DateTimeFormat("es-AR", { dateStyle: "short", timeStyle: "short", timeZone: "America/Argentina/Buenos_Aires" });

export const money = (n: string | number, moneda: Moneda) => (moneda === "USD" ? "US$ " : "$ ") + monto.format(Number(n));
export const num = (n: string | number) => unidades.format(Number(n));
export const fecha = (iso: string) => dia.format(new Date(iso));
export const iniciales = (nombre: string) => nombre.trim().split(/\s+/).slice(0, 2).map((parte) => parte[0]).join("").toUpperCase();
