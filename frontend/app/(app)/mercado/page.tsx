"use client";

import { useCallback, useState } from "react";
import { Enlace, EstadoCarga, Head, Tabla } from "@/components/ui";
import { useCuenta } from "@/context/SessionContext";
import { api } from "@/lib/api";
import { monedas, money, tipos } from "@/lib/format";
import type { Activo } from "@/lib/types";
import { useResource } from "@/lib/useResource";

export default function MercadoPage() {
  const { perfil, setPerfil } = useCuenta();
  const [buscar, setBuscar] = useState("");
  const [tipo, setTipo] = useState("");
  const [moneda, setMoneda] = useState("");
  const [soloFavoritos, setSoloFavoritos] = useState(false);
  const [ocupado, setOcupado] = useState<number | null>(null);
  const [aviso, setAviso] = useState("");
  const cargar = useCallback(() => api.activos({ tipo, moneda }), [tipo, moneda]);
  const recurso = useResource(cargar);

  async function favorito(activo: Activo) {
    setOcupado(activo.id);
    setAviso("");
    const quitar = perfil.favoritos.includes(activo.id);
    try {
      if (quitar) await api.quitarFavorito(activo.id);
      else await api.marcarFavorito(activo.id);
      setPerfil((actual) => actual && ({
        ...actual, favoritos: quitar ? actual.favoritos.filter((id) => id !== activo.id) : [...actual.favoritos, activo.id],
      }));
    } catch (error) {
      setAviso((error as Error).message);
    } finally {
      setOcupado(null);
    }
  }

  if (recurso.error || !recurso.data) return <EstadoCarga {...recurso} />;
  const palabra = buscar.trim().toLowerCase();
  const filtrados = recurso.data.filter((a) =>
    (!tipo || a.tipo === tipo) && (!moneda || a.moneda === moneda)
    && (!soloFavoritos || perfil.favoritos.includes(a.id))
    && `${a.ticker} ${a.nombre}`.toLowerCase().includes(palabra));

  return <>
    <Head title="Mercado" sub="Acciones, CEDEARs y bonos con precios del simulador"
      extra={<span className="pill up">Abierto 24 horas</span>} />
    <section className="card">
      <div className="inline-form panel-gap">
        <label className="field">Buscar<input type="search" placeholder="Ticker o nombre" value={buscar} onChange={(e) => setBuscar(e.target.value)} /></label>
        <label className="field">Tipo<select value={tipo} onChange={(e) => setTipo(e.target.value)}>
          <option value="">Todos</option>{Object.entries(tipos).map(([valor, etiqueta]) => <option key={valor} value={valor}>{etiqueta}</option>)}
        </select></label>
        <label className="field">Moneda<select value={moneda} onChange={(e) => setMoneda(e.target.value)}>
          <option value="">Todas</option>{monedas.map((m) => <option key={m}>{m}</option>)}
        </select></label>
        <button type="button" className="btn btn-ghost" aria-pressed={soloFavoritos} onClick={() => setSoloFavoritos(!soloFavoritos)}>Solo favoritos</button>
      </div>
      {aviso && <p className="err" role="alert">{aviso}</p>}
      <Tabla columnas={["Favorito", "Activo", "Tipo", "Precio", "Riesgo", "Estado"]} vacio="No hay activos para estos filtros."
        filas={filtrados.map((a) => {
          const marcado = perfil.favoritos.includes(a.id);
          return [
            <button type="button" key={a.id} className={`star${marcado ? " on" : ""}`} disabled={ocupado !== null}
              aria-pressed={marcado} aria-label={`${marcado ? "Quitar" : "Agregar"} ${a.ticker} de favoritos`}
              onClick={() => void favorito(a)}>{marcado ? "★" : "☆"}</button>,
            <Enlace key={a.ticker} href={`/mercado/${a.id}`}><b>{a.ticker}</b><div className="sname">{a.nombre}</div></Enlace>,
            tipos[a.tipo], money(a.precio_actual, a.moneda), a.nivel_riesgo,
            <span key="estado" className={`pill ${a.activo ? "up" : "down"}`}>{a.activo ? "Operable" : "Suspendido"}</span>,
          ];
        })} />
    </section>
  </>;
}
