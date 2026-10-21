# Chat privado — validación

Worktree `.worktrees/private-chat`, rama `feature/private-chat`. Implementación exclusivamente en `app/modules/chat`, `tests/chat` y `migrations/versions/0009_chat.py` (rutas relativas a backend).

## Comandos ejecutados

Desde la raíz del worktree:

```sh
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements.lock
docker --context default run -d --name research-chat-test -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=chat_module_test -p 55438:5432 postgres:16
.venv/bin/ruff check --config backend/pyproject.toml backend --fix
.venv/bin/ruff check --config backend/pyproject.toml backend
git diff --check
```

Entorno de pruebas: Python 3.14, PostgreSQL 16 desechable propio. Desde `backend`, usando `DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:55438/chat_module_test`:

```sh
../.venv/bin/pytest -q
../.venv/bin/pytest -q tests/chat
../.venv/bin/alembic check
../.venv/bin/alembic downgrade base
../.venv/bin/pytest -q
../.venv/bin/alembic check
```

Resultados: primera suite completa 57 aprobadas; tras añadir prueba concurrente, módulo 7 aprobadas y suite final desde esquema vacío 58 aprobadas. Ruff global y diff --check sin errores. Alembic check sin diferencias; downgrade base exitoso exclusivamente contra esta base desechable y upgrade ejercitado por suite posterior. No hubo pruebas fallidas. Advertencias existentes de TestClient/httpx y clave del token HS384 de prueba en auth.

## Cobertura y límites

Privacidad de lectura/escritura incluso frente a terceros Admin, identidad ausente, lectura por participante no verificado y escritura rechazada; remitente derivado del Principal sin aceptar sender_id; mensajes vacíos/blancos/mayores de 5000 rechazados, longitud máxima aceptada; paginación y empates por UUID; servicio idempotente, contexto incompatible, participantes distintos, rollback externo y carrera real de dos sesiones PostgreSQL con savepoint que conserva operativa la transacción perdedora.

Conversaciones y mensajes usan FK reales a proyectos/usuarios. application_id es único, sin FK hasta integración del coordinador. No se crean conversaciones desde endpoints públicos. No hay websockets: consulta periódica. Las pruebas específicas de permisos usan dependency_overrides local y limpian overrides; la autenticación de producción no se modifica. La integración solicitudes → conversación y FK a solicitudes corresponde al coordinador, no se declara probada en esta rama aislada.
