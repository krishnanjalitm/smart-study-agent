// smart-study-agent/frontend/src/context/AuthContext.jsx
// Global authentication state — provides user object, login, logout helpers.

import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { authAPI } from "../services/api";
import toast from "react-hot-toast";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser]       = useState(null);
  const [loading, setLoading] = useState(true);

  // ── Bootstrap: rehydrate from storage on first load ──────────────────────
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      authAPI.me()
        .then(({ data }) => setUser(data))
        .catch(() => localStorage.clear())
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  // ── Login ─────────────────────────────────────────────────────────────────
  const login = useCallback(async (email, password) => {
    const { data } = await authAPI.login({ email, password });
    localStorage.setItem("access_token",  data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
    setUser(data.user);
    toast.success(`Welcome back, ${data.user.name}!`);
    return data;
  }, []);

  // ── Register ──────────────────────────────────────────────────────────────
  const register = useCallback(async (name, email, password) => {
    const { data } = await authAPI.register({ name, email, password });
    localStorage.setItem("access_token",  data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
    setUser(data.user);
    toast.success(`Account created! Welcome, ${data.user.name}!`);
    return data;
  }, []);

  // ── Logout ────────────────────────────────────────────────────────────────
  const logout = useCallback(() => {
    localStorage.clear();
    setUser(null);
    toast("Logged out.");
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside <AuthProvider>");
  return ctx;
};
