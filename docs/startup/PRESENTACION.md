# Nexo Académico — de una idea a un equipo

Material para facultades, incubadoras y direcciones de investigación. Estado: MVP;
piloto y modelo comercial por validar. Abrir `/universidades` durante la exposición.

## Pitch de 60 segundos

Una buena idea universitaria necesita encontrar a las personas capaces de hacerla
avanzar. Nuestra hipótesis es que esa búsqueda se dispersa entre grupos, contactos
personales y convocatorias que no siempre llegan a quienes pueden aportar.

Nexo Académico reúne proyectos, habilidades y oportunidades: un estudiante publica
lo que quiere construir, otro descubre la idea y se postula; el creador revisa la
solicitud y ambos conversan para acordar los siguientes pasos.

Contamos con un MVP que permite demostrar ese recorrido. Buscamos una facultad aliada
para un piloto de ocho semanas: acompañar una comunidad pequeña, medir si se generan
colaboraciones y aprender qué necesita una universidad para adoptarlo.

## Guion de siete minutos

| Tiempo | Mensaje | Qué mostrar |
| --- | --- | --- |
| 0:00–0:45 | El talento necesita encontrar dónde aportar; hipótesis por validar. | Encabezado de `/universidades`. |
| 0:45–1:30 | De descubrimiento a conversación con contexto académico. | Recorrido visual. |
| 1:30–4:00 | Dos estudiantes forman una conexión. | Proyecto → solicitud → decisión → conversación. |
| 4:00–5:00 | Un piloto acotado y acompañado. | Plan de ocho semanas. |
| 5:00–6:00 | Suscripción institucional como hipótesis de ingreso. | Explicar que precio y disposición de pago no están validados. |
| 6:00–7:00 | Pedimos un responsable y una reunión de diseño del piloto. | Objetivos y siguiente paso. |

## Demo reproducible

1. Iniciar frontend y backend según README. Para demostrar el flujo sin proveedor de
   correo, usar exclusivamente el servidor y PostgreSQL de pruebas descritos en
   `frontend/README.md`; nunca habilitar ese servidor en producción.
2. Abrir `/universidades` y entrar en «Explorar la plataforma».
3. Con una cuenta verificada de pruebas publicar un proyecto marcado «Demostración».
4. En otro contexto de navegador, entrar con un segundo estudiante, buscarlo y postularse.
5. Con el creador abrir solicitudes recibidas, aceptar y abrir la conversación.
6. Enviar un mensaje y comprobarlo con el postulante. Mostrar la notificación.
7. Consultar eventos sin presentar convocatorias ficticias como oportunidades reales.
8. Volver al piloto. Si falla un servicio, explicar el estado real; no presentar capturas
   o grabaciones como una sesión en vivo.

`frontend/e2e/mvp.spec.ts` reproduce el recorrido con backend real. Sus credenciales y
buzón solo sirven en el entorno de pruebas. No añadir datos ficticios a producción.

## Piloto propuesto

Ocho semanas, una facultad o semillero y un responsable de cada parte. La universidad
invita participantes y propone retos; Nexo prepara la operación y acompaña la activación.

- Semanas 1–2: entrevistas, alcance, objetivos, participantes, entorno y correo.
- Semanas 3–6: publicaciones, postulaciones y acompañamiento semanal.
- Semanas 7–8: entrevistas de cierre, métricas y decisión de continuidad.

Acordar antes alcance, soporte, responsabilidades y manejo de datos. No hay convenio
ni oferta comercial cerrada. Los números del plan son propuestas, no resultados.

## Métricas propuestas

No existe un panel institucional de analítica. Comenzar con evaluación manual agregada
sin divulgar mensajes privados. Fijar las metas con la institución antes de iniciar.

| Indicador | Definición |
| --- | --- |
| Activación | Participantes que publican o se postulan / registrados del piloto. |
| Conexión | Proyectos con alguna solicitud aceptada / proyectos del piloto. |
| Primera solicitud | Mediana de tiempo desde publicación; informar aparte los proyectos sin solicitudes. |
| Continuidad | Equipos que confirman colaboración al cierre / equipos entrevistados. |

Una aceptación no demuestra resultados de investigación. Las entrevistas deben
contrastar si se empezó a colaborar y qué obstáculos persistieron.

## Hipótesis de negocio

Usuario: estudiante que busca proyectos o colaboradores. Posible comprador: dirección
de investigación, innovación o emprendimiento. Promotor interno: docente o responsable
de semillero. Hipótesis: suscripción institucional con acompañamiento, manteniendo acceso
de estudiantes dentro del convenio.

Entrevistar al comprador para validar presupuesto, prioridad y disposición de pago.
Estimar infraestructura, correo, soporte y activación antes de fijar precio. No se afirma
un tamaño de mercado ni una ventaja competitiva probada. La propuesta a contrastar es
un recorrido de descubrimiento y formación de equipos entre comunidades universitarias.

## Preguntas previsibles

- ¿Clientes o alianzas? No hay tracción, ingresos ni convenios documentados como validados.
- ¿Producción? MVP local; envío de correo y preparación operativa pendientes.
- ¿IA o matching automático? No. El descubrimiento actual usa búsqueda y filtros.
- ¿Chat en tiempo real? Consulta periódica, no WebSocket.
- ¿SSO o analítica institucional? No forman parte del MVP.
- ¿Qué pedimos? Responsable institucional, entrevistas y reunión para acordar el piloto.

## De demo a piloto

Pendientes: entrega de correo real y dominios habilitados; entorno con HTTPS y secretos;
copias y recuperación verificadas; responsables de soporte y condiciones de tratamiento
de datos acordadas. No son certificaciones ni funcionalidades completadas. En esta
etapa no se despliega a hosting externo.
