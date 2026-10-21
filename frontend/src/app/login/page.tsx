import { Suspense } from "react";
import { LoginScreen } from "@/features/identity/screens";
export default function LoginPage() {
  return (
    <Suspense fallback={<p role="status">Cargando acceso…</p>}>
      <LoginScreen />
    </Suspense>
  );
}
