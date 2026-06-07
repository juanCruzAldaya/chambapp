import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { Button, Card, ErrorMsg, Field, TextInput } from "../components/ui";
import { useCategorias } from "../hooks/useCategorias";
import { ApiError, api } from "../lib/api";

export function PublishServicePage() {
  const { categorias } = useCategorias();
  const navigate = useNavigate();

  const [mainCategory, setMainCategory] = useState("");
  const [secondaryCategory, setSecondaryCategory] = useState("");
  const [description, setDescription] = useState("");
  const [state, setState] = useState("");
  const [department, setDepartment] = useState("");
  const [locality, setLocality] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const subcategorias = useMemo(
    () =>
      categorias.find((c) => c.id === Number(mainCategory))?.subcategorias ?? [],
    [categorias, mainCategory],
  );

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    if (!mainCategory) {
      setError("Elegí una categoría");
      return;
    }
    setLoading(true);
    try {
      const servicio = await api.createServicio({
        main_category: Number(mainCategory),
        secondary_category: secondaryCategory
          ? Number(secondaryCategory)
          : undefined,
        description: description || undefined,
        state: state || undefined,
        department: department || undefined,
        locality: locality || undefined,
      });
      navigate(`/servicios/${servicio.id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo publicar");
    } finally {
      setLoading(false);
    }
  }

  const selectClass =
    "w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-marca-500 focus:ring-2 focus:ring-marca-100";

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="mb-6 text-2xl font-bold text-slate-800">Publicar un servicio</h1>
      <Card>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <Field label="Categoría">
              <select
                value={mainCategory}
                onChange={(e) => {
                  setMainCategory(e.target.value);
                  setSecondaryCategory("");
                }}
                required
                className={selectClass}
              >
                <option value="">Elegí…</option>
                {categorias.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.nombre}
                  </option>
                ))}
              </select>
            </Field>
            <Field label="Subcategoría (opcional)">
              <select
                value={secondaryCategory}
                onChange={(e) => setSecondaryCategory(e.target.value)}
                disabled={subcategorias.length === 0}
                className={selectClass}
              >
                <option value="">—</option>
                {subcategorias.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.nombre}
                  </option>
                ))}
              </select>
            </Field>
          </div>

          <Field label="Descripción">
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={4}
              placeholder="Contá qué ofrecés, experiencia, qué incluye…"
              className={selectClass}
            />
          </Field>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <Field label="Provincia">
              <TextInput value={state} onChange={(e) => setState(e.target.value)} />
            </Field>
            <Field label="Departamento">
              <TextInput
                value={department}
                onChange={(e) => setDepartment(e.target.value)}
              />
            </Field>
            <Field label="Localidad">
              <TextInput
                value={locality}
                onChange={(e) => setLocality(e.target.value)}
              />
            </Field>
          </div>

          <ErrorMsg>{error}</ErrorMsg>
          <Button type="submit" disabled={loading}>
            {loading ? "Publicando…" : "Publicar servicio"}
          </Button>
        </form>
      </Card>
    </div>
  );
}
