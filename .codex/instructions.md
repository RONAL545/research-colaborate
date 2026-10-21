# 📋 Requirements Engineering & Validation Skills (QA & Product)

## 1. Captura & Estructuración de Requerimientos (Product Discovery)
- **Transformación de Ideas Informales a User Stories:** 
  Convierte ideas abstractas publicadas por los estudiantes en historias de usuario estructuradas con el formato:
  > *Como [tipo de usuario], quiero [acción/funcionalidad] para [beneficio/propósito].*
- **Criterios de Aceptación (Gherkin Format):**
  Cada funcionalidad clave del proyecto debe incluir criterios de aceptación redactados en estilo BDD:
  ```gherkin
  Given (Dado que) el estudiante está autenticado con su correo institucional
  When (Cuando) presiona "Solicitar unirme al equipo" en un proyecto
  Then (Entonces) se envía una notificación al creador y se habilita una sala de chat privada.

# Project Overview: Academic Research & Co-Founding Social Platform

## 🎯 Visión del Proyecto
Una plataforma social y colaborativa tipo "Reddit/LinkedIn Académico" enfocada en la investigación universitaria, prototipado y proyectos de ingeniería/tecnología.
Permite a estudiantes publicar ideas de proyectos, conectar con co-fundadores/compañeros de equipo de su propia universidad o de otras, contactar docentes asesores y consultar un directorio/inventario actualizado de congresos, eventos, convocatorias y semilleros de investigación.

---

## 🎨 UI/UX & Design System Skills
- **Diseño centrado en el usuario académico:** Interfaz limpia, profesional y moderna (estilo Tailwind UI, Shadcn/Radix o Material 3).
- **Flujos clave (User Journeys):**
  1. **Feed de Ideas:** Filtros por área (Sistemas, Electrónica, IA, etc.), estado del proyecto (Búsqueda de equipo, En desarrollo, Fase de idea) y universidad.
  2. **Publicación de Proyecto/Idea:** Formulario ágil con título, hipótesis/resumen, habilidades requeridas (Frontend, Backend, Hardware, QA, etc.) y rol buscado.
  3. **Networking y Chat:** Sistema de solicitud de conexión ("Unirme al equipo") y chat en tiempo real o mensajería directa entre creador e interesado.
  4. **Directorio de Congresos y Semilleros:** Tarjetas/Calendario con fechas límites de envío de papers (*call for papers*), ubicación, enlaces oficiales y semilleros disponibles.
  5. **Perfil de Usuario / Docente:** Muestra de proyectos pasados, skills, carrera, universidad y rol (Estudiante, Docente Asesor, Mentor).
- **Responsive & Accesibilidad:** Diseño adaptable (Mobile-First / Desktop) con soporte para modo oscuro/claro y contraste accesible.

---

## 💻 Frontend Development Skills (Flutter / Web React/Next.js)
- **Arquitectura:** Clean Architecture / Feature-First con manejo claro de estado (BLoC/Riverpod en Flutter o Zustand/Redux en Web).
- **Componentes Reutilizables:** Modales de postulación, tarjetas de proyecto, badges de tecnología, buscador con autocompletado y filtros dinámicos.
- **Integraciones:** Websockets / Socket.IO o Firebase Realtime para notificaciones y mensajería en vivo.
- **Optimización:** Carga diferida (lazy loading), paginación infinita en el feed y caché local de publicaciones.

---

## ⚙️ Backend Development Skills (FastAPI / Python)
- **Arquitectura & Modularity:** API Restful modular usando FastAPI con Pydantic V2 para validación estricta de esquemas.
- **Autenticación & Seguridad:** JWT (JSON Web Tokens) con soporte para verificación de correo institucional (`@unaj.edu.pe`, etc.) y control de acceso basado en roles (Student, Teacher, Admin).
- **Base de Datos & ORM:** PostgreSQL con SQLAlchemy 2.0 / Tortoise ORM o asyncpg. Migraciones automatizadas con Alembic.
- **Estructura de Datos Relacional:**
  - `Users` (id, email, role, university_id, bio, skills[])
  - `Projects` (id, author_id, title, description, category, required_roles[], status)
  - `ProjectApplications` (id, project_id, applicant_id, status, message)
  - `Events` (id, title, category [congreso, semillero, call_for_papers], deadline, url, university)
  - `ChatMessages` (id, sender_id, receiver_id, content, timestamp)
- **Búsqueda Eficiente:** Búsqueda vectorial o Full-Text Search (Postgres TSVector) para buscar proyectos por palabras clave o tecnologías.

---

## 🧪 Testing & QA Skills
- **Estrategia TDD / BDD:** Cobertura de pruebas en módulos críticos antes de despliegue.
- **Backend Testing:** Pruebas unitarias e integración con `pytest`, `httpx` / `TestClient`, probando flujos de autenticación, creación de post y permisos.
- **Frontend Testing:** Pruebas unitarias de modelos/lógica y pruebas de integración/UI para el feed y flujo de solicitud de equipo.
- **Integración Continua:** Configuración de scripts para correr tests de manera automática antes de cada commit/push.

---

## 🚀 Git, Workflow & Deployment Rules
- **Control de Versiones:** Uso de Git con estrategia GitFlow. Trabaja en la rama `dev`.
- **Commits:** Sigue la convención *Conventional Commits* (`feat:`, `fix:`, `docs:`, `test:`, `style:`).
- **Automatización de Tareas:** Ejecución autónoma de tareas de creación de carpetas, código, dependencias y pruebas sin solicitar confirmación constante si el modo auto/full-permissions está activo.
- **Push a Remoto:** Al validar pruebas en verde, realiza los commits descriptivos y sube los cambios a `git push origin dev`.

# 🔀 Isolation & Modular Parallel Workflow Rules

## 1. Aislamiento por Módulos y Ramas (Feature Isolation)
- **Operación por Rama:** Cada tarea o módulo asignado DEBE desarrollarse en su propia rama dedicada creada a partir de `dev` (ejemplo: `feature/auth`, `feature/projects-feed`, `feature/applications-chat`, `feature/events-directory`).
- **Prohibido trabajar directo en `dev`:** Ningún agente escribirá o modificará código directamente en `dev` mientras esté desarrollando un módulo asignado.
- **Sin Dependencias Cruzadas Innecesarias:** Cada módulo debe diseñarse de forma desacoplada (usando interfaces, contratos de API / DTOs claros) para que no dependa de código incompleto de otros componentes en paralelo.

## 2. Definición de Contratos (API Contracts First)
- Antes de implementar la lógica interna de un módulo, el agente definirá o respetará los esquemas/interfaces de datos (modelos Pydantic / DTOs en `/schemas`).
- Esto permite que el agente de Frontend y el de Backend o de diferentes módulos puedan avanzar simultáneamente basándose en el mismo contrato.

## 3. Criterios para Integración en `dev` (Merge Readiness)
Un módulo individual solo se fusionará e integrará a la rama `dev` cuando cumpla:
1. Pruebas automáticas del módulo ejecutadas y aprobadas en verde (`pytest` / `flutter test`).
2. Commit con mensajes explicativos en formato Conventional Commits.
3. Proceso de integración:
   ```bash
   git checkout dev
   git pull origin dev
   git merge feature/nombre-del-modulo
   git push origin dev