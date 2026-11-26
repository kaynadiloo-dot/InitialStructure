"use client";

import { useCallback } from "react";
import { Campo, Elegir, EstadoCarga, Formulario, Head, Tabla } from "@/components/ui";
import { useCuenta } from "@/context/SessionContext";
import { api } from "@/lib/api";
import { fecha, monedas, money } from "@/lib/format";
import type { Moneda, TipoTransferencia } from "@/lib/types";
import { useResource } from "@/lib/useResource";

const nombres = { deposito: "Depósito", extraccion: "Extracción", dividendo: "Dividendo" };

export default function MovimientosPage() {
  const { cuenta } = useCuenta();
  const cargar = useCallback(() => Promise.all([api.cartera(cuenta.id), api.movimientos(cuenta.id)]), [cuenta.id]);
  const recurso = useResource(cargar);
  if (recurso.error || !recurso.data) return <EstadoCarga {...recurso} />;
  const [cartera, movimientos] = recurso.data;

  return <>
    <Head title="Movimientos" sub="Depósitos, extracciones y dividendos" />
    <div className="grid g3 panel-gap">
      <div className="card kpi"><small>Saldo en pesos</small><strong>{money(cartera.cuenta.saldo_ars, "ARS")}</strong></div>
      <div className="card kpi"><small>Saldo en dólares</small><strong>{money(cartera.cuenta.saldo_usd, "USD")}</strong></div>
      <Formulario className="card" boton="Confirmar movimiento" limpiar enviar={async (datos) => {
        const mov = await api.transferir(cuenta.id, datos.get("tipo") as TipoTransferencia,
          datos.get("moneda") as Moneda, String(datos.get("monto")));
        recurso.reload();
        return `${nombres[mov.tipo]} por ${money(mov.monto, mov.moneda)} confirmado.`;
      }}>
        <div className="inline-form panel-gap">
          <Elegir label="Tipo" name="tipo"><option value="deposito">Depositar</option><option value="extraccion">Extraer</option></Elegir>
          <Elegir label="Moneda" name="moneda">{monedas.map((m) => <option key={m}>{m}</option>)}</Elegir>
          <Campo label="Monto" name="monto" type="number" min="0.00000001" step="0.00000001" />
        </div>
      </Formulario>
    </div>
    <section className="card">
      <Tabla columnas={["Fecha", "Tipo", "Detalle", "Monto"]} vacio="Todavía no hay movimientos."
        filas={movimientos.map((m) => [fecha(m.fecha), nombres[m.tipo], m.descripcion || "—",
          <b key={m.id} className={m.tipo === "extraccion" ? "down" : "up"}>
            {m.tipo === "extraccion" ? "−" : "+"}{money(m.monto, m.moneda)}
          </b>])} />
    </section>
  </>;
}
