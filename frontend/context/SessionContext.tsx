"use client";

import { createContext, useContext, useEffect, useState, type Dispatch, type ReactNode, type SetStateAction } from "react";
import { api, ApiError } from "@/lib/api";
import type { PerfilPanel } from "@/lib/types";

const Sesion = createContext<{
  perfil: PerfilPanel | null;
  pendiente: boolean;
  error: string;
  setPerfil: Dispatch<SetStateAction<PerfilPanel | null>>;
  salir: () => Promise<void>;
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
    api.perfil().then((datos) => {
      if (vigente) setPerfil(datos);
    }).catch((err: Error) => {
      if (!vigente) return;
      if (!(err instanceof ApiError && err.status === 401)) setError(err.message);
    }).finally(() => {
      if (vigente) setPendiente(false);
    });
    return () => {
      vigente = false;
      window.removeEventListener("pageshow", restaurar);
    };
  }, []);

  async function salir() {
    try {
      await api.salir();
      window.location.assign("/login");
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo cerrar la sesión.");
    }
  }

  return <Sesion.Provider value={{ perfil, pendiente, error, setPerfil, salir }}>{children}</Sesion.Provider>;
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
