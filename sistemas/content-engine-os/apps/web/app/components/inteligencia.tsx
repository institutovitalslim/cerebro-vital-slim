'use client'

import { useEffect, useState, useCallback } from 'react'

const api = process.env.NEXT_PUBLIC_API_BASE_URL || '/api'

type Intel = { id: string; titulo: string | null; conteudo: string; status: string; tipo: string | null; created_at: string }

const STATUS: Record<string, { label: string; color: string }> = {
  pendente: { label: 'Pendente', color: '#E0B871' },
  aprovado: { label: 'Aprovado ✓', color: '#7CCB8E' },
  rejeitado: { label: 'Rejeitado', color: '#D98A8A' },
}

export function InteligenciaCriativa() {
  const [items, setItems] = useState<Intel[]>([])
  const [busy, setBusy] = useState(false)
  const [msg, setMsg] = useState<string | null>(null)
  const [titulo, setTitulo] = useState('')
  const [conteudo, setConteudo] = useState('')

  const load = useCallback(async () => {
    try {
      const r = await fetch(`${api}/generation/intelligence?tenant_slug=demo`, { cache: 'no-store' })
      const d = await r.json()
      setItems(d.items || [])
    } catch { /* */ }
  }, [])
  useEffect(() => { load() }, [load])

  async function validate(id: string, status: string) {
    await fetch(`${api}/generation/intelligence/${id}/validate`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ status }),
    })
    load()
  }
  async function ingest() {
    setBusy(true); setMsg(null)
    try {
      const r = await fetch(`${api}/generation/intelligence/ingest?tenant_slug=demo`, { method: 'POST' })
      const d = await r.json()
      setMsg(d.ingested ? `${d.ingested} diretrizes destiladas (pendentes de validação).` : (d.msg || 'Nada para destilar.'))
      load()
    } catch { setMsg('Erro ao destilar.') } finally { setBusy(false) }
  }
  async function add() {
    if (!conteudo.trim()) return
    setBusy(true)
    await fetch(`${api}/generation/intelligence`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tenant_slug: 'demo', titulo: titulo || null, conteudo }),
    })
    setTitulo(''); setConteudo(''); setBusy(false); load()
  }

  const pend = items.filter((i) => i.status === 'pendente')
  const aprov = items.filter((i) => i.status === 'aprovado')

  return (
    <section className="section" style={{ marginTop: 28 }}>
      <div className="sectionHeaderInline" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 10 }}>
        <div>
          <h3 className="sectionTitle" style={{ margin: 0 }}>🧠 Inteligência de Marca & Posicionamento</h3>
          <p className="muted small" style={{ margin: '2px 0 0' }}>
            Conteúdo das fontes de Marca alimenta a criação — mas só vira inteligência criativa <strong>depois de validado</strong>.
            {aprov.length ? ` ${aprov.length} aprovada(s) já guiam o gerador.` : ''}
          </p>
        </div>
        <button className="primaryButton" onClick={ingest} disabled={busy}>{busy ? 'Destilando…' : 'Destilar das fontes de Marca'}</button>
      </div>
      {msg ? <p className="muted small" style={{ marginTop: 8 }}>{msg}</p> : null}

      {/* adicionar manual */}
      <div className="card" style={{ marginTop: 12, display: 'grid', gap: 8, padding: 12 }}>
        <label className="muted small">Adicionar diretriz manualmente</label>
        <input className="input" placeholder="Título (opcional) — ex.: Tom de voz" value={titulo} onChange={(e) => setTitulo(e.target.value)} />
        <textarea className="textarea" placeholder="Diretriz de marca/posicionamento — ex.: nunca culpar a paciente; falar de mecanismo e causa…" value={conteudo} onChange={(e) => setConteudo(e.target.value)} style={{ minHeight: 56 }} />
        <button className="secondaryLink" onClick={add} disabled={busy || !conteudo.trim()} style={{ width: 'fit-content' }}>Adicionar (vai para validação)</button>
      </div>

      {/* pendentes */}
      {pend.length ? (
        <div style={{ marginTop: 16 }}>
          <p className="muted small" style={{ margin: '0 0 8px' }}>Pendentes de validação ({pend.length})</p>
          <div style={{ display: 'grid', gap: 8 }}>
            {pend.map((i) => (
              <div key={i.id} className="card" style={{ padding: 12, display: 'grid', gap: 6 }}>
                {i.titulo ? <strong style={{ fontSize: 14 }}>{i.titulo}</strong> : null}
                <p className="small" style={{ margin: 0, color: '#cdbfa6' }}>{i.conteudo}</p>
                <div style={{ display: 'flex', gap: 8, marginTop: 2 }}>
                  <button className="primaryButton" style={{ padding: '5px 12px', fontSize: 13 }} onClick={() => validate(i.id, 'aprovado')}>Aprovar</button>
                  <button className="secondaryLink" onClick={() => validate(i.id, 'rejeitado')}>Rejeitar</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : null}

      {/* aprovadas */}
      {aprov.length ? (
        <div style={{ marginTop: 16 }}>
          <p className="muted small" style={{ margin: '0 0 8px' }}>Aprovadas — guiando o gerador ({aprov.length})</p>
          <div style={{ display: 'grid', gap: 6 }}>
            {aprov.map((i) => (
              <div key={i.id} className="card" style={{ padding: '8px 12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 10 }}>
                <span className="small">{i.titulo ? <strong>{i.titulo}: </strong> : null}{i.conteudo.slice(0, 140)}</span>
                <button className="secondaryLink" style={{ flexShrink: 0 }} onClick={() => validate(i.id, 'rejeitado')}>Remover</button>
              </div>
            ))}
          </div>
        </div>
      ) : null}

      {!items.length ? <p className="muted small" style={{ marginTop: 12 }}>Nenhuma inteligência ainda. Destile das fontes de Marca ou adicione uma diretriz manual.</p> : null}
    </section>
  )
}
