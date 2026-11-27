"use client";

import { useCallback } from "react";
import { useParams } from "next/navigation";
import { Campo, Elegir, Enlace, EstadoCarga, Formulario, Head } from "@/components/ui";
import { api } from "@/lib/api";
import { comision, money, num, tipos } from "@/lib/format";
import type { TipoOrden } from "@/lib/types";
import { useResource } from "@/lib/useResource";

export default function ActivoPage() {
  const { id } = useParams<{ id: string }>();
  const cargar = useCallback(() => Promise.all([api.activo(Number(id)), api.cartera()]), [id]);
  const recurso = useResource(cargar);
  if (recurso.error || !recurso.data) return <EstadoCarga {...recurso} />;
  const [activo, cartera] = recurso.data;
  const posicion = cartera.posiciones.find((p) => p.activo_id === activo.id);
  const saldo = activo.moneda === "ARS" ? cartera.cuenta.saldo_ars : cartera.cuenta.saldo_usd;

  return <>
    <Head title={activo.ticker} sub={activo.nombre} extra={<Enlace className="btn btn-ghost" href="/mercado">Volver al mercado</Enlace>} />
    <div className="grid g2e">
      <section className="card kpi">
        <small>{tipos[activo.tipo]} · Precio del catálogo</small>
        <strong>{money(activo.precio_actual, activo.moneda)}</strong>
        <p>Riesgo {activo.nivel_riesgo} de 5</p>
        <p>Saldo disponible {money(saldo, activo.moneda)}</p>
        <p>En cartera {num(posicion?.cantidad ?? 0)} unidades</p>
      </section>
      <section className="card">
        <h2>Compra y venta</h2>
        {activo.activo ? <>
          <p className="muted">Comisión del {num(comision * 100)} % sobre el importe.</p>
          <Formulario boton="Ejecutar orden" limpiar enviar={async (datos) => {
            const tipo = datos.get("tipo") as TipoOrden;
            const orden = await api.operar(activo.id, tipo, String(datos.get("cantidad")));
            recurso.reload();
            return `${tipo === "compra" ? "Compra" : "Venta"} ejecutada por ${money(orden.total, activo.moneda)}.`;
          }}>
            <Elegir label="Operación" name="tipo"><option value="compra">Comprar</option><option value="venta">Vender</option></Elegir>
            <Campo label="Cantidad" name="cantidad" type="number" min="0.00000001" step="0.00000001" />
          </Formulario>
        </> : <p className="empty">Este activo está suspendido.</p>}
      </section>
    </div>
  </>;
}
