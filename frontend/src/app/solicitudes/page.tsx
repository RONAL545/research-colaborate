import { Suspense } from "react";
import { ApplicationsView } from "@/features/collaboration/views";
export default function Page() {
  return (
    <Suspense fallback={<p role="status">Cargando…</p>}>
      <ApplicationsView />
    </Suspense>
  );
}
