/** @type {import("next").NextConfig} */
const apiBaseUrl = (process.env.API_BASE_URL || 'http://api:8010').replace(/\/$/, '')
const nextConfig = {
  typedRoutes: false,
  typescript: { ignoreBuildErrors: true },
  async rewrites() {
    return [
      { source: '/api/:path*', destination: `${apiBaseUrl}/:path*` },
    ]
  },
  async redirects() {
    // Rotas antigas → destino novo. Query string é preservada automaticamente.
    return [
      { source: '/operacao', destination: '/hoje', permanent: false },
      { source: '/studio', destination: '/criar', permanent: false },
      { source: '/onboarding', destination: '/hoje', permanent: false },
      { source: '/jobs', destination: '/banco-criativos', permanent: false },
      { source: '/briefings', destination: '/ideias', permanent: false },
      { source: '/temas', destination: '/ideias', permanent: false },
      { source: '/oportunidades', destination: '/ideias', permanent: false },
      { source: '/dashboards', destination: '/business-intelligence', permanent: false },
      { source: '/producao/motion-videos', destination: '/criar', permanent: false },
      { source: '/estrategia', destination: '/criar', permanent: false },
    ]
  },
}
export default nextConfig
