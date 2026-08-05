import type { Metadata } from 'next'
import Link from 'next/link'
import styles from './layout.module.css'

export const metadata: Metadata = {
  title: 'Hook Intelligence · Content Engine OS',
  description: 'Gerador, biblioteca e inteligência de hooks do Instituto Vital Slim.',
}

const tabs = [
  { href: '/hook-intelligence', label: 'Gerador' },
  { href: '/hook-intelligence/biblioteca', label: 'Biblioteca' },
  { href: '/hook-intelligence/salvos', label: 'Salvos' },
]

export default function HookIntelligenceLayout({ children }: { children: React.ReactNode }) {
  return (
    <section className={styles.scope}>
      <header className={styles.header}>
        <div>
          <p className={styles.eyebrow}>Content Engine OS · Criar</p>
          <h2>Hook Intelligence</h2>
          <p>Criação determinística, comparação e acervo editorial com IA opcional.</p>
        </div>
        <span className={styles.badge}>Cockpit editorial</span>
      </header>
      <nav className={styles.tabs} aria-label="Navegação do Hook Intelligence">
        {tabs.map(tab => <Link key={tab.href} href={tab.href}>{tab.label}</Link>)}
      </nav>
      <div className={styles.surface}>{children}</div>
    </section>
  )
}
