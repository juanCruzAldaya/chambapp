import { useState } from "react";

import { Button, Card, ErrorMsg, Field, TextInput } from "../components/ui";
import { useAuth } from "../hooks/useAuth";
import { formatRating } from "../lib/format";
import { ApiError, api } from "../lib/api";

export function ProfilePage() {
  const { user, refresh } = useAuth();

  const [nombre, setNombre] = useState(user?.nombre ?? "");
  const [apellido, setApellido] = useState(user?.apellido ?? "");
  const [contacto, setContacto] = useState(user?.contacto ?? "");
  const [ciudad, setCiudad] = useState(user?.ciudad ?? "");
  const [error, setError] = useState("");
  const [ok, setOk] = useState(false);
  const [loading, setLoading] = useState(false);

  if (!user) return null;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setOk(false);
    setLoading(true);
    try {
      await api.updateMe({
        nombre: nombre || null,
        apellido: apellido || null,
        contacto: contacto || null,
        ciudad: ciudad || null,
      });
      await refresh();
      setOk(true);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo guardar");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-xl space-y-6">
      <h1 className="text-2xl font-bold text-slate-800">Mi perfil</h1>

      <Card>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-slate-500">{user.email}</p>
            <p className="text-sm text-amber-500">
              {formatRating(user.calificacion_promedio)}
            </p>
          </div>
        </div>
      </Card>

      <Card>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <Field label="Nombre">
              <TextInput value={nombre} onChange={(e) => setNombre(e.target.value)} />
            </Field>
            <Field label="Apellido">
              <TextInput
                value={apellido}
                onChange={(e) => setApellido(e.target.value)}
              />
            </Field>
            <Field label="Contacto">
              <TextInput
                value={contacto}
                onChange={(e) => setContacto(e.target.value)}
                placeholder="Tel / WhatsApp"
              />
            </Field>
            <Field label="Ciudad">
              <TextInput value={ciudad} onChange={(e) => setCiudad(e.target.value)} />
            </Field>
          </div>
          <ErrorMsg>{error}</ErrorMsg>
          {ok && (
            <p className="rounded-lg bg-green-50 px-3 py-2 text-sm text-green-700">
              Perfil actualizado.
            </p>
          )}
          <Button type="submit" disabled={loading}>
            {loading ? "Guardando…" : "Guardar cambios"}
          </Button>
        </form>
      </Card>
    </div>
  );
}
