# Colaboración académica — backend MVP

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

Módulos implementados: autenticación y perfil, proyectos/feed, directorio de eventos,
solicitudes de equipo, notificaciones privadas y conversaciones con mensajes.
Validación del coordinador en [docs/VALIDATION.md](docs/VALIDATION.md). Las pruebas
integradas usan JWT real y comprueban concurrencia y rollback de los tres módulos de
colaboración en una única transacción. El correo real sigue pendiente de proveedor
y la interfaz aún no está implementada.

Swagger: http://localhost:8000/docs; salud: /health (proceso, no disponibilidad DB). Configuración por variables de entorno o .env en raíz. Cambiar JWT_SECRET fuera de desarrollo. INSTITUTIONAL_DOMAINS es una lista JSON. El adaptador de correo predeterminado no envía mensajes. No versionar secretos.

Pruebas (DATABASE_URL debe apuntar a una base **desechable**, el test de migraciones ejecuta downgrade):

```bash
.venv/bin/ruff check --config backend/pyproject.toml backend
cd backend
DATABASE_URL=postgresql+psycopg://mvp:mvp@localhost:5432/mvp_test ../.venv/bin/pytest -q
```

CI crea PostgreSQL aislado y ejecuta las mismas comprobaciones. requirements.lock registra las versiones de validación; requirements*.txt expresan rangos para actualizaciones deliberadas.

## Trabajo paralelo

Los agentes de segunda etapa trabajan en ramas y worktrees separados. Para abrir
cada consola desde la raíz (los módulos ya fueron implementados):

```bash
cd .worktrees/applications
codex 'Lee AGENTS.md y docs/agents/applications.md. Trabaja solo en tu módulo y rama; no integres en dev.'
```
```bash
cd .worktrees/notifications
codex 'Lee AGENTS.md y docs/agents/notifications.md. Trabaja solo en tu módulo y rama; no integres en dev.'
```
```bash
cd .worktrees/private-chat
codex 'Lee AGENTS.md y docs/agents/private-chat.md. Trabaja solo en tu módulo y rama; no integres en dev.'
```

Cada agente usa su propio venv y base desechable. Los worktrees conservan sus commits
de entrega; no asumir que contienen las integraciones posteriores del coordinador.

Solo el coordinador revisa e integra, de uno en uno, resolviendo Alembic heads y
probando TODO el conjunto antes de publicar dev. Las revisiones merge preservan
los historiales independientes; las FK de colaboración se agregan al final.
No declarar aprobadas pruebas o CI remota que no se hayan ejecutado y observado.
