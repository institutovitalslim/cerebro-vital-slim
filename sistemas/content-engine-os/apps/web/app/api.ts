const isServer = typeof window === 'undefined'

export const apiBase = isServer
  ? process.env.API_BASE_URL || 'http://api:8010'
  : process.env.NEXT_PUBLIC_API_BASE_URL || '/api'

export async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${apiBase}${path}`, { cache: 'no-store' })
  if (!response.ok) {
    throw new Error(`Erro ao buscar ${path}: ${response.status}`)
  }
  return response.json()
}
