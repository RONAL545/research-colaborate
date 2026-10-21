// @vitest-environment node
import { afterEach, expect, it, vi } from "vitest";
import { NextRequest } from "next/server";
import { GET, POST } from "@/app/api/backend/[...path]/route";
afterEach(() => vi.unstubAllGlobals());
it("keeps login token in an HttpOnly cookie and never returns it to JS", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(Response.json({ access_token: "secret-test-token", token_type: "bearer" })));
  const response = await POST(new NextRequest("http://localhost:3000/api/backend/auth/login", { method: "POST", headers: { origin: "http://localhost:3000" }, body: JSON.stringify({ email: "a@u.edu", password: "test" }) }), { params: Promise.resolve({ path: ["auth", "login"] }) });
  expect(await response.json()).toEqual({ authenticated: true }); expect(response.headers.get("set-cookie")).toContain("HttpOnly"); expect(response.cookies.get("nexo_session")?.value).toBe("secret-test-token");
});
it("forwards only the server cookie as bearer and refuses cross-origin mutations", async () => {
  const fetch = vi.fn().mockResolvedValue(Response.json({ id: "one" })); vi.stubGlobal("fetch", fetch);
  await GET(new NextRequest("http://localhost:3000/api/backend/auth/me", { headers: { cookie: "nexo_session=session-token", authorization: "Bearer forged" } }), { params: Promise.resolve({ path: ["auth", "me"] }) });
  expect(fetch).toHaveBeenCalledWith(expect.any(String), expect.objectContaining({ headers: expect.objectContaining({ Authorization: "Bearer session-token" }) }));
  const response = await POST(new NextRequest("http://localhost:3000/api/backend/projects", { method: "POST", headers: { origin: "https://other.example" } }), { params: Promise.resolve({ path: ["projects"] }) }); expect(response.status).toBe(403); expect(fetch).toHaveBeenCalledTimes(1);
});
it("rejects paths outside API resources", async () => { const response = await GET(new NextRequest("http://localhost/api/backend/__test__/mail"), { params: Promise.resolve({ path: ["__test__", "mail"] }) }); expect(response.status).toBe(404); });
