import { useCallback, useEffect, useState } from "react";
import type { ReactNode } from "react";

import { api, clearToken, getToken, setToken } from "../lib/api";
import type { Usuario } from "../lib/types";
import { AuthContext } from "./auth-context";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<Usuario | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    if (!getToken()) {
      setUser(null);
      return;
    }
    try {
      setUser(await api.me());
    } catch {
      clearToken();
      setUser(null);
    }
  }, []);

  // Hidrata el usuario al cargar (si hay token) y escucha logouts por 401.
  useEffect(() => {
    refresh().finally(() => setLoading(false));

    const onLogout = () => setUser(null);
    window.addEventListener("auth:logout", onLogout);
    return () => window.removeEventListener("auth:logout", onLogout);
  }, [refresh]);

  const login = useCallback(async (email: string, password: string) => {
    const { access_token } = await api.login(email, password);
    setToken(access_token);
    setUser(await api.me());
  }, []);

  const register = useCallback(
    async (email: string, password: string, nombre?: string) => {
      await api.register({ email, password, nombre });
      const { access_token } = await api.login(email, password);
      setToken(access_token);
      setUser(await api.me());
    },
    [],
  );

  const logout = useCallback(() => {
    clearToken();
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{ user, loading, login, register, logout, refresh }}
    >
      {children}
    </AuthContext.Provider>
  );
}
