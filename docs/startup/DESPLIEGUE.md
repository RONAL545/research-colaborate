# Prueba cerrada en Render y Vercel

Autorizada por el usuario el 2026-11-02. Esta etapa permite hosting externo para la
prueba; no implica lanzamiento institucional. Los CSV personales y credenciales
quedan excluidos de Git y no forman parte del despliegue frontend.

## Render

Crear Blueprint desde la rama dev usando render.yaml. Define API normal y PostgreSQL
16, ambos free, sin cambiar recursos de otros proyectos. Si el cupo gratuito está
ocupado, no eliminar recursos ni contratar un plan sin acuerdo sobre el costo.

El arranque ejecuta deploy/render_start.py: adapta la URL PostgreSQL al driver psycopg,
aplica upgrade head y solo arranca Uvicorn si las migraciones terminaron bien.
Nunca ejecuta downgrade. JWT_SECRET se genera en Render; ENVIRONMENT=staging impide
el secreto de desarrollo. No se despliega tests/ui_server.py ni un buzón de pruebas.
La base no admite conexiones externas por defecto. /health comprueba el proceso;
la comprobación funcional también debe consultar /api/v1/projects para verificar DB.

## Vercel

Crear proyecto separado con Root Directory frontend, framework Next.js y Node 24.
Configurar BACKEND_URL con la URL HTTPS de la API Render, sin /api/v1 y sin prefijo
NEXT_PUBLIC_. NEXT_PUBLIC_EMAIL_DELIVERY_ENABLED=false hasta disponer de proveedor.
Desplegar después de comprobar que la API y migraciones están listas.

## Cuentas y comprobación final

Crear las 26 cuentas student y la cuenta admin de los CSV solamente en la nueva DB
remota, con contraseñas nuevas individuales, hash Argon2 y verificación exclusiva
para la prueba cerrada. No reutilizar claves locales, publicar CSV, añadir un endpoint
de importación ni habilitar el servidor E2E. Si la importación requiere conexión
externa, limitar temporalmente a la IP del operador y retirar el acceso al acabar.
Guardar credenciales fuera del repositorio y compartirlas individualmente.

Comprobar por HTTPS login de ambos roles, cookie HTTP-only/Secure, proyecto, solicitud,
notificación, decisión, mensaje privado y evento administrativo. Probar que un tercero
no puede leer mensajes ajenos. Una URL del frontend por sí sola no valida el despliegue.

## Límites

Render Postgres free expira a los 30 días según documentación consultada el 2026-11-02:
https://render.com/docs/free. Acordar duración y conservación de datos antes de que venza.
Servicios web gratuitos pueden tardar en arrancar; comprobar el comportamiento frente
al timeout de 15 segundos del proxy durante la prueba remota. No afirmar disponibilidad
permanente ni envío real de correo. La autenticación en las cuentas cloud es necesaria
para crear recursos y comprobar esta configuración en el proveedor.

## Evidencia local del 2026-11-02

- `ruff check --config backend/pyproject.toml backend deploy`: aprobado.
- `npm test --prefix frontend`: 43 aprobadas.
- `npm run build --prefix frontend` y `npm run typecheck --prefix frontend`: aprobados.
- Desde backend, `DATABASE_URL=postgresql+psycopg://mvp:mvp@127.0.0.1:55440/cloud_deploy_validation_test ../.venv/bin/pytest -q`: 79 aprobadas, advertencia previa de Starlette/httpx.
- `DATABASE_URL=postgresql://mvp:mvp@127.0.0.1:55440/cloud_start_validation_test PORT=18003 .venv/bin/python deploy/render_start.py`: migraciones desde base vacía y arranque aprobados; /health y /api/v1/projects respondieron 200.
- Primer intento de arranque compartió por error DB con pytest y falló al crear
  alembic_version concurrentemente. Se corrigió usando otra DB exclusiva; no se
  considera aprobado ese primer intento. No se tocaron cuentas de prueba del usuario.
- `render blueprints validate render.yaml --output json`: bloqueado por HTTP 401;
  no se atribuye validación remota al YAML. Render CLI informa token vencido;
  comprobación de identidad Vercel devuelve HTTP 403.
- `git diff --check`: aprobado. CSV de origen ignorados; sin secretos añadidos.

Pendiente: conexiones cloud válidas, validación del proveedor, creación de recursos,
importación remota de cuentas y prueba HTTPS. No hay URL pública confirmada todavía.

Prueba navegador de preparación: dos intentos con Chrome del sistema dieron 2 passed,
1 failed. El primero abortó navegación con ERR_ABORTED; el segundo informó Target
crashed en la pestaña del flujo de chat. No se consideran aprobados. Se ensayó además
un wrapper temporal de Chrome con --disable-dev-shm-usage; no cambia código productivo.

El wrapper de Chrome tampoco resolvió el cierre de pestaña (2 passed, 1 failed).
El intento sin ejecutable explícito no pudo iniciar ningún caso: faltaba la revisión
Chromium 1248 esperada por Playwright. Se ejecutó `npx playwright install chromium`
para instalar la revisión correspondiente antes de volver a probar.

El usuario confirmó conectar ambos proveedores y el catálogo confirmó installed=true
para Render y Vercel. Sus herramientas aún no estaban expuestas en el turno de trabajo;
no confundir esto con falta de instalación ni con despliegue completado.

La instalación de Chromium se interrumpió al informar ENOSPC. `df -h /` mostró
100 % de uso y 84 MB disponibles. No se borraron archivos del usuario. Se intentó
usar el Chromium headless 1243 ya instalado con TMPDIR=/dev/shm, sin descargar ni
modificar dependencias del proyecto. La revisión 1243 no es la predeterminada 1248.

Resultado final de navegador: `TMPDIR=/dev/shm DATABASE_URL=postgresql+psycopg://mvp:mvp@127.0.0.1:55440/cloud_browser_validation_test PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/home/ellis/.cache/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell UI_E2E_PRODUCTION=1 npm run test:e2e --prefix frontend` → **3 passed (15.8 s)**. Valida los flujos locales; no sustituye prueba remota HTTPS.
