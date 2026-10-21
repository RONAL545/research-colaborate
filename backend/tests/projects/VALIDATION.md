# Entrega de proyectos

Rama: `feature/projects-feed`.

Implementación en `backend/app/modules/projects/{models,router}.py`, migración
`backend/migrations/versions/0003_projects.py` y pruebas en
`backend/tests/projects/test_projects.py`. Sin cambios a core, schemas ni main.

Validación ejecutada el 2026-10-20:

- Desde la raíz: `.venv/bin/ruff check backend/app/modules/projects backend/tests/projects backend/migrations/versions/0003_projects.py`: aprobado.
- Desde la raíz: `git diff --check`: aprobado.
- Desde backend: `DATABASE_URL=postgresql+psycopg://projects:projects@127.0.0.1:55433/projects_test ../.venv/bin/pytest -q -x`: **20 passed**, 1 advertencia de deprecación de Starlette/TestClient con httpx. Incluye bootstrap, permisos, validación, filtros combinados, búsqueda literal, paginación con fechas empatadas y migraciones upgrade/check/downgrade/upgrade.
- `.venv/bin/ruff check backend`: falla por I001 preexistentes en `migrations/env.py`, `tests/test_bootstrap.py` y `tests/test_migrations.py`; no se modificaron por pertenecer al coordinador.
- El primer intento de instalar dependencias falló por DNS restringido; la repetición autorizada completó la instalación en `.venv` exclusivo.
- El primer intento de pytest sin acceso de red local falló al conectar PostgreSQL; la ejecución autorizada indicada arriba pasó.

Base exclusiva y desechable: contenedor `research-projects-test`, imagen postgres:16,
puerto local 55433, base `projects_test`. Ningún downgrade usa datos reales.
Las identidades se sobrescriben solamente en cada aplicación local de pruebas y se
limpian al terminar. La autenticación de producción sigue dependiendo del core.

Pendiente del coordinador: integrar con auth, añadir FK de author_id a users,
resolver cabezas Alembic y validar el conjunto integrado antes de publicar dev.
La paginación usa offset y orden created_at DESC, id DESC; garantiza orden estable
para datos sin cambios entre consultas, sin prometer una instantánea ante nuevas
publicaciones concurrentes. La búsqueda cubre título y descripción.
