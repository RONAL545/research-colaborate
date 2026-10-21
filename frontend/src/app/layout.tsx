import type { Metadata } from "next";
import { AppShell } from "@/components/shell";
import "./globals.css";
export const metadata: Metadata = { title: { default: "Nexo Académico · Ideas que conectan", template: "%s · Nexo Académico" }, description: "Encuentra proyectos universitarios, comparte tus ideas y construye tu próximo equipo de investigación." };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="es"><body><AppShell>{children}</AppShell></body></html>; }
