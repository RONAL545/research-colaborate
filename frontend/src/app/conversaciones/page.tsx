import { Suspense } from "react";
import { ConversationsView } from "@/features/collaboration/views";
export default function Page(){return <Suspense fallback={<p role="status">Cargando…</p>}><ConversationsView/></Suspense>;}
