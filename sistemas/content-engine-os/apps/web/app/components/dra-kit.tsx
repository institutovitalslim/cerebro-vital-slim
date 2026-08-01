'use client'

import { useEffect, useState, useCallback } from 'react'

const api = process.env.NEXT_PUBLIC_API_BASE_URL || '/api'

// Kit de Gravação da Dra — roteiro p/ teleprompter + direção de arte + upload do vídeo.
// Compartilhado entre Reels e Stories (vídeo 9:16 serve os dois).
export function DraRecordingKit({ cid }: { cid: string }) {
  const [da, setDa] = useState<string | null>(null)
  const [hasVideo, setHasVideo] = useState(false)
  const [busy, setBusy] = useState(false)
  const [upMsg, setUpMsg] = useState('')

  const load = useCallback(async () => {
    try {
      const r = await fetch(`${api}/generation/creatives/${cid}/direcao-arte`, { cache: 'no-store' })
      const d = await r.json()
      setDa(d.direcao_arte || null); setHasVideo(!!d.has_video)
    } catch { /* */ }
  }, [cid])
  useEffect(() => { load() }, [load])

  async function gerarDirecao() {
    setBusy(true)
    try {
      const r = await fetch(`${api}/generation/creatives/${cid}/direcao-arte`, { method: 'POST' })
      const d = await r.json(); setDa(d.direcao_arte || null)
    } catch { /* */ }
    setBusy(false)
  }

  async function upload(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0]; if (!f) return
    setBusy(true); setUpMsg('Enviando vídeo…')
    const fd = new FormData(); fd.append('file', f)
    try {
      const r = await fetch(`${api}/generation/creatives/${cid}/dra-video`, { method: 'POST', body: fd })
      const d = await r.json()
      if (d.ok) { setHasVideo(true); setUpMsg('Vídeo enviado ✓ (' + f.name + ')') } else setUpMsg('Falha no envio')
    } catch { setUpMsg('Falha no envio') }
    setBusy(false)
  }

  return (
    <div style={{ marginTop: 14, borderTop: '1px solid rgba(255,255,255,.08)', paddingTop: 14 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 10 }}>
        <strong style={{ fontSize: '.95rem' }}>🎥 Gravação da Dra</strong>
        {hasVideo ? <span className="badge" style={{ border: '1px solid #6bbf6b' }}>vídeo enviado ✓</span> : null}
      </div>
      <p className="muted small" style={{ margin: '6px 0 0' }}>
        Baixe o roteiro para o teleprompter do celular, siga a direção de arte e suba o vídeo gravado da Dra. Serve para Reels e Stories (vertical 9:16).
      </p>
      <div style={{ display: 'flex', gap: 8, marginTop: 10, flexWrap: 'wrap' }}>
        <a className="secondaryLink" href={`${api}/generation/creatives/${cid}/roteiro.txt`}>⬇️ Roteiro (.txt)</a>
        <a className="secondaryLink" href={`${api}/generation/creatives/${cid}/kit.txt`}>⬇️ Kit completo (roteiro + arte)</a>
        <button className="secondaryLink" onClick={gerarDirecao} disabled={busy}>
          {busy ? '…' : (da ? 'Regerar direção de arte' : 'Gerar direção de arte')}
        </button>
        <label className="primaryButton" style={{ marginLeft: 'auto', cursor: 'pointer' }}>
          {busy ? 'Enviando…' : (hasVideo ? 'Trocar vídeo' : 'Subir vídeo gravado')}
          <input type="file" accept="video/*" onChange={upload} style={{ display: 'none' }} />
        </label>
      </div>
      {upMsg ? <p className="muted small" style={{ marginTop: 6 }}>{upMsg}</p> : null}
      {da ? (
        <details style={{ marginTop: 10 }}>
          <summary className="muted small" style={{ cursor: 'pointer' }}>Ver direção de arte</summary>
          <pre style={{ whiteSpace: 'pre-wrap', fontSize: 12, color: '#cdbfa6', marginTop: 8, fontFamily: 'inherit' }}>{da}</pre>
        </details>
      ) : null}
    </div>
  )
}
