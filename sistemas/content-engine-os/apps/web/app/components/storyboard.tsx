'use client'

import { useEffect, useState, useCallback } from 'react'

const api = process.env.NEXT_PUBLIC_API_BASE_URL || '/api'

type Beat = { i: number; start: number; end: number; text: string; who: string; prompt: string }
type SB = { voice: string; dur: number; beats: Beat[]; status?: string }

export function StoryboardPanel({ cid }: { cid: string }) {
  const [status, setStatus] = useState<string | null>(null)
  const [reelUrl, setReelUrl] = useState<string | null>(null)
  const [sb, setSb] = useState<SB | null>(null)
  const [busy, setBusy] = useState(false)
  const [saved, setSaved] = useState(false)

  const load = useCallback(async () => {
    try {
      const r = await fetch(`${api}/generation/creatives/${cid}/storyboard`, { cache: 'no-store' })
      const d = await r.json()
      setStatus(d.reel_status || null)
      setReelUrl(d.reel_url || null)
      if (d.storyboard) setSb(d.storyboard)
    } catch { /* */ }
  }, [cid])

  useEffect(() => { load() }, [load])
  // poll enquanto estiver processando
  useEffect(() => {
    if (status && (status.endsWith('_pendente') || status.endsWith('_gerando'))) {
      const t = setInterval(load, 5000)
      return () => clearInterval(t)
    }
  }, [status, load])

  async function gerar() {
    setBusy(true)
    await fetch(`${api}/generation/creatives/${cid}/storyboard`, { method: 'POST' })
    setStatus('storyboard_pendente'); setBusy(false)
  }
  function editBeat(i: number, patch: Partial<Beat>) {
    if (!sb) return
    setSb({ ...sb, beats: sb.beats.map((b) => (b.i === i ? { ...b, ...patch } : b)) }); setSaved(false)
  }
  async function salvar() {
    if (!sb) return
    setBusy(true)
    await fetch(`${api}/generation/creatives/${cid}/storyboard`, {
      method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ beats: sb.beats }),
    })
    setBusy(false); setSaved(true)
  }
  async function aprovarRenderizar() {
    setBusy(true)
    if (sb) await fetch(`${api}/generation/creatives/${cid}/storyboard`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ beats: sb.beats }) })
    await fetch(`${api}/generation/creatives/${cid}/reel`, { method: 'POST' })
    setStatus('render_pendente'); setBusy(false)
  }

  const processando = status === 'storyboard_pendente' || status === 'storyboard_gerando'
  const renderizando = status === 'render_pendente' || status === 'render_gerando'

  return (
    <div style={{ marginTop: 14, borderTop: '1px solid rgba(255,255,255,.08)', paddingTop: 14 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 10 }}>
        <strong style={{ fontSize: '.95rem' }}>🎬 Storyboard do reel</strong>
        {sb ? <span className="muted small">{sb.beats.length} cenas · {sb.dur}s · corte ~{(sb.dur / sb.beats.length).toFixed(1)}s</span> : null}
      </div>

      {reelUrl ? (
        <div style={{ marginTop: 10 }}>
          <video src={`${api}${reelUrl}`} controls style={{ width: '100%', borderRadius: 12, background: '#000', maxHeight: '60vh' }} />
          <p className="muted small" style={{ margin: '6px 0 0' }}>Reel renderizado ✓ — edite o storyboard e renderize de novo se quiser.</p>
        </div>
      ) : null}

      {renderizando ? <p className="muted small" style={{ marginTop: 8 }}>Renderizando o reel (gera imagens + monta)… isso leva alguns minutos.</p> : null}

      {!sb && !processando ? (
        <button className="primaryButton" style={{ marginTop: 10 }} onClick={gerar} disabled={busy}>
          {busy ? 'Iniciando…' : 'Gerar storyboard'}
        </button>
      ) : null}
      {processando ? <p className="muted small" style={{ marginTop: 8 }}>Gerando storyboard (narração + cenas)…</p> : null}

      {sb ? (
        <>
          <div style={{ marginTop: 10, display: 'grid', gap: 8, maxHeight: '46vh', overflow: 'auto', paddingRight: 4 }}>
            {sb.beats.map((b) => (
              <div key={b.i} className="card" style={{ padding: 10, display: 'grid', gap: 6 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 8 }}>
                  <span className="muted small">cena {b.i + 1} · {b.start}–{b.end}s</span>
                  <div style={{ display: 'flex', gap: 4 }}>
                    {['broll', 'dra'].map((w) => (
                      <button key={w} onClick={() => editBeat(b.i, { who: w })}
                        className="badge" style={{ cursor: 'pointer', border: b.who === w ? '1px solid #b6945b' : '1px solid transparent', opacity: b.who === w ? 1 : 0.5 }}>
                        {w === 'dra' ? 'Dra.' : 'B-roll'}
                      </button>
                    ))}
                  </div>
                </div>
                <p className="small" style={{ margin: 0, color: '#cdbfa6' }}>“{b.text}”</p>
                <textarea className="textarea" value={b.prompt} onChange={(e) => editBeat(b.i, { prompt: e.target.value })}
                  style={{ minHeight: 50, fontSize: 12 }} placeholder="imagem que ilustra esta fala…" />
              </div>
            ))}
          </div>
          <div style={{ display: 'flex', gap: 8, marginTop: 10, flexWrap: 'wrap' }}>
            <button className="secondaryLink" onClick={salvar} disabled={busy}>{saved ? 'Salvo ✓' : 'Salvar alterações'}</button>
            <button className="secondaryLink" onClick={gerar} disabled={busy}>Regerar storyboard</button>
            <button className="primaryButton" onClick={aprovarRenderizar} disabled={busy || renderizando} style={{ marginLeft: 'auto' }}>
              {renderizando ? 'Renderizando…' : 'Aprovar e renderizar reel'}
            </button>
          </div>
        </>
      ) : null}
    </div>
  )
}
