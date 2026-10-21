# Contratos v1

Fuente de DTOs: backend/app/schemas. UUID en JSON como string; fechas ISO 8601 con zona horaria; errores FastAPI con detail; validación 422, identidad ausente o inválida 401, permisos 403, recurso ausente 404, duplicados 409.

- Auth: POST /api/v1/auth/register (Register → Profile, 201); POST /login (Login → Token); POST /verify (Verification → mensaje); POST /resend-verification (ResendVerification → respuesta genérica); GET y PUT /me (Profile / ProfileUpdate). JWT Bearer con sub UUID, exp y algoritmo fijo. Registro nunca acepta role ni email_verified.
- Projects: POST /api/v1/projects (ProjectCreate → ProjectRead, 201); GET /projects y GET /projects/{id}; PUT /projects/{id} reemplaza campos editables con ProjectCreate. Lectura pública, escritura solo verificados, edición solo autor. Feed Page[ProjectRead] con q, university, category, status, page>=1 y page_size 1..100; orden estable por created_at e id. Universidad copiada del Principal; autor nunca viene del cliente.
- Events: GET /api/v1/events y /events/{id}; POST /events (EventCreate → EventRead, 201); PUT /events/{id} (EventCreate → EventRead). Lectura pública paginada Page[EventRead], escritura solo Admin verificado.

get_current_user devuelve Principal; require_verified y require_admin son las únicas entradas de autorización compartidas. El bootstrap rechaza identidad hasta implementar auth. Las pruebas de módulos pueden sobrescribir get_current_user en su aplicación local y deben limpiar overrides.

Solicitudes, notificaciones, chat e interfaz quedan para la siguiente etapa del MVP; esta entrega inicial no declara completo el recorrido del MVP.
