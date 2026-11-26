"use client";

import { useEffect, useState, type ReactNode } from "react";
import { usePathname } from "next/navigation";
import { api } from "@/lib/api";
import { iniciales } from "@/lib/format";
import { useSession } from "@/context/SessionContext";
import { Enlace, EstadoCarga, Formulario, Marca } from "@/components/ui";
import { IcoAdmin, IcoCartera, IcoInicio, IcoMep, IcoMercado, IcoMovimientos, IcoOperaciones, IcoRankings, IcoToggle, TabCartera, TabInicio, TabMas, TabMercado } from "./icons";

const nav = [
  { href: "/", label: "Inicio", Icono: IcoInicio },
  { href: "/mercado", label: "Mercado", Icono: IcoMercado },
  { href: "/cartera", label: "Mi cartera", Icono: IcoCartera },
  { href: "/operaciones", label: "Operaciones", Icono: IcoOperaciones },
  { href: "/movimientos", label: "Movimientos", Icono: IcoMovimientos },
  { href: "/mep", label: "Dólar MEP", Icono: IcoMep },
  { href: "/rankings", label: "Rankings", Icono: IcoRankings },
  { href: "/admin", label: "Administración", Icono: IcoAdmin },
];

export default function AppShell({ children }: { children: ReactNode }) {
  const { perfil, pendiente, error, seleccionar, salir } = useSession();
  const ruta = usePathname();
  const [menu, setMenu] = useState(false);
  const [acciones, setAcciones] = useState(false);
  const [oscuro, setOscuro] = useState(false);

  useEffect(() => {
    if (!pendiente && !perfil && !error) window.location.replace("/login");
  }, [pendiente, perfil, error]);

  useEffect(() => {
    const abierto = window.localStorage.getItem("iolAula_menu") === "abierto";
    const temaOscuro = document.documentElement.dataset.theme === "dark";
    queueMicrotask(() => {
      setMenu(abierto);
      setOscuro(temaOscuro);
    });
    document.body.classList.toggle("menu-open", abierto);
    return () => document.body.classList.remove("menu-open");
  }, []);

  function alternarTema() {
    const tema = oscuro ? "light" : "dark";
    document.documentElement.dataset.theme = tema;
    window.localStorage.setItem("iolAula_tema", tema);
    setOscuro(!oscuro);
  }

  function alternarMenu() {
    document.body.classList.toggle("menu-open", !menu);
    window.localStorage.setItem("iolAula_menu", menu ? "cerrado" : "abierto");
    setMenu(!menu);
  }

  const cargar = () => window.location.reload();
  if (!perfil) return <main className="login"><EstadoCarga error={error} reload={cargar} /></main>;
  const { inversor, cuenta } = perfil;
  const activo = (href: string) => ruta === href || (href !== "/" && ruta.startsWith(href + "/"));

  return <>
    <aside className="sidebar">
      <button type="button" className="side-toggle" aria-expanded={menu} aria-label="Menú lateral" onClick={alternarMenu}>
        <IcoToggle /><span className="lbl">Zeno Investments</span>
      </button>
      <nav className="nav" aria-label="Secciones">
        {nav.map(({ href, label, Icono }) => <Enlace key={href} href={href} data-tip={label}
          aria-current={activo(href) ? "page" : undefined} aria-label={label} className={`nav-item${activo(href) ? " active" : ""}`}>
          <Icono /><span className="lbl">{label}</span>
        </Enlace>)}
      </nav>
      <div className="side-bottom">
        <div className="pp-wrap">
          <Enlace href="/perfil" className="nav-item side-profile" aria-label="Mi perfil">
            <span className="avatar">{iniciales(inversor.nombre)}</span>
            <span className="who lbl">{inversor.nombre}<small>Mi perfil</small></span>
          </Enlace>
          <div className="profile-pop">
            <button type="button" className="pp-item" onClick={alternarTema}>{oscuro ? "Modo claro" : "Modo oscuro"}</button>
            <button type="button" className="pp-item danger" onClick={salir}>Cambiar de inversor</button>
          </div>
        </div>
      </div>
    </aside>
    <main className="main"><div className="view">
      {cuenta ? children : <section className="card">
        <Marca />
        <h1>Abrí tu cuenta comitente</h1>
        <p className="muted">Tu inversor ya está registrado. Creá la cuenta para registrar fondos y operar.</p>
        <Formulario boton="Abrir cuenta" enviar={async () => {
          seleccionar(await api.abrirCuenta(inversor.id));
          return "Cuenta comitente abierta.";
        }} />
      </section>}
    </div></main>
    <nav className="tabbar" aria-label="Menú móvil">
      <Enlace href="/" className={activo("/") ? "active" : undefined} aria-label="Inicio"><TabInicio /></Enlace>
      <Enlace href="/mercado" className={activo("/mercado") ? "active" : undefined} aria-label="Mercado"><TabMercado /></Enlace>
      <button type="button" aria-label="Más secciones" aria-expanded={acciones} onClick={() => setAcciones(!acciones)}><TabMas /></button>
      <Enlace href="/cartera" className={activo("/cartera") ? "active" : undefined} aria-label="Cartera"><TabCartera /></Enlace>
      <Enlace href="/perfil" className={activo("/perfil") ? "active" : undefined} aria-label="Perfil"><span className="avatar">{iniciales(inversor.nombre)}</span></Enlace>
    </nav>
    {acciones && <>
      <button type="button" className="sheet-bg open" aria-label="Cerrar menú" onClick={() => setAcciones(false)} />
      <section className="sheet open" aria-label="Más secciones">
        <div className="grabber" /><h3>Ir a una sección</h3>
        <div className="actions-grid">
          {nav.slice(3).map(({ href, label, Icono }) => <Enlace className="action" key={href} href={href}>
            <span className="ai" style={{ background: "var(--brand2)" }}><Icono /></span>{label}
          </Enlace>)}
        </div>
      </section>
    </>}
  </>;
}
