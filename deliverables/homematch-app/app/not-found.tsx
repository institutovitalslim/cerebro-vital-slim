import Link from "next/link";
import { Button, Card, Container } from "@/components/ui";

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 px-4">
      <Container className="max-w-md">
        <Card className="p-8 text-center">
          <h1 className="font-serif text-4xl text-slate-900 mb-2">404</h1>
          <p className="text-slate-500 mb-6">
            Página não encontrada. O imóvel que você procura pode ter sido vendido.
          </p>
          <Link href="/">
            <Button>Voltar ao início</Button>
          </Link>
        </Card>
      </Container>
    </div>
  );
}
