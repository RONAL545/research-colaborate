# Interfaz del MVP académico

## Navegación y diseño

Marca provisional: Nexo Académico. Interfaz en español, orientada a descubrir proyectos
y formar equipos. Fondo marfil, texto tinta, acento verde bosque, paneles blancos y
bordes suaves; modo oscuro equivalente. Jerarquía editorial, tarjetas de proyectos
legibles, navegación persistente en escritorio y accesible desde móvil. Sin cifras,
proyectos o eventos ficticios presentados como datos reales.

Navegación: Explorar, Eventos, Solicitudes, Conversaciones, Notificaciones y Perfil.
Lecturas públicas de proyectos/eventos; resto requiere sesión. Acciones de publicación,
postulación y mensajes requieren correo verificado. Mostrar reenvío de verificación
sin afirmar que se ha entregado correo mientras el proveedor siga pendiente.

## Pantallas y recorrido

1. Explorar: búsqueda textual, filtros universidad/categoría/estado, paginación;
   estados de carga, error con reintento y vacío con llamada útil a publicar.
2. Proyecto: título, resumen, habilidades, roles, estado, universidad; editar solo autor;
   solicitar unirse solo usuario verificado distinto del autor y recruiting.
3. Publicar/editar: formulario validado según DTO; no aceptar autor/universidad del cliente.
4. Identidad: registro, login, verificación desde token, reenvío y perfil editable propio.
5. Solicitudes: enviadas/recibidas, proyecto y mensaje, decisión del creador en pendientes;
   estado explícito y acceso a conversación asociada.
6. Conversaciones: lista privada, mensajes paginados, remitente propio, envío validado,
   consulta periódica cancelable sin duplicar mensajes ni borrar borradores.
7. Notificaciones: lista propia, filtro sin leer, marcar lectura y vínculo a solicitud.
8. Eventos: directorio público, fecha límite/enlace oficial; formulario de administración
   únicamente Admin verificado. No ocultar oportunidades por depender de datos simulados.

## Criterios de aceptación

```gherkin
Given un visitante sin sesión
When busca un proyecto o consulta eventos
Then ve datos del backend, filtros y paginación
And puede iniciar sesión para participar

Given un estudiante verificado
When publica una idea y otro estudiante se postula
Then el autor puede revisar la solicitud y decidir
And ambos pueden conversar sin exponer mensajes a otros usuarios

Given una respuesta fallida, una lista vacía o una carga pendiente
When se muestra la pantalla
Then el estado es comprensible y no se presenta como un éxito

Given una pantalla móvil o escritorio y navegación por teclado
When recorre la interfaz
Then los controles tienen etiquetas, foco visible y no requieren desplazamiento horizontal
```

Proveedor de correo pendiente: no simular verificación exitosa ni exponer tokens por
rutas de producción. Las pruebas de extremo a extremo pueden usar buzón exclusivo de
pruebas y base PostgreSQL desechable. El cliente no reemplaza permisos del servidor.
