"use client";
import { useCallback, useEffect, useState } from "react";
import { api, ApiError } from "./api";
export function useRemote<T>(path: string | null, options: { pollMs?: number } = {}) {
  const [revision, setRevision] = useState(0);
  const [state, setState] = useState<{ path: string | null; data: T | null; error: ApiError | null; loading: boolean }>({ path: null, data: null, error: null, loading: true });
  const reload = useCallback(() => setRevision(value => value + 1), []);
  useEffect(() => {
    if (!path) { setState({ path: null, data: null, error: null, loading: false }); return; }
    let active = true;
    let fetching = false;
    const controller = new AbortController();
    const load = async () => {
      if (fetching) return;
      fetching = true;
      setState(previous => ({ path, data: previous.path === path ? previous.data : null, error: null, loading: previous.path !== path || previous.data === null }));
      try { const data = await api.get<T>(path, controller.signal); if (active) setState({ path, data, error: null, loading: false }); }
      catch (error) { if (active && !(error instanceof Error && error.name === "AbortError")) setState(previous => ({ ...previous, path, error: error as ApiError, loading: false })); }
      finally { fetching = false; }
    };
    void load();
    const timer = options.pollMs ? window.setInterval(() => { if (!document.hidden) void load(); }, options.pollMs) : undefined;
    return () => { active = false; controller.abort(); if (timer) window.clearInterval(timer); };
  }, [path, revision, options.pollMs]);
  return { data: path && state.path === path ? state.data : null, error: path && state.path === path ? state.error : null, loading: Boolean(path) && (state.path !== path || state.loading), reload };
}
