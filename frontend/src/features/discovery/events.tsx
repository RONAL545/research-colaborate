"use client";
import Link from "next/link";
import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { api, errorMessage, queryString } from "@/lib/api";
import { useRemote } from "@/lib/use-remote";
import { useSession } from "@/lib/session";
import { eventCategoryLabel, formatDate } from "@/lib/format";
import type { AcademicEvent, EventCategory, Page } from "@/lib/types";
import {
  Badge,
  Button,
  PageHeader,
  Pagination,
  StatePanel,
} from "@/components/ui";
import { ParticipationGate } from "./project";
import s from "./discovery.module.css";
export function EventsDirectory() {
  const [page, setPage] = useState(1);
  const { user } = useSession();
  const remote = useRemote<Page<AcademicEvent>>(
    `/events${queryString({ page, page_size: 12 })}`,
  );
  return (
    <>
      <PageHeader
        eyebrow="MÁS ALLÁ DEL AULA"
        title="Oportunidades para ir más lejos"
        description="Congresos, semilleros y convocatorias para compartir lo que estás construyendo."
        actions={
          user?.role === "admin" && user.email_verified ? (
            <Link className="button button-primary" href="/eventos/nuevo">
              Publicar evento
            </Link>
          ) : undefined
        }
      />
      {remote.loading ? (
        <StatePanel kind="loading" title="Cargando oportunidades…" />
      ) : remote.error ? (
        <StatePanel
          kind="error"
          title="No pudimos cargar los eventos"
          description={remote.error.message}
          action={<Button onClick={remote.reload}>Reintentar</Button>}
        />
      ) : remote.data?.items.length ? (
        <>
          <p className="muted small">
            {remote.data.total} oportunidades publicadas
          </p>
          <div className={s.cards}>
            {remote.data.items.map((event) => (
              <article className={s.card} key={event.id}>
                <div>
                  <Badge tone="green">
                    {eventCategoryLabel[event.category]}
                  </Badge>
                </div>
                <h2>{event.title}</h2>
                <p>{event.university}</p>
                <div className={s.roles}>
                  <strong>Fecha límite</strong>
                  <p>{formatDate(event.deadline)}</p>
                </div>
                <a href={event.url} target="_blank" rel="noopener noreferrer">
                  Visitar sitio oficial ↗
                </a>
                {user?.role === "admin" && user.email_verified && (
                  <Link href={`/eventos/${event.id}/editar`}>
                    Editar evento
                  </Link>
                )}
              </article>
            ))}
          </div>
          <Pagination
            page={page}
            pageSize={12}
            total={remote.data.total}
            onChange={setPage}
          />
        </>
      ) : (
        <StatePanel
          kind="empty"
          title="Próximamente, nuevas oportunidades"
          description="Aún no hay eventos publicados. Vuelve a consultar el directorio pronto."
        />
      )}
    </>
  );
}
export function EventEditor({ id }: { id?: string }) {
  const { user } = useSession();
  const remote = useRemote<AcademicEvent>(id ? `/events/${id}` : null);
  return (
    <ParticipationGate>
      {user?.role !== "admin" ? (
        <StatePanel
          kind="error"
          title="Esta sección es para administradores"
          description="Puedes consultar todas las oportunidades en el directorio."
          action={<Link href="/eventos">Ver eventos</Link>}
        />
      ) : id && remote.loading ? (
        <StatePanel kind="loading" title="Cargando evento…" />
      ) : id && remote.error ? (
        <StatePanel
          kind="error"
          title="No pudimos cargar el evento"
          description={remote.error.message}
          action={<Button onClick={remote.reload}>Reintentar</Button>}
        />
      ) : (
        <EventForm event={remote.data} />
      )}
    </ParticipationGate>
  );
}
function localDate(value: string | null | undefined) {
  if (!value) return "";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return "";
  return new Date(d.getTime() - d.getTimezoneOffset() * 60000)
    .toISOString()
    .slice(0, 16);
}
function EventForm({ event }: { event: AcademicEvent | null }) {
  const router = useRouter();
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  async function save(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const d = new FormData(e.currentTarget);
    const title = String(d.get("title")).trim(),
      university = String(d.get("university")).trim(),
      url = String(d.get("url")).trim(),
      deadline = String(d.get("deadline"));
    if (!title || !university) {
      setError("Completa el título y la universidad.");
      return;
    }
    try {
      const parsed = new URL(url);
      if (!["https:", "http:"].includes(parsed.protocol)) throw new Error();
    } catch {
      setError("Indica un enlace oficial HTTP o HTTPS válido.");
      return;
    }
    const body = {
      title,
      university,
      url,
      category: String(d.get("category")) as EventCategory,
      deadline: deadline ? new Date(deadline).toISOString() : null,
    };
    setError("");
    setBusy(true);
    try {
      if (event) await api.put(`/events/${event.id}`, body);
      else await api.post("/events", body);
      router.push("/eventos");
    } catch (e) {
      setError(errorMessage(e));
      setBusy(false);
    }
  }
  return (
    <div className="content-narrow">
      <PageHeader
        eyebrow="ADMINISTRACIÓN"
        title={event ? "Editar evento" : "Publicar oportunidad"}
        description="Comparte información oficial y una fecha límite actualizada."
      />
      <form className={`panel ${s.form}`} onSubmit={save}>
        <label className="form-field">
          Título
          <input
            name="title"
            required
            maxLength={200}
            defaultValue={event?.title}
          />
        </label>
        <label className="form-field">
          Tipo
          <select name="category" defaultValue={event?.category || "congreso"}>
            {Object.entries(eventCategoryLabel).map(([v, l]) => (
              <option key={v} value={v}>
                {l}
              </option>
            ))}
          </select>
        </label>
        <label className="form-field">
          Universidad u organización
          <input
            name="university"
            required
            maxLength={200}
            defaultValue={event?.university}
          />
        </label>
        <label className="form-field">
          Fecha límite (opcional)
          <input
            name="deadline"
            type="datetime-local"
            defaultValue={localDate(event?.deadline)}
          />
          <small>Se usa tu zona horaria local.</small>
        </label>
        <label className="form-field">
          Enlace oficial
          <input
            name="url"
            type="url"
            required
            defaultValue={event?.url}
            placeholder="https://"
          />
        </label>
        {error && (
          <p role="alert" className="form-error">
            {error}
          </p>
        )}
        <div className="form-actions">
          <Button type="submit" disabled={busy}>
            {busy
              ? "Guardando…"
              : event
                ? "Guardar cambios"
                : "Publicar evento"}
          </Button>
          <Link href="/eventos">Cancelar</Link>
        </div>
      </form>
    </div>
  );
}
