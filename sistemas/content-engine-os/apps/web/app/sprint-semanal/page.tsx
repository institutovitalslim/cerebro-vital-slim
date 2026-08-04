import { redirect } from 'next/navigation'

// O Sprint semanal global deixou de existir: cada formato tem o seu próprio
// planejamento semanal dentro do Estúdio. Redireciona preservando a query
// (tese, hook, objetivo etc. continuam chegando na produção).
export default async function SprintSemanalRedirect({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>
}) {
  const sp = await searchParams
  const query = new URLSearchParams()
  for (const [key, value] of Object.entries(sp)) {
    if (Array.isArray(value)) {
      for (const item of value) query.append(key, item)
    } else if (value != null) {
      query.append(key, value)
    }
  }
  const qs = query.toString()
  redirect(qs ? `/criar?${qs}` : '/criar')
}
