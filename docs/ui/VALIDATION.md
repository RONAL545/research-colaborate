# Validación de la interfaz

## Base y sesión

Elección inicial: web React/Next.js (preferencia consultada, sin otra elección recibida).
Se conservó el backend y se trabajó localmente en el repositorio sin hosting externo.
Base c198a67: 7 pruebas de cliente/proxy, build de producción y TypeScript aprobados.
CI del merge d2b33a5: Frontend 39548419245 y Backend 39548419192 success observados.

La sesión usa cookie HTTP-only same-site; el proxy no devuelve access_token al
navegador, acepta solo recursos conocidos, comprueba origen en escrituras y remite
Bearer desde cookie. Pruebas adicionales del coordinador verifican limpieza de datos
privados cuando path=null e ignorar respuestas tardías tras cambiar filtros.

## Identidad

Commit recibido 4c3d053. Revisados formularios, redirección next local, honestidad de
correo pendiente, confirmación antes de consumir token y refresco automático de perfil.
El coordinador pidió sustituir actualización manual de sesión por refresco automático.
Desde frontend ejecutados npm test: **20 passed**, npm run build y npm run typecheck:
aprobados. Incluye 11 pruebas de identidad y 9 pruebas compartidas. git diff --check limpio.
Pruebas del módulo usan mocks; navegador contra FastAPI/PostgreSQL pendiente de integración.

## Descubrimiento

Commit recibido 5b00ed0. Revisados feed real, filtros combinados, páginas, publicación,
autoría, postulación y formularios Admin de eventos. El coordinador pidió respetar
el límite de 2000 caracteres de solicitud y un único h1 por pantalla; corregidos por agente.
Ejecutados desde frontend npm test: **31 passed**, npm run build y npm run typecheck:
aprobados. git diff --check limpio. Aún no se atribuye E2E a estas pruebas con mocks.

## Colaboración e integración de navegador

Commit recibido 8ea2dbf. Corregidos durante revisión de agente: contexto al cambiar de
application a conversation, títulos reales de proyectos en bandeja y salto a última
página tras enviar sin alterar lectura histórica durante polling. Con identidad y
descubrimiento integrados: npm test **41 passed**, build y TypeScript aprobados.

Pruebas de navegador con Playwright y Chrome del sistema, FastAPI real y PostgreSQL 16
(ui_browser_test exclusiva). El servidor tests/ui_server.py requiere bandera explícita,
nombre DB terminado _test y loopback; buzón y Admin solo de pruebas. Producción no importa
ni expone rutas de ese servidor y el proxy bloquea recursos __test__.

Incidentes observados y corregidos por el coordinador:
- Primera ejecución no abrió navegador por revisión de Chromium no instalada; se configuró
  PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH para Chrome existente. CI instala su Chromium.
- La protección de origen rechazaba POST válidos: Next normaliza el URL de loopback.
  Se compara Origin con el Host real, conservando rechazo de origen externo/sec-fetch-site.
  Dos pruebas de regresión nuevas verifican ese límite.
- Un selector exacto de label de select no coincidía con texto de sus opciones; se interrumpió
  esa ejecución y se corrigió a combobox con nombre accesible. No se atribuye aprobación.
- La prueba de error reenviaba filtros idénticos sin petición nueva; se cambió el filtro antes
  de simular respuesta 503. La aserción se acota al aviso de aplicación, sin confundirse con
  el anunciador de rutas de Next. La simulación de 503 solo existe en esta prueba.
- Un comando local de formato/captura usó ruta frontend duplicada y no modificó esos archivos;
  se repitió con directorio correcto.

Resultados ejecutados por coordinador el 2026-10-21:

- Desde frontend: npm test → **43 passed**.
- npm run build → aprobado, todas las rutas generadas; npm run typecheck → aprobado.
- Desde backend:
  `DATABASE_URL=postgresql+psycopg://mvp:mvp@localhost:55432/ui_regression_test ../.venv/bin/pytest -q`
  → **79 passed**, DB desechable nueva, incluidas migraciones y concurrencia.
- Ruff global backend con configuración explícita y git diff --check → aprobados.
- Desde raíz:
  `DATABASE_URL=postgresql+psycopg://mvp:mvp@localhost:55432/ui_browser_test PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/opt/google/chrome/chrome npm run test:e2e --prefix frontend`
  → **3 passed** (22.7 s), servidor de desarrollo.
- Tras build, mismo comando con UI_E2E_PRODUCTION=1 → **3 passed** (15.8 s), servidor de
  producción. Cookie HTTP-only comprobada en navegador; JWT ausente de document.cookie.

Recorridos: registro/verificación/login/perfil → proyecto → solicitud → aceptación →
notificación leída → mensajes en ambas cuentas; un Admin ajeno recibe 404 y no ve chat.
Móvil 390 px sin overflow horizontal, teclado y foco del salto de contenido, navegación,
modo oscuro persistente, vacío y error. Admin publica/edita evento y visitante ve el
resultado sin controles de administración. Se comprobó ausencia de excepciones JS en
el recorrido principal. Capturas desktop y móvil inspeccionadas visualmente en /tmp.

Límites: correo real sigue pendiente (UI lo explica), pruebas usan buzón aislado para
obtener el enlace; no se probó entrega SMTP. Navegador validado Chromium/Chrome, no
Safari/Firefox ni lector de pantalla. Los 43 tests de componentes usan mocks donde
corresponde; no se presentan como sustitutos de los tres recorridos reales.
Advertencias previas del backend y avisos de entorno Python/colores en servidores de
prueba no causaron fallos. No se publicó hosting externo; únicamente código en dev.
