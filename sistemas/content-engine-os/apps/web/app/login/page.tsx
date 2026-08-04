'use client'

import { useState } from 'react'

const api = process.env.NEXT_PUBLIC_API_BASE_URL || '/api'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [err, setErr] = useState('')
  const [loading, setLoading] = useState(false)

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    setErr('')
    setLoading(true)
    try {
      const r = await fetch(`${api}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ email, password }),
      })
      if (!r.ok) {
        setErr('E-mail ou senha inválidos.')
        setLoading(false)
        return
      }
      // navegação "hard": recarrega de verdade -> manda o cookie -> middleware libera
      window.location.assign('/')
    } catch {
      setErr('Falha de conexão. Tente de novo.')
      setLoading(false)
    }
  }

  return (
    <div style={{
      position: 'fixed', inset: 0, zIndex: 50, display: 'grid', placeItems: 'center', padding: 24,
      background: 'radial-gradient(1200px 800px at 72% -12%, #1b160d 0%, #0b0b0e 55%, #08080a 100%)',
    }}>
      <form onSubmit={submit} className="card" style={{ width: 'min(400px, 92vw)', display: 'grid', gap: 16, margin: 0 }}>
        <div>
          <p className="eyebrow">Instituto Vital Slim</p>
          <h2 className="pageTitle" style={{ margin: '4px 0 0' }}>Content Engine OS</h2>
          <p className="muted small" style={{ marginTop: 6 }}>Entre para acessar o cockpit.</p>
        </div>
        <label className="small">E-mail
          <input className="input" type="email" autoComplete="username" value={email}
            onChange={(e) => setEmail(e.target.value)} required autoFocus />
        </label>
        <label className="small">Senha
          <input className="input" type="password" autoComplete="current-password" value={password}
            onChange={(e) => setPassword(e.target.value)} required />
        </label>
        {err ? (
          <div className="briefingBox" style={{ borderColor: 'rgba(255,141,135,.45)', background: 'rgba(255,141,135,.07)' }}>
            <p className="small" style={{ margin: 0, color: 'var(--danger)' }}>{err}</p>
          </div>
        ) : null}
        <button type="submit" className="primaryButton" disabled={loading} style={{ cursor: loading ? 'wait' : 'pointer' }}>
          {loading ? 'Entrando…' : 'Entrar'}
        </button>
      </form>
    </div>
  )
}
