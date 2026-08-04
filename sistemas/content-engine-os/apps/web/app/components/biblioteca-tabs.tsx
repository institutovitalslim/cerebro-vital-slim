'use client'

import { useCallback, useEffect, useState, type ChangeEvent } from 'react'
import { AssetUploadForm } from './forms'
import { DraPhotos } from './dra-photos'
import { EmptyState } from './empty-state'

const api = process.env.NEXT_PUBLIC_API_BASE_URL || '/api'

export type Asset = {
  id: string
  title: string
  original_filename: string
  mime_type: string | null
  file_size_bytes: number
  asset_kind: string
  tags: string[]
  created_at: string
}

type BrollItem = {
  file: string
  kind: string
  tags: string
  theme: string
  note: string
  url: string
  thumb: string | null
}

export type TabId = 'assets' | 'dra' | 'broll'

function assetIcon(a: Asset): string {
  const mime = a.mime_type || ''
  if (mime.startsWith('video/')) return '🎬'
  if (mime === 'application/pdf') return '📄'
  if (mime.startsWith('audio/')) return '🎧'
  if (a.asset_kind === 'proof') return '🧾'
  if (a.asset_kind === 'brand') return '✨'
  return '🗂️'
}

// ————— Aba 1: Assets genéricos (lista + upload de /assets) —————

function AssetsTab({ assets, erro, atualizando, onReload }: {
  assets: Asset[]
  erro: boolean
  atualizando: boolean
  onReload: () => void
}) {
  return (
    <>
      <section className="section grid" style={{ gridTemplateColumns: '1fr 1fr' }}>
        {/* Form existente reutilizado por import; o capture dispara a atualização da lista após o upload */}
        <div onSubmitCapture={() => { setTimeout(onReload, 1500); setTimeout(onReload, 5000) }}>
          <AssetUploadForm />
        </div>
        <article className="card" style={{ alignSelf: 'start' }}>
          <details>
            <summary style={{ cursor: 'pointer', fontWeight: 700 }}>Como usar a biblioteca</summary>
            <div className="tableLike" style={{ marginTop: 10 }}>
              <div className="row"><span className="muted">Suba vídeos crus, imagens, PDFs e prints relevantes.</span></div>
              <div className="row"><span className="muted">Classifique por tipo e tags para reaproveitamento futuro.</span></div>
              <div className="row"><span className="muted">Use a biblioteca como memória operacional do cliente.</span></div>
            </div>
          </details>
        </article>
      </section>

      <section className="section">
        <div className="sectionHeaderInline">
          <h3 className="sectionTitle">Assets salvos</h3>
          <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
            <button className="secondaryLink" style={{ minHeight: 34, fontSize: '.74rem' }} onClick={onReload} disabled={atualizando}>
              {atualizando ? 'Atualizando…' : '↻ Atualizar'}
            </button>
            <span className="badge">{assets.length} assets</span>
          </div>
        </div>

        {erro ? (
          <div className="errorBox">
            Não consegui carregar os assets agora — a lista abaixo pode estar incompleta ou desatualizada. Tente atualizar em instantes.
          </div>
        ) : null}

        {assets.length === 0 ? (
          erro ? null : (
            <EmptyState title="Nenhum asset salvo" hint="Suba vídeos crus, imagens, PDFs e prints para alimentar a geração de criativos. Use o formulário acima." />
          )
        ) : (
          <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(190px, 1fr))' }}>
            {assets.map((item) => {
              const dl = `${api}/assets/${item.id}/download`
              const isImage = (item.mime_type || '').startsWith('image/')
              return (
                <figure key={item.id} className="card" style={{ padding: 10, margin: 0, display: 'grid', gap: 8, alignContent: 'start' }}>
                  {isImage ? (
                    <a href={dl} target="_blank" rel="noreferrer" style={{ display: 'block' }}>
                      <img src={dl} alt={item.title} loading="lazy"
                        style={{ width: '100%', aspectRatio: '4 / 3', objectFit: 'cover', borderRadius: 10, background: '#000' }} />
                    </a>
                  ) : (
                    <div style={{ aspectRatio: '4 / 3', display: 'grid', placeItems: 'center', borderRadius: 10, background: 'rgba(255,255,255,.04)', fontSize: '1.8rem' }}>
                      {assetIcon(item)}
                    </div>
                  )}
                  <figcaption style={{ display: 'grid', gap: 4 }}>
                    <div className="rowTop">
                      <strong style={{ fontSize: '.85rem', lineHeight: 1.25 }}>{item.title}</strong>
                      <span className="badge" style={{ fontSize: '.6rem' }}>{item.asset_kind}</span>
                    </div>
                    <span className="muted small" style={{ wordBreak: 'break-word' }}>
                      {item.original_filename} · {Math.max(1, Math.round(item.file_size_bytes / 1024))} KB
                    </span>
                    <span className="muted small">{item.tags?.length ? item.tags.join(', ') : 'sem tags'}</span>
                  </figcaption>
                  <a className="secondaryLink" style={{ width: '100%', minHeight: 32, fontSize: '.72rem' }} href={dl} target="_blank" rel="noreferrer">Baixar</a>
                </figure>
              )
            })}
          </div>
        )}
      </section>
    </>
  )
}

// ————— Aba 2: Fotos da Dra (componente existente) —————

function DraTab() {
  return (
    <>
      <p className="muted" style={{ margin: '0 0 4px', maxWidth: 760 }}>
        Fotos reais da Dra Daniely usadas nos criativos. Toda foto nova passa pelo gate de compliance
        (sem medicação, seringa, caneta de aplicação, jaleco ou ambiente clínico). Padrão da marca:
        fundo preto, look elegante.
      </p>
      <DraPhotos />
    </>
  )
}

// ————— Aba 3: B-roll (upload + acervo; o planejamento por tema segue na página completa) —————

function BrollTab({ items, carregado, erro, onReload }: {
  items: BrollItem[]
  carregado: boolean
  erro: boolean
  onReload: () => void
}) {
  const [uploading, setUploading] = useState(false)
  const [tags, setTags] = useState('')
  const [utheme, setUtheme] = useState('')
  const [msg, setMsg] = useState('')

  async function onUpload(e: ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0]
    e.target.value = ''
    if (!f) return
    setUploading(true); setMsg('')
    const fd = new FormData()
    fd.append('file', f); fd.append('tags', tags); fd.append('theme', utheme)
    try {
      const r = await fetch(`${api}/stories/broll/upload`, { method: 'POST', body: fd })
      const d = await r.json()
      if (d.ok) { setMsg(`✓ ${d.kind} adicionado: ${d.file}`); setTags(''); onReload() }
      else setMsg(`✕ ${d.detail || 'falha no upload'}`)
    } catch { setMsg('✕ falha de rede') }
    setUploading(false)
  }

  async function apagar(file: string) {
    if (!confirm(`Remover "${file}" da biblioteca?`)) return
    try { await fetch(`${api}/stories/broll/${file}`, { method: 'DELETE' }); onReload() } catch { /* */ }
  }

  return (
    <>
      <section className="section grid" style={{ gridTemplateColumns: '1fr 1fr' }}>
        <article className="formCard">
          <div className="formHeader"><h3>Carregar foto/vídeo</h3></div>
          <p className="muted small" style={{ marginTop: -4 }}>
            Fotos e vídeos curtos que a Dra grava — viram matéria-prima de <strong>Stories e Reels</strong>.
          </p>
          <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(160px,1fr))' }}>
            <label className="small">Tema (opcional)
              <input className="input" placeholder="ex.: sono, menopausa" value={utheme} onChange={(e) => setUtheme(e.target.value)} />
            </label>
            <label className="small">Tags (vírgula)
              <input className="input" placeholder="acolhedor, caminhada" value={tags} onChange={(e) => setTags(e.target.value)} />
            </label>
          </div>
          <label className="primaryButton" style={{ cursor: uploading ? 'wait' : 'pointer', marginTop: 4 }}>
            {uploading ? 'Enviando…' : '＋ Enviar foto ou vídeo'}
            <input type="file" accept="image/png,image/jpeg,image/webp,video/mp4,video/quicktime,video/webm" onChange={onUpload} disabled={uploading} style={{ display: 'none' }} />
          </label>
          {msg ? <p className="small" style={{ marginTop: 6 }}>{msg}</p> : null}
        </article>
        <article className="card" style={{ alignSelf: 'start' }}>
          <h3 style={{ marginTop: 0 }}>Planejar o que gravar</h3>
          <p className="muted small">
            A lista de gravação por tema (objetos → ações → sequências) continua na página completa do b-roll.
          </p>
          <a className="secondaryLink" href="/stories-engine/broll">Sugerir gravações por tema →</a>
        </article>
      </section>

      <div className="sectionHeaderInline">
        <h3 className="sectionTitle">Acervo de b-roll</h3>
        <span className="badge">{items.length} itens</span>
      </div>

      {erro ? (
        <div className="errorBox">
          Não consegui carregar o acervo de b-roll agora — o que aparece abaixo pode estar incompleto.{' '}
          <button className="secondaryLink" style={{ minHeight: 30, fontSize: '.72rem', marginLeft: 6 }} onClick={onReload}>Tentar de novo</button>
        </div>
      ) : null}
      {!carregado && !erro ? <div className="empty">Carregando acervo…</div> : null}
      {carregado && !erro && items.length === 0 ? (
        <div className="empty">Nenhum b-roll ainda. Grave e carregue aqui — ou peça a lista de gravação por tema na página completa.</div>
      ) : null}

      {items.length > 0 ? (
        <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(160px,1fr))' }}>
          {items.map((p) => (
            <figure key={p.file} className="card" style={{ padding: 8, margin: 0, display: 'grid', gap: 6 }}>
              {p.kind === 'foto' ? (
                <a href={`${api}${p.url}`} target="_blank" rel="noreferrer">
                  <img src={`${api}${p.thumb || p.url}`} alt={p.tags || p.file} loading="lazy"
                    style={{ width: '100%', aspectRatio: '9/16', objectFit: 'cover', borderRadius: 10, background: '#000' }} />
                </a>
              ) : (
                <video src={`${api}${p.url}`} controls preload="metadata"
                  style={{ width: '100%', aspectRatio: '9/16', objectFit: 'cover', borderRadius: 10, background: '#000' }} />
              )}
              <figcaption className="muted small" style={{ lineHeight: 1.3 }}>
                <span className="badge" style={{ fontSize: '.6rem' }}>{p.kind === 'video' ? '🎬 vídeo' : '📸 foto'}</span>{' '}
                {p.theme || p.tags || ''}
              </figcaption>
              <button className="secondaryLink" style={{ width: '100%', minHeight: 32, fontSize: '.72rem' }} onClick={() => apagar(p.file)}>Remover</button>
            </figure>
          ))}
        </div>
      ) : null}
    </>
  )
}

// ————— Container das abas —————

export function BibliotecaTabs({ initialAssets, assetsErro, initialTab = 'assets' }: {
  initialAssets: Asset[]
  assetsErro: boolean
  initialTab?: TabId
}) {
  const [tab, setTab] = useState<TabId>(initialTab)
  const [assets, setAssets] = useState<Asset[]>(initialAssets)
  const [erroAssets, setErroAssets] = useState(assetsErro)
  const [atualizando, setAtualizando] = useState(false)

  const [broll, setBroll] = useState<BrollItem[]>([])
  const [brollCarregado, setBrollCarregado] = useState(false)
  const [erroBroll, setErroBroll] = useState(false)

  const recarregarAssets = useCallback(async () => {
    setAtualizando(true)
    try {
      const r = await fetch(`${api}/assets?tenant_slug=demo`, { cache: 'no-store', credentials: 'include' })
      if (!r.ok) throw new Error(String(r.status))
      const d = await r.json()
      setAssets(d.items || [])
      setErroAssets(false)
    } catch { setErroAssets(true) }
    setAtualizando(false)
  }, [])

  const carregarBroll = useCallback(async () => {
    try {
      const r = await fetch(`${api}/stories/broll`, { cache: 'no-store' })
      if (!r.ok) throw new Error(String(r.status))
      const d = await r.json()
      setBroll(d.items || [])
      setErroBroll(false)
    } catch { setErroBroll(true) }
    setBrollCarregado(true)
  }, [])

  useEffect(() => {
    if (tab === 'broll' && !brollCarregado) carregarBroll()
  }, [tab, brollCarregado, carregarBroll])

  function trocar(t: TabId) {
    setTab(t)
    try {
      window.history.replaceState(null, '', t === 'assets' ? '/biblioteca' : `/biblioteca?tab=${t}`)
    } catch { /* */ }
  }

  const abas: { id: TabId; rotulo: string; badge?: number }[] = [
    { id: 'assets', rotulo: '🗂 Assets', badge: assets.length },
    { id: 'dra', rotulo: '📸 Fotos da Dra' },
    { id: 'broll', rotulo: '🎬 B-roll', badge: brollCarregado ? broll.length : undefined },
  ]

  return (
    <div>
      <nav style={{ display: 'flex', gap: 8, margin: '4px 0 14px', flexWrap: 'wrap' }}>
        {abas.map((a) => (
          <button key={a.id} type="button" onClick={() => trocar(a.id)}
            style={{
              background: tab === a.id ? 'rgba(201,162,39,.16)' : 'rgba(255,255,255,.04)',
              border: `1px solid ${tab === a.id ? '#c9a227' : 'rgba(255,255,255,.09)'}`,
              color: 'inherit', borderRadius: 12, padding: '10px 18px', fontWeight: 700,
              fontSize: '.95rem', cursor: 'pointer',
            }}>
            {a.rotulo}{typeof a.badge === 'number' ? ` (${a.badge})` : ''}
          </button>
        ))}
      </nav>

      {tab === 'assets' ? (
        <AssetsTab assets={assets} erro={erroAssets} atualizando={atualizando} onReload={recarregarAssets} />
      ) : null}
      {tab === 'dra' ? <DraTab /> : null}
      {tab === 'broll' ? (
        <BrollTab items={broll} carregado={brollCarregado} erro={erroBroll} onReload={carregarBroll} />
      ) : null}
    </div>
  )
}
