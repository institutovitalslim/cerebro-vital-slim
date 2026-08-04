'use client'

import { useCallback, useEffect, useState } from 'react'

const api = process.env.NEXT_PUBLIC_API_BASE_URL || '/api'

type Shot = { shot: string; na_biblioteca: boolean }
type BrollAction = { acao: string; shot: string; transicao: string; som_ambiente?: string }
type BrollObject = { objeto: string; categoria: string; proposito_visual: string; acoes: BrollAction[]; na_biblioteca?: boolean }
type BrollSequenceShot = {
  ordem: number; funcao_narrativa?: string; objeto: string; acao: string; enquadramento: string; movimento_camera: string; movimento_categoria?: string; duracao_s: string;
  entrada_movimento?: string; saida_movimento?: string; continuidade_direcao?: string; transicao_camera?: string; transicao_para_proximo: string; som_ambiente?: string; setup_luz?: string;
  tratamento_edicao?: string; ponto_de_corte?: string; alinhamento_emocional?: string; observacao: string
}
type BrollSequence = { nome: string; objetivo: string; tipo_broll?: string; eixo_horizontal?: string; eixo_vertical?: string; shots: BrollSequenceShot[] }
type BrollGrid = { tipos?: string[]; eixos?: string[]; criterios?: string[] }
type BrollGrammar = { cobertura_minima?: string[]; alcas_de_transicao?: string[]; tratamentos_edicao?: string[]; movimentos_camera?: string[]; pares_movimento_transicao?: string[]; broll_grid_profissional?: BrollGrid; pergunta_de_grid?: string; pergunta_de_qualidade?: string; pergunta_de_edicao?: string; pergunta_de_movimento?: string }
type BrollStrategy = { tipo_broll?: string; eixo_horizontal?: string; eixo_vertical?: string; pico_emocional?: string; subtexto?: string; decisao_de_poder?: string }
type PlanoBroll = { metodo?: { etapas?: string[]; guardrails?: string[]; gramatica_visual?: BrollGrammar }; gramatica_visual?: BrollGrammar; estrategia_edicao?: BrollStrategy; objetos: BrollObject[]; sequencias: BrollSequence[]; checklist: string[] }
type Suggest = {
  tema: string
  coringa: { fotos: Shot[]; videos: Shot[] }
  do_tema: { fotos: Shot[]; videos: Shot[] }
  plano_broll?: PlanoBroll
  roteiro_filmagem?: { objetos_acoes: string[]; sequencias: string[]; checklist: string[] }
  biblioteca_total: number
}
type Item = { file: string; kind: string; tags: string; theme: string; note: string; url: string; thumb: string | null }

function ShotList({ title, shots }: { title: string; shots: Shot[] }) {
  if (!shots?.length) return null
  return (
    <div style={{ marginBottom: 12 }}>
      <p className="eyebrow small" style={{ margin: '0 0 6px' }}>{title}</p>
      <ul style={{ margin: 0, paddingLeft: 18, display: 'grid', gap: 4 }}>
        {shots.map((s, i) => (
          <li key={i} className="small" style={{ lineHeight: 1.35 }}>
            {s.na_biblioteca ? '✅ ' : '🎬 '}<span className={s.na_biblioteca ? 'muted' : ''}>{s.shot}</span>
            {s.na_biblioteca ? <span className="muted small"> (já tem)</span> : null}
          </li>
        ))}
      </ul>
    </div>
  )
}

function PlanoBrollView({ plano }: { plano?: PlanoBroll }) {
  if (!plano) return null
  return (
    <div className="card" style={{ marginTop: 12 }}>
      <div className="formHeader"><h3>🎥 Roteiro de filmagem B-roll: objetos → ações → sequências</h3></div>
      {plano.metodo?.etapas?.length ? (
        <div style={{ marginBottom: 12 }}>
          <p className="eyebrow small" style={{ margin: '0 0 6px' }}>Método aplicado</p>
          <ol className="muted small" style={{ margin: 0, paddingLeft: 18, lineHeight: 1.45 }}>
            {plano.metodo.etapas.map((e, i) => <li key={i}>{e}</li>)}
          </ol>
        </div>
      ) : null}
      {(plano.gramatica_visual || plano.metodo?.gramatica_visual) ? (
        <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(220px,1fr))', gap: 10, marginBottom: 12 }}>
          <div className="card" style={{ padding: 10, margin: 0 }}>
            <p className="eyebrow small" style={{ margin: '0 0 6px' }}>Cobertura mínima</p>
            <ul className="muted small" style={{ margin: 0, paddingLeft: 18, lineHeight: 1.4 }}>
              {(plano.gramatica_visual?.cobertura_minima || plano.metodo?.gramatica_visual?.cobertura_minima || []).map((x, i) => <li key={i}>{x}</li>)}
            </ul>
          </div>
          <div className="card" style={{ padding: 10, margin: 0 }}>
            <p className="eyebrow small" style={{ margin: '0 0 6px' }}>Alças de transição</p>
            <ul className="muted small" style={{ margin: 0, paddingLeft: 18, lineHeight: 1.4 }}>
              {(plano.gramatica_visual?.alcas_de_transicao || plano.metodo?.gramatica_visual?.alcas_de_transicao || []).map((x, i) => <li key={i}>{x}</li>)}
            </ul>
          </div>
          <div className="card" style={{ padding: 10, margin: 0 }}>
            <p className="eyebrow small" style={{ margin: '0 0 6px' }}>Tratamento de edição</p>
            <ul className="muted small" style={{ margin: 0, paddingLeft: 18, lineHeight: 1.4 }}>
              {(plano.gramatica_visual?.tratamentos_edicao || plano.metodo?.gramatica_visual?.tratamentos_edicao || []).map((x, i) => <li key={i}>{x}</li>)}
            </ul>
          </div>
          <div className="card" style={{ padding: 10, margin: 0 }}>
            <p className="eyebrow small" style={{ margin: '0 0 6px' }}>Movimentos de câmera</p>
            <ul className="muted small" style={{ margin: 0, paddingLeft: 18, lineHeight: 1.4 }}>
              {(plano.gramatica_visual?.movimentos_camera || plano.metodo?.gramatica_visual?.movimentos_camera || []).map((x, i) => <li key={i}>{x}</li>)}
            </ul>
          </div>
          <div className="card" style={{ padding: 10, margin: 0 }}>
            <p className="eyebrow small" style={{ margin: '0 0 6px' }}>Movimento → transição</p>
            <ul className="muted small" style={{ margin: 0, paddingLeft: 18, lineHeight: 1.4 }}>
              {(plano.gramatica_visual?.pares_movimento_transicao || plano.metodo?.gramatica_visual?.pares_movimento_transicao || []).map((x, i) => <li key={i}>{x}</li>)}
            </ul>
          </div>
          <div className="card" style={{ padding: 10, margin: 0 }}>
            <p className="eyebrow small" style={{ margin: '0 0 6px' }}>Grid profissional B-roll</p>
            <ul className="muted small" style={{ margin: 0, paddingLeft: 18, lineHeight: 1.4 }}>
              {(plano.gramatica_visual?.broll_grid_profissional?.tipos || plano.metodo?.gramatica_visual?.broll_grid_profissional?.tipos || []).map((x, i) => <li key={`t-${i}`}>{x}</li>)}
              {(plano.gramatica_visual?.broll_grid_profissional?.eixos || plano.metodo?.gramatica_visual?.broll_grid_profissional?.eixos || []).map((x, i) => <li key={`e-${i}`}>{x}</li>)}
            </ul>
          </div>
        </div>
      ) : null}
      {plano.estrategia_edicao ? (
        <div className="card" style={{ padding: 10, margin: '0 0 12px' }}>
          <p className="eyebrow small" style={{ margin: '0 0 6px' }}>Estratégia de edição validada</p>
          <p className="muted small" style={{ margin: 0, lineHeight: 1.45 }}>
            Tipo: {plano.estrategia_edicao.tipo_broll || 'n/d'} · H: {plano.estrategia_edicao.eixo_horizontal || 'n/d'} · V: {plano.estrategia_edicao.eixo_vertical || 'n/d'}<br />
            Pico emocional: {plano.estrategia_edicao.pico_emocional || 'n/d'} · Subtexto: {plano.estrategia_edicao.subtexto || 'n/d'} · Decisão de poder: {plano.estrategia_edicao.decisao_de_poder || 'n/d'}
          </p>
        </div>
      ) : null}
      <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(240px,1fr))', gap: 12 }}>
        <div>
          <p className="eyebrow small" style={{ margin: '0 0 6px' }}>1. Objetos e ações possíveis</p>
          <div style={{ display: 'grid', gap: 8 }}>
            {plano.objetos?.map((o, i) => (
              <div key={i} className="card" style={{ padding: 10, margin: 0 }}>
                <strong>{o.na_biblioteca ? '✅ ' : '🎬 '}{o.objeto}</strong>
                <p className="muted small" style={{ margin: '4px 0' }}>{o.categoria} · {o.proposito_visual}</p>
                <ul className="small" style={{ margin: 0, paddingLeft: 18, lineHeight: 1.4 }}>
                  {o.acoes?.map((a, j) => <li key={j}>{a.acao}: {a.shot} <span className="muted">→ {a.transicao}{a.som_ambiente ? ` · som: ${a.som_ambiente}` : ''}</span></li>)}
                </ul>
              </div>
            ))}
          </div>
        </div>
        <div>
          <p className="eyebrow small" style={{ margin: '0 0 6px' }}>2. Sequências de filmagem</p>
          <div style={{ display: 'grid', gap: 8 }}>
            {plano.sequencias?.map((seq, i) => (
              <div key={i} className="card" style={{ padding: 10, margin: 0 }}>
                <strong>{seq.nome}</strong>
                <p className="muted small" style={{ margin: '4px 0' }}>{seq.objetivo}</p>
                {(seq.tipo_broll || seq.eixo_horizontal || seq.eixo_vertical) ? <p className="muted small" style={{ margin: '4px 0' }}>Tipo: {seq.tipo_broll || 'n/d'} · H: {seq.eixo_horizontal || 'n/d'} · V: {seq.eixo_vertical || 'n/d'}</p> : null}
                <ol className="small" style={{ margin: 0, paddingLeft: 18, lineHeight: 1.4 }}>
                  {seq.shots?.map((sh, j) => (
                    <li key={j}>
                      <strong>{sh.funcao_narrativa || sh.objeto}</strong> — {sh.objeto}: {sh.acao}; {sh.enquadramento}; {sh.movimento_camera}; {sh.duracao_s}s.
                      <span className="muted"> {sh.alinhamento_emocional ? `Emoção: ${sh.alinhamento_emocional} · ` : ''}Movimento: {sh.movimento_categoria || sh.movimento_camera || 'n/d'} · Entra: {sh.entrada_movimento || 'n/d'} · Sai: {sh.saida_movimento || 'n/d'}{sh.continuidade_direcao ? ` · Direção: ${sh.continuidade_direcao}` : ''}{sh.transicao_camera ? ` · Transição-câmera: ${sh.transicao_camera}` : ''} · Transição: {sh.transicao_para_proximo}{sh.som_ambiente ? ` · Som: ${sh.som_ambiente}` : ''}{sh.setup_luz ? ` · Luz: ${sh.setup_luz}` : ''}{sh.tratamento_edicao ? ` · Edição: ${sh.tratamento_edicao}` : ''}{sh.ponto_de_corte ? ` · Corte: ${sh.ponto_de_corte}` : ''}</span>
                    </li>
                  ))}
                </ol>
              </div>
            ))}
          </div>
        </div>
      </div>
      {plano.checklist?.length ? (
        <div style={{ marginTop: 12 }}>
          <p className="eyebrow small" style={{ margin: '0 0 6px' }}>Checklist de gravação</p>
          <ul className="muted small" style={{ margin: 0, paddingLeft: 18, lineHeight: 1.45 }}>
            {plano.checklist.map((c, i) => <li key={i}>{c}</li>)}
          </ul>
        </div>
      ) : null}
    </div>
  )
}

export default function BrollPage() {
  const [items, setItems] = useState<Item[]>([])
  const [tema, setTema] = useState('')
  const [sug, setSug] = useState<Suggest | null>(null)
  const [sugLoading, setSugLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [tags, setTags] = useState('')
  const [utheme, setUtheme] = useState('')
  const [msg, setMsg] = useState('')

  const load = useCallback(async () => {
    try {
      const r = await fetch(`${api}/stories/broll`, { cache: 'no-store' })
      const d = await r.json()
      setItems(d.items || [])
    } catch { /* */ }
  }, [])
  useEffect(() => { load() }, [load])

  async function sugerir() {
    setSugLoading(true); setSug(null)
    try {
      const r = await fetch(`${api}/stories/broll/suggest?tema=${encodeURIComponent(tema)}`, { cache: 'no-store' })
      setSug(await r.json())
    } catch { /* */ }
    setSugLoading(false)
  }

  async function onUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0]; e.target.value = ''
    if (!f) return
    setUploading(true); setMsg('')
    const fd = new FormData()
    fd.append('file', f); fd.append('tags', tags); fd.append('theme', utheme)
    try {
      const r = await fetch(`${api}/stories/broll/upload`, { method: 'POST', body: fd })
      const d = await r.json()
      if (d.ok) { setMsg(`✓ ${d.kind} adicionado: ${d.file}`); setTags(''); await load() }
      else setMsg(`✕ ${d.detail || 'falha no upload'}`)
    } catch { setMsg('✕ falha de rede') }
    setUploading(false)
  }

  async function apagar(file: string) {
    if (!confirm(`Remover "${file}" da biblioteca?`)) return
    try { await fetch(`${api}/stories/broll/${file}`, { method: 'DELETE' }); await load() } catch { /* */ }
  }

  return (
    <div className="section">
      <header className="pageHeader">
        <p className="eyebrow">Stories & Reels</p>
        <h2 className="pageTitle">Biblioteca de b-roll</h2>
        <p className="muted">Fotos e vídeos curtos que a Dra grava e guarda aqui — usados na geração de <strong>Stories e Reels</strong>. Peça uma lista de gravação pelo tema do dia/semana.</p>
      </header>

      {/* Sugestão por tema */}
      <article className="formCard">
        <div className="formHeader"><h3>Sugerir gravações (por tema)</h3></div>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          <input className="input" style={{ flex: 1, minWidth: 220 }} placeholder="Tema do dia/semana (ex.: sono, cortisol e menopausa)"
            value={tema} onChange={(e) => setTema(e.target.value)} />
          <button className="primaryButton" onClick={sugerir} disabled={sugLoading} style={{ cursor: sugLoading ? 'wait' : 'pointer' }}>
            {sugLoading ? 'Pensando…' : 'Sugerir lista de gravação'}
          </button>
        </div>
        {sug ? (
          <div className="grid" style={{ gridTemplateColumns: '1fr 1fr', marginTop: 12, gap: 16 }}>
            <div className="card" style={{ margin: 0 }}>
              <h4 style={{ marginTop: 0 }}>🎯 Do tema</h4>
              <ShotList title="Fotos" shots={sug.do_tema.fotos} />
              <ShotList title="Vídeos" shots={sug.do_tema.videos} />
              {!sug.do_tema.fotos.length && !sug.do_tema.videos.length ? <p className="muted small">Informe um tema e gere a lista.</p> : null}
            </div>
            <div className="card" style={{ margin: 0 }}>
              <h4 style={{ marginTop: 0 }}>♾️ Coringa (evergreen)</h4>
              <ShotList title="Fotos" shots={sug.coringa.fotos} />
              <ShotList title="Vídeos" shots={sug.coringa.videos} />
            </div>
          </div>
        ) : null}
        {sug?.plano_broll ? <PlanoBrollView plano={sug.plano_broll} /> : null}
      </article>

      {/* Upload */}
      <article className="formCard">
        <div className="formHeader"><h3>Carregar foto/vídeo</h3></div>
        <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(180px,1fr))' }}>
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

      {/* Biblioteca */}
      <div className="sectionHeaderInline">
        <h3 className="sectionTitle">Biblioteca</h3>
        <span className="badge">{items.length} itens</span>
      </div>
      {items.length === 0 ? (
        <div className="empty">Nenhum b-roll ainda. Grave os coringas acima e carregue aqui.</div>
      ) : (
        <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(160px,1fr))' }}>
          {items.map((p) => (
            <figure key={p.file} className="card" style={{ padding: 8, margin: 0, display: 'grid', gap: 6 }}>
              {p.kind === 'foto' ? (
                <a href={`${api}${p.url}`} target="_blank" rel="noreferrer">
                  <img src={`${api}${p.thumb}`} alt={p.tags || p.file} style={{ width: '100%', aspectRatio: '9/16', objectFit: 'cover', borderRadius: 10, background: '#000' }} />
                </a>
              ) : (
                <video src={`${api}${p.url}`} controls preload="metadata" style={{ width: '100%', aspectRatio: '9/16', objectFit: 'cover', borderRadius: 10, background: '#000' }} />
              )}
              <figcaption className="muted small" style={{ lineHeight: 1.3 }}>
                <span className="badge" style={{ fontSize: '.6rem' }}>{p.kind === 'video' ? '🎬 vídeo' : '📸 foto'}</span>{' '}
                {p.theme || p.tags || ''}
              </figcaption>
              <button className="secondaryLink" style={{ width: '100%', minHeight: 32, fontSize: '.72rem' }} onClick={() => apagar(p.file)}>Remover</button>
            </figure>
          ))}
        </div>
      )}
    </div>
  )
}
