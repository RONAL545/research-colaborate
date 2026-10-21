import { Suspense } from "react";
import { VerifyScreen } from "@/features/identity/screens";
export default function VerifyPage() { return <Suspense fallback={<p role="status">Cargando verificación…</p>}><VerifyScreen /></Suspense>; }
