# Solicitudes — validación del agente

Rama: feature/applications. PostgreSQL 16 Alpine desechable en contenedor
research-applications-test, puerto 55436, base application_module_test. Entorno
virtual propio `.venv`, dependencias de backend/requirements.lock.

## Implementación y contratos

- app/modules/applications/models.py: FK users/projects, estados restringidos e
  índice parcial único uq_applications_active para pending/accepted.
- app/modules/applications/router.py: creación, detalle privado, bandejas sent y
  received paginadas; decisiones exclusivamente del autor verificado.
- migrations/versions/0010_applications.py desciende de 0007_merge_events.
- Bloqueo SELECT FOR UPDATE del proyecto tanto al crear como al decidir;
  bloqueo adicional de solicitud al decidir, estados terminales irreversibles.
- Puertos submitted/decided tras flush y antes de commit. Ante error rollback
  explícito de la solicitud, decisión y efectos del puerto. No importar chat o
  notificaciones. Puerto no configurado falla cerrado con 503.

## Comandos ejecutados y resultados

Desde la raíz del worktree:

```bash
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements.lock
# Contenedor dedicado creado con postgres:16-alpine, usuario/clave locales app.
.venv/bin/ruff check backend --config backend/pyproject.toml --fix
.venv/bin/ruff check backend --config backend/pyproject.toml
git diff --check
```

La primera ejecución Ruff encontró y corrigió un orden de imports en la
migración propia. La comprobación global final terminó `All checks passed!`.
`git diff --check` terminó con código 0. Ningún fallo pytest registrado:
primera suite 60 passed, ampliación 62 passed y suite final 62 passed.

Desde backend, última ejecución:

```bash
DATABASE_URL=postgresql+psycopg://app:app@localhost:55436/application_module_test ../.venv/bin/alembic downgrade base
DATABASE_URL=postgresql+psycopg://app:app@localhost:55436/application_module_test ../.venv/bin/pytest -q
```

Resultado final ejecutado: **62 passed, 2 warnings in 7.22s**. Base vacía al
iniciar; incluye suite previa y 11 casos de solicitudes. La prueba global de
migraciones ejecutó upgrade, Alembic check, downgrade base y upgrade head.
Warnings preexistentes: deprecación TestClient/httpx y clave corta en caso
negativo de algoritmo JWT.

Cobertura de solicitudes: identidad ausente/no verificada, proyecto propio o
no recruiting, UUID inexistentes, validación, privacidad, scopes, paginación
estable, decisión ajena/terminal, rechazo seguido de nueva postulación,
duplicado aceptado, índice parcial PostgreSQL comprobado directamente.
Concurrencia: sesiones/conexiones independientes, dos creaciones simultáneas
(201/409), dos decisiones simultáneas (200/409) y creación concurrente frente a
cambio de estado del proyecto. Fallo del puerto comprueba rollback de creación
y decisión, además de una escritura ficticia del puerto en la misma sesión.

## Limitaciones y pendientes del coordinador

Solo se usan puertos ficticios en pruebas locales; no se ha ejecutado el flujo
integrado con notificaciones/chat reales ni JWT real para solicitudes en esta
rama. Coordinador debe conectar puertos, añadir FK de los otros módulos a
applications, resolver heads Alembic y ejecutar la suite integrada completa.
No merge ni push de dev por el agente.
