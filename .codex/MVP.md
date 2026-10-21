# MVP: colaboración académica

Propuesta inicial derivada de `instructions.md`. Este documento define el alcance; no implica funcionalidades implementadas.

## Objetivo

Permitir que un estudiante publique una idea, encuentre colaboradores y gestione solicitudes para formar un equipo.

## Alcance inicial

1. Registro, verificación del correo institucional e inicio de sesión.
2. Perfil básico: nombre, universidad, carrera, biografía y habilidades.
3. Publicación y edición de proyectos propios: título, resumen, categoría, habilidades, roles buscados y estado.
4. Feed con búsqueda por texto, filtros por universidad, categoría y estado, y paginación.
5. Solicitudes para unirse a un proyecto, con mensaje y estados pendiente, aceptada o rechazada.
6. Notificaciones dentro de la plataforma y conversación privada entre creador y postulante.
7. Directorio básico de eventos con fechas y enlaces oficiales, administrado por un usuario con rol Admin.

Se posponen recomendaciones, búsqueda vectorial, carga infinita, notificaciones push, calendarios avanzados y herramientas específicas de mentoría. El chat puede comenzar con consulta periódica; el tiempo real no bloquea el flujo principal.

## Historias y criterios de aceptación

### Identidad

Como estudiante, quiero verificar mi correo institucional para participar con una identidad académica validada.

```gherkin
Given un correo perteneciente a un dominio institucional habilitado
When el usuario completa el registro y utiliza un enlace de verificación vigente
Then su correo queda verificado y puede publicar y postularse

Given un enlace de verificación vencido o utilizado
When alguien intenta usarlo
Then la verificación no se completa y se permite solicitar otro enlace
```

### Perfil

Como estudiante, quiero presentar mi universidad y habilidades para que otros evalúen mi participación.

```gherkin
Given un usuario autenticado
When guarda su perfil con datos válidos
Then los cambios aparecen en su perfil
And no puede modificar el perfil de otro usuario
```

### Proyectos

Como estudiante, quiero publicar una idea y los roles que necesito para encontrar colaboradores.

```gherkin
Given un estudiante autenticado con correo verificado
When publica un proyecto con título, resumen, categoría y roles válidos
Then el proyecto aparece en el feed y queda asociado a su autor

Given un proyecto existente
When un usuario distinto de su autor intenta editarlo
Then el sistema rechaza la operación
```

### Descubrimiento

Como estudiante, quiero buscar y filtrar proyectos para encontrar oportunidades compatibles con mis intereses.

```gherkin
Given proyectos de distintas universidades, categorías y estados
When el usuario combina búsqueda y filtros
Then recibe únicamente proyectos que cumplen los criterios
And puede consultar las siguientes páginas sin duplicados
```

### Formación de equipos

Como estudiante, quiero solicitar unirme a un proyecto para aportar mis habilidades.

```gherkin
Given un estudiante verificado y un proyecto de otro usuario que busca equipo
When envía una solicitud con un mensaje
Then se crea una solicitud pendiente
And el creador recibe una notificación dentro de la plataforma
And se habilita una conversación privada entre ambos

Given una solicitud pendiente o aceptada para el mismo proyecto y estudiante
When el estudiante intenta enviar otra solicitud
Then el sistema evita el duplicado

Given una solicitud pendiente
When el creador la acepta o rechaza
Then se actualiza el estado y se notifica al postulante
And ningún otro usuario puede tomar esa decisión
```

### Mensajería

Como postulante o creador, quiero conversar sobre la colaboración para acordar los próximos pasos.

```gherkin
Given una conversación habilitada por una solicitud
When uno de sus dos participantes envía un mensaje válido
Then el mensaje queda guardado y disponible para ambos
And otros usuarios no pueden leerlo ni enviar mensajes en esa conversación
```

### Eventos

Como estudiante, quiero consultar eventos y convocatorias para encontrar oportunidades académicas.

```gherkin
Given eventos publicados por un administrador
When un estudiante consulta el directorio
Then ve el título, tipo, fecha límite cuando corresponda y enlace oficial

Given un usuario sin rol Admin
When intenta crear o modificar un evento
Then el sistema rechaza la operación
```

## Orden de implementación propuesto

1. Preparar repositorio, rama dev, configuración y estructura modular.
2. Crear backend FastAPI, PostgreSQL, migraciones y autenticación.
3. Completar perfiles, proyectos, búsqueda y filtros.
4. Completar solicitudes, permisos, notificaciones y mensajería.
5. Construir la interfaz y conectar el recorrido completo.
6. Incorporar directorio de eventos y validar el MVP integrado.

El cliente inicial se implementó como interfaz web con React/Next.js en `frontend/`, adaptable a móvil y escritorio. Flutter queda fuera de esta primera entrega.

## Condiciones para considerar listo el MVP

- Dos estudiantes pueden completar el recorrido registro → verificación → proyecto → solicitud → decisión → conversación.
- Las pruebas cubren autenticación, verificación, permisos, creación de proyectos, solicitudes duplicadas y privacidad de mensajes.
- Las migraciones permiten preparar una base de datos vacía.
- La interfaz funciona en móvil y escritorio, con estados de carga, vacío y error, contraste accesible y modo claro/oscuro.
- El repositorio documenta configuración, variables de entorno y comandos de ejecución y pruebas, sin secretos versionados.
- Las comprobaciones de CI pasan antes del commit y push a dev indicados en las instrucciones.

## Datos necesarios para puesta en marcha

- Código o remoto existente, si el proyecto ya comenzó en otra ubicación.
- Dominios institucionales permitidos y proveedor para enviar verificaciones de correo.
- Entorno de despliegue y configuración de base de datos.
- Elección de cliente inicial: web o Flutter.
