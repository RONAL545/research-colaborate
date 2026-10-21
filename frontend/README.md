# Nexo Académico — interfaz web

React/Next.js, TypeScript y componentes por funcionalidad. Node 24. Desde la raíz:

```bash
npm ci --prefix frontend
cp frontend/.env.example frontend/.env.local
npm run dev --prefix frontend
```

Abrir http://127.0.0.1:3000. FastAPI debe estar ejecutándose en http://127.0.0.1:8000
(con PostgreSQL y migraciones preparadas según el README raíz). BACKEND_URL en
frontend/.env.local cambia el destino del proxy; no lleva prefijo /api/v1.
No requiere CORS: el navegador llama a Next y Next se comunica con FastAPI.

Sesión: JWT retenido en cookie HTTP-only, SameSite=Lax y Secure en producción.
No se guarda en localStorage ni se devuelve al navegador tras login. Producción
requiere HTTPS. Las escrituras comprueban origen y permisos siguen en el backend.
NEXT_PUBLIC_EMAIL_DELIVERY_ENABLED=false mantiene avisos honestos sobre correo pendiente;
poner true no configura un proveedor: primero se debe integrar el envío real en FastAPI.

Pantallas: explorar, proyectos (detalle/publicar/editar/postularse), eventos (incluida
administración), registro/login/verificación, perfil, solicitudes, notificaciones y chat.
El chat consulta cada 10 s. No hay datos ficticios por defecto ni bypass de verificación.

```bash
npm test --prefix frontend
npm run build --prefix frontend
npm run typecheck --prefix frontend
```

## Pruebas de navegador

Requieren venv Python en la raíz con backend/requirements.lock y una base PostgreSQL
**desechable** cuyo nombre termine en _test, distinta de cualquier base en uso.
Playwright inicia y detiene automáticamente los servidores en 127.0.0.1:13000 y :18000.

```bash
cd frontend
npx playwright install chromium
DATABASE_URL=postgresql+psycopg://mvp:mvp@127.0.0.1:5432/mvp_ui_test npm run test:e2e
```

Para validar el servidor de producción: npm run build y repetir con UI_E2E_PRODUCTION=1.
Si se usa un navegador del sistema, PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH admite una ruta
absoluta a Chrome/Chromium. CI instala su propio Chromium y prueba la compilación de
producción contra PostgreSQL aislado.

El buzón y cuenta administrativa de backend/tests/ui_server.py existen **solo** en el
servidor E2E, con bandera explícita, base _test y enlace a loopback. La aplicación de
producción no registra sus rutas y el proxy del cliente las rechaza. Las pruebas obtienen
el token del buzón exclusivo para simular el enlace recibido, sin exponer tokens reales.
No ejecutar ese servidor como la aplicación de producción.

Evidencia y límites en docs/ui/VALIDATION.md (desde raíz). Capturas de revisión locales
en /tmp/nexo-desktop.png y /tmp/nexo-mobile-dark.png tras ejecutar E2E.
