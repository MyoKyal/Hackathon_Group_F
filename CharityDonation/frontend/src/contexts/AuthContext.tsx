import { createContext, useEffect, useState, type ReactNode } from "react";
import * as authApi from "../api/auth";
import type { User } from "../types";

interface AuthContextValue {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (payload: authApi.SignupPayload) => Promise<void>;
  logout: () => Promise<void>;
}

export const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(() => localStorage.getItem("token"));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) {
      setLoading(false);
      return;
    }
    authApi
      .getMe()
      .then(setUser)
      .catch(() => {
        localStorage.removeItem("token");
        setToken(null);
      })
      .finally(() => setLoading(false));
  }, [token]);

  async function login(email: string, password: string) {
    const res = await authApi.login(email, password);
    localStorage.setItem("token", res.access_token);
    setToken(res.access_token);
    setUser(res.user);
  }

  async function signup(payload: authApi.SignupPayload) {
    const res = await authApi.signup(payload);
    localStorage.setItem("token", res.access_token);
    setToken(res.access_token);
    setUser(res);
  }

  async function logout() {
    try {
      await authApi.logout();
    } catch {
      // ignore - client discards token regardless
    }
    localStorage.removeItem("token");
    setToken(null);
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, token, loading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
