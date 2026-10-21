"use client";
import Link from "next/link";
import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { api, ApiError, errorMessage } from "@/lib/api";
import { useSession } from "@/lib/session";
import { useRemote } from "@/lib/use-remote";
import { commaList, projectStatusLabel } from "@/lib/format";
import type { Application, Project, ProjectStatus } from "@/lib/types";
import { Badge, Button, PageHeader, StatePanel } from "@/components/ui";
import s from "./discovery.module.css";
export function ParticipationGate({ children }: { children: React.ReactNode }) {
  const { user, loading } = useSession();
  if (loading)
    return <StatePanel kind="loading" title="Comprobando tu cuenta…" />;
  if (!user)
    return (
      <StatePanel
        kind="empty"
        title="Comparte tu próxima idea"
        description="Inicia sesión con tu cuenta institucional para participar."
        action={
          <Link className="button button-primary" href="/login">
            Iniciar sesión
          </Link>
        }
      />
    );
  if (!user.email_verified)
    return (
      <StatePanel
        kind="empty"
        title="Verifica tu correo para participar"
        description="Puedes seguir explorando mientras verificas tu identidad institucional."
        action={<Link href="/verificar">Verificar correo</Link>}
      />
    );
  return <>{children}</>;
}
export function ProjectDetail({ id }: { id: string }) {
  const { user } = useSession();
  const remote = useRemote<Project>(`/projects/${id}`);
  const [error, setError] = useState("");
  const [sent, setSent] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  async function apply(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const message = String(
      new FormData(e.currentTarget).get("message") || "",
    ).trim();
    if (!message || message.length > 2000) {
      setError(
        "Escribe entre 1 y 2000 caracteres para contar cómo te gustaría aportar.",
      );
      return;
    }
    setBusy(true);
    setError("");
    try {
      const result = await api.post<Application>(
        `/applications/projects/${id}`,
        { message },
      );
      setSent(result.id);
    } catch (e) {
      setError(
        e instanceof ApiError && e.status === 409
          ? "Ya existe una solicitud pendiente o aceptada, o el proyecto dejó de buscar equipo. Consulta tus solicitudes."
          : errorMessage(e),
      );
    } finally {
      setBusy(false);
    }
  }
  if (remote.loading)
    return <StatePanel kind="loading" title="Cargando proyecto…" />;
  if (remote.error || !remote.data)
    return (
      <StatePanel
        kind="error"
        title="No pudimos abrir este proyecto"
        description={remote.error?.message}
        action={<Button onClick={remote.reload}>Reintentar</Button>}
      />
    );
  const p = remote.data;
  return (
    <>
      <Link href="/">← Explorar proyectos</Link>
      <PageHeader
        eyebrow={p.category}
        title={p.title}
        description={p.university}
        actions={
          user?.id === p.author_id && user.email_verified ? (
            <Link
              className="button button-secondary"
              href={`/proyectos/${id}/editar`}
            >
              Editar proyecto
            </Link>
          ) : undefined
        }
      />
      <div className={s.detail}>
        <article className="panel">
          <Badge tone={p.status === "recruiting" ? "green" : "neutral"}>
            {projectStatusLabel[p.status]}
          </Badge>
          <h2>La idea</h2>
          <p className={s.prose}>{p.description}</p>
          <h2>Habilidades que suman</h2>
          <div className={s.meta}>
            {p.skills.length ? (
              p.skills.map((v) => <Badge key={v}>{v}</Badge>)
            ) : (
              <span>Sin habilidades específicas.</span>
            )}
          </div>
          <h2>Roles que buscamos</h2>
          <ul>
            {p.required_roles.map((v) => (
              <li key={v}>{v}</li>
            ))}
          </ul>
        </article>
        <aside className="panel">
          <h2>Construyamos en equipo</h2>
          {user?.id === p.author_id ? (
            <>
              <p>Este es tu proyecto. Revisa quién quiere colaborar contigo.</p>
              <Link href="/solicitudes?scope=received">
                Ver solicitudes recibidas →
              </Link>
            </>
          ) : p.status !== "recruiting" ? (
            <p className="muted">
              Este proyecto no está recibiendo solicitudes por ahora.
            </p>
          ) : sent ? (
            <div role="status">
              <p className="form-success">Tu solicitud fue enviada.</p>
              <Link href={`/conversaciones?application=${sent}`}>
                Conversar con el creador →
              </Link>
            </div>
          ) : (
            <ParticipationGate>
              <form className={s.form} onSubmit={apply}>
                <label className="form-field">
                  ¿Cómo te gustaría aportar?
                  <textarea
                    name="message"
                    required
                    maxLength={2000}
                    rows={6}
                    placeholder="Cuéntale al equipo sobre tu experiencia e interés."
                  />
                </label>
                {error && (
                  <p className="form-error" role="alert">
                    {error}{" "}
                    <Link href="/solicitudes?scope=sent">
                      Ver mis solicitudes
                    </Link>
                  </p>
                )}
                <Button disabled={busy} type="submit">
                  {busy ? "Enviando…" : "Solicitar unirme al equipo"}
                </Button>
              </form>
            </ParticipationGate>
          )}
        </aside>
      </div>
    </>
  );
}
export function ProjectEditor({ id }: { id?: string }) {
  const { user } = useSession();
  const remote = useRemote<Project>(id ? `/projects/${id}` : null);
  return (
    <ParticipationGate>
      {id && remote.loading ? (
        <StatePanel kind="loading" title="Cargando proyecto…" />
      ) : id && remote.error ? (
        <StatePanel
          kind="error"
          title="No pudimos cargar el proyecto"
          description={remote.error.message}
          action={<Button onClick={remote.reload}>Reintentar</Button>}
        />
      ) : id && remote.data?.author_id !== user?.id ? (
        <StatePanel
          kind="error"
          title="Solo el autor puede editar este proyecto"
        />
      ) : (
        <ProjectForm key={id || "new"} project={remote.data} />
      )}
    </ParticipationGate>
  );
}
function ProjectForm({ project }: { project: Project | null }) {
  const router = useRouter();
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const d = new FormData(e.currentTarget);
    const roles = commaList(String(d.get("roles")));
    const skills = commaList(String(d.get("skills")));
    if (!roles.length || roles.length > 30 || skills.length > 30) {
      setError("Indica entre 1 y 30 roles y hasta 30 habilidades.");
      return;
    }
    const body = {
      title: String(d.get("title")).trim(),
      description: String(d.get("description")).trim(),
      category: String(d.get("category")).trim(),
      required_roles: roles,
      skills,
      status: String(d.get("status")) as ProjectStatus,
    };
    if (!body.title || !body.description || !body.category) {
      setError("Completa los campos sin usar solo espacios.");
      return;
    }
    setBusy(true);
    setError("");
    try {
      const saved = project
        ? await api.put<Project>(`/projects/${project.id}`, body)
        : await api.post<Project>("/projects", body);
      router.push(`/proyectos/${saved.id}`);
    } catch (e) {
      setError(errorMessage(e));
      setBusy(false);
    }
  }
  return (
    <div className="content-narrow">
      <PageHeader
        eyebrow="DE LA IDEA AL EQUIPO"
        title={project ? "Editar proyecto" : "Comparte tu idea"}
        description="Explica qué quieres construir y a quién necesitas para hacerlo realidad."
      />
      <form className={`panel ${s.form}`} onSubmit={submit}>
        <label className="form-field">
          Título
          <input
            name="title"
            required
            maxLength={200}
            defaultValue={project?.title}
          />
        </label>
        <label className="form-field">
          Resumen e hipótesis
          <textarea
            name="description"
            required
            maxLength={10000}
            rows={8}
            defaultValue={project?.description}
          />
        </label>
        <label className="form-field">
          Categoría
          <input
            name="category"
            required
            maxLength={100}
            placeholder="Ej. Inteligencia artificial"
            defaultValue={project?.category}
          />
        </label>
        <label className="form-field">
          Habilidades (separadas por comas)
          <input
            name="skills"
            defaultValue={project?.skills.join(", ")}
            placeholder="Python, diseño, investigación"
          />
        </label>
        <label className="form-field">
          Roles buscados (separados por comas)
          <input
            name="roles"
            required
            defaultValue={project?.required_roles.join(", ")}
            placeholder="Backend, investigación"
          />
        </label>
        <label className="form-field">
          Estado
          <select name="status" defaultValue={project?.status || "idea"}>
            {Object.entries(projectStatusLabel).map(([v, l]) => (
              <option key={v} value={v}>
                {l}
              </option>
            ))}
          </select>
        </label>
        {error && (
          <p className="form-error" role="alert">
            {error}
          </p>
        )}
        <div className="form-actions">
          <Button type="submit" disabled={busy}>
            {busy
              ? "Guardando…"
              : project
                ? "Guardar cambios"
                : "Publicar proyecto"}
          </Button>
          <Link href={project ? `/proyectos/${project.id}` : "/"}>
            Cancelar
          </Link>
        </div>
      </form>
    </div>
  );
}
