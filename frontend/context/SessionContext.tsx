"use client";

import { createContext, useContext, useEffect, useState, type Dispatch, type ReactNode, type SetStateAction } from "react";
import { api, ApiError } from "@/lib/api";
import type { PerfilPanel } from "@/lib/types";

const clave = "zeno.inversor";
const Sesion = createContext<{
  perfil: PerfilPanel | null;
  pendiente: boolean;
  error: string;
  seleccionar: (perfil: PerfilPanel) => void;
  setPerfil: Dispatch<SetStateAction<PerfilPanel | null>>;
  salir: () => void;
} | null>(null);

export function SessionProvider({ children }: { children: ReactNode }) {
  const [perfil, setPerfil] = useState<PerfilPanel | null>(null);
  const [pendiente, setPendiente] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let vigente = true;
    function restaurar(evento: PageTransitionEvent) {
      if (evento.persisted) window.location.reload();
    }
    window.addEventListener("pageshow", restaurar);
    async function cargar() {
      const id = Number(window.sessionStorage.getItem(clave));
      return Number.isSafeInteger(id) && id > 0 ? api.perfil(id) : null;
    }
    cargar().then((datos) => {
      if (vigente) setPerfil(datos);
    }).catch((err: Error) => {
      if (!vigente) return;
      if (err instanceof ApiError && err.status === 404) window.sessionStorage.removeItem(clave);
      else setError(err.message);
    }).finally(() => {
      if (vigente) setPendiente(false);
    });
    return () => {
      vigente = false;
      window.removeEventListener("pageshow", restaurar);
    };
  }, []);

  function seleccionar(datos: PerfilPanel) {
    window.sessionStorage.setItem(clave, String(datos.inversor.id));
    setPerfil(datos);
  }

  function salir() {
    window.sessionStorage.removeItem(clave);
    window.location.assign("/login");
  }

  return <Sesion.Provider value={{ perfil, pendiente, error, seleccionar, setPerfil, salir }}>{children}</Sesion.Provider>;
}

export function useSession() {
  const sesion = useContext(Sesion);
  if (!sesion) throw new Error("Falta el proveedor de sesión.");
  return sesion;
}

export function useCuenta() {
  const sesion = useSession();
  const perfil = sesion.perfil;
  if (!perfil?.cuenta) throw new Error("Seleccioná una cuenta comitente.");
  return { ...sesion, perfil, cuenta: perfil.cuenta };
}
