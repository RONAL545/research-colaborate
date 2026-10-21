# Validación eventos

Rama: feature/events-directory. Base: bootstrap d0225e8. No se integró ni publicó dev.

Implementación: models.py y router.py de app/modules/events; migración
migrations/versions/0004_events.py (desciende de 0001_bootstrap); pruebas locales
con overrides de get_current_user/get_db, limpiados al terminar cada prueba.
No modifica contratos, core ni otros módulos.

Entorno propio: backend/.venv-events, Python 3.14; PostgreSQL 16 desechable
research-events-test, puerto 127.0.0.1:55435, base events_test. Instalación:
`python3 -m venv backend/.venv-events` y
`backend/.venv-events/bin/pip install -r backend/requirements-dev.txt`.

Comandos desde backend (2026-10-20):

- `DATABASE_URL=postgresql+psycopg://postgres:test@127.0.0.1:55435/events_test .venv-events/bin/alembic upgrade head`: exit 0.
- `DATABASE_URL=postgresql+psycopg://postgres:test@127.0.0.1:55435/events_test .venv-events/bin/pytest -q`: 21 passed (16 eventos y 5 bootstrap). Incluye upgrade/check/downgrade/upgrade contra esta base desechable.
- `DATABASE_URL=postgresql+psycopg://postgres:test@127.0.0.1:55435/events_test .venv-events/bin/alembic check`: exit 0, No new upgrade operations detected.
- `.venv-events/bin/ruff check app/modules/events tests/events migrations/versions/0004_events.py --fix`: exit 0, All checks passed.
- `.venv-events/bin/ruff check . --config 'lint.isort.known-first-party=["app"]'`: tres errores I001 preexistentes en migrations/env.py, tests/test_bootstrap.py y tests/test_migrations.py. Fuera de mi ámbito, sin modificar.

Cobertura funcional: lectura pública vacía/detalle, creación/reemplazo Admin,
persistencia de deadline con zona horaria, deadline opcional, paginación estable,
límites de página, ID inválido/ausente, rechazo anónimo/Student/Teacher/Admin sin
verificar para ambos verbos de escritura, URL y fecha inválidas, campos extras.

Limitaciones: identidad se simula únicamente mediante overrides en aplicación
local de pruebas; la integración real JWT/auth y las migraciones con múltiples
heads deben comprobarse por el coordinador. No se declara aprobado ese conjunto.
La suite emite un aviso de obsolescencia Starlette/httpx sin fallos.

Revisión del coordinador: preparación automática desde base vacía añadida en
fixture de sesión, con validación del dialecto PostgreSQL y nombre de base test.
Se ejecutó también:

- `DATABASE_URL=postgresql+psycopg://postgres:test@127.0.0.1:55435/events_test .venv-events/bin/alembic downgrade base` seguido de pytest: 21 passed.
- `docker --context default exec research-events-test createdb -U postgres events_fresh_test`: base nueva creada, exit 0.
- `DATABASE_URL=postgresql+psycopg://postgres:test@127.0.0.1:55435/events_fresh_test .venv-events/bin/pytest -q`: 21 passed sin upgrade manual previo.
- Ruff acotado repetido tras la corrección: All checks passed.
