"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button, Card, Container, Input, Select, TextArea } from "@/components/ui";
import { SessionGuard } from "@/components/session-guard";

export default function OfferPage() {
  const router = useRouter();
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
    setTimeout(() => router.push("/dashboard/"), 2000);
  };

  return (
    <SessionGuard>
      <div className="min-h-screen bg-slate-50 py-12">
        <Container className="max-w-lg">
          <div className="text-center mb-8">
            <h1 className="font-serif text-3xl text-slate-900 mb-2">
              Proposta de troca
            </h1>
            <p className="text-slate-500">
              Envie sua proposta para o proprietário
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
                  Proposta enviada!
                </h2>
                <p className="text-slate-500">
                  O proprietário será notificado e responderá em até 48h.
                </p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-5">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    Propriedade
                  </label>
                  <Select required>
                    <option value="">Selecione</option>
                    <option value="aurora-park-101">
                      Aurora Park Residence — R$ 2.450.000
                    </option>
                    <option value="costa-mar-22">
                      Costa do Mar — R$ 3.890.000
                    </option>
                    <option value="verde-habitat-8">
                      Verde Habitat — R$ 1.890.000
                    </option>
                  </Select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    Valor da proposta
                  </label>
                  <Input placeholder="Ex: R$ 2.300.000" required />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    Forma de pagamento
                  </label>
                  <Select required>
                    <option value="">Selecione</option>
                    <option value="avista">À vista</option>
                    <option value="financiamento">Financiamento</option>
                    <option value="parcelado">Parcelado direto</option>
                    <option value="permuta">Permuta</option>
                  </Select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    Condições especiais
                  </label>
                  <TextArea
                    placeholder="Ex: prazo de pagamento, inclusão de móveis..."
                    rows={3}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    Mensagem ao proprietário
                  </label>
                  <TextArea
                    placeholder="Escreva uma mensagem pessoal..."
                    rows={3}
                    required
                  />
                </div>

                <Button type="submit" variant="secondary" className="w-full">
                  Enviar proposta
                </Button>
              </form>
            )}
          </Card>
        </Container>
      </div>
    </SessionGuard>
  );
}
