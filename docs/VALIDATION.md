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
