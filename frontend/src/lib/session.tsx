"use client";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { api, ApiError } from "./api";
import type { Profile } from "./types";
interface Session {
  user: Profile | null;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}
const SessionContext = createContext<Session | null>(null);
export function SessionProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setUser(await api.get<Profile>("/auth/me"));
    } catch (failure) {
      if (failure instanceof ApiError && failure.status === 401) setUser(null);
      else setError("No pudimos comprobar tu sesión. Inténtalo de nuevo.");
    } finally {
      setLoading(false);
    }
  }, []);
  useEffect(() => {
    void refresh();
    const expired = () => setUser(null);
    window.addEventListener("session-expired", expired);
    return () => window.removeEventListener("session-expired", expired);
  }, [refresh]);
  const login = async (email: string, password: string) => {
    await api.post("/auth/login", { email, password });
    setUser(await api.get<Profile>("/auth/me"));
    setError(null);
  };
  const logout = async () => {
    const response = await fetch("/api/session", { method: "DELETE" });
    if (!response.ok)
      throw new Error("No pudimos cerrar sesión. Inténtalo de nuevo.");
    setUser(null);
  };
  return (
    <SessionContext.Provider
      value={{ user, loading, error, refresh, login, logout }}
    >
      {children}
    </SessionContext.Provider>
  );
}
export function useSession(): Session {
  const context = useContext(SessionContext);
  if (!context) throw new Error("SessionProvider is required");
  return context;
}
