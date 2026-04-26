"use client";

import Link from "next/link";
import { Button, Card, Container, SectionHeading, Badge } from "@/components/ui";
import { SessionGuard } from "@/components/session-guard";
import { useAuth } from "@/components/auth-provider";
import { properties } from "@/lib/mock-data";

export default function DashboardPage() {
  const { user } = useAuth();

  return (
    <SessionGuard>
      <div className="min-h-screen bg-slate-50 pb-20">
        <div className="bg-white border-b border-slate-100 py-8">
          <Container>
            <h1 className="font-serif text-3xl text-slate-900 mb-1">
              Olá, {user?.name?.split(" ")[0] || "Membro"}
            </h1>
            <p className="text-slate-500">
              Aqui está o resumo da sua jornada no HomeMatch Club
            </p>
          </Container>
        </div>

        <Container className="py-8">
          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            {[
              { label: "Matches", value: "12" },
              { label: "Visitas agendadas", value: "3" },
              { label: "Propostas enviadas", value: "1" },
              { label: "Favoritos", value: "5" },
            ].map((s) => (
              <Card key={s.label} className="p-5 text-center">
                <div className="text-2xl font-semibold text-slate-900 mb-1">
                  {s.value}
                </div>
                <div className="text-xs text-slate-500">{s.label}</div>
              </Card>
            ))}
          </div>

          {/* Recent matches */}
          <SectionHeading title="Matches recentes" />
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
            {properties.slice(0, 2).map((p) => (
              <Card key={p.id} className="group hover:shadow-md transition-shadow">
                <Link href={`/properties/${p.id}/`}>
                  <div className="aspect-[4/3] overflow-hidden">
                    <img
                      src={p.image}
                      alt={p.title}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                    />
                  </div>
                  <div className="p-5">
                    <div className="flex items-center justify-between mb-2">
                      <Badge>{p.type}</Badge>
                      <span className="text-brand-700 font-semibold text-sm">
                        {p.price}
                      </span>
                    </div>
                    <h3 className="font-serif text-lg text-slate-900 mb-1">
                      {p.title}
                    </h3>
                    <p className="text-sm text-slate-500">
                      {p.neighborhood}, {p.location}
                    </p>
                  </div>
                </Link>
              </Card>
            ))}
            <Card className="flex items-center justify-center p-8 border-dashed border-2 border-slate-200">
              <Link href="/feed/">
                <Button variant="outline">Ver mais no feed</Button>
              </Link>
            </Card>
          </div>

          {/* Activity */}
          <SectionHeading title="Atividade recente" />
          <Card className="p-6">
            <div className="space-y-4">
              {[
                {
                  action: "Proposta enviada",
                  target: "Aurora Park Residence",
                  time: "Há 2 horas",
                  status: "Pendente",
                },
                {
                  action: "Visita agendada",
                  target: "Costa do Mar",
                  time: "Ontem",
                  status: "Confirmada",
                },
                {
                  action: "Novo match",
                  target: "Verde Habitat",
                  time: "Há 3 dias",
                  status: "Novo",
                },
              ].map((item, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between py-3 border-b border-slate-50 last:border-0"
                >
                  <div>
                    <p className="text-sm font-medium text-slate-800">
                      {item.action}
                    </p>
                    <p className="text-xs text-slate-500">
                      {item.target} • {item.time}
                    </p>
                  </div>
                  <Badge
                    className={
                      item.status === "Pendente"
                        ? "bg-amber-50 text-amber-700"
                        : item.status === "Confirmada"
                        ? "bg-brand-50 text-brand-700"
                        : "bg-slate-100 text-slate-600"
                    }
                  >
                    {item.status}
                  </Badge>
                </div>
              ))}
            </div>
          </Card>
        </Container>
      </div>
    </SessionGuard>
  );
}
