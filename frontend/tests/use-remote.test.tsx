import { act, renderHook, waitFor } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { useRemote } from "@/lib/use-remote";
import { api } from "@/lib/api";
afterEach(() => vi.restoreAllMocks());
it("clears private data when the session disables a resource", async () => {
  vi.spyOn(api, "get").mockResolvedValue({ items: ["private"] });
  const { result, rerender } = renderHook(
    ({ path }) => useRemote<{ items: string[] }>(path),
    { initialProps: { path: "/conversations" as string | null } },
  );
  await waitFor(() => expect(result.current.data?.items).toEqual(["private"]));
  rerender({ path: null });
  expect(result.current.data).toBeNull();
  expect(result.current.loading).toBe(false);
});
it("ignores late responses after changing filters", async () => {
  let resolveOld: (value: unknown) => void = () => {};
  vi.spyOn(api, "get").mockImplementation((path) =>
    path === "/projects?q=old"
      ? new Promise((resolve) => {
          resolveOld = resolve;
        })
      : Promise.resolve({ items: ["new"] }),
  );
  const { result, rerender } = renderHook(
    ({ path }) => useRemote<{ items: string[] }>(path),
    { initialProps: { path: "/projects?q=old" } },
  );
  rerender({ path: "/projects?q=new" });
  await waitFor(() => expect(result.current.data?.items).toEqual(["new"]));
  await act(async () => resolveOld({ items: ["old"] }));
  expect(result.current.data?.items).toEqual(["new"]);
});
