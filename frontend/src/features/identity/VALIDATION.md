# Identidad web — validación de rama

Rama: feature/ui-identity. Base compartida: dev de interfaz.

Implementación en src/features/identity y app/login, registro, verificar, perfil:

- Login con sesión HTTP-only compartida y next restringido a rutas locales.
- Registro institucional sin aceptar rol, IDs ni estado de verificación.
- Enlace de verificación con confirmación explícita; éxito solo tras HTTP satisfactorio.
- Reenvío genérico sin afirmar entrega cuando correo está deshabilitado.
- Perfil propio, límites DTO, habilidades por comas (máximo 30) y refresh automático de sesión.

Comandos ejecutados en frontend/:

- `npm ci`: aprobado, 131 paquetes, auditoría sin vulnerabilidades.
- `npm test`: aprobado, 18 tests (11 de identidad y 7 compartidos), tres archivos.
- `npm run typecheck`: aprobado, tsc --noEmit sin errores.
- `npm run build`: aprobado, Next.js 16.4.2, ocho rutas generadas con éxito.
- `git diff --check` desde worktree: aprobado.

Pruebas propias: redirect externo/contrabarras/control, login exitoso e inválido, DTO registro, rechazo dominio, verificación real mediante API mock de test, enlace vencido, reenvío honesto, perfil inaccesible sin sesión, payload edición y límite habilidades. Mocks exclusivamente en tests.

Incidencia durante ejecución: se intentó escribir inicialmente el archivo de tests con un prefijo frontend/ estando ya en frontend/. El shell reportó rutas inexistentes y solo se ejecutaron los 7 tests base. Se corrigió el directorio, se crearon los tests propios y se repitió la suite completa dos veces (18 aprobados). No se contabilizó la ejecución inicial como validación de identidad.

Limitaciones: esta rama no ejecutó navegador ni PostgreSQL; los verificará el coordinador tras integrar los tres módulos. La entrega de correo real continúa pendiente. No se expone ni fabrica token para desbloquear cuentas. El enlace exige pulsar «Verificar mi correo» para evitar consumirlo por prelecturas o dobles efectos de React.
