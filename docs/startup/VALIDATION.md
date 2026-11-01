# Validación — presentación universitaria

Fecha: 2026-10-31 (America/Bogota). Coordinador, rama codex/university-presentation.
Alcance: nueva ruta /universidades, entrada en shell, desplazamiento vertical del menú,
README y kit de presentación. Sin modificaciones a módulos de agentes ni contratos API.

## Comandos y resultados

- `npm test --prefix frontend`: 43 passed.
- `npm run build --prefix frontend`: aprobado; repetido tras ajuste del menú.
- `npm run typecheck --prefix frontend`: aprobado.
- `.venv/bin/ruff check --config backend/pyproject.toml backend`: aprobado.
- Desde backend, `DATABASE_URL=postgresql+psycopg://mvp:mvp@127.0.0.1:55440/presentation_test ../.venv/bin/pytest -q`: 79 passed, 2 advertencias previas (Starlette/httpx y alias Pydantic).
- `DATABASE_URL=postgresql+psycopg://mvp:mvp@127.0.0.1:55440/presentation_browser_test PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/opt/google/chrome/chrome UI_E2E_PRODUCTION=1 npm run test:e2e --prefix frontend`: 3 passed, 19.2 s.
- Playwright directo sobre /universidades: ancla piloto, FAQ y ausencia de overflow
  horizontal a 390, 768 y 1440 px aprobados. Capturas desktop/móvil en /tmp.
- `git diff --check`: aprobado antes de commit.

PostgreSQL 16 exclusivo en contenedor nexo-presentation-host-test; bases nuevas,
sin datos reales. El backend de vista previa normal usa otra base vacía,
presentation_preview; no expone el buzón ni el administrador de pruebas.

## Incidentes y límites

La primera instancia con puerto Docker 55439 agotó el tiempo de conexión, también
por IP del bridge. Pytest se interrumpió sin resultado válido; E2E falló por timeout
al iniciar webServer. Se repitieron completos contra otro contenedor aislado con
network host y PostgreSQL escuchando solo 127.0.0.1:55440, con los resultados anteriores.

Un comando de documentación se lanzó desde backend y falló al crear docs/startup;
el apéndice README creado en ese directorio se movió al README raíz y se eliminó
el archivo accidental. La primera captura sin backend mostró error de sesión real;
se inició backend normal con DB vacía para la vista previa final.

No se valida entrega SMTP, Safari/Firefox, lectores de pantalla, hosting externo,
clientes, ingresos ni alianzas. Modelo de negocio y métricas son hipótesis explícitas.
No se ejecutó ni se atribuye aprobación a CI remota en esta entrega.

La vista previa final se inspeccionó en escritorio y móvil con backend disponible;
sin aviso de error de sesión. Un chequeo exploratorio que contaba cualquier role=alert
falló por el anunciador vacío de Next; se inspeccionó su texto (vacío) y las capturas.
No se atribuye a ese chequeo una prueba de tema oscuro.

Integración por avance rápido: mismo árbol validado, sin resolución de conflictos.
