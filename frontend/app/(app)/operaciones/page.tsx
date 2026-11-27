"use client";

import { useCallback, useState } from "react";
import { Campo, Elegir, Enlace, EstadoCarga, Head, Tabla } from "@/components/ui";
import { api } from "@/lib/api";
import { fecha, money, num } from "@/lib/format";
import { useResource } from "@/lib/useResource";

export default function OperacionesPage() {
  const [filtros, setFiltros] = useState<Record<string, string>>({});
  const cargar = useCallback(() => Promise.all([
    api.historial(filtros), api.ganancias(),
  ]), [filtros]);
  const recurso = useResource(cargar);

  return <>
    <Head title="Operaciones" sub="Historial de compras y ventas" extra={<Enlace className="btn btn-primary" href="/mercado">Ver mercado</Enlace>} />
    <section className="card panel-gap">
      <form className="inline-form panel-gap" onSubmit={(evento) => {
        evento.preventDefault();
        const valores = new FormData(evento.currentTarget);
        setFiltros(Object.fromEntries([...valores].map(([campo, valor]) => [campo, String(valor)])));
      }}>
        <Campo label="Desde" name="desde" type="date" required={false} />
        <Campo label="Hasta" name="hasta" type="date" required={false} />
        <Elegir label="Tipo" name="tipo" required={false}>
          <option value="">Todas</option><option value="compra">Compras</option><option value="venta">Ventas</option>
        </Elegir>
        <Campo label="Ticker" name="ticker" maxLength={20} required={false} />
        <button type="submit" className="btn btn-ghost">Filtrar</button>
      </form>
      {recurso.error || !recurso.data ? <EstadoCarga {...recurso} /> : <>
        <p className="muted">Comisiones del período: {money(recurso.data[0].total_comisiones.ARS, "ARS")} · {money(recurso.data[0].total_comisiones.USD, "USD")}</p>
        <Tabla columnas={["Fecha", "Activo", "Tipo", "Cantidad", "Precio", "Comisión", "Total", "Resultado"]} vacio="Sin operaciones para este filtro."
          filas={recurso.data[0].operaciones.map((orden) => [
            fecha(orden.fecha), <Enlace key={orden.id} href={`/mercado/${orden.activo_id}`}>{orden.ticker}</Enlace>,
            orden.tipo === "compra" ? "Compra" : "Venta", num(orden.cantidad),
            money(orden.precio_unitario, orden.moneda), money(orden.comision, orden.moneda),
            money(orden.total, orden.moneda),
            orden.ganancia_realizada === null ? "—" : money(orden.ganancia_realizada, orden.moneda),
          ])} />
      </>}
    </section>
    {recurso.data && <section className="card">
      <h2>Ganancias realizadas por año</h2>
      <Tabla columnas={["Año", "Pesos", "Dólares"]} vacio="Todavía no hay resultados de ventas."
        filas={recurso.data[1].map(({ anio, total_por_moneda }) => [
          anio, money(total_por_moneda.ARS, "ARS"), money(total_por_moneda.USD, "USD"),
        ])} />
    </section>}
  </>;
}
