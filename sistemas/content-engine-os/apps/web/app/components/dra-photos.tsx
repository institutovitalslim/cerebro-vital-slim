'use client'

import { useEffect, useState, useCallback } from 'react'

const api = process.env.NEXT_PUBLIC_API_BASE_URL || '/api'

type Photo = {
  file: string
  width: number
  height: number
  background: string
  outfit: string
  tags: string[]
  source: string
  ads_safe?: boolean
  url: string
  thumb: string
}

type UploadResult = {
  approved: boolean
  file?: string
  violations?: string[]
  reason?: string
}

export function DraPhotos() {
  const [items, setItems] = useState<Photo[]>([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [outfit, setOutfit] = useState('')
  const [background, setBackground] = useState('preto')
  const [tags, setTags] = useState('')
  const [result, setResult] = useState<UploadResult | null>(null)
  const [adsMode, setAdsMode] = useState(false)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const r = await fetch(`${api}/assets/dra${adsMode ? '?ads=1' : ''}`, { cache: 'no-store' })
      const d = await r.json()
      setItems(d.items || [])
    } catch { /* */ }
    setLoading(false)
  }, [adsMode])
  useEffect(() => { load() }, [load])

  async function onUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0]
    e.target.value = ''
    if (!f) return
    setUploading(true); setResult(null)
    const fd = new FormData()
    fd.append('file', f)
    fd.append('outfit', outfit)
    fd.append('background', background)
    fd.append('tags', tags)
    try {
      const r = await fetch(`${api}/assets/dra/upload`, { method: 'POST', body: fd })
      const d: UploadResult = await r.json()
      setResult(d)
      if (d.approved) { setOutfit(''); setTags(''); await load() }
    } catch {
      setResult({ approved: false, reason: 'Falha de rede no upload.' })
    }
    setUploading(false)
  }

  async function quarantine(file: string) {
    if (!confirm(`Mover "${file}" para a quarentena? Ela sai do acervo usado nos criativos.`)) return
    const fd = new FormData(); fd.append('filename', file)
    try {
      await fetch(`${api}/assets/dra/quarantine`, { method: 'POST', body: fd })
      await load()
    } catch { /* */ }
  }

  return (
    <div className="section">
      {/* Upload + gate */}
      <article className="formCard">
        <div className="formHeader"><h3>Adicionar foto da Dra</h3></div>
        <p className="muted small" style={{ marginTop: -4 }}>
          Toda foto passa por um <strong>gate de compliance</strong> (IA de visão): medicação, seringa, caneta de
          aplicação, jaleco, ambiente clínico ou antes/depois são <strong>bloqueados</strong> antes de entrar.
          Padrão da marca: <strong>fundo preto</strong>, vestida de forma elegante.
        </p>
        <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))' }}>
          <label className="small">Roupa
            <input className="input" placeholder="ex: blazer off-white" value={outfit} onChange={(e) => setOutfit(e.target.value)} />
          </label>
          <label className="small">Fundo
            <input className="input" value={background} onChange={(e) => setBackground(e.target.value)} />
          </label>
          <label className="small">Tags (vírgula)
            <input className="input" placeholder="autoridade, sorriso" value={tags} onChange={(e) => setTags(e.target.value)} />
          </label>
        </div>
        <label className="primaryButton" style={{ cursor: uploading ? 'wait' : 'pointer', marginTop: 4 }}>
          {uploading ? 'Validando no gate…' : '＋ Enviar foto'}
          <input type="file" accept="image/png,image/jpeg,image/webp" onChange={onUpload} disabled={uploading} style={{ display: 'none' }} />
        </label>

        {result ? (
          result.approved ? (
            <div className="briefingBox" style={{ borderColor: 'rgba(127,208,165,.4)', background: 'rgba(127,208,165,.07)' }}>
              <p><strong style={{ color: 'var(--success)' }}>✓ Aprovada e adicionada</strong> — {result.file}</p>
              {result.reason ? <p className="muted small">{result.reason}</p> : null}
            </div>
          ) : (
            <div className="briefingBox" style={{ borderColor: 'rgba(255,141,135,.45)', background: 'rgba(255,141,135,.07)' }}>
              <p><strong style={{ color: 'var(--danger)' }}>✕ Bloqueada pelo gate de compliance</strong></p>
              {result.violations?.length ? (
                <ul style={{ margin: '4px 0 0 18px' }} className="muted small">
                  {result.violations.map((v, i) => <li key={i}>{v}</li>)}
                </ul>
              ) : null}
              {result.reason ? <p className="muted small">{result.reason}</p> : null}
            </div>
          )
        ) : null}
      </article>

      {/* Galeria */}
      <div className="sectionHeaderInline">
        <h3 className="sectionTitle">Acervo da Dra</h3>
        <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          <button className="secondaryLink" style={{ minHeight: 34, fontSize: '0.74rem' }} onClick={() => setAdsMode((v) => !v)}>
            {adsMode ? '👁️ Mostrar todas' : '📣 Modo anúncio (oculta medicação)'}
          </button>
          <span className="badge">{items.length} fotos</span>
        </div>
      </div>
      {loading ? (
        <div className="empty">Carregando acervo…</div>
      ) : items.length === 0 ? (
        <div className="empty">Nenhuma foto no acervo ainda.</div>
      ) : (
        <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))' }}>
          {items.map((p) => (
            <figure key={p.file} className="card" style={{ padding: 8, margin: 0, display: 'grid', gap: 8 }}>
              <a href={`${api}${p.url}`} target="_blank" rel="noreferrer" style={{ display: 'block' }}>
                <img src={`${api}${p.thumb}`} alt={p.outfit || p.file}
                  style={{ width: '100%', aspectRatio: '3 / 4', objectFit: 'cover', borderRadius: 12, background: '#000' }} />
              </a>
              <figcaption className="muted small" style={{ lineHeight: 1.3 }}>
                {p.outfit || p.file.replace(/^daniely-\d+-/, '').replace(/\.(png|jpg|jpeg|webp)$/, '')}
                {p.source === 'upload' ? <span className="badge" style={{ marginLeft: 6, fontSize: '.6rem' }}>novo</span> : null}
                {p.ads_safe === false ? <span className="badge" style={{ marginLeft: 6, fontSize: '.6rem', borderColor: 'rgba(255,241,168,.4)', color: 'var(--accent-hi)' }} title="Só feed orgânico — não usar em Meta Ads">🔒 só feed</span> : null}
              </figcaption>
              <button className="secondaryLink" style={{ width: '100%', minHeight: 34, fontSize: '.74rem' }}
                onClick={() => quarantine(p.file)}>Quarentena</button>
            </figure>
          ))}
        </div>
      )}
    </div>
  )
}
