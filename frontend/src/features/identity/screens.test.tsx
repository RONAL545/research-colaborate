import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { LoginScreen, ProfileScreen, RegisterScreen, ResendVerification, safeNext, VerifyScreen } from "./screens";
import { ApiError } from "@/lib/api";
const mocks = vi.hoisted(() => ({ post: vi.fn(), put: vi.fn(), login: vi.fn(), refresh: vi.fn(), replace: vi.fn(), params: new URLSearchParams(), user: null as null | Record<string, unknown> }));
vi.mock("next/navigation", () => ({ useRouter: () => ({ replace: mocks.replace }), useSearchParams: () => mocks.params }));
vi.mock("@/lib/session", () => ({ useSession: () => ({ user: mocks.user, loading: false, error: null, login: mocks.login, refresh: mocks.refresh }) }));
vi.mock("@/lib/api", async (original) => ({ ...(await original<typeof import("@/lib/api")>()), api: { post: mocks.post, put: mocks.put } }));
afterEach(cleanup);
beforeEach(() => { vi.clearAllMocks(); mocks.params = new URLSearchParams(); mocks.user = null; });
function fill(label: string, value: string) { fireEvent.change(screen.getByLabelText(label), { target: { value } }); }
function register() { fill("Nombre completo", "Ana"); fill("Correo institucional", "ana@universidad.edu"); fill("Universidad", "Universidad"); fill("Carrera", "Ingeniería"); fill("Contraseña", "contraseña-segura"); fireEvent.click(screen.getByRole("button", { name: "Crear cuenta" })); }
const profile = { id: "ana", name: "Ana", email: "ana@u.edu", university: "U", career: "C", bio: "", skills: [], email_verified: true, role: "student" };
describe("identidad", () => {
  it("rechaza redirecciones externas y conserva rutas locales", () => {
    for (const value of ["https://evil.test", "//evil.test", "/\\evil.test", "/\n/evil.test", null]) expect(safeNext(value)).toBe("/");
    expect(safeNext("/proyectos/nuevo?from=login")).toBe("/proyectos/nuevo?from=login");
  });
  it("inicia sesión con next seguro", async () => {
    mocks.params.set("next", "//evil.test"); mocks.login.mockResolvedValue(undefined); render(<LoginScreen />);
    fill("Correo institucional", "estudiante@universidad.edu"); fill("Contraseña", "contraseña-segura"); fireEvent.click(screen.getByRole("button", { name: "Iniciar sesión" }));
    await waitFor(() => expect(mocks.replace).toHaveBeenCalledWith("/"));
    expect(mocks.login).toHaveBeenCalledWith("estudiante@universidad.edu", "contraseña-segura");
  });
  it("explica credenciales inválidas sin navegar", async () => {
    mocks.login.mockRejectedValue(new ApiError(401, "401")); render(<LoginScreen />); fill("Correo institucional", "a@u.edu"); fill("Contraseña", "incorrecta"); fireEvent.click(screen.getByRole("button", { name: "Iniciar sesión" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("no son correctos"); expect(mocks.replace).not.toHaveBeenCalled();
  });
  it("registra solo datos permitidos y no finge envío de correo", async () => {
    mocks.post.mockResolvedValue({}); render(<RegisterScreen />); register();
    expect(await screen.findByRole("heading", { name: "Tu cuenta está creada" })).toBeInTheDocument();
    expect(mocks.post).toHaveBeenCalledWith("/auth/register", { name: "Ana", email: "ana@universidad.edu", university: "Universidad", career: "Ingeniería", password: "contraseña-segura" });
    expect(screen.getByText(/El envío de correo todavía/)).toBeInTheDocument();
  });
  it("muestra rechazo institucional sin éxito falso", async () => {
    mocks.post.mockRejectedValue(new ApiError(422, "422", "Institutional domain required")); render(<RegisterScreen />); register();
    expect(await screen.findByRole("alert")).toHaveTextContent("institución habilitada");
  });
  it("verifica token únicamente tras confirmación y respuesta real", async () => {
    mocks.params.set("token", "valid-token"); mocks.post.mockResolvedValue({}); render(<VerifyScreen />); expect(mocks.post).not.toHaveBeenCalled(); fireEvent.click(screen.getByRole("button", { name: "Verificar mi correo" }));
    expect(await screen.findByRole("status")).toHaveTextContent("Correo verificado"); expect(mocks.post).toHaveBeenCalledWith("/auth/verify", { token: "valid-token" }); expect(mocks.refresh).toHaveBeenCalled();
  });
  it("permite reenvío tras enlace vencido", async () => {
    mocks.params.set("token", "expired"); mocks.post.mockRejectedValue(new ApiError(400, "400")); render(<VerifyScreen />); fireEvent.click(screen.getByRole("button", { name: "Verificar mi correo" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("ha vencido"); expect(screen.getByRole("button", { name: "Solicitar enlace" })).toBeInTheDocument(); expect(screen.queryByText(/Correo verificado/)).not.toBeInTheDocument();
  });
  it("solicita reenvío con respuesta genérica honesta", async () => {
    mocks.post.mockResolvedValue({}); render(<ResendVerification />); fill("Correo institucional", "ana@u.edu"); fireEvent.click(screen.getByRole("button", { name: "Solicitar enlace" }));
    expect(await screen.findByRole("status")).toHaveTextContent("no podemos confirmar la entrega");
  });
  it("no muestra perfil privado sin sesión", () => { render(<ProfileScreen />); expect(screen.getByRole("link", { name: "Iniciar sesión" })).toHaveAttribute("href", "/login?next=/perfil"); expect(screen.queryByLabelText("Nombre completo")).not.toBeInTheDocument(); });
  it("edita perfil propio y normaliza habilidades", async () => {
    mocks.user = profile; mocks.put.mockResolvedValue({}); render(<ProfileScreen />); fill("Habilidades", "Python, React, , Diseño "); fill("Sobre mí", "Me interesa investigar."); fireEvent.click(screen.getByRole("button", { name: "Guardar perfil" }));
    await waitFor(() => expect(mocks.put).toHaveBeenCalledWith("/auth/me", { name: "Ana", university: "U", career: "C", bio: "Me interesa investigar.", skills: ["Python", "React", "Diseño"] })); expect(mocks.refresh).toHaveBeenCalled();
  });
  it("impide más de 30 habilidades", () => {
    mocks.user = profile; render(<ProfileScreen />); fill("Habilidades", Array.from({ length: 31 }, (_, index) => `H${index}`).join(",")); fireEvent.click(screen.getByRole("button", { name: "Guardar perfil" })); expect(screen.getByRole("alert")).toHaveTextContent("hasta 30"); expect(mocks.put).not.toHaveBeenCalled();
  });
});
