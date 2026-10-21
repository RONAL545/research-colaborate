# Validación: descubrimiento web

Rama feature/ui-discovery. Alcance: frontend/src/features/discovery, app/page.tsx,
app/proyectos y app/eventos. Sin cambios a backend, componentes compartidos ni dependencias.

## Comandos ejecutados

Desde frontend/ de este worktree (node_modules propio):

- `npm ci`: terminado correctamente.
- `npm test`: resultado final 18 pruebas aprobadas, 3 archivos (11 pruebas de descubrimiento y 7 de base). Cobertura de filtros combinados, paginación, error/reintento, edición exclusiva, bloqueo sin verificación, solicitud exitosa, duplicado 409, payload de publicación sin identidad del cliente y permisos admin.
- `npm run typecheck`: aprobado.
- `npm run build`: aprobado, incluyendo rutas dinámicas de proyectos y eventos.
- Desde raíz `git diff --check`: aprobado.

Fallos registrados durante desarrollo: escritura inicial de eventos usó ruta frontend/ estando ya en frontend; no se crearon archivos en esa ejecución y se corrigió la ruta. Prueba de paginación inicialmente buscó texto Siguiente en lugar del nombre accesible Página siguiente; corregido. Prueba de publicación inicialmente usó mock de lista para un useRemote(null), corregido para reflejar el contrato real. Todos los tests pasaron en la ejecución final.

## Limitaciones y coordinación

UI productiva consume únicamente API real. Solo tests usan mocks. PostgreSQL/navegador real y pruebas E2E quedan a cargo del coordinador con los módulos integrados; no se declaran ejecutadas aquí. El backend no expone DELETE eventos: administración ofrece crear y editar según contratos, sin borrado simulado. Los filtros universidad y categoría son campos libres porque no existe catálogo público. Identidad, reenvío y verificación enlazan al módulo correspondiente. Hero mantiene verde bosque fijo para conservar contraste también en modo oscuro.
