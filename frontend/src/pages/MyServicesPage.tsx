import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { ServiceCard } from "../components/ServiceCard";
import { Button, EmptyState, ErrorMsg, Spinner } from "../components/ui";
import { useAuth } from "../hooks/useAuth";
import { api } from "../lib/api";
import type { Servicio } from "../lib/types";

export function MyServicesPage() {
  const { user } = useAuth();
  const [servicios, setServicios] = useState<Servicio[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!user) return;
    api
      .searchServicios({ profesional_id: user.id, limit: 100 })
      .then(setServicios)
      .catch(() => setError("No se pudieron cargar tus servicios"))
      .finally(() => setLoading(false));
  }, [user]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-800">Mis servicios</h1>
        <Link to="/publicar">
          <Button>Publicar nuevo</Button>
        </Link>
      </div>

      <ErrorMsg>{error}</ErrorMsg>

      {loading ? (
        <Spinner />
      ) : servicios.length === 0 ? (
        <EmptyState>
          Todavía no publicaste servicios.{" "}
          <Link to="/publicar" className="font-semibold text-marca-600">
            Publicá el primero
          </Link>
          .
        </EmptyState>
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
