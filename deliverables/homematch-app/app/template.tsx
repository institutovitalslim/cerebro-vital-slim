"use client";

import { AuthProvider } from "@/components/auth-provider";
import { Navbar, Footer } from "@/components/layout";

export default function Template({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <Navbar />
      <main className="flex-1">{children}</main>
      <Footer />
    </AuthProvider>
  );
}
