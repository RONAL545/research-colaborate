# Colaboración académica — base backend

Python 3.12+; FastAPI, SQLAlchemy, PostgreSQL 16 y Alembic. Alcance: `.codex/MVP.md`. Contratos en [docs/contracts.md](docs/contracts.md); aislamiento en [AGENTS.md](AGENTS.md).

```bash
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements.lock
cp .env.example .env
docker compose up -d --wait db
cd backend
../.venv/bin/alembic upgrade head
../.venv/bin/uvicorn app.main:app --reload
```

Módulos implementados: autenticación y perfil, proyectos/feed y directorio de eventos.
Validación del coordinador en [docs/VALIDATION.md](docs/VALIDATION.md). Las pruebas
integradas usan JWT real; el correo real sigue pendiente de proveedor. Solicitudes,
chat, notificaciones e interfaz aún no están implementados.

Swagger: http://localhost:8000/docs; salud: /health (proceso, no disponibilidad DB). Configuración por variables de entorno o .env en raíz. Cambiar JWT_SECRET fuera de desarrollo. INSTITUTIONAL_DOMAINS es una lista JSON. No hay envío real de correo en bootstrap. No versionar secretos.

Pruebas (DATABASE_URL debe apuntar a una base **desechable**, el test de migraciones ejecuta downgrade):

```bash
.venv/bin/ruff check --config backend/pyproject.toml backend
cd backend
DATABASE_URL=postgresql+psycopg://mvp:mvp@localhost:5432/mvp_test ../.venv/bin/pytest -q
```

CI crea PostgreSQL aislado y ejecuta las mismas comprobaciones. requirements.lock registra las versiones de validación; requirements*.txt expresan rangos para actualizaciones deliberadas.

## Consolas por módulo

El coordinador crea los worktrees después de integrar bootstrap. En tres terminales independientes, desde la raíz:

```bash
cd .worktrees/auth
codex 'Lee AGENTS.md y docs/agents/auth.md. Implementa y prueba tu módulo en esta rama. No integres en dev.'
```
```bash
cd .worktrees/projects-feed
codex 'Lee AGENTS.md y docs/agents/projects-feed.md. Implementa y prueba tu módulo en esta rama. No integres en dev.'
```
```bash
cd .worktrees/events-directory
codex 'Lee AGENTS.md y docs/agents/events-directory.md. Implementa y prueba tu módulo en esta rama. No integres en dev.'
```

Cada consola crea su propio .venv y usa base desechable diferente. Coordinador: actualizar dev con fast-forward, revisar cada módulo, ejecutar sus pruebas, integrar uno, resolver Alembic heads, ejecutar TODAS las pruebas contra PostgreSQL y solo entonces publicar dev. Si falla el conjunto, corregir en rama de integración antes de publicar; nunca integrar simultáneamente. Añadir prueba real auth→proyecto y auth→evento cuando estén disponibles. No afirmar que la CI remota pasó sin observar su ejecución.
