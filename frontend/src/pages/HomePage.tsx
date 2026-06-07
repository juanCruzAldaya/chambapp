import { useCallback, useEffect, useState } from "react";

import { ServiceCard } from "../components/ServiceCard";
import { Button, Card, EmptyState, ErrorMsg, Field, Spinner, TextInput } from "../components/ui";
import { useCategorias } from "../hooks/useCategorias";
import { api } from "../lib/api";
import type { BusquedaServicios, Servicio } from "../lib/types";

export function HomePage() {
  const { categorias } = useCategorias();
  const [servicios, setServicios] = useState<Servicio[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [q, setQ] = useState("");
  const [mainCategory, setMainCategory] = useState("");
  const [locality, setLocality] = useState("");

  const buscar = useCallback(async (filtros: BusquedaServicios) => {
    setLoading(true);
    setError("");
    try {
      setServicios(await api.searchServicios(filtros));
    } catch {
      setError("No se pudieron cargar los servicios");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    buscar({});
  }, [buscar]);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    buscar({
      q: q || undefined,
      main_category: mainCategory ? Number(mainCategory) : undefined,
      locality: locality || undefined,
    });
  }

  return (
    <div className="space-y-8">
      <section className="rounded-2xl bg-gradient-to-br from-marca-600 to-marca-500 px-6 py-10 text-white">
        <h1 className="text-3xl font-extrabold">Encontrá quien te resuelva la changa</h1>
        <p className="mt-2 max-w-xl text-marca-50">
          Plomería, electricidad, limpieza, clases y mucho más. Profesionales
          cerca tuyo.
        </p>
      </section>

      <Card>
        <form
          onSubmit={handleSubmit}
          className="grid grid-cols-1 gap-4 md:grid-cols-[2fr_1fr_1fr_auto] md:items-end"
        >
          <Field label="¿Qué necesitás?">
            <TextInput
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Ej: arreglar una canilla"
            />
          </Field>
          <Field label="Categoría">
            <select
              value={mainCategory}
              onChange={(e) => setMainCategory(e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-marca-500 focus:ring-2 focus:ring-marca-100"
            >
              <option value="">Todas</option>
              {categorias.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.nombre}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Localidad">
            <TextInput
              value={locality}
              onChange={(e) => setLocality(e.target.value)}
              placeholder="Ej: Centro"
            />
          </Field>
          <Button type="submit">Buscar</Button>
        </form>
      </Card>

      <ErrorMsg>{error}</ErrorMsg>

      {loading ? (
        <Spinner />
      ) : servicios.length === 0 ? (
        <EmptyState>No hay servicios que coincidan con tu búsqueda.</EmptyState>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {servicios.map((s) => (
            <ServiceCard key={s.id} servicio={s} />
          ))}
        </div>
      )}
    </div>
  );
}
