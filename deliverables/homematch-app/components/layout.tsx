"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "./auth-provider";
import { RoleSwitcher } from "./role-switcher";

const navLinks = [
  { href: "/feed/", label: "Feed", roles: ["member", "admin"] },
  { href: "/dashboard/", label: "Painel", roles: ["member", "admin"] },
  { href: "/chat/", label: "Chat", roles: ["member", "admin"] },
  { href: "/admin/", label: "Admin", roles: ["admin"] },
];

export function Navbar() {
  const { user, logout } = useAuth();
  const pathname = usePathname();

  const visibleLinks = navLinks.filter(
    (link) => !user || link.roles.includes(user.role)
  );

  return (
    <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-slate-100">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <Link
          href="/"
          className="font-serif text-xl text-slate-900 tracking-tight"
        >
          HomeMatch <span className="text-brand-700">Club</span>
        </Link>

        <nav className="hidden md:flex items-center gap-1">
          {visibleLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={`px-3 py-2 rounded-xl text-sm font-medium transition-colors ${
                pathname === link.href
                  ? "bg-slate-100 text-slate-900"
                  : "text-slate-500 hover:text-slate-800"
              }`}
            >
              {link.label}
            </Link>
          ))}
        </nav>

        <div className="flex items-center gap-3">
          {user ? (
            <>
              <RoleSwitcher />
              <button
                onClick={logout}
                className="text-xs text-slate-400 hover:text-slate-600 transition-colors"
              >
                Sair
              </button>
            </>
          ) : (
            <Link
              href="/auth/"
              className="text-sm font-medium text-slate-700 hover:text-slate-900"
            >
              Entrar
            </Link>
          )}
        </div>
      </div>
    </header>
  );
}

export function Footer() {
  return (
    <footer className="border-t border-slate-100 bg-white mt-auto">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-sm text-slate-400">
            &copy; {new Date().getFullYear()} HomeMatch Club. Todos os direitos
            reservados.
          </p>
          <div className="flex items-center gap-4 text-sm text-slate-400">
            <Link href="/" className="hover:text-slate-600 transition-colors">
              Início
            </Link>
            <Link
              href="/onboarding/"
              className="hover:text-slate-600 transition-colors"
            >
              Aplicar
            </Link>
            <Link
              href="/auth/"
              className="hover:text-slate-600 transition-colors"
            >
              Login
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
