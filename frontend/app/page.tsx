"use client";

import { useCallback } from "react";
import AppShell from "@/components/AppShell";
import { Enlace, EstadoCarga, Marca } from "@/components/ui";
import { useCuenta } from "@/context/SessionContext";
import { api } from "@/lib/api";
import { money, num } from "@/lib/format";
import { useResource } from "@/lib/useResource";

function Inicio() {
  const { perfil, cuenta } = useCuenta();
  const cargar = useCallback(() => Promise.all([api.cartera(cuenta.id), api.activos(), api.rankings()]), [cuenta.id]);
  const recurso = useResource(cargar);
  if (recurso.error || !recurso.data) return <EstadoCarga {...recurso} />;
  const [cartera, activos, ranking] = recurso.data;
  const favoritos = activos.filter((a) => perfil.favoritos.includes(a.id));

  return <>
    <div className="home-head"><Marca /><span className="pill neutral">Modo simulación</span></div>
    <section className="hero">
      <div>
        <div className="hero-label">Hola, {perfil.inversor.nombre.split(" ")[0]}. Tu saldo en pesos</div>
        <div className="hero-num">{money(cartera.cuenta.saldo_ars, "ARS")}</div>
        <div className="hero-sub">Cuenta comitente {cartera.cuenta.numero_comitente}</div>
      </div>
      <div className="card kpi"><small>Saldo en dólares</small><strong>{money(cartera.cuenta.saldo_usd, "USD")}</strong>
        <Enlace className="btn btn-primary btn-sm" href="/movimientos">Depositar o extraer</Enlace>
      </div>
    </section>
    <div className="home-grid">
      <section className="card">
        <div className="ctitle"><h2>Inversiones</h2><Enlace className="btn btn-ghost btn-sm" href="/cartera">Ver cartera</Enlace></div>
        <div className="kpi"><small>Posiciones valorizadas en ARS</small><strong>{money(cartera.total_valorizado.ARS, "ARS")}</strong><small>{cartera.posiciones.length} posiciones abiertas</small></div>
      </section>
      <section className="card">
        <div className="ctitle"><h2>Favoritos</h2><Enlace className="btn btn-ghost btn-sm" href="/mercado">Mercado</Enlace></div>
        {favoritos.length ? favoritos.slice(0, 5).map((a) => <Enlace className="home-row" key={a.id} href={`/mercado/${a.id}`}>
          <b>{a.ticker}</b><span>{money(a.precio_actual, a.moneda)}</span>
        </Enlace>) : <p className="empty">Todavía no tenés activos favoritos.</p>}
      </section>
      <section className="card">
        <div className="ctitle"><h2>Más operados esta semana</h2><Enlace className="btn btn-ghost btn-sm" href="/rankings">Rankings</Enlace></div>
        {ranking.operados.length ? ranking.operados.slice(0, 5).map(({ activo, unidades }) => <Enlace className="home-row" key={activo.id} href={`/mercado/${activo.id}`}>
          <b>{activo.ticker}</b><span>{num(unidades)} unidades</span>
        </Enlace>) : <p className="empty">Todavía no hay operaciones registradas.</p>}
      </section>
    </div>
  </>;
}

export default function Home() {
  return <AppShell><Inicio /></AppShell>;
}
