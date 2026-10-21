import { afterEach, describe, expect, it, vi } from "vitest";
import { api, ApiError, queryString } from "@/lib/api";
afterEach(() => vi.unstubAllGlobals());
describe("API boundary", () => {
  it("encodes combined filters and keeps pagination", () => { expect(queryString({ q: "IA & redes", page: 2, university: "", status: undefined })).toBe("?q=IA+%26+redes&page=2"); });
  it("uses same origin without exposing tokens", async () => { const fetch = vi.fn().mockResolvedValue(Response.json({ items: [] })); vi.stubGlobal("fetch", fetch); await api.get("/projects"); expect(fetch).toHaveBeenCalledWith("/api/backend/projects", expect.objectContaining({ credentials: "same-origin", cache: "no-store" })); });
  it("keeps validation and permission errors visible", async () => { vi.stubGlobal("fetch", vi.fn().mockResolvedValue(Response.json({ detail: "Forbidden" }, { status: 403 }))); await expect(api.post("/projects", {})).rejects.toMatchObject({ status: 403 }); });
  it("does not turn network failures into successful empty data", async () => { vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("offline"))); await expect(api.get("/events")).rejects.toBeInstanceOf(ApiError); });
});
