"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button, Card, Container, Input } from "@/components/ui";
import { useAuth, UserRole } from "@/components/auth-provider";

export default function AuthPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [role, setRole] = useState<UserRole>("member");

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    login({ name: name || "Membro", email: email || "membro@homematch.club", role });
    router.push("/feed/");
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 px-4">
      <Container className="max-w-md">
        <Card className="p-8">
          <div className="text-center mb-8">
            <h1 className="font-serif text-2xl text-slate-900 mb-2">
              HomeMatch Club
            </h1>
            <p className="text-slate-500 text-sm">
              Entre com sua conta ou simule um perfil
            </p>
          </div>

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Nome
              </label>
              <Input
                placeholder="Seu nome"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                E-mail
              </label>
              <Input
                type="email"
                placeholder="seu@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Perfil
              </label>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value as UserRole)}
                className="w-full px-4 py-3 rounded-2xl border border-slate-200 bg-white text-slate-800 focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all appearance-none"
              >
                <option value="member">Membro</option>
                <option value="admin">Administrador</option>
                <option value="guest">Visitante</option>
              </select>
            </div>
            <Button type="submit" className="w-full mt-2">
              Entrar
            </Button>
          </form>

          <p className="text-center text-xs text-slate-400 mt-6">
            Login simulado para demonstração. Nenhum dado é enviado a servidores.
          </p>
        </Card>
      </Container>
    </div>
  );
}
