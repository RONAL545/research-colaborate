# Coordinación del MVP

Lee `.codex/instructions.md`, `.codex/MVP.md`, `docs/contracts.md` y tu instrucción en `docs/agents/`.

Solo el coordinador integra y publica `dev`, de uno en uno, después de revisar el diff y ejecutar las pruebas del conjunto. Ningún agente desarrolla en dev, hace merge, push a dev ni modifica carpetas ajenas. No declarar aprobadas pruebas no ejecutadas. Registrar comando, resultado y limitaciones.

| Rama | Responsabilidad exclusiva |
| --- | --- |
| feature/bootstrap | Coordinador: core, schemas, CI, infraestructura y contratos |
| feature/auth | app/modules/auth, tests/auth, migración 0002_auth; adaptador get_current_user en core/dependencies.py |
| feature/projects-feed | app/modules/projects, tests/projects, migración 0003_projects |
| feature/events-directory | app/modules/events, tests/events, migración 0004_events |

Todas las rutas anteriores son relativas a backend/. No modificar contratos compartidos sin coordinación. Importar Base y get_db del core; no crear motores ni bases declarativas propias. Proyectos y eventos dependen de Principal y las dependencias del core, nunca de auth. Aislar pruebas con dependency_overrides, sin falsear la autenticación de producción. Cada agente usa una base PostgreSQL desechable distinta. Nunca ejecutar downgrade contra una base con datos reales.

Migraciones: cada módulo parte de 0001_bootstrap en su rama, crea tablas solo de su módulo. Proyectos guarda author_id UUID con índice; el coordinador añadirá FK a users al integrar. El coordinador resuelve cabezas Alembic con revisión merge y valida upgrade/downgrade/check. No renumerar migraciones ajenas.

Antes del commit: ejecutar Ruff y pytest contra PostgreSQL; Conventional Commits. Entregar hash, rutas, comandos ejecutados y pendientes al coordinador. No compartir venv mutable entre agentes.
