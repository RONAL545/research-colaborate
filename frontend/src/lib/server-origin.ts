import type { NextRequest } from "next/server";

/** Next may normalize loopback URLs; compare with the actual HTTP Host header. */
export function isSameOrigin(request: NextRequest): boolean {
  if (request.headers.get("sec-fetch-site") === "cross-site") return false;
  const origin = request.headers.get("origin");
  if (!origin) return true;
  try {
    const target = new URL(request.url);
    target.host = request.headers.get("host") ?? target.host;
    return new URL(origin).origin === target.origin;
  } catch {
    return false;
  }
}
