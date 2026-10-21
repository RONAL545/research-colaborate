# Validación de notificaciones

Rama `feature/notifications`; worktree `.worktrees/notifications`; 2026-10-20.

Implementación: listado privado paginado con filtro de no leídos, marca leída
idempotente y servicio interno transaccional idempotente. No existe creación pública.
Migración `0008_notifications` desciende de `0007_merge_events`; FK de destinatario
contra users, application_id UUID pendiente de FK en integración.

## Comandos ejecutados y resultados

Desde raíz de este worktree:

- `python3 -m venv .venv`: correcto, entorno exclusivo.
- `.venv/bin/pip install -r backend/requirements.lock`: correcto.
- `docker --context default run -d --name research-notifications-test -e POSTGRES_PASSWORD=test -e POSTGRES_DB=notifications_module_test -p 55437:5432 postgres:16-alpine`: correcto, base exclusiva desechable.
- `.venv/bin/ruff check backend --config backend/pyproject.toml --fix`: detectó y corrigió un orden de imports en la migración propia; sin errores restantes.
- Primera suite completa: `cd backend && DATABASE_URL=postgresql+psycopg://postgres:test@localhost:55437/notifications_module_test ../.venv/bin/pytest -q`: **55 passed**.
- Se añadió prueba de carrera concurrente con dos sesiones reales; antes de suite final:
  `docker --context default exec research-notifications-test psql -U postgres -d postgres -c 'DROP DATABASE notifications_module_test WITH (FORCE)'`
  y `docker --context default exec research-notifications-test psql -U postgres -d postgres -c 'CREATE DATABASE notifications_module_test'`: correctos, exclusivamente base de prueba propia.
- Suite completa final, mismo comando pytest: **56 passed**, desde base vacía. Incluye roundtrip Alembic upgrade/check/downgrade/upgrade.
- `.venv/bin/ruff check backend --config backend/pyproject.toml`: **All checks passed!**
- `git diff --check`: correcto.

No fallaron pruebas. Dos avisos existentes: deprecación httpx de Starlette y longitud
de clave del caso deliberado wrong_algorithm de auth. Un intento inicial de lectura
buscó schemas/collaboration.py, tests/conftest.py y alembic/versions; no existen;
se localizaron las rutas reales sin modificar otros módulos.

## Cobertura y límites

Cinco pruebas nuevas comprueban identidad ausente, ausencia de endpoint creador,
ausencia de filtración entre usuarios, IDs forjados en URL/body/query, paginación
estable, límites, marca leída repetida, servicio idempotente, rollback externo sin
persistencia y carrera real de unicidad conservando utilizable la transacción externa.
Las pruebas locales sobrescriben identidad de manera explícita; autenticación de
producción permanece intacta. JWT real con solicitudes/chat requiere integración
por coordinador. Los cuerpos ajenos a la operación read no se usan para determinar
identidad ni destinatario.

Pendiente del coordinador: conectar puertos transaccionales, añadir FK application_id,
resolver heads y ejecutar pruebas integradas con JWT real. Sin merge ni push dev.
