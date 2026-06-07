import { useCallback, useEffect, useState } from "react";

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
import { ApiError, api } from "../lib/api";
import { formatFecha, formatHora } from "../lib/format";
import type { Calendario, Evento } from "../lib/types";

const MESES = [
  "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
  "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
];

export function AgendaPage() {
  const [calendarios, setCalendarios] = useState<Calendario[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const ahora = new Date();
  const [anio, setAnio] = useState(String(ahora.getFullYear()));
  const [mes, setMes] = useState(String(ahora.getMonth() + 1));

  const cargar = useCallback(async () => {
    try {
      setCalendarios(await api.listCalendarios());
    } catch {
      setError("No se pudieron cargar tus calendarios");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    cargar();
  }, [cargar]);

  async function crearCalendario(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try {
      await api.createCalendario({ anio: Number(anio), mes: Number(mes) });
      cargar();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo crear");
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-800">Mi agenda</h1>
      <p className="text-sm text-slate-500">
        Creá calendarios por mes y cargá los turnos en los que estás disponible.
        Tus clientes los verán al contratarte.
      </p>

      <Card>
        <form
          onSubmit={crearCalendario}
          className="grid grid-cols-1 gap-4 sm:grid-cols-[1fr_1fr_auto] sm:items-end"
        >
          <Field label="Año">
            <TextInput
              type="number"
              value={anio}
              onChange={(e) => setAnio(e.target.value)}
              min={2000}
              max={2100}
              required
            />
          </Field>
          <Field label="Mes">
            <select
              value={mes}
              onChange={(e) => setMes(e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            >
              {MESES.map((m, i) => (
                <option key={m} value={i + 1}>
                  {m}
                </option>
              ))}
            </select>
          </Field>
          <Button type="submit">Crear calendario</Button>
        </form>
      </Card>

      <ErrorMsg>{error}</ErrorMsg>

      {loading ? (
        <Spinner />
      ) : calendarios.length === 0 ? (
        <EmptyState>Todavía no tenés calendarios. Creá el primero arriba.</EmptyState>
      ) : (
        <div className="space-y-4">
          {calendarios.map((cal) => (
            <CalendarSection key={cal.id} calendario={cal} onChange={cargar} />
          ))}
        </div>
      )}
    </div>
  );
}

function CalendarSection({
  calendario,
  onChange,
}: {
  calendario: Calendario;
  onChange: () => void;
}) {
  const [eventos, setEventos] = useState<Evento[]>([]);
  const [error, setError] = useState("");
  const [fecha, setFecha] = useState("");
  const [horaInicio, setHoraInicio] = useState("09:00");
  const [horaFin, setHoraFin] = useState("10:00");

  const cargarEventos = useCallback(async () => {
    try {
      setEventos(await api.listEventos(calendario.id));
    } catch {
      setError("No se pudieron cargar los turnos");
    }
  }, [calendario.id]);

  useEffect(() => {
    cargarEventos();
  }, [cargarEventos]);

  async function agregarEvento(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try {
      await api.createEvento({
        calendario_id: calendario.id,
        fecha,
        hora_inicio: `${horaInicio}:00`,
        hora_fin: `${horaFin}:00`,
      });
      setFecha("");
      cargarEventos();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "No se pudo agregar el turno");
    }
  }

  async function eliminarEvento(id: number) {
    await api.deleteEvento(id);
    cargarEventos();
  }

  async function eliminarCalendario() {
    if (!confirm("¿Eliminar este calendario y sus turnos?")) return;
    await api.deleteCalendario(calendario.id);
    onChange();
  }

  const titulo =
    calendario.mes && calendario.anio
      ? `${MESES[calendario.mes - 1]} ${calendario.anio}`
      : `Calendario #${calendario.id}`;

  return (
    <Card>
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-slate-800">{titulo}</h2>
        <Button variant="ghost" onClick={eliminarCalendario}>
          Eliminar
        </Button>
      </div>

      {eventos.length > 0 && (
        <ul className="mb-4 space-y-2">
          {eventos.map((ev) => (
            <li
              key={ev.id}
              className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2 text-sm"
            >
              <span>
                {formatFecha(ev.fecha)} · {formatHora(ev.hora_inicio)}–
                {formatHora(ev.hora_fin)}
              </span>
              <div className="flex items-center gap-2">
                <Badge color={ev.estado === "disponible" ? "green" : "amber"}>
                  {ev.estado}
                </Badge>
                <button
                  onClick={() => eliminarEvento(ev.id)}
                  className="text-xs text-red-500 hover:underline"
                >
                  quitar
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}

      <form
        onSubmit={agregarEvento}
        className="grid grid-cols-1 gap-3 sm:grid-cols-[1fr_auto_auto_auto] sm:items-end"
      >
        <Field label="Fecha">
          <TextInput
            type="date"
            value={fecha}
            onChange={(e) => setFecha(e.target.value)}
            required
          />
        </Field>
        <Field label="Desde">
          <TextInput
            type="time"
            value={horaInicio}
            onChange={(e) => setHoraInicio(e.target.value)}
            required
          />
        </Field>
        <Field label="Hasta">
          <TextInput
            type="time"
            value={horaFin}
            onChange={(e) => setHoraFin(e.target.value)}
            required
          />
        </Field>
        <Button type="submit" variant="secondary">
          Agregar turno
        </Button>
      </form>
      <ErrorMsg>{error}</ErrorMsg>
    </Card>
  );
}
