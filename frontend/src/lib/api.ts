export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public detail?: unknown,
  ) {
    super(message);
    this.name = "ApiError";
  }
}
const messages: Record<number, string> = {
  401: "Inicia sesión para continuar.",
  403: "Tu cuenta no tiene permiso para realizar esta acción.",
  404: "No encontramos este contenido o no tienes acceso.",
  409: "La acción no se pudo completar porque el estado cambió. Actualiza e inténtalo de nuevo.",
  422: "Revisa los datos del formulario.",
  429: "Hay demasiadas solicitudes. Inténtalo en unos momentos.",
};
async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`/api/backend${path}`, {
      ...init,
      credentials: "same-origin",
      cache: "no-store",
      headers: {
        ...(init.body ? { "Content-Type": "application/json" } : {}),
        ...init.headers,
      },
    });
  } catch (error) {
    if (error instanceof Error && error.name === "AbortError") throw error;
    throw new ApiError(
      0,
      "No pudimos conectar. Revisa tu conexión e inténtalo de nuevo.",
    );
  }
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    if (
      response.status === 401 &&
      path !== "/auth/login" &&
      typeof window !== "undefined"
    )
      window.dispatchEvent(new Event("session-expired"));
    throw new ApiError(
      response.status,
      messages[response.status] ??
        "El servicio no está disponible. Inténtalo de nuevo.",
      data?.detail,
    );
  }
  return data as T;
}
export const api = {
  request,
  get: <T>(path: string, signal?: AbortSignal) => request<T>(path, { signal }),
  post: <T>(path: string, body: unknown) =>
    request<T>(path, { method: "POST", body: JSON.stringify(body) }),
  put: <T>(path: string, body: unknown) =>
    request<T>(path, { method: "PUT", body: JSON.stringify(body) }),
  patch: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: "PATCH",
      ...(body === undefined ? {} : { body: JSON.stringify(body) }),
    }),
};
export function queryString(
  values: Record<string, string | number | boolean | undefined | null>,
): string {
  const params = new URLSearchParams();
  Object.entries(values).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "")
      params.set(key, String(value));
  });
  return params.size ? `?${params}` : "";
}
export function errorMessage(error: unknown): string {
  return error instanceof Error
    ? error.message
    : "Ocurrió un error. Inténtalo de nuevo.";
}
