// Tipos que reflejan los schemas Pydantic del backend (app/schemas).

export interface Token {
  access_token: string;
  token_type: string;
}

export interface Usuario {
  id: number;
  email: string;
  nombre: string | null;
  apellido: string | null;
  contacto: string | null;
  ciudad: string | null;
  nacimiento: string | null;
  // Decimal -> string en JSON (Pydantic v2)
  calificacion_promedio: string | null;
  created_at: string;
}

export interface UsuarioUpdate {
  nombre?: string | null;
  apellido?: string | null;
  contacto?: string | null;
  ciudad?: string | null;
  nacimiento?: string | null;
}

export interface SubCategoria {
  id: number;
  nombre: string;
  categoria_id: number;
}

export interface Categoria {
  id: number;
  nombre: string;
}

export interface CategoriaConSubcategorias extends Categoria {
  subcategorias: SubCategoria[];
}

export interface ProfesionalResumen {
  id: number;
  nombre: string | null;
  apellido: string | null;
  calificacion_promedio: string | null;
}

export interface Servicio {
  id: number;
  profesional_id: number;
  description: string | null;
  main_category: number;
  secondary_category: number | null;
  state: string | null;
  department: string | null;
  locality: string | null;
  created_at: string;
  categoria_principal: Categoria | null;
  subcategoria: SubCategoria | null;
  profesional: ProfesionalResumen | null;
}

export interface ServicioCreate {
  main_category: number;
  secondary_category?: number | null;
  description?: string | null;
  state?: string | null;
  department?: string | null;
  locality?: string | null;
}

export interface BusquedaServicios {
  q?: string;
  main_category?: number;
  secondary_category?: number;
  state?: string;
  department?: string;
  locality?: string;
  profesional_id?: number;
  skip?: number;
  limit?: number;
}

export interface Evento {
  id: number;
  calendario_id: number;
  fecha: string;
  hora_inicio: string;
  hora_fin: string;
  estado: string;
}

export interface EventoCreate {
  calendario_id: number;
  fecha: string;
  hora_inicio: string;
  hora_fin: string;
  estado?: string;
}

export interface Calendario {
  id: number;
  usuario_id: number;
  anio: number | null;
  mes: number | null;
}

export interface CalendarioConEventos extends Calendario {
  eventos: Evento[];
}

export type RolContratacion = "cliente" | "profesional";

export interface Contratacion {
  id: number;
  cliente_id: number;
  servicio_id: number;
  calendario_id: number;
  evento_id: number | null;
  fecha_contratacion: string;
  hora_contratacion: string;
  contacto: string;
  domicilio: string;
  estado: string;
  comentarios: string | null;
  servicio: Servicio | null;
}

export interface ContratacionCreate {
  servicio_id: number;
  calendario_id: number;
  evento_id?: number | null;
  fecha_contratacion: string;
  hora_contratacion: string;
  contacto: string;
  domicilio: string;
  comentarios?: string | null;
}

export interface Resena {
  id: number;
  servicio_id: number;
  cliente_id: number;
  calificacion: number;
  comentario: string | null;
  fecha: string;
}

export interface ResenaCreate {
  servicio_id: number;
  calificacion: number;
  comentario?: string | null;
}
