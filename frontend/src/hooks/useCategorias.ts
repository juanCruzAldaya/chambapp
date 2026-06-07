import { useEffect, useState } from "react";

import { api } from "../lib/api";
import type { CategoriaConSubcategorias } from "../lib/types";

/** Carga el árbol de categorías una vez (para filtros y formularios). */
export function useCategorias() {
  const [categorias, setCategorias] = useState<CategoriaConSubcategorias[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .listCategorias()
      .then(setCategorias)
      .catch(() => setCategorias([]))
      .finally(() => setLoading(false));
  }, []);

  return { categorias, loading };
}
