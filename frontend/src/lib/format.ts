import type { ApplicationStatus, EventCategory, ProjectStatus } from "./types";
export const projectStatusLabel: Record<ProjectStatus, string> = { idea: "En fase de idea", recruiting: "Busca equipo", in_progress: "En desarrollo" };
export const applicationStatusLabel: Record<ApplicationStatus, string> = { pending: "Pendiente", accepted: "Aceptada", rejected: "Rechazada" };
export const eventCategoryLabel: Record<EventCategory, string> = { congreso: "Congreso", semillero: "Semillero", call_for_papers: "Convocatoria" };
export function formatDate(value: string | null): string { if (!value) return "Sin fecha límite"; const date = new Date(value); return Number.isNaN(date.getTime()) ? "Fecha no disponible" : new Intl.DateTimeFormat("es-PE", { day: "numeric", month: "short", year: "numeric" }).format(date); }
export function commaList(value: string): string[] { return value.split(",").map(item => item.trim()).filter(Boolean); }
