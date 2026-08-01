const isServer = typeof window === 'undefined'

export const apiBase = isServer
  ? process.env.API_BASE_URL || 'http://api:8010'
  : process.env.NEXT_PUBLIC_API_BASE_URL || '/api'

export async function fetchJson<T>(path: string): Promise<T> {
  const init: RequestInit = { cache: 'no-store' }
  if (isServer) {
    // SSR: repassa o cookie de sessão do request atual p/ a API (senão o gate de auth bloquearia).
    try {
      const { cookies } = await import('next/headers')
      const cookie = (await cookies()).toString()
      if (cookie) init.headers = { cookie }
    } catch {
      /* fora de um request scope (build) — segue sem cookie */
    }
  } else {
    init.credentials = 'include'
  }
  const response = await fetch(`${apiBase}${path}`, init)
  if (!response.ok) {
    throw new Error(`Erro ao buscar ${path}: ${response.status}`)
  }
  return response.json()
}
