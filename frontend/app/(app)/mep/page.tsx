"use client";

import { useCallback, useState } from "react";
import { Campo, Enlace, EstadoCarga, Formulario, Head } from "@/components/ui";
import { api } from "@/lib/api";
import { money, num } from "@/lib/format";
import type { ResultadoMep } from "@/lib/types";
import { useResource } from "@/lib/useResource";

export default function MepPage() {
  const [resultado, setResultado] = useState<ResultadoMep | null>(null);
  const cargar = useCallback(() => Promise.all([
    api.cartera(), api.activos({ tipo: "bono" }),
  ]), []);
  const recurso = useResource(cargar);
  if (recurso.error || !recurso.data) return <EstadoCarga {...recurso} />;
  const [cartera, bonos] = recurso.data;
  const al30 = bonos.find((a) => a.ticker.toUpperCase() === "AL30" && a.moneda === "ARS" && a.activo);
  const al30d = bonos.find((a) => a.ticker.toUpperCase() === "AL30D" && a.moneda === "USD" && a.activo);

  return <>
    <Head title="Dólar MEP" sub="Comprá AL30 en pesos y vendelo como AL30D en dólares en una sola operación." />
    <div className="grid g2e panel-gap">
      <section className="card kpi">
        <small>Saldo en pesos</small><strong>{money(cartera.saldos_disponibles.ARS, "ARS")}</strong>
        <small>Saldo en dólares</small><strong>{money(cartera.saldos_disponibles.USD, "USD")}</strong>
        {al30 && al30d && <p>Tipo de cambio del catálogo: {money(Number(al30.precio_actual) / Number(al30d.precio_actual), "ARS")} por dólar.</p>}
      </section>
      <section className="card">
        <h2>Convertir pesos a dólares</h2>
        {!al30 || !al30d ? <p>Para operar, tienen que estar habilitados AL30 en ARS y AL30D en USD. <Enlace href="/admin">Ver catálogo</Enlace></p>
          : <Formulario boton="Convertir a dólares" limpiar enviar={async (datos) => {
            const conversion = await api.mep(String(datos.get("monto")));
            setResultado(conversion);
            recurso.reload();
            return `${money(conversion.monto_usd_acreditado, "USD")} acreditados.`;
          }}>
            <Campo label="Presupuesto en pesos" name="monto" type="number" min="0.00000001" step="0.00000001" />
          </Formulario>}
      </section>
    </div>
    {resultado && <section className="card" aria-label="Última conversión">
      <h2>Última conversión</h2>
      <dl className="profile-data">
        <dt>Pesos debitados</dt><dd>{money(resultado.monto_ars_debitado, "ARS")}</dd>
        <dt>Dólares acreditados</dt><dd>{money(resultado.monto_usd_acreditado, "USD")}</dd>
        <dt>Tipo de cambio</dt><dd>{money(resultado.tipo_cambio, "ARS")}</dd>
        <dt>Nominales</dt><dd>{num(resultado.compra.cantidad)}</dd>
      </dl>
      <Enlace href="/operaciones" className="btn btn-ghost">Ver operaciones</Enlace>
    </section>}
  </>;
}
