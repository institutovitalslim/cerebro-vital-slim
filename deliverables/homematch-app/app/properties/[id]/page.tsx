import React from "react";
import { notFound } from "next/navigation";
import Link from "next/link";
import { properties, getPropertyById } from "@/lib/mock-data";
import { Button, Card, Container, Badge } from "@/components/ui";

export function generateStaticParams() {
  return properties.map((p) => ({ id: p.id }));
}

export default function PropertyPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = React.use(params);
  const p = getPropertyById(id);
  if (!p) return notFound();

  return (
    <div className="min-h-screen bg-slate-50 pb-20">
      {/* Hero image */}
      <div className="relative h-72 sm:h-96 overflow-hidden">
        <img
          src={p.image}
          alt={p.title}
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent" />
        <div className="absolute bottom-0 left-0 right-0 p-6 sm:p-10">
          <Container>
            <div className="flex items-center gap-2 mb-2">
              <Badge className="bg-white/90 text-slate-800">{p.type}</Badge>
              <span className="bg-brand-600 text-white text-xs font-medium px-3 py-1 rounded-full">
                Match {p.score}%
              </span>
            </div>
            <h1 className="font-serif text-3xl sm:text-4xl text-white mb-1">
              {p.title}
            </h1>
            <p className="text-white/80">
              {p.neighborhood}, {p.location}
            </p>
          </Container>
        </div>
      </div>

      <Container className="py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Quick stats */}
            <Card className="p-6">
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <div className="text-2xl font-semibold text-slate-900">{p.beds}</div>
                  <div className="text-xs text-slate-500">Quartos</div>
                </div>
                <div>
                  <div className="text-2xl font-semibold text-slate-900">{p.baths}</div>
                  <div className="text-xs text-slate-500">Banheiros</div>
                </div>
                <div>
                  <div className="text-2xl font-semibold text-slate-900">{p.area}m²</div>
                  <div className="text-xs text-slate-500">Área útil</div>
                </div>
              </div>
            </Card>

            {/* Summary */}
            <Card className="p-6">
              <h2 className="font-serif text-xl text-slate-900 mb-3">Resumo</h2>
              <p className="text-slate-600 leading-relaxed">{p.summary}</p>
              <div className="mt-4 p-4 bg-brand-50 rounded-2xl border border-brand-100">
                <p className="text-sm text-brand-800 font-medium">
                  Destaque: {p.highlight}
                </p>
              </div>
            </Card>

            {/* Match reasons */}
            <Card className="p-6">
              <h2 className="font-serif text-xl text-slate-900 mb-4">
                Por que este match?
              </h2>
              <ul className="space-y-3">
                {p.matchReasons.map((reason, i) => (
                  <li key={i} className="flex items-start gap-3">
                    <span className="w-5 h-5 rounded-full bg-brand-100 text-brand-700 flex items-center justify-center text-xs font-semibold shrink-0 mt-0.5">
                      {i + 1}
                    </span>
                    <span className="text-slate-600">{reason}</span>
                  </li>
                ))}
              </ul>
            </Card>

            {/* Details */}
            {p.detailSections.map((section) => (
              <Card key={section.title} className="p-6">
                <h2 className="font-serif text-xl text-slate-900 mb-3">
                  {section.title}
                </h2>
                <p className="text-slate-600 leading-relaxed">
                  {section.content}
                </p>
              </Card>
            ))}

            {/* Amenities */}
            <Card className="p-6">
              <h2 className="font-serif text-xl text-slate-900 mb-4">
                Amenidades
              </h2>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                {p.amenities.map((a) => (
                  <div
                    key={a}
                    className="flex items-center gap-2 text-sm text-slate-600"
                  >
                    <span className="w-1.5 h-1.5 rounded-full bg-brand-500" />
                    {a}
                  </div>
                ))}
              </div>
            </Card>

            {/* Gallery */}
            <Card className="p-6">
              <h2 className="font-serif text-xl text-slate-900 mb-4">Galeria</h2>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                {p.gallery.map((img, i) => (
                  <div key={i} className="aspect-square rounded-2xl overflow-hidden">
                    <img
                      src={img}
                      alt={`${p.title} ${i + 1}`}
                      className="w-full h-full object-cover hover:scale-105 transition-transform"
                    />
                  </div>
                ))}
              </div>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Price card */}
            <Card className="p-6 sticky top-24">
              <div className="text-3xl font-semibold text-slate-900 mb-1">
                {p.price}
              </div>
              <p className="text-sm text-slate-500 mb-6">
                Condomínio + IPTU sob consulta
              </p>

              {/* Market signals */}
              <div className="space-y-3 mb-6">
                {p.marketSignals.map((s) => (
                  <div
                    key={s.label}
                    className="flex items-center justify-between text-sm"
                  >
                    <span className="text-slate-500">{s.label}</span>
                    <span className="font-medium text-slate-800">
                      {s.value}
                    </span>
                  </div>
                ))}
              </div>

              {/* Visit windows */}
              <div className="mb-6">
                <h3 className="text-sm font-medium text-slate-700 mb-2">
                  Horários de visita
                </h3>
                <div className="space-y-1">
                  {p.visitWindows.map((w) => (
                    <div
                      key={w.day}
                      className="flex items-center justify-between text-sm"
                    >
                      <span className="text-slate-500">{w.day}</span>
                      <span className="text-slate-700">{w.time}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Actions */}
              <div className="space-y-2">
                {p.nextActions.map((action) => (
                  <Link key={action.label} href={action.href}>
                    <Button
                      variant={
                        action.label === "Fazer proposta"
                          ? "secondary"
                          : "outline"
                      }
                      className="w-full"
                    >
                      {action.label}
                    </Button>
                  </Link>
                ))}
              </div>
            </Card>
          </div>
        </div>
      </Container>
    </div>
  );
}
