"use client";

import { useState } from "react";
import { Campo, Elegir, Formulario, Marca } from "@/components/ui";
import { useSession } from "@/context/SessionContext";
import { api } from "@/lib/api";
import { perfiles } from "@/lib/format";
import type { Perfil } from "@/lib/types";

export default function LoginPage() {
  const [alta, setAlta] = useState(false);
  const { seleccionar } = useSession();

  return <main className="login">
    <div className="login-bg" aria-hidden="true"><div className="login-grid" /><div className="login-glow g1" /><div className="login-glow g2" /></div>
    <div className="login-main">
      <header className="login-brand"><Marca /></header>
      <section className="login-card">
        <div className="tabs">
          <button type="button" className={alta ? "tab" : "tab active"} aria-pressed={!alta} onClick={() => setAlta(false)}>Seleccionar inversor</button>
          <button type="button" className={alta ? "tab active" : "tab"} aria-pressed={alta} onClick={() => setAlta(true)}>Crear cuenta</button>
        </div>
        <h1>{alta ? "Abrí tu cuenta" : "Bienvenido a Zeno"}</h1>
        <p className="login-sub">{alta ? "Creá tu inversor y su cuenta comitente." : "Ingresá el ID de inversor para acceder al simulador."}</p>
        <Formulario key={String(alta)} boton={alta ? "Crear cuenta comitente" : "Abrir panel"} enviar={async (datos) => {
          const perfil = alta ? await api.alta({
            nombre: String(datos.get("nombre")).trim(),
            email: String(datos.get("email")).trim(),
            cuit: String(datos.get("cuit")).trim(),
            perfil_riesgo: datos.get("perfil_riesgo") as Perfil,
          }) : await api.perfil(Number(datos.get("inversor_id")));
          seleccionar(perfil);
          window.location.assign("/");
          return "Cuenta seleccionada.";
        }}>
          {alta ? <>
            <Campo label="Nombre completo" name="nombre" maxLength={100} autoComplete="name" />
            <Campo label="Correo electrónico" name="email" type="email" autoComplete="email" />
            <Campo label="CUIT de 11 dígitos" name="cuit" inputMode="numeric" pattern="[0-9]{11}" maxLength={11} />
            <Elegir label="Perfil de riesgo" name="perfil_riesgo" defaultValue="conservador">
              {perfiles.map((p) => <option key={p}>{p}</option>)}
            </Elegir>
          </> : <Campo label="ID de inversor" name="inversor_id" type="number" min="1" step="1" />}
        </Formulario>
      </section>
    </div>
  </main>;
}
