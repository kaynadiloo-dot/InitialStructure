"use client";

import { Campo, Elegir, EstadoCarga, Formulario, Head, Tabla } from "@/components/ui";
import { api } from "@/lib/api";
import { monedas, money, tipos } from "@/lib/format";
import type { Moneda, TipoActivo } from "@/lib/types";
import { useResource } from "@/lib/useResource";

export default function AdminPage() {
  const recurso = useResource(api.activos);
  if (recurso.error || !recurso.data) return <EstadoCarga {...recurso} />;
  const activos = recurso.data;
  const conDividendos = activos.filter((a) => a.tipo === "accion" || a.tipo === "cedear");

  return <>
    <Head title="Administración" sub="Catálogo, precios manuales y dividendos del simulador" />
    <div className="grid g3 panel-gap">
      <Formulario className="card" boton="Agregar activo" limpiar enviar={async (datos) => {
        const activo = await api.crearActivo({
          ticker: String(datos.get("ticker")).trim().toUpperCase(),
          nombre: String(datos.get("nombre")).trim(),
          tipo: datos.get("tipo") as TipoActivo,
          moneda: datos.get("moneda") as Moneda,
          precio_actual: String(datos.get("precio")),
          nivel_riesgo: Number(datos.get("riesgo")),
          activo: true,
        });
        recurso.reload();
        return `${activo.ticker} agregado al catálogo.`;
      }}>
        <h2>Nuevo activo</h2>
        <Campo label="Ticker" name="ticker" maxLength={20} />
        <Campo label="Nombre del activo" name="nombre" maxLength={100} />
        <Elegir label="Tipo de activo" name="tipo">{Object.entries(tipos).map(([tipo, nombre]) => <option key={tipo} value={tipo}>{nombre}</option>)}</Elegir>
        <Elegir label="Moneda del activo" name="moneda">{monedas.map((m) => <option key={m}>{m}</option>)}</Elegir>
        <Campo label="Precio inicial" name="precio" type="number" min="0.00000001" step="0.00000001" />
        <Campo label="Riesgo" name="riesgo" type="number" min="1" max="5" step="1" />
      </Formulario>
      <section className="card">
        <h2>Actualizar catálogo</h2>
        {activos.length ? <Formulario boton="Guardar cambios" enviar={async (datos) => {
          const id = Number(datos.get("activo_id"));
          const anterior = await api.activo(id);
          const modo = String(datos.get("modo"));
          const precio = String(datos.get("precio") ?? "");
          if (!modo && !precio) return "Ingresá un precio o un nuevo estado.";
          const activo = !modo
            ? await api.cambiarPrecio(id, precio)
            : await api.actualizarActivo({ ...anterior, precio_actual: precio || anterior.precio_actual, activo: modo === "activo" });
          recurso.reload();
          return `${activo.ticker} actualizado.`;
        }}>
          <Elegir label="Activo para actualizar" name="activo_id">{activos.map((a) => <option key={a.id} value={a.id}>{a.ticker}</option>)}</Elegir>
          <Campo label="Nuevo precio (opcional)" name="precio" type="number" required={false} min="0.00000001" step="0.00000001" />
          <Elegir label="Estado" name="modo" required={false}>
            <option value="">Conservar estado</option><option value="activo">Habilitar</option><option value="inactivo">Suspender</option>
          </Elegir>
        </Formulario> : <p className="muted">Agregá un activo para actualizar el catálogo.</p>}
      </section>
      <section className="card">
        <h2>Pagar dividendo</h2>
        {conDividendos.length ? <Formulario boton="Acreditar dividendo" limpiar enviar={async (datos) => {
          const pago = await api.pagarDividendo(Number(datos.get("activo_id")), String(datos.get("monto")), String(datos.get("fecha_pago")));
          const cuentas = pago.cuentas_acreditadas === 1 ? "cuenta" : "cuentas";
          return `${money(pago.total_pagado, pago.moneda)} acreditados en ${pago.cuentas_acreditadas} ${cuentas}.`;
        }}>
          <Elegir label="Activo del dividendo" name="activo_id">{conDividendos.map((a) => <option key={a.id} value={a.id}>{a.ticker}</option>)}</Elegir>
          <Campo label="Monto por unidad" name="monto" type="number" min="0.00000001" step="0.00000001" />
          <Campo label="Fecha de pago" name="fecha_pago" type="date" />
        </Formulario> : <p className="muted">Los dividendos se registran sobre acciones y CEDEARs.</p>}
      </section>
    </div>
    <section className="card">
      <Tabla columnas={["Ticker", "Nombre", "Precio actual", "Estado"]} vacio="El catálogo está vacío."
        filas={activos.map((a) => [a.ticker, a.nombre, money(a.precio_actual, a.moneda), a.activo ? "Operable" : "Suspendido"])} />
    </section>
  </>;
}
