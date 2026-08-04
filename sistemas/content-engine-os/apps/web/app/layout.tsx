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

const topLinks = [
  { href: '/hoje', label: '🏠 Hoje' },
]

const groups = [
  {
    title: 'Acompanhar',
    links: [
      { href: '/trafego', label: '🎯 Central de Tráfego' },
      { href: '/business-intelligence', label: '📊 Instagram & funil' },
      { href: '/social-selling', label: '🤝 Pessoas & social selling' },
    ],
  },
  {
    title: 'Criar',
    links: [
      { href: '/ideias', label: '💡 Ideias do dia' },
      { href: '/criar', label: '🎬 Estúdio' },
      { href: '/producao/video-bruto', label: '🎥 Vídeo bruto → Reel' },
      { href: '/stories-engine', label: '📱 Stories' },
    ],
  },
  {
    title: 'Publicar',
    links: [
      { href: '/banco-criativos', label: '✅ Revisão & aprovação' },
      { href: '/calendario', label: '📅 Calendário · orgânico' },
      { href: '/planejamento', label: '📦 Campanhas Meta · ads' },
    ],
  },
  {
    title: 'Aprender',
    links: [
      { href: '/aprendizado', label: '📈 Aprendizado' },
      { href: '/criativos-campeoes', label: '🏆 Campeões' },
    ],
  },
  {
    title: 'Acervo',
    links: [
      { href: '/biblioteca', label: '🗂 Biblioteca' },
      { href: '/banco-roteiros', label: '📜 Banco de roteiros' },
      { href: '/fontes', label: '🛰 Fontes & sinais' },
      { href: '/radar-externo', label: '🔭 Radar externo' },
    ],
  },
]

const utilityLinks = [
  { href: '/compliance', label: '🛡 Compliance' },
  { href: '/ajuda', label: '❔ Ajuda' },
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

            <Sidebar groups={groups} topLinks={topLinks} utilityLinks={utilityLinks} />

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
