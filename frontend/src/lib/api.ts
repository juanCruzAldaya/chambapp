// Cliente HTTP tipado contra la API de chambapp.
// Maneja el token JWT en localStorage y centraliza errores.

import type {
  BusquedaServicios,
  Calendario,
  CalendarioConEventos,
  CategoriaConSubcategorias,
  Contratacion,
  ContratacionCreate,
  Evento,
  EventoCreate,
  Resena,
  ResenaCreate,
  RolContratacion,
  Servicio,
  ServicioCreate,
  SubCategoria,
  Token,
  Usuario,
  UsuarioUpdate,
} from "./types";

const BASE_URL = import.meta.env.VITE_API_URL ?? "/api/v1";
const TOKEN_KEY = "chambapp_token";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = "ApiError";
  }
}

/** Extrae un mensaje legible del cuerpo de error de FastAPI. */
function parseDetail(body: unknown, fallback: string): string {
  if (body && typeof body === "object" && "detail" in body) {
    const detail = (body as { detail: unknown }).detail;
    if (typeof detail === "string") return detail;
    // Errores de validación (422): lista de {loc, msg}
    if (Array.isArray(detail) && detail.length > 0) {
      const first = detail[0] as { msg?: string };
      if (first?.msg) return first.msg;
    }
  }
  return fallback;
}

interface RequestOptions {
  method?: string;
  body?: unknown;
  query?: Record<string, string | number | undefined | null>;
  /** form-urlencoded en vez de JSON (para el login OAuth2). */
  form?: Record<string, string>;
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = "GET", body, query, form } = options;

  const url = new URL(`${BASE_URL}${path}`, window.location.origin);
  if (query) {
    for (const [key, value] of Object.entries(query)) {
      if (value !== undefined && value !== null && value !== "") {
        url.searchParams.set(key, String(value));
      }
    }
  }

  const headers: Record<string, string> = {};
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  let payload: BodyInit | undefined;
  if (form) {
    headers["Content-Type"] = "application/x-www-form-urlencoded";
    payload = new URLSearchParams(form).toString();
  } else if (body !== undefined) {
    headers["Content-Type"] = "application/json";
    payload = JSON.stringify(body);
  }

  const res = await fetch(url.toString().replace(window.location.origin, ""), {
    method,
    headers,
    body: payload,
  });

  if (res.status === 401) {
    clearToken();
    window.dispatchEvent(new Event("auth:logout"));
  }

  if (res.status === 204) {
    return undefined as T;
  }

  const data = await res.json().catch(() => null);
  if (!res.ok) {
    throw new ApiError(res.status, parseDetail(data, `Error ${res.status}`));
  }
  return data as T;
}

// ─── Auth ────────────────────────────────────────────────────
export const api = {
  register: (payload: {
    email: string;
    password: string;
    nombre?: string;
  }): Promise<Usuario> =>
    request("/auth/register", { method: "POST", body: payload }),

  login: (email: string, password: string): Promise<Token> =>
    request("/auth/login", {
      method: "POST",
      form: { username: email, password },
    }),

  // ─── Usuarios ──────────────────────────────────────────────
  me: (): Promise<Usuario> => request("/usuarios/me"),

  updateMe: (payload: UsuarioUpdate): Promise<Usuario> =>
    request("/usuarios/me", { method: "PATCH", body: payload }),

  getUsuario: (id: number): Promise<Usuario> => request(`/usuarios/${id}`),

  getCalendariosDeUsuario: (id: number): Promise<CalendarioConEventos[]> =>
    request(`/usuarios/${id}/calendarios`),

  // ─── Categorías ────────────────────────────────────────────
  listCategorias: (): Promise<CategoriaConSubcategorias[]> =>
    request("/categorias"),

  listSubcategorias: (categoriaId: number): Promise<SubCategoria[]> =>
    request(`/categorias/${categoriaId}/subcategorias`),

  // ─── Servicios ─────────────────────────────────────────────
  searchServicios: (filtros: BusquedaServicios = {}): Promise<Servicio[]> =>
    request("/servicios", { query: filtros as Record<string, string | number> }),

  getServicio: (id: number): Promise<Servicio> => request(`/servicios/${id}`),

  createServicio: (payload: ServicioCreate): Promise<Servicio> =>
    request("/servicios", { method: "POST", body: payload }),

  deleteServicio: (id: number): Promise<void> =>
    request(`/servicios/${id}`, { method: "DELETE" }),

  // ─── Calendarios / Eventos ─────────────────────────────────
  listCalendarios: (): Promise<Calendario[]> => request("/calendarios"),

  createCalendario: (payload: {
    anio?: number;
    mes?: number;
  }): Promise<Calendario> =>
    request("/calendarios", { method: "POST", body: payload }),

  getCalendario: (id: number): Promise<CalendarioConEventos> =>
    request(`/calendarios/${id}`),

  deleteCalendario: (id: number): Promise<void> =>
    request(`/calendarios/${id}`, { method: "DELETE" }),

  listEventos: (calendarioId: number): Promise<Evento[]> =>
    request("/eventos", { query: { calendario_id: calendarioId } }),

  createEvento: (payload: EventoCreate): Promise<Evento> =>
    request("/eventos", { method: "POST", body: payload }),

  deleteEvento: (id: number): Promise<void> =>
    request(`/eventos/${id}`, { method: "DELETE" }),

  // ─── Contrataciones ────────────────────────────────────────
  listContrataciones: (rol: RolContratacion): Promise<Contratacion[]> =>
    request("/contrataciones", { query: { rol } }),

  createContratacion: (payload: ContratacionCreate): Promise<Contratacion> =>
    request("/contrataciones", { method: "POST", body: payload }),

  updateContratacion: (
    id: number,
    payload: { estado?: string; comentarios?: string },
  ): Promise<Contratacion> =>
    request(`/contrataciones/${id}`, { method: "PATCH", body: payload }),

  // ─── Reseñas ───────────────────────────────────────────────
  listResenas: (servicioId: number): Promise<Resena[]> =>
    request("/resenas", { query: { servicio_id: servicioId } }),

  createResena: (payload: ResenaCreate): Promise<Resena> =>
    request("/resenas", { method: "POST", body: payload }),
};
