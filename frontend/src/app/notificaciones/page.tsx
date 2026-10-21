import { Suspense } from "react";
import { NotificationsView } from "@/features/collaboration/views";
export default function Page(){return <Suspense fallback={<p role="status">Cargando…</p>}><NotificationsView/></Suspense>;}
