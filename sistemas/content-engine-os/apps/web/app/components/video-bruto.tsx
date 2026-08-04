'use client'

import { useState, useEffect, useCallback } from 'react'

const api = process.env.NEXT_PUBLIC_API_BASE_URL || '/api'

type Phase = 'idle' | 'enviando' | 'processando' | 'pronto' | 'erro'

export function VideoBruto() {
  const [title, setTitle] = useState('')
  const [hook, setHook] = useState('')
  const [cid, setCid] = useState<string | null>(null)
  const [phase, setPhase] = useState<Phase>('idle')
  const [reelUrl, setReelUrl] = useState<string | null>(null)
  const [msg, setMsg] = useState('')

  async function onFile(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0]
    e.target.value = ''
    if (!f) return
    setPhase('enviando'); setReelUrl(null); setMsg(`Enviando "${f.name}"…`)
    const fd = new FormData()
    fd.append('file', f); fd.append('title', title); fd.append('hook', hook)
    try {
      const r = await fetch(`${api}/generation/raw-reel`, { method: 'POST', body: fd })
      const d = await r.json()
      if (!r.ok || !d.id) throw new Error(d.detail || 'falha no upload')
      setCid(d.id); setPhase('processando')
      setMsg('Vídeo recebido. Gerando cortes, sincronização, legenda cinética, b-roll compliant, efeitos e transições… (pode levar ~20-40 min)')
    } catch {
      setPhase('erro'); setMsg('Falha ao enviar o vídeo.')
    }
  }

  const poll = useCallback(async () => {
    if (!cid) return
    try {
      const r = await fetch(`${api}/generation/creatives?tenant_slug=demo&limit=80`, { cache: 'no-store' })
      const d = await r.json()
      const c = (d.items || []).find((x: { id: string }) => x.id === cid)
      if (c?.reel_url) { setReelUrl(c.reel_url); setPhase('pronto'); setMsg('Reel pronto!') }
      else if (c && String(c.reel_status || '').includes('erro')) { setPhase('erro'); setMsg('Erro ao processar o vídeo.') }
    } catch { /* */ }
  }, [cid])

  useEffect(() => {
    if (phase !== 'processando') return
    const t = setInterval(poll, 8000)
    return () => clearInterval(t)
  }, [phase, poll])

  const busy = phase === 'enviando' || phase === 'processando'

  return (
    <div className="section">
      <article className="formCard">
        <div className="formHeader"><h3>Enviar vídeo bruto</h3></div>
        <p className="muted small" style={{ marginTop: -4 }}>
          Suba a gravação crua (a Dra falando, 9:16 de preferência). O sistema gera <strong>cortes + sincronização,
          legenda cinética, b-roll compliant (gate Codex), intro de gancho, transições e SFX</strong> — e devolve o reel pronto.
        </p>
        <div className="grid" style={{ gridTemplateColumns: '1fr 1fr' }}>
          <label className="small">Título (opcional)
            <input className="input" placeholder="ex: Tireoide e cansaço 40+" value={title} onChange={(e) => setTitle(e.target.value)} disabled={busy} />
          </label>
          <label className="small">Gancho / tese (opcional, vira a intro)
            <input className="input" placeholder="ex: Depois dos 40, o cansaço não é frescura" value={hook} onChange={(e) => setHook(e.target.value)} disabled={busy} />
          </label>
        </div>
        <label className="primaryButton" style={{ cursor: busy ? 'wait' : 'pointer', marginTop: 4 }}>
          {phase === 'enviando' ? 'Enviando…' : phase === 'processando' ? 'Processando…' : '＋ Enviar vídeo bruto'}
          <input type="file" accept="video/*" onChange={onFile} disabled={busy} style={{ display: 'none' }} />
        </label>
        {msg ? (
          <div className="briefingBox" style={phase === 'erro' ? { borderColor: 'rgba(255,141,135,.45)', background: 'rgba(255,141,135,.07)' } : undefined}>
            <p className="small" style={{ margin: 0, color: phase === 'erro' ? 'var(--danger)' : phase === 'pronto' ? 'var(--success)' : 'var(--text-soft)' }}>
              {phase === 'processando' ? '⏳ ' : phase === 'pronto' ? '✓ ' : phase === 'erro' ? '✕ ' : ''}{msg}
            </p>
          </div>
        ) : null}
      </article>

      {phase === 'pronto' && reelUrl ? (
        <article className="card" style={{ display: 'grid', gap: 12, justifyItems: 'center' }}>
          <h3 className="sectionTitle" style={{ alignSelf: 'start' }}>Reel pronto</h3>
          <video src={`${api}${reelUrl}`} controls playsInline
            style={{ width: 'min(360px, 90%)', aspectRatio: '9 / 16', borderRadius: 18, background: '#000' }} />
          <div style={{ display: 'flex', gap: 8 }}>
            <a className="primaryLink" href={`${api}${reelUrl}`} download target="_blank" rel="noreferrer">⬇️ Baixar</a>
            <a className="secondaryLink" href="/banco-criativos">Ver no Banco de Criativos</a>
          </div>
        </article>
      ) : null}
    </div>
  )
}
