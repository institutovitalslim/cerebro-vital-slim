"use client";

import { useAuth, UserRole } from "./auth-provider";

const roles: { value: UserRole; label: string }[] = [
  { value: "guest", label: "Visitante" },
  { value: "member", label: "Membro" },
  { value: "admin", label: "Admin" },
];

export function RoleSwitcher() {
  const { user, switchRole } = useAuth();

  if (!user) return null;

  return (
    <div className="flex items-center gap-2">
      <span className="text-xs text-slate-400">Perfil:</span>
      <select
        value={user.role}
        onChange={(e) => switchRole(e.target.value as UserRole)}
        className="text-xs bg-slate-100 border border-slate-200 rounded-xl px-2 py-1 text-slate-700 focus:outline-none"
      >
        {roles.map((r) => (
          <option key={r.value} value={r.value}>
            {r.label}
          </option>
        ))}
      </select>
    </div>
  );
}
