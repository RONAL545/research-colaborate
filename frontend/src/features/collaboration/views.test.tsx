import {
  act,
  fireEvent,
  render,
  screen,
  waitFor,
  cleanup,
} from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import {
  ApplicationsView,
  ConversationsView,
  NotificationsView,
} from "./views";
const mocks = vi.hoisted(() => ({
  user: { id: "author", email_verified: true } as {
    id: string;
    email_verified: boolean;
  } | null,
  search: "",
  get: vi.fn(),
  patch: vi.fn(),
  post: vi.fn(),
}));
vi.mock("next/navigation", () => ({
  useSearchParams: () => new URLSearchParams(mocks.search),
}));
vi.mock("@/lib/session", () => ({
  useSession: () => ({
    user: mocks.user,
    loading: false,
    error: null,
    refresh: vi.fn(),
  }),
}));
vi.mock("@/lib/api", async (original) => ({
  ...(await original<typeof import("@/lib/api")>()),
  api: { get: mocks.get, post: mocks.post, patch: mocks.patch },
}));
const application = {
  id: "application",
  project_id: "project",
  applicant_id: "applicant",
  status: "pending",
  message: "Quiero aportar",
  created_at: "2026-10-21T12:00:00Z",
};
const page = (items: unknown[], total = items.length) => ({
  items,
  total,
  page: 1,
  page_size: 20,
});
beforeEach(() => {
  mocks.user = { id: "author", email_verified: true };
  mocks.search = "";
  mocks.get.mockReset();
  mocks.patch.mockReset();
  mocks.post.mockReset();
  mocks.get.mockImplementation((p: string) =>
    Promise.resolve(
      p.startsWith("/projects/") ? { title: "Proyecto académico" } : page([]),
    ),
  );
});
afterEach(() => {
  cleanup();
  vi.useRealTimers();
});
describe("colaboración privada", () => {
  it("pide sesión sin consultar datos privados", () => {
    mocks.user = null;
    render(<ApplicationsView />);
    expect(screen.getByText("Este espacio es privado")).toBeInTheDocument();
    expect(mocks.get).not.toHaveBeenCalled();
  });
  it("decide solicitudes recibidas", async () => {
    mocks.search = "scope=received";
    mocks.get.mockImplementation((p: string) =>
      Promise.resolve(
        p.startsWith("/projects/")
          ? { title: "Proyecto" }
          : page([application]),
      ),
    );
    render(<ApplicationsView />);
    fireEvent.click(await screen.findByText("Aceptar solicitud"));
    await waitFor(() =>
      expect(mocks.patch).toHaveBeenCalledWith("/applications/application", {
        status: "accepted",
      }),
    );
  });
  it("muestra errores de decisión", async () => {
    mocks.search = "application=application";
    mocks.patch.mockRejectedValue(new Error("El estado cambió"));
    mocks.get.mockImplementation((p: string) =>
      Promise.resolve(
        p === "/applications/application"
          ? application
          : p.startsWith("/projects/")
            ? { title: "Proyecto" }
            : page([]),
      ),
    );
    render(<ApplicationsView />);
    fireEvent.click(await screen.findByText("Rechazar"));
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "El estado cambió",
    );
  });
  it("filtra notificaciones y marca lectura", async () => {
    mocks.get.mockResolvedValue(
      page([
        {
          id: "note",
          application_id: "application",
          kind: "application_received",
          read_at: null,
          created_at: application.created_at,
        },
      ]),
    );
    render(<NotificationsView />);
    fireEvent.click(await screen.findByText("Marcar como leída"));
    await waitFor(() =>
      expect(mocks.patch).toHaveBeenCalledWith("/notifications/note/read"),
    );
    fireEvent.click(screen.getByLabelText("Mostrar solo sin leer"));
    await waitFor(() =>
      expect(
        mocks.get.mock.calls.some(([p]) => p.includes("unread_only=true")),
      ).toBe(true),
    );
  });
  it("conserva borrador con polling y cancela al desmontar", async () => {
    mocks.search = "conversation=room";
    const view = render(<ConversationsView />);
    const draft = await screen.findByLabelText("Mensaje");
    fireEvent.change(draft, { target: { value: "Mi borrador" } });
    vi.useFakeTimers();
    await act(async () => {
      vi.advanceTimersByTime(10000);
    });
    expect(draft).toHaveValue("Mi borrador");
    const signal = mocks.get.mock.calls.find(([p]) =>
      p.startsWith("/conversations/room/messages"),
    )?.[1] as AbortSignal;
    view.unmount();
    expect(signal.aborted).toBe(true);
  });
  it("conserva borrador ante fallo de envío", async () => {
    mocks.search = "conversation=room";
    mocks.post.mockRejectedValue(new Error("No se pudo enviar"));
    render(<ConversationsView />);
    fireEvent.change(await screen.findByLabelText("Mensaje"), {
      target: { value: "Mensaje importante" },
    });
    fireEvent.click(screen.getByText("Enviar mensaje"));
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "No se pudo enviar",
    );
    expect(screen.getByLabelText("Mensaje")).toHaveValue("Mensaje importante");
  });
  it("oculta compositor si no hay acceso", async () => {
    mocks.search = "conversation=private";
    mocks.get.mockImplementation((p: string) =>
      p.includes("/messages")
        ? Promise.reject(new Error("No tienes acceso"))
        : Promise.resolve(page([])),
    );
    render(<ConversationsView />);
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "No tienes acceso",
    );
    expect(screen.queryByLabelText("Mensaje")).not.toBeInTheDocument();
  });
  it("pagina mensajes recientes sin salto automático", async () => {
    mocks.search = "conversation=room";
    mocks.get.mockImplementation((p: string) =>
      Promise.resolve(
        p.includes("/messages")
          ? page(
              [
                {
                  id: "m",
                  sender_id: "author",
                  content: "Mensaje antiguo",
                  created_at: application.created_at,
                },
              ],
              42,
            )
          : page([]),
      ),
    );
    render(<ConversationsView />);
    fireEvent.click(await screen.findByText("Ir a los últimos mensajes"));
    await waitFor(() =>
      expect(
        mocks.get.mock.calls.some(([p]) => p.includes("messages?page=3")),
      ).toBe(true),
    );
  });
  it("muestra la última página después de enviar desde el histórico", async () => {
    mocks.search = "conversation=room";
    mocks.post.mockResolvedValue({ id: "new" });
    mocks.get.mockImplementation((p: string) =>
      Promise.resolve(p.includes("/messages") ? page([], 40) : page([])),
    );
    render(<ConversationsView />);
    fireEvent.change(await screen.findByLabelText("Mensaje"), {
      target: { value: "Nuevo mensaje" },
    });
    fireEvent.click(screen.getByText("Enviar mensaje"));
    await waitFor(() =>
      expect(
        mocks.get.mock.calls.some(([p]) => p.includes("messages?page=3")),
      ).toBe(true),
    );
    expect(screen.getByLabelText("Mensaje")).toHaveValue("");
  });
  it("borra la vista privada al perder sesión", async () => {
    mocks.search = "conversation=room";
    const view = render(<ConversationsView />);
    await screen.findByLabelText("Mensaje");
    mocks.user = null;
    view.rerender(<ConversationsView />);
    expect(screen.queryByLabelText("Mensaje")).not.toBeInTheDocument();
    expect(screen.getByText("Este espacio es privado")).toBeInTheDocument();
  });
});
