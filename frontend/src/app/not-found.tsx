import Link from "next/link";
import { StatePanel } from "@/components/ui";
export default function NotFound() {
  return (
    <StatePanel
      kind="empty"
      title="No encontramos esta página"
      description="Vuelve a explorar y encuentra tu próxima oportunidad."
      action={
        <Link className="button button-primary" href="/">
          Explorar proyectos
        </Link>
      }
    />
  );
}
