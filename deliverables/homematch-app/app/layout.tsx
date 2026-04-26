import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "HomeMatch Club",
  description: "O clube exclusivo para quem busca o imóvel certo.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR">
      <body className="min-h-screen bg-slate-50 text-slate-800 antialiased">
        {children}
      </body>
    </html>
  );
}
