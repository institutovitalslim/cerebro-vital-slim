"use client";

import React, { createContext, useContext, useEffect, useState } from "react";

export type UserRole = "guest" | "member" | "admin";

export interface User {
  name: string;
  email: string;
  role: UserRole;
}

interface AuthContextType {
  user: User | null;
  login: (user: User) => void;
  logout: () => void;
  switchRole: (role: UserRole) => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  login: () => {},
  logout: () => {},
  switchRole: () => {},
  isLoading: true,
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const stored = localStorage.getItem("homematch_user");
    if (stored) {
      try {
        setUser(JSON.parse(stored));
      } catch {
        localStorage.removeItem("homematch_user");
      }
    }
    setIsLoading(false);
  }, []);

  const login = (u: User) => {
    setUser(u);
    localStorage.setItem("homematch_user", JSON.stringify(u));
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem("homematch_user");
  };

  const switchRole = (role: UserRole) => {
    if (!user) return;
    const updated = { ...user, role };
    setUser(updated);
    localStorage.setItem("homematch_user", JSON.stringify(updated));
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, switchRole, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
