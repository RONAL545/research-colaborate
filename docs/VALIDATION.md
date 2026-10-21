# Validación del coordinador

## Autenticación

Commit recibido: e56385d. Revisados rutas, persistencia, hashes, verificación y JWT.
Ejecutado desde backend el 2026-10-20:

`DATABASE_URL=postgresql+psycopg://mvp:mvp@localhost:55432/coordinator_auth_test ../.venv/bin/pytest -q`

Resultado: **17 passed**. PostgreSQL 16 desechable exclusivo del coordinador.
Incluye upgrade/check/downgrade/upgrade. Advertencias: TestClient/httpx y clave HS384
corta usada por el caso negativo. Sin prueba de entrega real de correo; falta proveedor.

Ruff con configuración explícita inicialmente detectó clasificación variable de imports.
Se declaró app como first-party y se ordenaron imports compartidos.
`.venv/bin/ruff check --config backend/pyproject.toml backend`: aprobado tras corrección.
`git diff --check`: aprobado.

## Proyectos y autenticación integrados

Commit recibido: 4027b15. Revisados publicación, edición por autor, búsqueda parametrizada,
filtros, orden y paginación. Reejecución en su worktree:
`DATABASE_URL=postgresql+psycopg://projects:projects@localhost:55433/projects_test ../.venv/bin/pytest -q`
(desde backend): **20 passed**. Un intento anterior usó .venv en vez de ../.venv y no ejecutó pruebas.

Integración en rama integration/projects: revisión merge 0005 y FK 0006 sin modificar
las revisiones originales. Modelo con FK a users y datos de identidad persistidos en
las pruebas de proyectos. Pruebas adicionales con JWT real: publicación rechazada antes
de verificar, permitida después, edición ajena rechazada y feed consultable públicamente;
prueba de integridad que rechaza autor inexistente.

`DATABASE_URL=postgresql+psycopg://mvp:mvp@localhost:55432/coordinator_integrated_test ../.venv/bin/pytest -q`
(desde backend): **34 passed**, incluidas todas las pruebas auth/proyectos y
upgrade/check/downgrade/upgrade del grafo integrado. Base desechable nueva PostgreSQL 16.
`.venv/bin/ruff check --config backend/pyproject.toml backend` y `git diff --check`: aprobados.
Las dos advertencias de auth persisten; no se probó envío de correo real.
CI de dev con auth 4f160e1: success (GitHub Actions 39545199823).

## Eventos y conjunto completo

Commit recibido: 36e64c3 (implementación 6addf3f, preparación automática de DB 36e64c3).
Revisados permisos, paginación, fechas, DTOs y migración. El coordinador detectó
que la primera versión requería upgrade manual; el agente corrigió la preparación
de pruebas antes de la integración. Reejecución del coordinador en worktree de eventos:
`DATABASE_URL=postgresql+psycopg://postgres:test@localhost:55435/events_fresh_test .venv-events/bin/pytest -q`
(desde backend): **21 passed**.

Integración en rama integration/events, sin modificar migraciones de módulos: revisión
0007 reúne eventos con 0006. El archivo de pruebas integradas pasó a llamarse
test_workflows.py; añadió flujo real JWT de Admin, denegación sin correo verificado,
publicación/reemplazo público y revocación del rol con el mismo token.

`DATABASE_URL=postgresql+psycopg://mvp:mvp@localhost:55432/coordinator_full_test ../.venv/bin/pytest -q`
(desde backend): **51 passed**, PostgreSQL 16 en base vacía creada para esta ejecución.
Incluye todos los módulos, los flujos integrados y upgrade/check/downgrade/upgrade.
Ruff global con --config backend/pyproject.toml y git diff --check: aprobados.
Persisten las dos advertencias documentadas de dependencias/caso negativo JWT.
CI auth+proyectos f6cd977: success (GitHub Actions 39545283162).
No se declara completo el MVP: faltan proveedor de correo, solicitudes, chat,
notificaciones e interfaz.
