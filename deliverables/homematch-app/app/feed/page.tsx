"use client";

import Link from "next/link";
import { Button, Card, Container, SectionHeading, Badge } from "@/components/ui";
import { SessionGuard } from "@/components/session-guard";
import { properties } from "@/lib/mock-data";

export default function FeedPage() {
  return (
    <SessionGuard>
      <div className="min-h-screen bg-slate-50 pb-20">
        <div className="bg-white border-b border-slate-100 py-8">
          <Container>
            <h1 className="font-serif text-3xl text-slate-900 mb-2">
              Feed de propriedades
            </h1>
            <p className="text-slate-500">
              Propriedades selecionadas especialmente para você
            </p>
          </Container>
        </div>

        <Container className="py-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {properties.map((p) => (
              <Card key={p.id} className="group hover:shadow-md transition-shadow">
                <Link href={`/properties/${p.id}/`}>
                  <div className="aspect-[4/3] overflow-hidden relative">
                    <img
                      src={p.image}
                      alt={p.title}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                    />
                    <div className="absolute top-3 right-3 bg-white/90 backdrop-blur-sm rounded-full px-3 py-1 text-xs font-semibold text-slate-900">
                      Match {p.score}%
                    </div>
                  </div>
                  <div className="p-5">
                    <div className="flex items-center justify-between mb-2">
                      <Badge>{p.type}</Badge>
                      <span className="text-brand-700 font-semibold">
                        {p.price}
                      </span>
                    </div>
                    <h3 className="font-serif text-lg text-slate-900 mb-1">
                      {p.title}
                    </h3>
                    <p className="text-sm text-slate-500 mb-3">
                      {p.neighborhood}, {p.location}
                    </p>
                    <p className="text-sm text-slate-600 mb-4 line-clamp-2">
                      {p.summary}
                    </p>
                    <div className="flex flex-wrap gap-2 mb-4">
                      {p.tags.slice(0, 2).map((tag) => (
                        <span
                          key={tag}
                          className="text-xs bg-slate-50 text-slate-500 px-2 py-1 rounded-lg"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                    <div className="flex items-center gap-3 text-xs text-slate-400">
                      <span>{p.beds} quartos</span>
                      <span>{p.baths} banheiros</span>
                      <span>{p.area}m²</span>
                    </div>
                  </div>
                </Link>
              </Card>
            ))}
          </div>
        </Container>
      </div>
    </SessionGuard>
  );
}
