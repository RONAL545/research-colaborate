# Contratos frontend

React/Next.js App Router + TypeScript estricto. Navegación Link de next/link;
componentes interactivos con "use client". Todo texto de producto en español.
No introducir paquetes sin coordinación. El coordinador mantiene layout, CSS global,
components, lib, proxy y e2e; cada agente usa CSS modules dentro de su features/.

## API y sesión

- api de @/lib/api: get<T>(path, signal?), post<T>(path,body), put<T>, patch<T>(path,body?). Paths SIN /api/v1: /projects, /auth/me, etc. ApiError.status y errorMessage(error) listos; errores visibles en UI, nunca éxito silencioso.
- useRemote<T>(path:string|null,{pollMs?}): {data:T|null,error:ApiError|null,loading,reload}. null evita peticiones; pollMs para bandejas/chat. Cambiar page/filtros cambia path con queryString. Cancelar peticiones al desmontar. No retener datos privados cuando no hay sesión.
- useSession() de @/lib/session: {user:Profile|null,loading,error,refresh():Promise<void>,login(email,password):Promise<void>,logout():Promise<void>}. refresh tras editar perfil/verificar. La sesión vive en cookie HTTP-only; no usar localStorage/token ni headers Authorization del navegador. login hace /auth/login y /auth/me. No depender del cuerpo access_token (proxy devuelve authenticated:true).
- Datos compartidos en @/lib/types: Page<T>, Profile, ProfileInput, RegisterInput, Project, ProjectInput, ProjectStatus, AcademicEvent, EventInput, EventCategory, Application, ApplicationStatus, Conversation, ChatMessage, Notification, NotificationKind. Respetan backend/app/schemas.
- @/lib/format: projectStatusLabel, applicationStatusLabel, eventCategoryLabel, formatDate, commaList.

## Componentes y estilos

@/components/ui exporta:
- Button({...buttonProps,variant?:primary|secondary|ghost|danger})
- PageHeader({eyebrow?,title,description?,actions?:ReactNode})
- Badge({children,tone?:neutral|green|amber|red})
- StatePanel({kind:loading|empty|error,title,description?,action?:ReactNode})
- Pagination({page,pageSize,total,onChange})
- FieldError({message?:string|null})

Clases globales: panel, card, auth-panel, form-field (label + input + small), form-row,
form-actions, form-error, form-success, notice, notice-error, button button-primary,
button button-secondary (para Link), badge badge-green, grid, stack, muted, small,
content-narrow, pre-wrap. CSS vars --bg,--surface,--ink,--muted,--line,--accent,--soft,
--danger,--amber. Contraste, teclado, foco y móvil; formularios con labels visibles.
Título de cada vista mediante PageHeader o h1. Ninguna página requiere contenido ficticio
para verse cuidada. No crear barras laterales/topbars extra: shell compartido ya existe.

## Rutas y enlaces entre módulos

/ explorar; /proyectos/nuevo; /proyectos/{id}; /proyectos/{id}/editar;
/eventos; /eventos/nuevo; /eventos/{id}/editar;
/login?next={rutaLocal}; /registro; /verificar?token=...; /perfil;
/solicitudes?scope=sent|received; /solicitudes?application={id} selecciona solicitud;
/conversaciones?application={id} selecciona sala asociada, o ?conversation={id};
/notificaciones enlaza a /solicitudes?application={id}.

No aceptar next externo (solo ruta que empieza / y no // ni /\\). App Router: params
son Promise en páginas dinámicas; envolver useSearchParams en Suspense si se usa.
Sin endpoint de perfiles públicos: no inventar nombres de autores; mostrar universidad
y rol sin UUID largo. Las conversaciones no tienen título en DTO: resolver /projects/{id}
si se necesita mostrar contexto. No descargar todas las páginas solo para contar resultados.

NEXT_PUBLIC_EMAIL_DELIVERY_ENABLED=false por defecto. Registro/reenvío no deben afirmar
que llegó o se envió correo mientras envío real no está habilitado; explicar brevemente
que puede explorar mientras espera habilitación. Pantalla verificar acepta token de enlace
y muestra errores vencido/usado, reenvío genérico y éxito solo tras respuesta 200 real.
Las credenciales y datos ficticios solo se usan en tests. No desbloquear acciones verificadas
en cliente para compensar ausencia de correo.
