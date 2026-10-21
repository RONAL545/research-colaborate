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
