import { NextRequest, NextResponse } from "next/server";
const resources = new Set([
  "auth",
  "projects",
  "events",
  "applications",
  "notifications",
  "conversations",
]);
const cookieName = "nexo_session";
async function proxy(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> },
) {
  const { path } = await context.params;
  if (
    !resources.has(path[0]) ||
    path.some(
      (segment) =>
        segment === "." ||
        segment === ".." ||
        segment.includes("/") ||
        segment.includes("\\"),
    )
  )
    return NextResponse.json({ detail: "Not found" }, { status: 404 });
  if (!["GET", "HEAD"].includes(request.method)) {
    const origin = request.headers.get("origin");
    if (origin && origin !== request.nextUrl.origin)
      return NextResponse.json({ detail: "Invalid origin" }, { status: 403 });
    if (request.headers.get("sec-fetch-site") === "cross-site")
      return NextResponse.json({ detail: "Invalid origin" }, { status: 403 });
  }
  const base = (process.env.BACKEND_URL ?? "http://127.0.0.1:8000").replace(
    /\/$/,
    "",
  );
  const target = `${base}/api/v1/${path.map(encodeURIComponent).join("/")}${request.nextUrl.search}`;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  const session = request.cookies.get(cookieName)?.value;
  if (session) headers.Authorization = `Bearer ${session}`;
  try {
    const upstream = await fetch(target, {
      method: request.method,
      headers,
      body: ["GET", "HEAD"].includes(request.method)
        ? undefined
        : await request.text(),
      cache: "no-store",
      redirect: "manual",
      signal: AbortSignal.timeout(15000),
    });
    if (upstream.status >= 300 && upstream.status < 400)
      return NextResponse.json(
        { detail: "Unexpected redirect" },
        { status: 502 },
      );
    const data = await upstream
      .json()
      .catch(() => ({ detail: "Invalid response" }));
    const login = path.join("/") === "auth/login";
    if (login && upstream.ok) {
      if (typeof data.access_token !== "string")
        return NextResponse.json(
          { detail: "Invalid session response" },
          { status: 502 },
        );
      const response = NextResponse.json({ authenticated: true });
      response.cookies.set(cookieName, data.access_token, {
        httpOnly: true,
        secure: process.env.NODE_ENV === "production",
        sameSite: "lax",
        path: "/",
      });
      response.headers.set("Cache-Control", "no-store");
      return response;
    }
    const response = NextResponse.json(data, { status: upstream.status });
    response.headers.set("Cache-Control", "no-store");
    if (upstream.status === 401 && !login) response.cookies.delete(cookieName);
    return response;
  } catch {
    return NextResponse.json(
      { detail: "Backend unavailable" },
      { status: 502 },
    );
  }
}
export { proxy as GET, proxy as POST, proxy as PUT, proxy as PATCH };
