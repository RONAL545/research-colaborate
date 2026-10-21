"use client";
import { Button, StatePanel } from "@/components/ui";
export default function ErrorPage({ reset }: { reset: () => void }) { return <StatePanel kind="error" title="No pudimos cargar esta página" description="Inténtalo de nuevo en unos momentos." action={<Button onClick={reset}>Reintentar</Button>} />; }
