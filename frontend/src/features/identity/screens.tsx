"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useState, type FormEvent } from "react";
import {
  Badge,
  Button,
  FieldError,
  PageHeader,
  StatePanel,
} from "@/components/ui";
import { api, ApiError, errorMessage } from "@/lib/api";
import { useSession } from "@/lib/session";
import type { Profile, ProfileInput } from "@/lib/types";

const deliveryEnabled =
  process.env.NEXT_PUBLIC_EMAIL_DELIVERY_ENABLED === "true";
export function safeNext(value: string | null): string {
  if (
    !value ||
    !value.startsWith("/") ||
    value.startsWith("//") ||
    value.includes("\\") ||
    /[\u0000-\u0020]/.test(value)
  )
    return "/";
  return value;
}
function identityError(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 401)
      return "El correo o la contraseña no son correctos.";
    if (error.detail === "Institutional domain required")
      return "Usa un correo de una institución habilitada.";
    if (error.detail === "Email already registered")
      return "Este correo ya está registrado. Inicia sesión.";
    if (error.status === 400)
      return "El enlace no es válido, ha vencido o ya se utilizó. Solicita uno nuevo.";
  }
  return errorMessage(error);
}
function DeliveryNotice() {
  return !deliveryEnabled ? (
    <p className="notice">
      El envío de correo todavía no está habilitado. Puedes explorar proyectos
      mientras se configura; publicar y postularte requiere verificar tu cuenta.
    </p>
  ) : null;
}
export function LoginScreen() {
  const { login } = useSession();
  const router = useRouter();
  const params = useSearchParams();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    setBusy(true);
    setError(null);
    try {
      await login(
        String(data.get("email")).trim(),
        String(data.get("password")),
      );
      router.replace(safeNext(params.get("next")));
    } catch (failure) {
      setError(identityError(failure));
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className="auth-panel">
      <PageHeader
        eyebrow="TU COMUNIDAD ACADÉMICA"
        title="Qué bueno verte"
        description="Vuelve a tus ideas, tu equipo y tus próximas oportunidades."
      />
      <form onSubmit={submit}>
        <EmailField />
        <div className="form-field">
          <label htmlFor="password">Contraseña</label>
          <input
            id="password"
            name="password"
            type="password"
            autoComplete="current-password"
            required
          />
        </div>
        <FieldError message={error} />
        <Button disabled={busy} type="submit">
          {busy ? "Iniciando sesión…" : "Iniciar sesión"}
        </Button>
      </form>
      <p className="auth-footer">
        ¿Aún no tienes cuenta? <Link href="/registro">Regístrate</Link>
      </p>
      <p className="auth-footer">
        <Link href="/verificar">Verificar correo o solicitar otro enlace</Link>
      </p>
    </section>
  );
}
function EmailField({ value }: { value?: string }) {
  return (
    <div className="form-field">
      <label htmlFor="email">Correo institucional</label>
      <input
        id="email"
        name="email"
        type="email"
        autoComplete="email"
        required
        defaultValue={value}
        maxLength={254}
      />
    </div>
  );
}
export function RegisterScreen() {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [created, setCreated] = useState(false);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    setBusy(true);
    setError(null);
    try {
      await api.post<Profile>("/auth/register", {
        email: String(data.get("email")).trim(),
        password: String(data.get("password")),
        name: String(data.get("name")).trim(),
        university: String(data.get("university")).trim(),
        career: String(data.get("career")).trim(),
      });
      setCreated(true);
    } catch (failure) {
      setError(identityError(failure));
    } finally {
      setBusy(false);
    }
  }
  if (created)
    return (
      <section className="auth-panel">
        <PageHeader
          title="Tu cuenta está creada"
          description={
            deliveryEnabled
              ? "Si el servicio de correo está disponible, recibirás un enlace para verificar tu cuenta."
              : "El siguiente paso es verificar tu correo cuando esté habilitado el envío."
          }
        />
        <DeliveryNotice />
        <Link className="button button-primary" href="/login">
          Iniciar sesión
        </Link>
        <p className="auth-footer">
          <Link href="/">Explorar proyectos</Link>
        </p>
      </section>
    );
  return (
    <section className="auth-panel">
      <PageHeader
        eyebrow="EMPIEZA UNA CONEXIÓN"
        title="Tus ideas tienen lugar aquí"
        description="Crea tu perfil con el correo de tu institución."
      />
      <DeliveryNotice />
      <form onSubmit={submit}>
        <TextField
          name="name"
          label="Nombre completo"
          max={120}
          autoComplete="name"
        />
        <EmailField />
        <div className="form-row">
          <TextField name="university" label="Universidad" max={200} />
          <TextField name="career" label="Carrera" max={200} />
        </div>
        <div className="form-field">
          <label htmlFor="password">Contraseña</label>
          <input
            id="password"
            name="password"
            type="password"
            autoComplete="new-password"
            minLength={12}
            maxLength={128}
            required
            aria-describedby="password-help"
          />
          <small id="password-help">Entre 12 y 128 caracteres.</small>
        </div>
        <FieldError message={error} />
        <Button type="submit" disabled={busy}>
          {busy ? "Creando cuenta…" : "Crear cuenta"}
        </Button>
      </form>
      <p className="auth-footer">
        ¿Ya eres parte? <Link href="/login">Iniciar sesión</Link>
      </p>
    </section>
  );
}
function TextField({
  name,
  label,
  max,
  value,
  autoComplete,
}: {
  name: string;
  label: string;
  max: number;
  value?: string;
  autoComplete?: string;
}) {
  return (
    <div className="form-field">
      <label htmlFor={name}>{label}</label>
      <input
        id={name}
        name={name}
        required
        maxLength={max}
        defaultValue={value}
        autoComplete={autoComplete}
        pattern=".*\S.*"
        title="Escribe al menos un carácter que no sea un espacio."
      />
    </div>
  );
}
export function ResendVerification({ email }: { email?: string }) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    setBusy(true);
    setError(null);
    setSuccess(false);
    try {
      await api.post("/auth/resend-verification", {
        email: String(data.get("email")).trim(),
      });
      setSuccess(true);
    } catch (failure) {
      setError(identityError(failure));
    } finally {
      setBusy(false);
    }
  }
  return (
    <section>
      <h2>Solicitar otro enlace</h2>
      <DeliveryNotice />
      <form onSubmit={submit}>
        <EmailField value={email} />
        <FieldError message={error} />
        {success && (
          <p role="status" className="form-success">
            {deliveryEnabled
              ? "Solicitud registrada. Si la cuenta necesita verificación, el servicio intentará enviar un enlace nuevo."
              : "Solicitud registrada. El envío de correo está pendiente de habilitación; todavía no podemos confirmar la entrega de un enlace."}
          </p>
        )}
        <Button variant="secondary" disabled={busy} type="submit">
          {busy ? "Solicitando…" : "Solicitar enlace"}
        </Button>
      </form>
    </section>
  );
}
export function VerifyScreen() {
  const params = useSearchParams();
  const token = params.get("token");
  const { refresh } = useSession();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [verified, setVerified] = useState(false);
  async function verify() {
    if (!token || busy) return;
    setBusy(true);
    setError(null);
    try {
      await api.post("/auth/verify", { token });
      setVerified(true);
      await refresh();
    } catch (failure) {
      setError(identityError(failure));
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="content-narrow stack">
      <section className="panel">
        <PageHeader
          eyebrow="IDENTIDAD ACADÉMICA"
          title="Verifica tu correo"
          description="Una identidad verificada abre la puerta a publicar y formar equipos."
        />
        {verified ? (
          <p className="form-success" role="status">
            Correo verificado. Ya puedes participar con tu cuenta.{" "}
            <Link href="/perfil">Ir a mi perfil</Link>
          </p>
        ) : token ? (
          <>
            <p>
              Confirma que quieres verificar el correo asociado a este enlace.
            </p>
            <FieldError message={error} />
            <Button onClick={verify} disabled={busy}>
              {busy ? "Verificando…" : "Verificar mi correo"}
            </Button>
          </>
        ) : (
          <p className="muted">
            Abre el enlace de verificación de tu correo. Si necesitas uno nuevo,
            solicítalo aquí.
          </p>
        )}
      </section>
      {!verified && (
        <div className="panel">
          <ResendVerification />
        </div>
      )}
    </div>
  );
}
export function ProfileScreen() {
  const { user, loading, error, refresh } = useSession();
  const [saved, setSaved] = useState(false);
  if (loading) return <StatePanel kind="loading" title="Cargando tu perfil" />;
  if (error)
    return (
      <StatePanel
        kind="error"
        title="No pudimos cargar tu perfil"
        description={error}
        action={<Button onClick={() => void refresh()}>Reintentar</Button>}
      />
    );
  if (!user)
    return (
      <StatePanel
        kind="empty"
        title="Tu perfil empieza con una conexión"
        description="Inicia sesión para presentar tu experiencia y tus intereses."
        action={
          <Link className="button button-primary" href="/login?next=/perfil">
            Iniciar sesión
          </Link>
        }
      />
    );
  return (
    <>
      {saved && (
        <p className="form-success" role="status">
          Tu perfil se guardó.
        </p>
      )}
      <ProfileForm
        key={user.id}
        user={user}
        refresh={async () => {
          await refresh();
          setSaved(true);
        }}
      />
    </>
  );
}
function ProfileForm({
  user,
  refresh,
}: {
  user: Profile;
  refresh: () => Promise<void>;
}) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const skills = String(data.get("skills"))
      .split(",")
      .map((value) => value.trim())
      .filter(Boolean);
    setError(null);
    setSuccess(false);
    if (skills.length > 30) {
      setError("Puedes añadir hasta 30 habilidades, separadas por comas.");
      return;
    }
    setBusy(true);
    const input: ProfileInput = {
      name: String(data.get("name")).trim(),
      university: String(data.get("university")).trim(),
      career: String(data.get("career")).trim(),
      bio: String(data.get("bio")),
      skills,
    };
    try {
      await api.put<Profile>("/auth/me", input);
      setSuccess(true);
      await refresh();
    } catch (failure) {
      setError(errorMessage(failure));
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="content-narrow stack">
      <PageHeader
        eyebrow="TU IDENTIDAD"
        title="Lo que puedes aportar"
        description="Presenta tus intereses y las habilidades que quieres compartir con tu próximo equipo."
      />
      <div className="panel">
        <p>
          <strong>{user.email}</strong>
        </p>
        <Badge tone={user.email_verified ? "green" : "amber"}>
          {user.email_verified ? "Correo verificado" : "Verificación pendiente"}
        </Badge>
      </div>
      <form className="panel" onSubmit={submit}>
        <TextField
          name="name"
          label="Nombre completo"
          max={120}
          value={user.name}
          autoComplete="name"
        />
        <div className="form-row">
          <TextField
            name="university"
            label="Universidad"
            max={200}
            value={user.university}
          />
          <TextField
            name="career"
            label="Carrera"
            max={200}
            value={user.career}
          />
        </div>
        <div className="form-field">
          <label htmlFor="bio">Sobre mí</label>
          <textarea
            id="bio"
            name="bio"
            maxLength={2000}
            defaultValue={user.bio}
          />
          <small>Hasta 2000 caracteres.</small>
        </div>
        <div className="form-field">
          <label htmlFor="skills">Habilidades</label>
          <input
            id="skills"
            name="skills"
            defaultValue={user.skills.join(", ")}
            aria-describedby="skills-help"
          />
          <small id="skills-help">
            Separadas por comas. Máximo 30 habilidades.
          </small>
        </div>
        <FieldError message={error} />
        {success && (
          <p className="form-success" role="status">
            Tu perfil se guardó.{" "}
          </p>
        )}
        <div className="form-actions">
          <Button type="submit" disabled={busy}>
            {busy ? "Guardando…" : "Guardar perfil"}
          </Button>
        </div>
      </form>
      {!user.email_verified && (
        <div className="panel">
          <ResendVerification email={user.email} />
        </div>
      )}
    </div>
  );
}
