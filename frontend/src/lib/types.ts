export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}
export type Role = "student" | "teacher" | "admin";
export interface ProfileInput {
  name: string;
  university: string;
  career: string;
  bio: string;
  skills: string[];
}
export interface Profile extends ProfileInput {
  id: string;
  email: string;
  role: Role;
  email_verified: boolean;
}
export interface RegisterInput {
  email: string;
  password: string;
  name: string;
  university: string;
  career: string;
}
export type ProjectStatus = "idea" | "recruiting" | "in_progress";
export interface ProjectInput {
  title: string;
  description: string;
  category: string;
  skills: string[];
  required_roles: string[];
  status: ProjectStatus;
}
export interface Project extends ProjectInput {
  id: string;
  author_id: string;
  university: string;
}
export type EventCategory = "congreso" | "semillero" | "call_for_papers";
export interface EventInput {
  title: string;
  category: EventCategory;
  deadline: string | null;
  url: string;
  university: string;
}
export interface AcademicEvent extends EventInput {
  id: string;
  created_at: string;
}
export type ApplicationStatus = "pending" | "accepted" | "rejected";
export interface Application {
  id: string;
  project_id: string;
  applicant_id: string;
  message: string;
  status: ApplicationStatus;
  created_at: string;
  updated_at: string;
}
export interface Conversation {
  id: string;
  application_id: string;
  project_id: string;
  author_id: string;
  applicant_id: string;
  created_at: string;
}
export interface ChatMessage {
  id: string;
  conversation_id: string;
  sender_id: string;
  content: string;
  created_at: string;
}
export type NotificationKind =
  "application_received" | "application_accepted" | "application_rejected";
export interface Notification {
  id: string;
  application_id: string;
  kind: NotificationKind;
  read_at: string | null;
  created_at: string;
}
