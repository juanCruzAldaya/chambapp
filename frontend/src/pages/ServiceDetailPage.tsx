import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import {
  Badge,
  Button,
  Card,
  EmptyState,
  ErrorMsg,
  Field,
  Spinner,
  TextInput,
} from "../components/ui";
import { useAuth } from "../hooks/useAuth";
import { ApiError, api } from "../lib/api";
import { formatFecha, formatHora, formatRating, nombreVisible } from "../lib/format";
import type {
  CalendarioConEventos,
  Evento,
  Resena,
  Servicio,
} from "../lib/types";

interface Slot extends Evento {
  calendario_id: number;
}

export function ServiceDetailPage() {
  const { id } = useParams<{ id: string }>();
  const servicioId = Number(id);
  const { user } = useAuth();
  const navigate = useNavigate();

  const [servicio, setServicio] = useState<Servicio | null>(null);
  const [resenas, setResenas] = useState<Resena[]>([]);
  const [disponibilidad, setDisponibilidad] = useState<CalendarioConEventos[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const cargar = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const serv = await api.getServicio(servicioId);
      setServicio(serv);
      const [revs, cals] = await Promise.all([
        api.listResenas(servicioId),
        api.getCalendariosDeUsuario(serv.profesional_id),
      ]);
      setResenas(revs);
      setDisponibilidad(cals);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo cargar");
    } finally {
      setLoading(false);
    }
  }, [servicioId]);

  useEffect(() => {
    cargar();
  }, [cargar]);

  const slots = useMemo<Slot[]>(
    () =>
      disponibilidad.flatMap((cal) =>
        cal.eventos
          .filter((e) => e.estado === "disponible")
          .map((e) => ({ ...e, calendario_id: cal.id })),
      ),
    [disponibilidad],
  );

  if (loading) return <Spinner />;
  if (error || !servicio) return <ErrorMsg>{error || "No encontrado"}</ErrorMsg>;

  const esPropio = user?.id === servicio.profesional_id;
  const ubicacion = [servicio.locality, servicio.department, servicio.state]
    .filter(Boolean)
    .join(", ");

  async function handleDelete() {
    if (!confirm("¿Eliminar este servicio?")) return;
    try {
      await api.deleteServicio(servicioId);
      navigate("/mis-servicios");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo eliminar");
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div className="flex flex-wrap gap-2">
            {servicio.categoria_principal && (
              <Badge color="indigo">{servicio.categoria_principal.nombre}</Badge>
            )}
            {servicio.subcategoria && <Badge>{servicio.subcategoria.nombre}</Badge>}
          </div>
          {esPropio && (
            <Button variant="danger" onClick={handleDelete}>
              Eliminar
            </Button>
          )}
        </div>

        <p className="mt-4 whitespace-pre-line text-slate-700">
          {servicio.description || "Sin descripción"}
        </p>
        {ubicacion && <p className="mt-3 text-sm text-slate-400">📍 {ubicacion}</p>}

        <div className="mt-4 flex items-center gap-3 border-t border-slate-100 pt-4">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-marca-100 font-bold text-marca-700">
            {nombreVisible(servicio.profesional).charAt(0).toUpperCase()}
          </div>
          <div>
            <p className="font-medium text-slate-700">
              {nombreVisible(servicio.profesional)}
            </p>
            <p className="text-sm text-amber-500">
              {formatRating(servicio.profesional?.calificacion_promedio ?? null)}
            </p>
          </div>
        </div>
      </Card>

      {esPropio ? (
        <Card>
          <p className="text-sm text-slate-500">
            Este es tu servicio. Para que te puedan contratar, publicá turnos
            disponibles en tu <strong>Agenda</strong>.
          </p>
        </Card>
      ) : user ? (
        <ContratarBox
          servicio={servicio}
          slots={slots}
          onDone={() => navigate("/contrataciones")}
        />
      ) : (
        <Card>
          <p className="text-sm text-slate-500">
            <button
              className="font-semibold text-marca-600"
              onClick={() => navigate("/login")}
            >
              Ingresá
            </button>{" "}
            para contratar este servicio o dejar una reseña.
          </p>
        </Card>
      )}

      <ResenasSection
        servicioId={servicioId}
        resenas={resenas}
        puedeResenar={!!user && !esPropio}
        onNueva={cargar}
      />
    </div>
  );
}

// ─── Contratar ─────────────────────────────────────────────────
function ContratarBox({
  servicio,
  slots,
  onDone,
}: {
  servicio: Servicio;
  slots: Slot[];
  onDone: () => void;
}) {
  const [slotId, setSlotId] = useState("");
  const [contacto, setContacto] = useState("");
  const [domicilio, setDomicilio] = useState("");
  const [comentarios, setComentarios] = useState("");
  const [error, setError] = useState("");
  const [ok, setOk] = useState(false);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    const slot = slots.find((s) => s.id === Number(slotId));
    if (!slot) {
      setError("Elegí un turno disponible");
      return;
    }
    setLoading(true);
    try {
      await api.createContratacion({
        servicio_id: servicio.id,
        calendario_id: slot.calendario_id,
        evento_id: slot.id,
        fecha_contratacion: slot.fecha,
        hora_contratacion: slot.hora_inicio,
        contacto,
        domicilio,
        comentarios: comentarios || undefined,
      });
      setOk(true);
      setTimeout(onDone, 800);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo contratar");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card>
      <h2 className="mb-4 text-lg font-semibold text-slate-800">
        Contratar este servicio
      </h2>
      {slots.length === 0 ? (
        <p className="text-sm text-slate-500">
          Este profesional todavía no publicó turnos disponibles.
        </p>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4">
          <Field label="Turno disponible">
            <select
              value={slotId}
              onChange={(e) => setSlotId(e.target.value)}
              required
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-marca-500 focus:ring-2 focus:ring-marca-100"
            >
              <option value="">Elegí un turno…</option>
              {slots.map((s) => (
                <option key={s.id} value={s.id}>
                  {formatFecha(s.fecha)} · {formatHora(s.hora_inicio)}–
                  {formatHora(s.hora_fin)}
                </option>
              ))}
            </select>
          </Field>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <Field label="Contacto">
              <TextInput
                value={contacto}
                onChange={(e) => setContacto(e.target.value)}
                placeholder="Tel / WhatsApp"
                required
              />
            </Field>
            <Field label="Domicilio">
              <TextInput
                value={domicilio}
                onChange={(e) => setDomicilio(e.target.value)}
                placeholder="Dónde es el trabajo"
                required
              />
            </Field>
          </div>
          <Field label="Comentarios (opcional)">
            <TextInput
              value={comentarios}
              onChange={(e) => setComentarios(e.target.value)}
              placeholder="Detalles del trabajo"
            />
          </Field>
          <ErrorMsg>{error}</ErrorMsg>
          {ok && (
            <p className="rounded-lg bg-green-50 px-3 py-2 text-sm text-green-700">
              ¡Listo! Te llevamos a tus contrataciones…
            </p>
          )}
          <Button type="submit" disabled={loading}>
            {loading ? "Enviando…" : "Confirmar contratación"}
          </Button>
        </form>
      )}
    </Card>
  );
}

// ─── Reseñas ───────────────────────────────────────────────────
function ResenasSection({
  servicioId,
  resenas,
  puedeResenar,
  onNueva,
}: {
  servicioId: number;
  resenas: Resena[];
  puedeResenar: boolean;
  onNueva: () => void;
}) {
  const [calificacion, setCalificacion] = useState(5);
  const [comentario, setComentario] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await api.createResena({
        servicio_id: servicioId,
        calificacion,
        comentario: comentario || undefined,
      });
      setComentario("");
      onNueva();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo reseñar");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card>
      <h2 className="mb-4 text-lg font-semibold text-slate-800">
        Reseñas ({resenas.length})
      </h2>

      {puedeResenar && (
        <form
          onSubmit={handleSubmit}
          className="mb-6 space-y-3 rounded-lg bg-slate-50 p-4"
        >
          <Field label="Tu calificación">
            <select
              value={calificacion}
              onChange={(e) => setCalificacion(Number(e.target.value))}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            >
              {[5, 4, 3, 2, 1].map((n) => (
                <option key={n} value={n}>
                  {"★".repeat(n)} ({n})
                </option>
              ))}
            </select>
          </Field>
          <Field label="Comentario (opcional)">
            <TextInput
              value={comentario}
              onChange={(e) => setComentario(e.target.value)}
              placeholder="¿Cómo fue tu experiencia?"
            />
          </Field>
          <ErrorMsg>{error}</ErrorMsg>
          <Button type="submit" disabled={loading}>
            {loading ? "Enviando…" : "Dejar reseña"}
          </Button>
        </form>
      )}

      {resenas.length === 0 ? (
        <EmptyState>Todavía no hay reseñas.</EmptyState>
      ) : (
        <ul className="space-y-3">
          {resenas.map((r) => (
            <li key={r.id} className="border-b border-slate-100 pb-3 last:border-0">
              <div className="flex items-center justify-between">
                <span className="text-amber-500">{"★".repeat(r.calificacion)}</span>
                <span className="text-xs text-slate-400">{formatFecha(r.fecha)}</span>
              </div>
              {r.comentario && (
                <p className="mt-1 text-sm text-slate-600">{r.comentario}</p>
              )}
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}
