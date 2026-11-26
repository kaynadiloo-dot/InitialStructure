"use client";

import { useCallback } from "react";
import { Donut } from "@/components/Donut";
import { Enlace, EstadoCarga, Head, Tabla } from "@/components/ui";
import { useCuenta } from "@/context/SessionContext";
import { api } from "@/lib/api";
import { colores, monedas, money, num, tipos } from "@/lib/format";
import { useResource } from "@/lib/useResource";

export default function CarteraPage() {
  const { cuenta } = useCuenta();
  const cargar = useCallback(() => api.cartera(cuenta.id), [cuenta.id]);
  const recurso = useResource(cargar);
  if (recurso.error || !recurso.data) return <EstadoCarga {...recurso} />;
  const { posiciones, total_valorizado, composicion_por_tipo } = recurso.data;

  return <>
    <Head title="Mi cartera" sub={`Cuenta comitente ${cuenta.numero_comitente}`} />
    <div className="grid g2e panel-gap">
      {monedas.map((moneda) => {
        const partes = (["accion", "cedear", "bono"] as const).map((tipo) =>
          ({ label: tipos[tipo], value: Number(composicion_por_tipo[moneda][tipo] ?? 0), color: colores[tipo] }));
        return <section className="card" key={moneda}>
          <div className="ctitle"><h2>Composición en {moneda}</h2><b>{money(total_valorizado[moneda], moneda)}</b></div>
          <Donut parts={partes} />
        </section>;
      })}
    </div>
    <section className="card">
      <div className="ctitle"><h2>Posiciones</h2><Enlace className="btn btn-ghost btn-sm" href="/mercado">Ver mercado</Enlace></div>
      <Tabla columnas={["Activo", "Cantidad", "Precio promedio", "Precio actual", "Valor actual", "Rendimiento"]} vacio="Todavía no tenés posiciones."
        filas={posiciones.map(({ activo, cantidad, precio_promedio, precio_actual, valor_actual, rendimiento_porcentaje }) => [
          <Enlace key={activo.id} href={`/mercado/${activo.id}`}><b>{activo.ticker}</b></Enlace>, num(cantidad),
          money(precio_promedio, activo.moneda), money(precio_actual, activo.moneda),
          money(valor_actual, activo.moneda),
          rendimiento_porcentaje === null ? "—" : `${num(rendimiento_porcentaje)} %`,
        ])} />
    </section>
  </>;
}
