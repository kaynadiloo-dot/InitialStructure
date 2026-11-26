"use client";

import { Enlace, EstadoCarga, Head, Tabla } from "@/components/ui";
import { api } from "@/lib/api";
import { num } from "@/lib/format";
import { useResource } from "@/lib/useResource";

export default function RankingsPage() {
  const recurso = useResource(api.rankings);
  if (recurso.error || !recurso.data) return <EstadoCarga {...recurso} />;
  const { operados, favoritos } = recurso.data;
  return <>
    <Head title="Rankings" />
    <div className="grid g2e">
      <section className="card"><h2>Más operados en los últimos 7 días</h2>
        <Tabla columnas={["Activo", "Unidades operadas"]} vacio="Todavía no hay operaciones."
          filas={operados.map(({ activo, unidades }) => [<Enlace key={activo.id} href={`/mercado/${activo.id}`}>{activo.ticker}</Enlace>, num(unidades)])} />
      </section>
      <section className="card"><h2>Más marcados como favoritos</h2>
        <Tabla columnas={["Activo", "Favoritos"]} vacio="Todavía no hay favoritos."
          filas={favoritos.map(({ activo, favoritos }) => [<Enlace key={activo.id} href={`/mercado/${activo.id}`}>{activo.ticker}</Enlace>, num(favoritos)])} />
      </section>
    </div>
  </>;
}
