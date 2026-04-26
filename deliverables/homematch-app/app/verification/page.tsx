"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button, Card, Container } from "@/components/ui";

export default function VerificationPage() {
  const router = useRouter();
  const [status, setStatus] = useState<"idle" | "verifying" | "done">("idle");

  const handleVerify = () => {
    setStatus("verifying");
    setTimeout(() => {
      setStatus("done");
      setTimeout(() => router.push("/auth/"), 1500);
    }, 2000);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 px-4">
      <Container className="max-w-md">
        <Card className="p-8 text-center">
          <div className="w-16 h-16 rounded-full bg-brand-100 flex items-center justify-center mx-auto mb-6">
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
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>

          {status === "idle" && (
            <>
              <h1 className="font-serif text-2xl text-slate-900 mb-2">
                Verificação de identidade
              </h1>
              <p className="text-slate-500 mb-6">
                Para garantir a segurança do clube, precisamos verificar sua
                identidade. Este processo leva apenas alguns segundos.
              </p>
              <Button onClick={handleVerify} className="w-full">
                Iniciar verificação
              </Button>
            </>
          )}

          {status === "verifying" && (
            <>
              <h1 className="font-serif text-2xl text-slate-900 mb-2">
                Verificando...
              </h1>
              <p className="text-slate-500">
                Estamos validando suas informações. Aguarde um momento.
              </p>
              <div className="mt-6 w-full h-1 bg-slate-100 rounded-full overflow-hidden">
                <div className="h-full bg-brand-600 animate-pulse w-2/3" />
              </div>
            </>
          )}

          {status === "done" && (
            <>
              <h1 className="font-serif text-2xl text-slate-900 mb-2">
                Verificação concluída
              </h1>
              <p className="text-slate-500">
                Sua identidade foi confirmada. Redirecionando para o login...
              </p>
            </>
          )}
        </Card>
      </Container>
    </div>
  );
}
