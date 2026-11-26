"use client";

import { useState, type ComponentProps, type FormEvent, type ReactNode } from "react";
import Image from "next/image";

export function Marca() {
  return <span className="brand">
    <Image className="brand-mark" src="/brand/zeno-mark.png" alt="" width={36} height={36} priority />
    <span className="wordmark">Zeno <span>Investments</span></span>
  </span>;
}

// Los enlaces de sección cargan un documento completo.
export function Enlace(props: ComponentProps<"a">) {
  return <a {...props} />;
}

export function Head({ title, sub, extra }: { title: string; sub?: string; extra?: ReactNode }) {
  return <div className="head"><div><h1>{title}</h1>{sub && <p>{sub}</p>}</div>{extra}</div>;
}

export function EstadoCarga({ error, reload }: { error: string; reload: () => void }) {
  return error ? <div className="card" role="alert">
    <p>{error}</p><button type="button" className="btn btn-primary" onClick={reload}>Reintentar</button>
  </div> : <div className="empty" role="status">Cargando…</div>;
}

export function Campo({ label, ...props }: ComponentProps<"input"> & { label: string }) {
  return <label className="field"><span>{label}</span><input required {...props} /></label>;
}

export function Elegir({ label, children, ...props }: ComponentProps<"select"> & { label: string }) {
  return <label className="field"><span>{label}</span><select required {...props}>{children}</select></label>;
}

export function Formulario({ children, enviar, boton, className, limpiar = false }: {
  children?: ReactNode;
  enviar: (datos: FormData) => Promise<string>;
  boton: string;
  className?: string;
  limpiar?: boolean;
}) {
  const [ocupado, setOcupado] = useState(false);
  const [aviso, setAviso] = useState<{ texto: string; error: boolean } | null>(null);

  async function submit(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    const form = evento.currentTarget;
    setOcupado(true);
    setAviso(null);
    try {
      const texto = await enviar(new FormData(form));
      if (limpiar) form.reset();
      setAviso({ texto, error: false });
    } catch (error) {
      setAviso({ texto: error instanceof Error ? error.message : "No se pudo completar la operación.", error: true });
    } finally {
      setOcupado(false);
    }
  }

  return <form className={className} onSubmit={submit}>
    {children}
    <button type="submit" className="btn btn-primary" disabled={ocupado}>{ocupado ? "Guardando…" : boton}</button>
    {aviso && <p className={aviso.error ? "err" : "up form-msg"} role={aviso.error ? "alert" : "status"}>{aviso.texto}</p>}
  </form>;
}

export function Tabla({ columnas, filas, vacio }: { columnas: string[]; filas: ReactNode[][]; vacio: string }) {
  return <div className="table-wrap"><table>
    <thead><tr>{columnas.map((columna) => <th key={columna} scope="col">{columna}</th>)}</tr></thead>
    <tbody>{filas.length ? filas.map((fila, index) => <tr key={index}>
      {fila.map((celda, indice) => <td key={indice}>{celda}</td>)}
    </tr>) : <tr><td colSpan={columnas.length}><div className="empty">{vacio}</div></td></tr>}</tbody>
  </table></div>;
}
