import { EventEditor } from "@/features/discovery/events";
export default async function Page({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <EventEditor id={id} />;
}
