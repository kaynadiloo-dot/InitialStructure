"use client";

import { useState } from "react";
import { Campo, Elegir, Formulario, Marca } from "@/components/ui";
import { api } from "@/lib/api";
import { perfiles } from "@/lib/format";
import type { Perfil } from "@/lib/types";

export default function LoginPage() {
  const [alta, setAlta] = useState(false);

  return <main className="login">
    <div className="login-bg" aria-hidden="true"><div className="login-grid" /><div className="login-glow g1" /><div className="login-glow g2" /></div>
    <div className="login-main">
      <header className="login-brand"><Marca /></header>
      <section className="login-card">
        <div className="tabs">
          <button type="button" className={alta ? "tab" : "tab active"} aria-pressed={!alta} onClick={() => setAlta(false)}>Iniciar sesión</button>
          <button type="button" className={alta ? "tab active" : "tab"} aria-pressed={alta} onClick={() => setAlta(true)}>Crear cuenta</button>
        </div>
        <h1>{alta ? "Abrí tu cuenta" : "Bienvenido a Zeno"}</h1>
        <p className="login-sub">{alta ? "Elegí las credenciales de tu cuenta comitente." : "Ingresá tu nombre de cuenta y contraseña."}</p>
        <Formulario key={String(alta)} boton={alta ? "Crear cuenta comitente" : "Entrar"} enviar={async (datos) => {
          const nombre_cuenta = String(datos.get("nombre_cuenta")).trim();
          const password = String(datos.get("password"));
          if (alta) await api.alta({
            nombre: String(datos.get("nombre")).trim(),
            email: String(datos.get("email")).trim(),
            cuit: String(datos.get("cuit")).trim(),
            perfil_riesgo: datos.get("perfil_riesgo") as Perfil,
            nombre_cuenta, password,
          });
          else await api.ingresar(nombre_cuenta, password);
          window.location.assign("/");
          return "Sesión iniciada.";
        }}>
          <Campo label="Nombre de cuenta" name="nombre_cuenta" autoComplete="username" minLength={3} maxLength={32} />
          <Campo label="Contraseña" name="password" type="password" autoComplete={alta ? "new-password" : "current-password"} minLength={8} maxLength={128} />
          {alta && <>
            <Campo label="Nombre completo" name="nombre" maxLength={100} autoComplete="name" />
            <Campo label="Correo electrónico" name="email" type="email" autoComplete="email" />
            <Campo label="CUIT de 11 dígitos" name="cuit" inputMode="numeric" pattern="[0-9]{11}" maxLength={11} />
            <Elegir label="Perfil de riesgo" name="perfil_riesgo" defaultValue="conservador">
              {perfiles.map((p) => <option key={p}>{p}</option>)}
            </Elegir>
          </>}
        </Formulario>
      </section>
    </div>
  </main>;
}
