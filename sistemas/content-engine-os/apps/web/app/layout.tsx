import type { Metadata } from 'next'
import { Playfair_Display, Montserrat } from 'next/font/google'
import './styles.css'
import { Sidebar } from './components/sidebar'

const playfair = Playfair_Display({
  subsets: ['latin'],
  variable: '--font-display',
  display: 'swap',
})

const montserrat = Montserrat({
  subsets: ['latin'],
  variable: '--font-sans',
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'Vital Slim · Content Engine OS',
  description: 'Cockpit de autoridade, conteúdo e BI do Instituto Vital Slim.',
}

const groups = [
  {
    title: 'Comando',
    links: [
      { href: '/', label: 'Cockpit executivo' },
      { href: '/sprint-semanal', label: 'Sprint semanal' },
      { href: '/business-intelligence', label: 'BI · Business Intelligence' },
      { href: '/social-selling', label: 'Social Selling' },
    ],
  },
  {
    title: 'Inteligência',
    links: [
      { href: '/fontes', label: 'Radar de fontes & sinais' },
      { href: '/banco-roteiros', label: 'Banco de roteiros' },
      { href: '/estrategia', label: 'Estratégia de marca' },
    ],
  },
  {
    title: 'Produção',
    links: [
      { href: '/criar', label: 'Produção · escolher formato' },
      { href: '/producao/carrosseis', label: 'Criar Carrosséis' },
      { href: '/producao/estaticos', label: 'Criar Estáticos' },
      { href: '/producao/reels', label: 'Criar Reels' },
      { href: '/stories-engine', label: 'Stories Engine' },
      { href: '/banco-criativos', label: 'Aprovar criativos' },
      { href: '/biblioteca', label: 'Biblioteca de assets' },
    ],
  },
  {
    title: 'Publicação & Aprendizado',
    links: [
      { href: '/planejamento', label: 'Planejamento de campanhas' },
      { href: '/calendario', label: 'Calendário editorial' },
      { href: '/aprendizado', label: 'Aprendizado de conteúdo' },
      { href: '/dashboards', label: 'Ads & canais pagos' },
      { href: '/criativos-campeoes', label: 'Criativos campeões' },
    ],
  },
  {
    title: 'Motor B · Pacientes',
    links: [{ href: '/apresentacoes', label: 'Apresentações de acompanhamento' }],
  },
]

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body className={`${playfair.variable} ${montserrat.variable}`}>
        <div className="shell">
          <aside className="sidebar">
            <div className="sidebarBackdrop" aria-hidden />
            <div className="sidebarTop">
              <p className="eyebrow">Instituto Vital Slim</p>
              <h1 className="brand">Content Engine OS</h1>
              <p className="muted sidebarDescription">
                Cockpit de autoridade: radar, criação, aprovação, publicação e BI em um fluxo único.
              </p>
            </div>

            <Sidebar groups={groups} />

            <div className="sidebarFooter">
              <span className="badge badgeDark">Regra de uso</span>
              <p className="muted small">
                Não gere peça solta. Comece por tese, crie família, aprove, publique, meça e realimente.
              </p>
            </div>
          </aside>
          <main className="content">{children}</main>
        </div>
      </body>
    </html>
  )
}
