'use client'

import { useState } from 'react'

const api = process.env.NEXT_PUBLIC_API_BASE_URL || '/api'

export default function ContaPage() {
  const [cur, setCur] = useState('')
  const [nw, setNw] = useState('')
  const [cf, setCf] = useState('')
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null)
  const [loading, setLoading] = useState(false)

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    setMsg(null)
    if (nw.length < 8) { setMsg({ ok: false, text: 'A nova senha precisa ter ao menos 8 caracteres.' }); return }
    if (nw !== cf) { setMsg({ ok: false, text: 'A confirmação não bate com a nova senha.' }); return }
    setLoading(true)
    try {
      const r = await fetch(`${api}/auth/change-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ current_password: cur, new_password: nw }),
      })
      const d = await r.json().catch(() => ({}))
      if (!r.ok) { setMsg({ ok: false, text: d?.detail || 'Não foi possível alterar a senha.' }); setLoading(false); return }
      setMsg({ ok: true, text: 'Senha alterada com sucesso.' })
      setCur(''); setNw(''); setCf('')
    } catch {
      setMsg({ ok: false, text: 'Falha de conexão. Tente de novo.' })
    }
    setLoading(false)
  }

  return (
    <div>
      <header className="pageHeader">
        <p className="eyebrow">Conta</p>
        <h2 className="pageTitle">Alterar senha</h2>
        <p className="muted">Defina uma nova senha de acesso ao Content Engine OS.</p>
      </header>

      <form onSubmit={submit} className="card" style={{ width: 'min(440px, 100%)', display: 'grid', gap: 14 }}>
        <label className="small">Senha atual
          <input className="input" type="password" autoComplete="current-password" value={cur}
            onChange={(e) => setCur(e.target.value)} required />
        </label>
        <label className="small">Nova senha <span className="muted">(mín. 8 caracteres)</span>
          <input className="input" type="password" autoComplete="new-password" value={nw}
            onChange={(e) => setNw(e.target.value)} required />
        </label>
        <label className="small">Confirmar nova senha
          <input className="input" type="password" autoComplete="new-password" value={cf}
            onChange={(e) => setCf(e.target.value)} required />
        </label>
        {msg ? (
          <div className="briefingBox" style={{
            borderColor: msg.ok ? 'rgba(127,208,165,.4)' : 'rgba(255,141,135,.45)',
            background: msg.ok ? 'rgba(127,208,165,.07)' : 'rgba(255,141,135,.07)',
          }}>
            <p className="small" style={{ margin: 0, color: msg.ok ? 'var(--success)' : 'var(--danger)' }}>{msg.text}</p>
          </div>
        ) : null}
        <button type="submit" className="primaryButton" disabled={loading} style={{ cursor: loading ? 'wait' : 'pointer' }}>
          {loading ? 'Salvando…' : 'Salvar nova senha'}
        </button>
      </form>
    </div>
  )
}
