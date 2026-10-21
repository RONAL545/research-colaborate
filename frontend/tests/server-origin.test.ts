// @vitest-environment node
import { expect, it } from "vitest";
import { NextRequest } from "next/server";
import { isSameOrigin } from "@/lib/server-origin";
it("accepts original Host when Next normalizes the loopback URL", () => {
  const request = new NextRequest(
    "http://localhost:13000/api/backend/projects",
    {
      method: "POST",
      headers: { host: "127.0.0.1:13000", origin: "http://127.0.0.1:13000" },
    },
  );
  expect(isSameOrigin(request)).toBe(true);
});
it("rejects foreign origins even on a valid host", () => {
  const request = new NextRequest(
    "http://localhost:13000/api/backend/projects",
    {
      method: "POST",
      headers: { host: "127.0.0.1:13000", origin: "https://external.example" },
    },
  );
  expect(isSameOrigin(request)).toBe(false);
});
