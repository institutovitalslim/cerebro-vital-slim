"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button, Card, Container, Input, Select, TextArea } from "@/components/ui";
import { SessionGuard } from "@/components/session-guard";

export default function NewPropertyPage() {
  const router = useRouter();
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
    setTimeout(() => router.push("/feed/"), 1500);
  };

  return (
    <SessionGuard>
      <div className="min-h-screen bg-slate-50 py-12">
        <Container className="max-w-2xl">
          <div className="text-center mb-8">
            <h1 className="font-serif text-3xl text-slate-900 mb-2">
              Cadastrar propriedade
            </h1>
            <p className="text-slate-500">
              Anuncie seu imóvel no HomeMatch Club
            </p>
          </div>

          <Card className="p-8">
            {submitted ? (
              <div className="text-center py-8">
                <div className="w-16 h-16 rounded-full bg-brand-100 flex items-center justify-center mx-auto mb-4">
                  <svg
                    className="w-8 h-8 text-brand-700"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={1.5}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                </div>
                <h2 className="font-serif text-xl text-slate-900 mb-2">
                  Propriedade cadastrada!
                </h2>
                <p className="text-slate-500">
                  Redirecionando para o feed...
                </p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-5">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">
                      Título
                    </label>
                    <Input placeholder="Ex: Apartamento Luxo Jardins" required />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">
                      Tipo
                    </label>
                    <Select required>
                      <option value="">Selecione</option>
                      <option value="apartamento">Apartamento</option>
                      <option value="casa">Casa</option>
                      <option value="cobertura">Cobertura</option>
                      <option value="loft">Loft</option>
                    </Select>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">
                      Cidade
                    </label>
                    <Input placeholder="Ex: São Paulo" required />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">
                      Bairro
                    </label>
                    <Input placeholder="Ex: Jardins" required />
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">
                      Quartos
                    </label>
                    <Input type="number" placeholder="3" required />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">
                      Banheiros
                    </label>
                    <Input type="number" placeholder="2" required />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">
                      Área (m²)
                    </label>
                    <Input type="number" placeholder="142" required />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    Preço
                  </label>
                  <Input placeholder="Ex: R$ 2.450.000" required />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    Descrição
                  </label>
                  <TextArea
                    placeholder="Descreva a propriedade..."
                    rows={4}
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    URL da imagem principal
                  </label>
                  <Input
                    type="url"
                    placeholder="https://..."
                  />
                </div>

                <Button type="submit" variant="secondary" className="w-full">
                  Cadastrar propriedade
                </Button>
              </form>
            )}
          </Card>
        </Container>
      </div>
    </SessionGuard>
  );
}
