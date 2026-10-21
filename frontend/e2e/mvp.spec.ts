import {
  test,
  expect,
  type Page,
  type APIRequestContext,
} from "@playwright/test";
const backend = "http://127.0.0.1:18000";
const password = "UI-test-password-123";

async function register(
  page: Page,
  request: APIRequestContext,
  email: string,
  name: string,
) {
  await page.goto("/registro");
  await page.getByLabel("Nombre completo").fill(name);
  await page.getByLabel("Correo institucional").fill(email);
  await page.getByLabel("Universidad", { exact: true }).fill("UNAJ");
  await page
    .getByLabel("Carrera", { exact: true })
    .fill("Ingeniería de Sistemas");
  await page.getByLabel("Contraseña", { exact: true }).fill(password);
  await page.getByRole("button", { name: "Crear cuenta", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Tu cuenta está creada" }),
  ).toBeVisible();
  await expect(
    page.getByText(/envío de correo todavía no está habilitado/),
  ).toBeVisible();
  const mail = await request.get(`${backend}/__test__/verification`, {
    params: { email },
  });
  expect(mail.ok()).toBeTruthy();
  const { token } = await mail.json();
  await page.goto(`/verificar?token=${encodeURIComponent(token)}`);
  await page
    .getByRole("button", { name: "Verificar mi correo", exact: true })
    .click();
  await expect(page.getByRole("status")).toContainText("Correo verificado");
}
async function login(page: Page, email: string, next = "/") {
  await page.goto(`/login?next=${encodeURIComponent(next)}`);
  await page.getByLabel("Correo institucional").fill(email);
  await page.getByLabel("Contraseña", { exact: true }).fill(password);
  await page
    .getByRole("button", { name: "Iniciar sesión", exact: true })
    .click();
  await expect(page).toHaveURL(
    new RegExp(`${next === "/" ? "/$" : next.replace(/[?]/g, "\\?")}`),
  );
}

test("two students complete project, application, decision and private conversation", async ({
  page,
  browser,
  request,
}) => {
  test.setTimeout(120000);
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  const run = Date.now().toString();
  const ownerEmail = `owner-${run}@unaj.edu.pe`;
  const candidateEmail = `candidate-${run}@unaj.edu.pe`;
  await register(page, request, ownerEmail, "Valeria Quispe");
  await login(page, ownerEmail, "/perfil");
  const cookie = (await page.context().cookies()).find(
    (item) => item.name === "nexo_session",
  );
  expect(cookie?.httpOnly).toBe(true);
  expect(await page.evaluate(() => document.cookie)).not.toContain(
    "nexo_session",
  );
  await page.getByLabel("Nombre completo").fill("Valeria Investigadora");
  await page
    .getByLabel("Sobre mí")
    .fill("Investigo soluciones de tecnología para mi comunidad.");
  await page
    .getByLabel("Habilidades", { exact: true })
    .fill("Python, Investigación");
  await page
    .getByRole("button", { name: "Guardar perfil", exact: true })
    .click();
  await expect(page.getByRole("status")).toContainText("Tu perfil se guardó");
  await expect(page.locator(".profile-link")).toContainText(
    "Valeria Investigadora",
  );
  await page.goto("/proyectos/nuevo");
  const title = `Sensores para cuidar el agua ${run}`;
  await page.getByLabel("Título", { exact: true }).fill(title);
  await page
    .getByLabel("Resumen e hipótesis")
    .fill(
      "Construimos una red de sensores para estudiar el consumo de agua y detectar oportunidades de ahorro en el campus.",
    );
  await page
    .getByLabel("Categoría", { exact: true })
    .fill("Tecnología ambiental");
  await page
    .getByLabel("Habilidades (separadas por comas)")
    .fill("Python, IoT");
  await page
    .getByLabel("Roles buscados (separados por comas)")
    .fill("Backend, Investigación");
  await page
    .getByRole("combobox", { name: /Estado/ })
    .selectOption("recruiting");
  await page
    .getByRole("button", { name: "Publicar proyecto", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { level: 1, name: title }),
  ).toBeVisible();
  const projectUrl = page.url();
  const candidateContext = await browser.newContext();
  const candidate = await candidateContext.newPage();
  await register(candidate, request, candidateEmail, "Diego Flores");
  await login(candidate, candidateEmail);
  await candidate.goto(projectUrl);
  const proposal = "Me gustaría aportar al backend y al análisis de datos.";
  await candidate.getByLabel("¿Cómo te gustaría aportar?").fill(proposal);
  await candidate
    .getByRole("button", { name: "Solicitar unirme al equipo" })
    .click();
  await expect(candidate.getByRole("status")).toContainText(
    "Tu solicitud fue enviada",
  );
  const conversationLink = await candidate
    .getByRole("link", { name: "Conversar con el creador" })
    .getAttribute("href");
  expect(conversationLink).toContain("application=");
  const applicationId = new URL(
    conversationLink!,
    "http://127.0.0.1:13000",
  ).searchParams.get("application");
  await page.goto("/solicitudes?scope=received");
  await expect(page.getByText(proposal, { exact: true })).toBeVisible();
  await page
    .getByRole("button", { name: "Aceptar solicitud", exact: true })
    .click();
  await expect(page.getByText("Aceptada", { exact: true })).toBeVisible();
  await candidate.goto("/notificaciones");
  await expect(
    candidate.getByRole("link", {
      name: "Tu solicitud fue aceptada",
      exact: true,
    }),
  ).toBeVisible();
  await candidate
    .getByRole("button", { name: "Marcar como leída", exact: true })
    .click();
  await expect(candidate.getByText("Leída", { exact: true })).toBeVisible();
  await candidate.goto(conversationLink!);
  await candidate
    .getByLabel("Mensaje", { exact: true })
    .fill("Hola, podemos comenzar con el diseño de la API.");
  await candidate
    .getByRole("button", { name: "Enviar mensaje", exact: true })
    .click();
  await expect(
    candidate.getByText("Hola, podemos comenzar con el diseño de la API.", {
      exact: true,
    }),
  ).toBeVisible();
  await page.goto(conversationLink!);
  await expect(
    page.getByText("Hola, podemos comenzar con el diseño de la API.", {
      exact: true,
    }),
  ).toBeVisible();
  await page
    .getByLabel("Mensaje", { exact: true })
    .fill("Perfecto, coordinemos los primeros pasos.");
  await page
    .getByRole("button", { name: "Enviar mensaje", exact: true })
    .click();
  await expect(
    page.getByText("Perfecto, coordinemos los primeros pasos.", {
      exact: true,
    }),
  ).toBeVisible();
  const outsiderContext = await browser.newContext();
  const outsider = await outsiderContext.newPage();
  await login(outsider, "ui-admin@unaj.edu.pe");
  const rooms = await page.request.get("/api/backend/conversations");
  const room = (await rooms.json()).items.find(
    (item: { application_id: string }) => item.application_id === applicationId,
  );
  const denied = await outsider.request.get(
    `/api/backend/conversations/${room.id}/messages`,
  );
  expect(denied.status()).toBe(404);
  await outsider.goto(`/conversaciones?conversation=${room.id}`);
  await expect(
    outsider.getByRole("alert").filter({ hasText: "No encontramos" }),
  ).toBeVisible();
  await expect(
    outsider.getByText("Perfecto, coordinemos los primeros pasos.", {
      exact: true,
    }),
  ).toHaveCount(0);
  await page.goto("/");
  await page.getByLabel("Buscar proyectos").fill(title);
  await page.getByRole("button", { name: "Buscar", exact: true }).click();
  await expect(
    page.getByRole("link", { name: title, exact: true }),
  ).toBeVisible();
  await page.evaluate(() => {
    window.scrollTo(0, 0);
    (document.activeElement as HTMLElement)?.blur();
  });
  await page.screenshot({ path: "/tmp/nexo-desktop.png", fullPage: true });
  expect(errors).toEqual([]);
  await outsiderContext.close();
  await candidateContext.close();
});

test("mobile, keyboard navigation, theme and real empty/error states", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
  await page.keyboard.press("Tab");
  await expect(
    page.getByRole("link", { name: "Saltar al contenido" }),
  ).toBeFocused();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  await page.getByRole("button", { name: "Abrir navegación" }).click();
  await page.getByRole("button", { name: "Modo oscuro" }).click();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  await page
    .getByRole("button", { name: "Cerrar navegación", exact: true })
    .first()
    .click();
  await page
    .getByLabel("Buscar proyectos")
    .fill("No existe este proyecto 000xyz");
  await page.getByRole("button", { name: "Buscar", exact: true }).click();
  await expect(page.getByRole("status")).toContainText(
    "Aquí puede empezar una buena idea",
  );
  await page.evaluate(() => {
    window.scrollTo(0, 0);
    (document.activeElement as HTMLElement)?.blur();
  });
  await page.screenshot({ path: "/tmp/nexo-mobile-dark.png", fullPage: true });
  await page.reload();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  await page.getByLabel("Buscar proyectos").fill("Simular fallo temporal");
  await page.route("**/api/backend/projects?*", (route) =>
    route.fulfill({
      status: 503,
      contentType: "application/json",
      body: JSON.stringify({ detail: "Temporary failure" }),
    }),
  );
  await page.getByRole("button", { name: "Buscar", exact: true }).click();
  await expect(
    page
      .getByRole("alert")
      .filter({ hasText: "No pudimos cargar los proyectos" }),
  ).toBeVisible();
});

test("verified administrator publishes and edits a public academic event", async ({ page, browser }) => {
  await login(page, "ui-admin@unaj.edu.pe", "/eventos");
  await page.getByRole("link", { name: "Publicar evento", exact: true }).click();
  const title = `Encuentro de investigación ${Date.now()}`;
  await page.getByLabel("Título", { exact: true }).fill(title);
  await page.getByRole("combobox", { name: /Tipo/ }).selectOption("congreso");
  await page.getByLabel("Universidad u organización").fill("UNAJ");
  await page.getByLabel("Fecha límite (opcional)").fill("2027-03-20T12:00");
  await page.getByLabel("Enlace oficial").fill("https://unaj.edu.pe/investigacion");
  await page.getByRole("button", { name: "Publicar evento", exact: true }).click();
  await expect(page.getByRole("heading", { name: title, exact: true })).toBeVisible();
  const card = page.getByRole("article").filter({ has: page.getByRole("heading", { name: title, exact: true }) });
  await card.getByRole("link", { name: "Editar evento", exact: true }).click();
  await page.getByLabel("Título", { exact: true }).fill(`${title} · actualizado`);
  await page.getByRole("button", { name: "Guardar cambios", exact: true }).click();
  await expect(page.getByRole("heading", { name: `${title} · actualizado`, exact: true })).toBeVisible();
  const anonymousContext = await browser.newContext(); const anonymous = await anonymousContext.newPage();
  await anonymous.goto("/eventos");
  await expect(anonymous.getByRole("heading", { name: `${title} · actualizado`, exact: true })).toBeVisible();
  await expect(anonymous.getByRole("link", { name: "Publicar evento", exact: true })).toHaveCount(0);
  await anonymous.goto("/eventos/nuevo");
  await expect(anonymous.getByRole("heading", { name: "Comparte tu próxima idea" })).toBeVisible();
  await anonymousContext.close();
});
