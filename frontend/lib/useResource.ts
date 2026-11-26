"use client";

import { useCallback, useEffect, useState } from "react";

export function useResource<T>(cargar: () => Promise<T>) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState("");
  const [revision, setRevision] = useState(0);
  const reload = useCallback(() => setRevision((n) => n + 1), []);

  useEffect(() => {
    let vigente = true;
    cargar().then((value) => {
      if (!vigente) return;
      setData(value);
      setError("");
    }).catch((err: Error) => {
      if (vigente) setError(err.message);
    });
    return () => { vigente = false; };
  }, [cargar, revision]);

  return { data, error, reload };
}
