/** Formatea la calificación promedio (string Decimal o null). */
export function formatRating(value: string | number | null): string {
  if (value === null || value === undefined) return "Sin calificaciones";
  const n = Number(value);
  if (Number.isNaN(n)) return "Sin calificaciones";
  return `★ ${n.toFixed(1)}`;
}

/** Nombre visible de un usuario/profesional. */
export function nombreVisible(
  p: { nombre: string | null; apellido?: string | null } | null,
): string {
  if (!p) return "Profesional";
  const full = [p.nombre, p.apellido].filter(Boolean).join(" ").trim();
  return full || "Profesional";
}

/** Fecha ISO -> dd/mm/aaaa. */
export function formatFecha(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleDateString("es-AR");
}

/** Recorta "HH:MM:SS" -> "HH:MM". */
export function formatHora(hora: string): string {
  return hora.slice(0, 5);
}
