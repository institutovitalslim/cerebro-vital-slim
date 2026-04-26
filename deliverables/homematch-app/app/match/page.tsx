"use client";

import Link from "next/link";
import { Button, Card, Container, SectionHeading } from "@/components/ui";
import { SessionGuard } from "@/components/session-guard";
import { properties } from "@/lib/mock-data";

export default function MatchPage() {
  return (
    <SessionGuard>
      <div className="min-h-screen bg-slate-50 pb-20">
        <div className="bg-white border-b border-slate-100 py-8">
          <Container>
            <h1 className="font-serif text-3xl text-slate-900 mb-2">
              Seus matches
            </h1>
            <p className="text-slate-500">
              Propriedades com maior compatibilidade com seu perfil
            </p>
          </Container>
        </div>

        <Container className="py-8">
          <div className="space-y-6">
            {properties.map((p) => (
              <Card key={p.id} className="p-6">
                <div className="flex flex-col md:flex-row gap-6">
                  <div className="w-full md:w-64 shrink-0">
                    <div className="aspect-[4/3] rounded-2xl overflow-hidden">
                      <img
                        src={p.image}
                        alt={p.title}
                        className="w-full h-full object-cover"
                      />
                    </div>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h3 className="font-serif text-xl text-slate-900">
                          {p.title}
                        </h3>
                        <p className="text-sm text-slate-500">
                          {p.neighborhood}, {p.location}
                        </p>
                      </div>
                      <span className="bg-brand-600 text-white text-sm font-semibold px-3 py-1 rounded-full">
                        {p.score}% match
                      </span>
                    </div>

                    <p className="text-slate-600 mb-4">{p.summary}</p>

                    <div className="mb-4">
                      <h4 className="text-sm font-medium text-slate-700 mb-2">
                        Por que combinamos:
                      </h4>
                      <ul className="space-y-1">
                        {p.matchReasons.map((r, i) => (
                          <li
                            key={i}
                            className="text-sm text-slate-500 flex items-start gap-2"
                          >
                            <span className="text-brand-500 mt-0.5">•</span>
                            {r}
                          </li>
                        ))}
                      </ul>
                    </div>

                    <div className="flex flex-wrap gap-2">
                      <Link href={`/properties/${p.id}/`}>
                        <Button variant="secondary" className="text-sm px-4 py-2">
                          Ver detalhes
                        </Button>
                      </Link>
                      <Link href="/offer/">
                        <Button variant="outline" className="text-sm px-4 py-2">
                          Fazer proposta
                        </Button>
                      </Link>
                      <Link href="/chat/">
                        <Button variant="ghost" className="text-sm px-4 py-2">
                          Conversar
                        </Button>
                      </Link>
                    </div>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </Container>
      </div>
    </SessionGuard>
  );
}
