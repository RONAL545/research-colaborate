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
