'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useEffect, useState } from 'react'

const api = process.env.NEXT_PUBLIC_API_BASE_URL || '/api'

type NavItem = { href: string; label: string }

type Group = {
  title: string
  links: NavItem[]
}

export function Sidebar({
  groups,
  topLinks = [],
  utilityLinks = [],
}: {
  groups: Group[]
  topLinks?: NavItem[]
  utilityLinks?: NavItem[]
}) {
  const pathname = usePathname()
  const [open, setOpen] = useState(false)
  const [user, setUser] = useState<{ name?: string; email?: string } | null>(null)

  useEffect(() => {
    fetch(`${api}/auth/session`, { credentials: 'include', cache: 'no-store' })
      .then((r) => r.json())
      .then((d) => { if (d?.authenticated) setUser(d.user) })
      .catch(() => {})
  }, [])

  async function logout() {
    try {
      await fetch(`${api}/auth/logout`, { method: 'POST', credentials: 'include' })
    } catch { /* segue p/ login mesmo se falhar */ }
    window.location.assign('/login')
  }

  function renderLink(link: NavItem, style?: React.CSSProperties) {
    const active = pathname === link.href
    return (
      <Link
        key={link.href}
        href={link.href}
        className={`navLink${active ? ' navLinkActive' : ''}`}
        aria-current={active ? 'page' : undefined}
        onClick={() => setOpen(false)}
        style={style}
      >
        <span className="navLinkLabel">{link.label}</span>
      </Link>
    )
  }

  return (
    <>
      <button
        type="button"
        className="navToggle"
        aria-expanded={open}
        aria-controls="mainNav"
        onClick={() => setOpen((v) => !v)}
      >
        <span>☰ Menu</span>
        <span className="navToggleHint">{open ? 'fechar' : 'abrir'}</span>
      </button>
      <nav
        id="mainNav"
        className={`nav${open ? '' : ' navCollapsed'}`}
        aria-label="Navegação principal do Content Engine OS"
      >
        {topLinks.length > 0 ? (
          <section className="navGroup">
            <div className="navGroupLinks">
              {topLinks.map((link) => renderLink(link))}
            </div>
          </section>
        ) : null}

        {groups.map((group) => (
          <section key={group.title} className="navGroup">
            <p className="eyebrow small navGroupTitle">{group.title}</p>
            <div className="navGroupLinks">
              {group.links.map((link) => renderLink(link))}
            </div>
          </section>
        ))}

        <section className="navGroup" style={{ marginTop: 'auto', borderTop: '1px solid rgba(255,255,255,.08)', paddingTop: 12 }}>
          {user ? (
            <p className="small muted" style={{ margin: '0 0 8px', lineHeight: 1.3 }}>
              Logado como<br /><strong style={{ color: 'var(--ink, #eee)' }}>{user.name || user.email}</strong>
            </p>
          ) : null}
          <div className="navGroupLinks">
            {utilityLinks.map((link) => renderLink(link, { fontSize: 13, opacity: 0.9 }))}
            <Link
              href="/conta"
              className={`navLink${pathname === '/conta' ? ' navLinkActive' : ''}`}
              onClick={() => setOpen(false)}
              style={{ fontSize: 13, opacity: 0.9 }}
            >
              <span className="navLinkLabel">🔑 Alterar senha</span>
            </Link>
            <button type="button" className="navLink" onClick={logout}
              style={{ background: 'none', border: 'none', textAlign: 'left', cursor: 'pointer', width: '100%', fontSize: 13, opacity: 0.9 }}>
              <span className="navLinkLabel">↩ Sair</span>
            </button>
          </div>
        </section>
      </nav>
    </>
  )
}
