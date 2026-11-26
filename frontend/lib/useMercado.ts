"use client";

import { useEffect } from "react";
import { api } from "./api";
import { useResource } from "./useResource";

export function useMercado() {
  const recurso = useResource(api.mercado);
  const { reload } = recurso;
  useEffect(() => {
    const intervalo = window.setInterval(reload, 30000);
    return () => window.clearInterval(intervalo);
  }, [reload]);
  return recurso;
}
