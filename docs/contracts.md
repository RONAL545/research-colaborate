# Contratos v1

Fuente de DTOs: backend/app/schemas. UUID en JSON como string; fechas ISO 8601 con zona horaria; errores FastAPI con detail; validación 422, identidad ausente o inválida 401, permisos 403, recurso ausente 404, duplicados 409.

- Auth: POST /api/v1/auth/register (Register → Profile, 201); POST /login (Login → Token); POST /verify (Verification → mensaje); POST /resend-verification (ResendVerification → respuesta genérica); GET y PUT /me (Profile / ProfileUpdate). JWT Bearer con sub UUID, exp y algoritmo fijo. Registro nunca acepta role ni email_verified.
- Projects: POST /api/v1/projects (ProjectCreate → ProjectRead, 201); GET /projects y GET /projects/{id}; PUT /projects/{id} reemplaza campos editables con ProjectCreate. Lectura pública, escritura solo verificados, edición solo autor. Feed Page[ProjectRead] con q, university, category, status, page>=1 y page_size 1..100; orden estable por created_at e id. Universidad copiada del Principal; autor nunca viene del cliente.
- Events: GET /api/v1/events y /events/{id}; POST /events (EventCreate → EventRead, 201); PUT /events/{id} (EventCreate → EventRead). Lectura pública paginada Page[EventRead], escritura solo Admin verificado.

get_current_user devuelve Principal; require_verified y require_admin son las únicas entradas de autorización compartidas. El bootstrap rechaza identidad hasta implementar auth. Las pruebas de módulos pueden sobrescribir get_current_user en su aplicación local y deben limpiar overrides.

Solicitudes, notificaciones, chat e interfaz quedan para la siguiente etapa del MVP; esta entrega inicial no declara completo el recorrido del MVP.

## Formación de equipos: contratos compartidos

- POST /api/v1/applications/projects/{project_id}: ApplicationCreate → ApplicationRead, 201. Solo identidad verificada, proyecto recruiting de otro autor; duplicado pendiente/aceptado 409; proyecto no recruiting 409; postularse a sí mismo 403. Tras rechazo puede enviarse una nueva solicitud. La protección de duplicados debe existir en PostgreSQL con índice parcial único (project_id, applicant_id) WHERE status IN ('pending','accepted').
- GET /api/v1/applications: Page[ApplicationRead], scope=sent (por defecto) o received; cada usuario solo ve solicitudes propias o de sus proyectos. GET /applications/{id}: solo autor del proyecto o postulante, ajenos reciben 404.
- PATCH /api/v1/applications/{id}: ApplicationDecision → ApplicationRead; solo autor verificado, únicamente pending → accepted/rejected. Pedir pending 422; decisión terminal repetida 409. Autor ajeno 403. Serializar decisiones y creación frente a cambios del proyecto (bloqueo fila del proyecto) y asegurar atomicidad.
- GET /api/v1/notifications: Page[NotificationRead], unread_only=false por defecto. PATCH /notifications/{id}/read: NotificationRead, marcar lectura idempotente; solo destinatario, ajenos 404. Autenticación requerida. No hay endpoint público para crear notificaciones.
- GET /api/v1/conversations: Page[ConversationRead] solo participantes. GET /conversations/{id}/messages: Page[MessageRead], orden created_at ASC, id ASC para consulta periódica. POST /conversations/{id}/messages: MessageCreate → MessageRead, 201; identidad verificada y participante. Ajenos reciben 404 en lecturas/escrituras. Lecturas autenticadas sin exigir correo verificado. Una conversación tiene exactamente los dos participantes originales, uno por solicitud; sigue disponible tras aceptación/rechazo. No hay endpoint público para abrir conversaciones ni elegir sender_id.

Todas las listas usan page>=1, page_size 1..100 y orden created_at DESC, id DESC salvo mensajes. Estados HTTP y DTOs anteriores siguen vigentes. Ningún endpoint acepta IDs de identidad o roles del cliente.

Puertos transaccionales de app/core/collaboration.py: ApplicationContext(id, project_id, author_id, applicant_id), CollaborationActions.submitted(db, context) y decided(db, context, status). El agente solicitudes los inyecta con Depends(get_collaboration_actions). Se ejecutan después de flush, dentro de la misma transacción que la solicitud y antes del commit. El coordinador conecta implementaciones; el adaptador provisional falla con 503 para evitar solicitudes sin efectos asociados. Las pruebas de solicitudes pueden inyectar un fake; las de integración no.

API interna acordada, sin commit/rollback de la sesión recibida:
- notifications/service.py: create_notification(db: Session, *, recipient_id: UUID, application_id: UUID, kind: NotificationKind) → Notification. Idempotente por (recipient_id, application_id, kind); usa savepoint para no abortar transacción externa ante duplicado.
- chat/service.py: open_conversation(db: Session, *, application_id: UUID, project_id: UUID, author_id: UUID, applicant_id: UUID) → Conversation. Idempotente por application_id, no cambia participantes existentes y rechaza contexto distinto. Usa savepoint ante duplicados.

submitted abre conversación y notifica al autor con application_received; decided notifica al postulante con application_accepted/rejected. FK application_id de notificaciones y conversaciones la añade coordinador tras integrar solicitudes. Cada módulo puede trabajar con UUID y datos ficticios solo en pruebas; no usa modelos incompletos de otro agente.

Historias: como estudiante quiero postularme y recibir una decisión; como creador quiero revisar y decidir solicitudes; como participante quiero recibir avisos privados y conversar. Criterios Gherkin en .codex/MVP.md, se validarán también con el recorrido completo usando JWT real.
