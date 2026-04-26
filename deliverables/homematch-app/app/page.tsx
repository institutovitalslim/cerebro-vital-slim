import Link from "next/link";
import { Button, Card, Container, SectionHeading, Badge } from "@/components/ui";
import { properties } from "@/lib/mock-data";

export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Hero */}
      <section className="relative bg-slate-900 text-white overflow-hidden">
        <div className="absolute inset-0 opacity-20">
          <img
            src="https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=1600&q=80"
            alt=""
            className="w-full h-full object-cover"
          />
        </div>
        <div className="relative max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-24 sm:py-32">
          <div className="max-w-2xl">
            <h1 className="font-serif text-4xl sm:text-5xl lg:text-6xl leading-tight mb-6">
              O clube exclusivo para quem busca o imóvel certo
            </h1>
            <p className="text-lg text-slate-300 mb-8 leading-relaxed">
              HomeMatch Club conecta pessoas exigentes com propriedades
              selecionadas. Aplicamos inteligência humana e algoritmos de match
              para encontrar o lugar onde você realmente pertence.
            </p>
            <div className="flex flex-wrap gap-3">
              <Link href="/onboarding/">
                <Button variant="secondary">Aplicar ao clube</Button>
              </Link>
              <Link href="/auth/">
                <Button variant="outline" className="border-slate-600 text-white hover:bg-slate-800">
                  Já sou membro
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Properties preview */}
      <section className="py-20 bg-slate-50">
        <Container>
          <SectionHeading
            title="Propriedades em destaque"
            subtitle="Um preview do que nossos membros têm acesso"
          />
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {properties.map((p) => (
              <Card key={p.id} className="group cursor-pointer hover:shadow-md transition-shadow">
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
                    <p className="text-sm text-slate-500 mb-3">
                      {p.neighborhood}, {p.location}
                    </p>
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
      </section>

      {/* How it works */}
      <section className="py-20 bg-white">
        <Container>
          <SectionHeading
            title="Como funciona"
            subtitle="Três passos para encontrar seu lugar"
          />
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                step: "01",
                title: "Aplique ao clube",
                desc: "Preencha nossa aplicação e passe pela verificação de identidade.",
              },
              {
                step: "02",
                title: "Receba matches",
                desc: "Nosso algoritmo cura propriedades compatíveis com seu perfil.",
              },
              {
                step: "03",
                title: "Visite e decida",
                desc: "Agende visitas, converse com corretores e faça sua proposta.",
              },
            ].map((item) => (
              <div key={item.step} className="text-center">
                <div className="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center mx-auto mb-4">
                  <span className="text-sm font-semibold text-slate-700">
                    {item.step}
                  </span>
                </div>
                <h3 className="font-serif text-xl text-slate-900 mb-2">
                  {item.title}
                </h3>
                <p className="text-slate-500 leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </Container>
      </section>

      {/* CTA */}
      <section className="py-20 bg-slate-900 text-white">
        <Container>
          <div className="text-center max-w-2xl mx-auto">
            <h2 className="font-serif text-3xl sm:text-4xl mb-4">
              Pronto para encontrar seu match?
            </h2>
            <p className="text-slate-300 mb-8">
              Junte-se a centenas de membros que já encontraram o imóvel ideal
              através do HomeMatch Club.
            </p>
            <Link href="/onboarding/">
              <Button variant="secondary">Aplicar agora</Button>
            </Link>
          </div>
        </Container>
      </section>
    </div>
  );
}
