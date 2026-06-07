import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { Badge, Button, Card, EmptyState, ErrorMsg, Spinner } from "../components/ui";
import { ApiError, api } from "../lib/api";
import { formatFecha, formatHora } from "../lib/format";
import type { Contratacion, RolContratacion } from "../lib/types";

const ESTADOS = ["pendiente", "aceptada", "rechazada", "completada"];

function colorEstado(estado: string): "slate" | "green" | "amber" | "indigo" {
  if (estado === "aceptada" || estado === "completada") return "green";
  if (estado === "pendiente") return "amber";
  return "slate";
}

export function ContractsPage() {
  const [rol, setRol] = useState<RolContratacion>("cliente");
  const [items, setItems] = useState<Contratacion[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const cargar = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      setItems(await api.listContrataciones(rol));
    } catch {
      setError("No se pudieron cargar las contrataciones");
    } finally {
      setLoading(false);
    }
  }, [rol]);

  useEffect(() => {
    cargar();
  }, [cargar]);

  async function cambiarEstado(id: number, estado: string) {
    try {
      await api.updateContratacion(id, { estado });
      cargar();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo actualizar");
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-800">Contrataciones</h1>

      <div className="inline-flex rounded-lg border border-slate-200 bg-white p-1">
        <button
          onClick={() => setRol("cliente")}
          className={`rounded-md px-4 py-1.5 text-sm font-medium transition ${
            rol === "cliente" ? "bg-marca-600 text-white" : "text-slate-600"
          }`}
        >
          Contraté
        </button>
        <button
          onClick={() => setRol("profesional")}
          className={`rounded-md px-4 py-1.5 text-sm font-medium transition ${
            rol === "profesional" ? "bg-marca-600 text-white" : "text-slate-600"
          }`}
        >
          Me contrataron
        </button>
      </div>

      <ErrorMsg>{error}</ErrorMsg>

      {loading ? (
        <Spinner />
      ) : items.length === 0 ? (
        <EmptyState>
          {rol === "cliente"
            ? "Todavía no contrataste ningún servicio."
            : "Todavía no te contrataron."}
        </EmptyState>
      ) : (
        <div className="space-y-3">
          {items.map((c) => (
            <Card key={c.id}>
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <p className="font-medium text-slate-800">
                    {c.servicio?.categoria_principal?.nombre ?? "Servicio"}{" "}
                    {c.servicio && (
                      <Link
                        to={`/servicios/${c.servicio.id}`}
                        className="text-sm font-normal text-marca-600"
                      >
                        ver
                      </Link>
                    )}
                  </p>
                  <p className="mt-1 text-sm text-slate-500">
                    {formatFecha(c.fecha_contratacion)} ·{" "}
                    {formatHora(c.hora_contratacion)}
                  </p>
                  <p className="text-sm text-slate-500">📍 {c.domicilio}</p>
                  {c.comentarios && (
                    <p className="mt-1 text-sm text-slate-600">“{c.comentarios}”</p>
                  )}
                </div>
                <Badge color={colorEstado(c.estado)}>{c.estado}</Badge>
              </div>

              {rol === "profesional" && (
                <div className="mt-4 flex flex-wrap gap-2 border-t border-slate-100 pt-3">
                  {ESTADOS.filter((e) => e !== c.estado).map((e) => (
                    <Button
                      key={e}
                      variant="secondary"
                      onClick={() => cambiarEstado(c.id, e)}
                    >
                      Marcar {e}
                    </Button>
                  ))}
                </div>
              )}
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
