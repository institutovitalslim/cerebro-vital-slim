"use client";

import { Suspense } from "react";
import { Card, Container, SectionHeading, Badge } from "@/components/ui";
import { SessionGuard } from "@/components/session-guard";
import { useAuth } from "@/components/auth-provider";
import { properties } from "@/lib/mock-data";

function AdminContent() {
  const { user } = useAuth();

  if (user && user.role !== "admin") {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <Card className="p-8 text-center max-w-md">
          <h1 className="font-serif text-2xl text-slate-900 mb-2">
            Acesso restrito
          </h1>
          <p className="text-slate-500 mb-4">
            Esta área é exclusiva para administradores.
          </p>
          <a
            href="/feed/"
            className="text-brand-700 text-sm font-medium hover:underline"
          >
            Voltar ao feed
          </a>
        </Card>
      </div>
    );
  }

  return (
    <SessionGuard>
      <div className="min-h-screen bg-slate-50 pb-20">
        <div className="bg-white border-b border-slate-100 py-8">
          <Container>
            <h1 className="font-serif text-3xl text-slate-900 mb-2">
              Painel administrativo
            </h1>
            <p className="text-slate-500">
              Visão geral do HomeMatch Club
            </p>
          </Container>
        </div>

        <Container className="py-8">
          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            {[
              { label: "Membros", value: "142" },
              { label: "Propriedades", value: "38" },
              { label: "Matches hoje", value: "24" },
              { label: "Propostas", value: "7" },
            ].map((s) => (
              <Card key={s.label} className="p-5 text-center">
                <div className="text-2xl font-semibold text-slate-900 mb-1">
                  {s.value}
                </div>
                <div className="text-xs text-slate-500">{s.label}</div>
              </Card>
            ))}
          </div>

          {/* Properties table */}
          <SectionHeading title="Propriedades cadastradas" />
          <Card className="overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-100">
                    <th className="text-left px-6 py-3 font-medium text-slate-500">
                      Propriedade
                    </th>
                    <th className="text-left px-6 py-3 font-medium text-slate-500">
                      Local
                    </th>
                    <th className="text-left px-6 py-3 font-medium text-slate-500">
                      Preço
                    </th>
                    <th className="text-left px-6 py-3 font-medium text-slate-500">
                      Status
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {properties.map((p) => (
                    <tr
                      key={p.id}
                      className="border-b border-slate-50 last:border-0 hover:bg-slate-50/50"
                    >
                      <td className="px-6 py-4">
                        <div className="font-medium text-slate-900">
                          {p.title}
                        </div>
                        <div className="text-xs text-slate-400">{p.type}</div>
                      </td>
                      <td className="px-6 py-4 text-slate-600">
                        {p.neighborhood}
                      </td>
                      <td className="px-6 py-4 font-medium text-slate-800">
                        {p.price}
                      </td>
                      <td className="px-6 py-4">
                        <Badge className="bg-brand-50 text-brand-700">
                          Ativo
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>

          {/* Recent activity */}
          <div className="mt-8">
            <SectionHeading title="Atividade recente" />
            <Card className="p-6">
              <div className="space-y-3">
                {[
                  "Novo membro: Ana Paula Silva",
                  "Proposta recebida: Aurora Park Residence",
                  "Visita confirmada: Costa do Mar",
                  "Propriedade cadastrada: Jardim Europa Loft",
                  "Match gerado: 3 novos matches",
                ].map((item, i) => (
                  <div
                    key={i}
                    className="flex items-center gap-3 text-sm text-slate-600 py-2 border-b border-slate-50 last:border-0"
                  >
                    <span className="w-2 h-2 rounded-full bg-brand-400 shrink-0" />
                    {item}
                  </div>
                ))}
              </div>
            </Card>
          </div>
        </Container>
      </div>
    </SessionGuard>
  );
}

export default function AdminPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="animate-pulse text-slate-400 text-sm">Carregando...</div>
      </div>
    }>
      <AdminContent />
    </Suspense>
  );
}
