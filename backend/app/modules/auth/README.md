# Autenticación

Implementa registro institucional, JWT Bearer HS256 con `sub` UUID y `exp`, verificación,
reenvío y lectura/actualización del perfil propio. El rol inicial es `student`; los DTOs
rechazan cambios de rol, identidad y estado de verificación enviados por el cliente.
La autorización consulta el usuario actual en PostgreSQL, sin confiar en roles del JWT.

Configuración del core existente: `DATABASE_URL`, `JWT_SECRET`, `ENVIRONMENT`,
`INSTITUTIONAL_DOMAINS` (lista JSON de dominios exactos, sin subdominios implícitos),
`ACCESS_TOKEN_MINUTES` y `VERIFICATION_TOKEN_MINUTES`.

Las contraseñas usan Argon2. Los tokens de correo son aleatorios; solo se guarda SHA-256,
caducidad y consumo. La verificación consume con un UPDATE condicional atómico; reenviar
invalida tokens anteriores. La API no devuelve tokens de verificación ni hashes.

## Correo pendiente de integración

`get_mailer` es la dependencia inyectable; el adaptador debe implementar
`send_verification(email, token)`. `TestMailbox` conserva mensajes únicamente cuando se
inyecta explícitamente en pruebas. El adaptador predeterminado `UnconfiguredMailer` no
envía ni registra nada: **el envío real está bloqueado hasta integrar un proveedor**.
Las respuestas genéricas no garantizan entrega. El coordinador debe inyectar el proveedor
y construir el enlace de verificación antes de habilitar registro en producción.

## Entrega y evidencia

Rama `feature/auth`. Rutas: `app/modules/auth/`, `tests/auth/`,
`migrations/versions/0002_auth.py` y el adaptador `core/dependencies.py`.
No se modificaron contratos, esquemas, main ni módulos ajenos.

Entorno propio: `/tmp/auth-mvp-venv`, Python 3.14.7; dependencias instaladas con
`/tmp/auth-mvp-venv/bin/pip install -r backend/requirements-dev.txt`.
PostgreSQL 16.15 extraído de paquetes Ubuntu sin instalación del sistema; clúster
exclusivo `/tmp/auth-mvp-pgdata`, puerto 55541, base desechable `auth_module_test`.
Docker no tenía daemon disponible y sudo requiere contraseña; no se usaron bases ajenas.

Comandos ejecutados el 2026-10-20 (desde `backend/`, salvo Ruff y git desde la raíz):

- `DATABASE_URL=postgresql+psycopg://ellis@127.0.0.1:55541/auth_module_test /tmp/auth-mvp-venv/bin/alembic upgrade head`: correcto.
- `DATABASE_URL=postgresql+psycopg://ellis@127.0.0.1:55541/auth_module_test /tmp/auth-mvp-venv/bin/pytest -q`: **17 passed**, 2.23 s.
  Incluye bootstrap, 12 casos auth y migración upgrade/check/downgrade base/upgrade.
  Solo se ejecutó downgrade contra esta base desechable.
- `/tmp/auth-mvp-venv/bin/ruff check backend/app/modules/auth backend/app/core/dependencies.py backend/migrations/versions/0002_auth.py backend/tests/auth`: correcto.
- `git diff --check`: correcto.
- `/tmp/auth-mvp-venv/bin/ruff check backend`: falla por I001 preexistentes en
  `migrations/env.py`, `tests/test_bootstrap.py`, `tests/test_migrations.py`.
  Pendiente del coordinador; no se corrigieron archivos ajenos.
- Una invocación inicial de pytest desde la raíz falló en colección por `app` fuera
  del path; se corrigió ejecutando desde `backend/`, donde vive `pyproject.toml`.

Limitaciones: advertencia de obsolescencia TestClient/httpx de las dependencias instaladas,
y advertencia por longitud de clave del JWT HS384 construido expresamente para rechazar
algoritmos distintos. No se probó entrega de correo real ni concurrencia bajo carga.
Pendientes del coordinador: proveedor de correo, errores Ruff globales e integración y
publicación en dev. Esta rama no integra ni publica dev.
