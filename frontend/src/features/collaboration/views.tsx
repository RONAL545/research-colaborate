"use client";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useEffect, useState, type FormEvent, type ReactNode } from "react";
import { api, errorMessage, queryString } from "@/lib/api";
import { useSession } from "@/lib/session";
import { useRemote } from "@/lib/use-remote";
import { applicationStatusLabel, formatDate } from "@/lib/format";
import type { Application, Conversation, ChatMessage, Notification, Page, Project } from "@/lib/types";
import { Badge, Button, PageHeader, Pagination, StatePanel } from "@/components/ui";
import styles from "./views.module.css";

function Protected({ children, path }: { children: ReactNode; path: string }) {
  const { user, loading, error, refresh } = useSession();
  if (loading) return <StatePanel kind="loading" title="Comprobando tu sesión" />;
  if (error) return <StatePanel kind="error" title={error} action={<Button onClick={() => void refresh()}>Reintentar</Button>} />;
  if (!user) return <StatePanel kind="empty" title="Este espacio es privado" description="Inicia sesión para continuar con tus colaboraciones." action={<Link className="button button-primary" href={`/login?next=${encodeURIComponent(path)}`}>Iniciar sesión</Link>} />;
  return <div key={user.id}>{children}</div>;
}
function RemoteState({ remote, empty }: { remote: {loading:boolean;error:Error|null;data:unknown;reload:()=>void}; empty?:boolean }) {
  if (remote.error) return <StatePanel kind="error" title={errorMessage(remote.error)} action={<Button onClick={remote.reload}>Reintentar</Button>} />;
  if (remote.loading) return <StatePanel kind="loading" title="Cargando tu espacio" />;
  if (empty) return <StatePanel kind="empty" title="Aún no hay contenido" description="Las novedades de tus colaboraciones aparecerán aquí." action={<Link href="/" className="button button-secondary">Explorar proyectos</Link>} />;
  return null;
}
function ProjectTitle({ id }: {id:string}) {
  const project = useRemote<Project>(`/projects/${encodeURIComponent(id)}`);
  return <Link className={styles.project} href={`/proyectos/${id}`}>{project.data?.title ?? (project.error ? "Ver proyecto" : "Cargando proyecto…")}</Link>;
}
function ApplicationCard({ application, received, reload }: {application:Application;received:boolean;reload:()=>void}) {
  const { user } = useSession(); const [busy,setBusy] = useState(false); const [error,setError] = useState("");
  async function decide(status:"accepted"|"rejected") { setBusy(true);setError("");try { await api.patch(`/applications/${application.id}`,{status});reload(); }catch(e){setError(errorMessage(e));}finally{setBusy(false);} }
  return <article className={`card ${styles.application}`}><div className={styles.row}><ProjectTitle id={application.project_id}/><Badge tone={application.status === "accepted" ? "green" : application.status === "pending" ? "amber" : "neutral"}>{applicationStatusLabel[application.status]}</Badge></div><p className="small muted">{received ? "Solicitud recibida" : "Tu solicitud"} · {formatDate(application.created_at)}</p><p className="pre-wrap">{application.message}</p><div className="form-actions"><Link href={`/conversaciones?application=${application.id}`} className="button button-secondary">Abrir conversación</Link>{received && user?.id !== application.applicant_id && application.status === "pending" && user?.email_verified && <><Button disabled={busy} onClick={()=>void decide("accepted")}>Aceptar solicitud</Button><Button variant="danger" disabled={busy} onClick={()=>void decide("rejected")}>Rechazar</Button></>}</div>{received && application.status === "pending" && !user?.email_verified && <p className="notice">Verifica tu correo para decidir solicitudes. <Link href="/verificar">Verificación</Link></p>}{error && <p role="alert" className="form-error">{error}</p>}</article>;
}
function ApplicationsContent() {
  const search = useSearchParams(); const { user }=useSession(); const scope=search.get("scope")==="received"?"received":"sent"; const selected=search.get("application");const [page,setPage]=useState(1);
  const list=useRemote<Page<Application>>(`/applications${queryString({scope,page,page_size:20})}`,{pollMs:10000});
  const detail=useRemote<Application>(selected?`/applications/${encodeURIComponent(selected)}`:null);
  return <><div className={styles.tabs}><Link aria-current={scope==="sent"?"page":undefined} href="/solicitudes?scope=sent" onClick={()=>setPage(1)}>Enviadas</Link><Link aria-current={scope==="received"?"page":undefined} href="/solicitudes?scope=received" onClick={()=>setPage(1)}>Recibidas</Link></div>{selected ? <><Link href={`/solicitudes?scope=${scope}`}>← Volver a la bandeja</Link><RemoteState remote={detail}/>{detail.data && <ApplicationCard application={detail.data} received={detail.data.applicant_id!==user?.id} reload={detail.reload}/>}</> : <><RemoteState remote={list} empty={list.data?.items.length===0}/><div className="stack">{list.data?.items.map(a=><ApplicationCard key={a.id} application={a} received={scope==="received"} reload={list.reload}/>)}</div>{list.data && <Pagination page={page} pageSize={20} total={list.data.total} onChange={setPage}/>}</>}</>;
}
export function ApplicationsView(){return <><PageHeader eyebrow="Forma tu equipo" title="Solicitudes" description="Comparte ideas, revisa propuestas y da el siguiente paso."/><Protected path="/solicitudes"><ApplicationsContent/></Protected></>;}
const notificationLabels = {application_received:"Tienes una nueva solicitud",application_accepted:"Tu solicitud fue aceptada",application_rejected:"Tu solicitud fue rechazada"};
function NotificationsContent(){
  const [unread,setUnread]=useState(false);const [page,setPage]=useState(1);const [busy,setBusy]=useState<string|null>(null);const [error,setError]=useState("");
  const list=useRemote<Page<Notification>>(`/notifications${queryString({unread_only:unread,page,page_size:20})}`,{pollMs:10000});
  async function read(id:string){setBusy(id);setError("");try{await api.patch(`/notifications/${id}/read`);list.reload();}catch(e){setError(errorMessage(e));}finally{setBusy(null);}}
  return <><label className={styles.filter}><input type="checkbox" checked={unread} onChange={e=>{setUnread(e.target.checked);setPage(1);}}/> Mostrar solo sin leer</label>{error && <p className="form-error" role="alert">{error}</p>}<RemoteState remote={list} empty={list.data?.items.length===0}/><div className="stack">{list.data?.items.map(n=><article key={n.id} className={`card ${styles.notification}`}><div><Badge tone={n.read_at?"neutral":"green"}>{n.read_at?"Leída":"Sin leer"}</Badge><h2><Link href={`/solicitudes?application=${n.application_id}`}>{notificationLabels[n.kind]}</Link></h2><p className="small muted">{formatDate(n.created_at)}</p></div>{!n.read_at && <Button variant="secondary" disabled={busy===n.id} onClick={()=>void read(n.id)}>Marcar como leída</Button>}</article>)}</div>{list.data && <Pagination page={page} pageSize={20} total={list.data.total} onChange={setPage}/>}</>;
}
export function NotificationsView(){return <><PageHeader eyebrow="Tu actividad" title="Notificaciones" description="Las novedades de tus solicitudes, en un solo lugar."/><Protected path="/notificaciones"><NotificationsContent/></Protected></>;}

function RoomTitle({id}:{id:string}){const project=useRemote<Project>(`/projects/${encodeURIComponent(id)}`);return <span>{project.data?.title??"Conversación de proyecto"}</span>;}
function Chat({conversationId,projectId}:{conversationId:string;projectId?:string}){
  const {user}=useSession();const [page,setPage]=useState(1);const [draft,setDraft]=useState("");const [busy,setBusy]=useState(false);const [error,setError]=useState("");
  const messages=useRemote<Page<ChatMessage>>(`/conversations/${encodeURIComponent(conversationId)}/messages${queryString({page,page_size:20})}`,{pollMs:10000});
  async function send(e:FormEvent){e.preventDefault();if(!draft.trim()||busy)return;const submitted=draft;setBusy(true);setError("");try{await api.post(`/conversations/${conversationId}/messages`,{content:submitted.trim()});setDraft(current=>current===submitted?"":current);setPage(Math.max(1,Math.ceil(((messages.data?.total??0)+1)/20)));messages.reload();}catch(e){setError(errorMessage(e));}finally{setBusy(false);}}
  const latest=Math.max(1,Math.ceil((messages.data?.total??0)/20));
  return <section className={`panel ${styles.chat}`} aria-label="Conversación privada"><div className={styles.chatHeader}>{projectId?<ProjectTitle id={projectId}/>:<h2>Conversación privada</h2>}<p className="small muted">Solo tú y la otra persona participante pueden leer estos mensajes. Se actualiza cada 10 segundos.</p></div><RemoteState remote={messages} empty={messages.data?.items.length===0}/>{messages.data && !messages.error && <><div className={styles.messages} aria-label="Mensajes">{Array.from(new Map(messages.data.items.map(m=>[m.id,m])).values()).map(m=><article key={m.id} className={`${styles.message} ${m.sender_id===user?.id?styles.own:""}`}><span className="small muted">{m.sender_id===user?.id?"Tú":"Otra persona participante"} · {formatDate(m.created_at)}</span><p className="pre-wrap">{m.content}</p></article>)}</div><Pagination page={page} pageSize={20} total={messages.data.total} onChange={setPage}/>{latest>page && <Button variant="ghost" onClick={()=>setPage(latest)}>Ir a los últimos mensajes</Button>}</>}{!messages.error && <form onSubmit={send} className={styles.composer}><label className="form-field">Mensaje<textarea rows={3} maxLength={5000} value={draft} disabled={!user?.email_verified} onChange={e=>setDraft(e.target.value)} placeholder="Continúa la conversación…"/></label><div className={styles.row}><small className="muted">{draft.length}/5000</small><Button type="submit" disabled={busy||!draft.trim()||!user?.email_verified}>{busy?"Enviando…":"Enviar mensaje"}</Button></div>{!user?.email_verified && <p className="notice">Verifica tu correo para enviar mensajes. <Link href="/verificar">Verificación</Link></p>}{error && <p className="form-error" role="alert">{error}</p>}</form>}</section>;
}
function ConversationsContent(){
  const search=useSearchParams();const application=search.get("application");const selected=search.get("conversation");const [page,setPage]=useState(1);const [resolved,setResolved]=useState<Conversation|null>(null);const [lookupError,setLookupError]=useState("");const [looking,setLooking]=useState(false);const [retry,setRetry]=useState(0);
  const list=useRemote<Page<Conversation>>(`/conversations${queryString({page,page_size:20})}`,{pollMs:10000});
  useEffect(()=>{if(!application)return;const controller=new AbortController();let active=true;setLooking(true);setResolved(null);setLookupError("");void(async()=>{try{let next=1;while(active){const result=await api.get<Page<Conversation>>(`/conversations${queryString({page:next,page_size:100})}`,controller.signal);const found=result.items.find(c=>c.application_id===application);if(found){setResolved(found);return;}if(next*100>=result.total){setLookupError("No encontramos una conversación para esta solicitud o no tienes acceso.");return;}next++;}}catch(e){if(active)setLookupError(errorMessage(e));}finally{if(active)setLooking(false);}})();return()=>{active=false;controller.abort();};},[application,retry]);
  const id=application?(resolved?.application_id===application?resolved.id:undefined):selected;const context=application?resolved:list.data?.items.find(c=>c.id===id);
  return <div className={styles.workspace}><aside className={styles.inbox} aria-label="Tus conversaciones"><h2>Tu bandeja privada</h2><RemoteState remote={list} empty={list.data?.items.length===0}/>{list.data?.items.map(c=><Link key={c.id} className={`${styles.room} ${id===c.id?styles.active:""}`} href={`/conversaciones?conversation=${c.id}`}><RoomTitle id={c.project_id}/><small>{formatDate(c.created_at)}</small><span className="small">Abrir conversación →</span></Link>)}{list.data && <Pagination page={page} pageSize={20} total={list.data.total} onChange={setPage}/>}</aside><div className={styles.chatColumn}>{looking?<StatePanel kind="loading" title="Buscando la conversación"/>:lookupError&&application?<StatePanel kind="error" title={lookupError} action={<Button onClick={()=>setRetry(x=>x+1)}>Reintentar</Button>}/>:id?<Chat key={id} conversationId={id} projectId={context?.project_id}/>:<StatePanel kind="empty" title="Una buena colaboración empieza conversando" description="Selecciona una conversación de tu bandeja o abre el chat desde una solicitud."/>}</div></div>;
}
export function ConversationsView(){return <><PageHeader eyebrow="Conecta y construye" title="Conversaciones" description="Un espacio privado para acordar los próximos pasos."/><Protected path="/conversaciones"><ConversationsContent/></Protected></>;}
