import { Link } from "react-router-dom";

import { formatRating, nombreVisible } from "../lib/format";
import type { Servicio } from "../lib/types";
import { Badge, Card } from "./ui";

export function ServiceCard({ servicio }: { servicio: Servicio }) {
  const ubicacion = [servicio.locality, servicio.department, servicio.state]
    .filter(Boolean)
    .join(", ");

  return (
    <Link to={`/servicios/${servicio.id}`} className="block">
      <Card className="h-full transition hover:border-marca-300 hover:shadow-md">
        <div className="flex items-start justify-between gap-2">
          {servicio.categoria_principal && (
            <Badge color="indigo">{servicio.categoria_principal.nombre}</Badge>
          )}
          {servicio.subcategoria && (
            <Badge>{servicio.subcategoria.nombre}</Badge>
          )}
        </div>

        <p className="mt-3 line-clamp-3 text-sm text-slate-700">
          {servicio.description || "Sin descripción"}
        </p>

        <div className="mt-4 flex items-center justify-between text-sm">
          <span className="font-medium text-slate-700">
            {nombreVisible(servicio.profesional)}
          </span>
          <span className="text-amber-500">
            {formatRating(servicio.profesional?.calificacion_promedio ?? null)}
          </span>
        </div>

        {ubicacion && (
          <p className="mt-1 text-xs text-slate-400">📍 {ubicacion}</p>
        )}
      </Card>
    </Link>
  );
}
