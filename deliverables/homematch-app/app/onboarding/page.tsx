"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button, Card, Container, Input, Select, TextArea } from "@/components/ui";

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [form, setForm] = useState({
    fullName: "",
    email: "",
    phone: "",
    city: "",
    budget: "",
    propertyType: "",
    bedrooms: "",
    notes: "",
  });

  const update = (field: string, value: string) =>
    setForm((f) => ({ ...f, [field]: value }));

  const handleSubmit = () => {
    router.push("/verification/");
  };

  return (
    <div className="min-h-screen bg-slate-50 py-12">
      <Container className="max-w-lg">
        <div className="text-center mb-8">
          <h1 className="font-serif text-3xl text-slate-900 mb-2">
            Aplicar ao HomeMatch Club
          </h1>
          <p className="text-slate-500">
            Etapa {step} de 3 — leva menos de 2 minutos
          </p>
        </div>

        <Card className="p-8">
          {step === 1 && (
            <div className="space-y-4">
              <h2 className="font-medium text-slate-900">Seus dados</h2>
              <Input
                placeholder="Nome completo"
                value={form.fullName}
                onChange={(e) => update("fullName", e.target.value)}
              />
              <Input
                type="email"
                placeholder="E-mail"
                value={form.email}
                onChange={(e) => update("email", e.target.value)}
              />
              <Input
                placeholder="Telefone"
                value={form.phone}
                onChange={(e) => update("phone", e.target.value)}
              />
              <Input
                placeholder="Cidade de interesse"
                value={form.city}
                onChange={(e) => update("city", e.target.value)}
              />
              <Button onClick={() => setStep(2)} className="w-full">
                Continuar
              </Button>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-4">
              <h2 className="font-medium text-slate-900">Preferências</h2>
              <Select
                value={form.budget}
                onChange={(e) => update("budget", e.target.value)}
              >
                <option value="">Faixa de preço</option>
                <option value="ate-1m">Até R$ 1 milhão</option>
                <option value="1m-2m">R$ 1M – R$ 2M</option>
                <option value="2m-5m">R$ 2M – R$ 5M</option>
                <option value="5m+">Acima de R$ 5M</option>
              </Select>
              <Select
                value={form.propertyType}
                onChange={(e) => update("propertyType", e.target.value)}
              >
                <option value="">Tipo de imóvel</option>
                <option value="apartamento">Apartamento</option>
                <option value="casa">Casa</option>
                <option value="cobertura">Cobertura</option>
                <option value="loft">Loft</option>
              </Select>
              <Select
                value={form.bedrooms}
                onChange={(e) => update("bedrooms", e.target.value)}
              >
                <option value="">Quartos</option>
                <option value="1">1 quarto</option>
                <option value="2">2 quartos</option>
                <option value="3">3 quartos</option>
                <option value="4+">4+ quartos</option>
              </Select>
              <div className="flex gap-3">
                <Button variant="outline" onClick={() => setStep(1)} className="flex-1">
                  Voltar
                </Button>
                <Button onClick={() => setStep(3)} className="flex-1">
                  Continuar
                </Button>
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="space-y-4">
              <h2 className="font-medium text-slate-900">Finalizar</h2>
              <TextArea
                placeholder="Conte-nos mais sobre o que você busca (opcional)"
                rows={4}
                value={form.notes}
                onChange={(e) => update("notes", e.target.value)}
              />
              <div className="flex gap-3">
                <Button variant="outline" onClick={() => setStep(2)} className="flex-1">
                  Voltar
                </Button>
                <Button onClick={handleSubmit} variant="secondary" className="flex-1">
                  Enviar aplicação
                </Button>
              </div>
            </div>
          )}
        </Card>
      </Container>
    </div>
  );
}
