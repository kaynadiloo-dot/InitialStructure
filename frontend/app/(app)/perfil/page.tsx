"use client";

import { Elegir, Formulario, Head } from "@/components/ui";
import { useCuenta } from "@/context/SessionContext";
import { api } from "@/lib/api";
import { perfiles } from "@/lib/format";
import type { Perfil } from "@/lib/types";

export default function PerfilPage() {
  const { perfil, cuenta, setPerfil, salir } = useCuenta();
  const { inversor } = perfil;

  return <>
    <Head title="Mi perfil" sub={inversor.nombre} />
    <div className="grid g2e">
      <section className="card">
        <h2>Datos de la cuenta</h2>
        <dl className="profile-data">
          <dt>Nombre de cuenta</dt><dd>{inversor.nombre_cuenta}</dd>
          <dt>Correo electrónico</dt><dd>{inversor.email}</dd>
          <dt>CUIT</dt><dd>{inversor.cuit}</dd>
          <dt>Cuenta comitente</dt><dd>{cuenta.numero_comitente}</dd>
        </dl>
        <button type="button" className="btn btn-ghost" onClick={salir}>Cerrar sesión</button>
      </section>
      <Formulario className="card" boton="Guardar perfil" enviar={async (datos) => {
        const actualizado = await api.cambiarPerfil(datos.get("perfil_riesgo") as Perfil);
        setPerfil((actual) => actual && ({ ...actual, inversor: actualizado }));
        return "Perfil de riesgo actualizado.";
      }}>
        <h2>Perfil de riesgo</h2>
        <Elegir label="Perfil" name="perfil_riesgo" defaultValue={inversor.perfil_riesgo}>
          {perfiles.map((p) => <option key={p}>{p}</option>)}
        </Elegir>
      </Formulario>
    </div>
  </>;
}
