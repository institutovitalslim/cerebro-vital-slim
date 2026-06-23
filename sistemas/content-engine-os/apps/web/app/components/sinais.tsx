'use client'

import { useEffect, useState } from 'react'

const api = process.env.NEXT_PUBLIC_API_BASE_URL || '/api'
type Sinal = {
  id: string; classificacao: string; likes: number; comments: number; engagement: number
  caption: string | null; url: string | null; external_code: string; fonte: string
}
const CLS: Record<string, string> = { viral: '🔥 Viral', potencial: '⤴ Potencial', novo: 'novo' }

export function SinaisVirais() {
  const [items, setItems] = useState<Sinal[]>([])
  const [filtro, setFiltro] = useState('viral')
  const [msg, setMsg] = useState<string | null>(null)
  const [gerando, setGerando] = useState<string | null>(null)

  async function load() {
    try {
      const r = await fetch(`${api}/sources/signals?tenant_slug=demo&limit=60`, { cache: 'no-store' })
      const d = await r.json(); setItems(d.items || [])
    } catch { /* */ }
  }
  useEffect(() => { load() }, [])

  async function gerarRoteiro(s: Sinal) {
    setGerando(s.id); setMsg(null)
    try {
      const r = await fetch(`${api}/generation/engenharia-reversa`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tenant_slug: 'demo', handle: s.fonte, referencia: `${s.caption || ''}\n${s.url || ''} (${s.likes} likes, ${s.comments} comentários)` }),
      })
      const d = await r.json()
      setMsg(`✓ ${d.saved || 0} roteiro(s) gerado(s) deste viral → Banco de Roteiros.`)
    } catch { setMsg('Não consegui gerar agora.') } finally { setGerando(null) }
  }

  const vis = items.filter((s) => filtro === 'todos' || s.classificacao === filtro)

  return (
    <section className="section">
      <div className="sectionHeaderInline">
        <div>
          <p className="eyebrow">Monitoramento diário</p>
          <h3 className="sectionTitle">Sinais virais capturados</h3>
        </div>
        <div style={{ display: 'flex', gap: 6 }}>
          {['viral', 'potencial', 'todos'].map((f) => (
            <button key={f} className={f === filtro ? 'primaryButton' : 'secondaryLink'} style={{ padding: '4px 12px', fontSize: 13 }} onClick={() => setFiltro(f)}>{CLS[f] || f}</button>
          ))}
        </div>
      </div>
      {msg ? <p className="successText" style={{ margin: '0 0 10px' }}>{msg}</p> : null}
      {vis.length === 0 ? <p className="muted small">Sem sinais ainda — o monitor roda diariamente nas fontes de rede social ativas.</p> : null}
      <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fill,minmax(280px,1fr))', gap: 14 }}>
        {vis.map((s) => (
          <article key={s.id} className="card" style={{ display: 'grid', gap: 8 }}>
            <div className="rowTop">
              <span className={`badge ${s.classificacao === 'viral' ? '' : 'badgeDark'}`}>{CLS[s.classificacao] || s.classificacao}</span>
              <span className="muted small">{s.fonte}</span>
            </div>
            <p className="small" style={{ margin: 0, whiteSpace: 'pre-wrap', maxHeight: 96, overflow: 'hidden' }}>{(s.caption || '').slice(0, 200)}</p>
            <div className="rowTop">
              <span className="muted small">❤ {s.likes} · 💬 {s.comments}</span>
              {s.url ? <a className="secondaryLink" href={s.url} target="_blank" rel="noreferrer">ver no IG ↗</a> : null}
            </div>
            <button className="primaryButton" style={{ padding: '6px 12px', fontSize: 13 }} onClick={() => gerarRoteiro(s)} disabled={gerando === s.id}>{gerando === s.id ? 'Gerando…' : 'Gerar roteiro deste viral'}</button>
          </article>
        ))}
      </div>
    </section>
  )
}
