'use client'

import { useEffect, useMemo, useState } from 'react'

const api = process.env.NEXT_PUBLIC_API_BASE_URL || '/api'
type R = {
  codigo: string; origem: string | null; objetivo: string | null; classe_ivs: string | null
  mecanismo: string | null; hook_base: string | null; tese_central: string | null
  objecao_principal: string | null; adaptacao_ivs: string | null; status: string
  referencias?: { url: string; tipo: string }[] | null
  ideia_prompt?: string | null; plataforma?: string | null; fonte_raw?: string | null
}

export default function Page() {
  const [items, setItems] = useState<R[]>([])
  const [classes, setClasses] = useState<{ classe_ivs: string; n: number }[]>([])
  const [q, setQ] = useState('')
  const [cls, setCls] = useState('todas')
  const [ref, setRef] = useState('')
  const [handle, setHandle] = useState('')
  const [erLoading, setErLoading] = useState(false)
  const [analise, setAnalise] = useState<{ por_que_viralizou?: string; tema_dominante?: string; scripts?: unknown[] } | null>(null)
  const [erMsg, setErMsg] = useState<string | null>(null)

  function load() {
    fetch(`${api}/generation/roteiros?tenant_slug=demo`, { cache: 'no-store' })
      .then((r) => r.json())
      .then((d) => { setItems(d.items || []); setClasses(d.classes || []) })
      .catch(() => {})
  }
  useEffect(() => { load() }, [])

  async function rodarEngReversa() {
    if (!ref.trim()) return
    setErLoading(true); setErMsg(null); setAnalise(null)
    try {
      const r = await fetch(`${api}/generation/engenharia-reversa`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tenant_slug: 'demo', handle: handle || null, referencia: ref }),
      })
      if (!r.ok) throw new Error()
      const d = await r.json()
      setAnalise(d.analise || null)
      setErMsg(`${d.saved} roteiro(s) adaptado(s) adicionado(s) ao banco.`)
      setRef(''); load()
    } catch { setErMsg('Não consegui rodar a análise agora.') } finally { setErLoading(false) }
  }

  const vis = useMemo(() => items.filter((r) => {
    if (cls !== 'todas' && r.classe_ivs !== cls) return false
    if (!q) return true
    const blob = `${r.hook_base} ${r.tese_central} ${r.adaptacao_ivs} ${r.objetivo}`.toLowerCase()
    return blob.includes(q.toLowerCase())
  }), [items, q, cls])

  return (
    <div className="dashboardRoot">
      <header className="pageHeader heroHeader">
        <div>
          <p className="eyebrow">Motor A · etapa 4</p>
          <h2 className="pageTitle">Banco de roteiros</h2>
          <p className="muted">
            Nosso bunker IVS: base adaptada com hook, tese, mecanismo e objeção prontos para alimentar criação, mídia e reaproveitamento.
          </p>
        </div>
      </header>

      <section className="metricGrid">
        <article className="metricCard">
          <span className="metricLabel">Adaptados</span>
          <strong className="metricValue">{items.length}</strong>
          <p className="muted small" style={{ margin: 0 }}>roteiros já prontos para virar peça</p>
        </article>
        <article className="metricCard">
          <span className="metricLabel">Classes IVS</span>
          <strong className="metricValue">{classes.length}</strong>
          <p className="muted small" style={{ margin: 0 }}>linhas narrativas organizadas no bunker</p>
        </article>
      </section>

      <section className="section">
        <article className="featurePanel featurePanelDark">
          <div className="sectionHeaderInline">
            <div>
              <p className="eyebrow">Engenharia reversa</p>
              <h3 className="sectionTitle">Reel ou anúncio campeão → novos roteiros IVS</h3>
            </div>
            <span className="muted small">cola a referência e o motor adapta para a voz da Dra.</span>
          </div>
          <p className="muted small" style={{ margin: 0 }}>Sai por que viralizou, tema dominante e novos scripts já prontos para entrar no banco.</p>
          <div className="grid" style={{ gridTemplateColumns: '220px minmax(0,1fr)', alignItems: 'start' }}>
            <input className="input" placeholder="@perfil (opcional)" value={handle} onChange={(e) => setHandle(e.target.value)} />
            <textarea className="textarea" placeholder="Cole aqui legenda, gancho ou descrição do reel/anúncio campeão…" value={ref} onChange={(e) => setRef(e.target.value)} style={{ minHeight: 120 }} />
          </div>
          <div style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap' }}>
            <button className="primaryButton" onClick={rodarEngReversa} disabled={erLoading || !ref.trim()}>{erLoading ? 'Analisando…' : 'Analisar e gerar roteiros'}</button>
            {erMsg ? <span className="successText">{erMsg}</span> : null}
          </div>
          {analise ? (
            <div className="resultBox">
              <p style={{ margin: 0 }}><strong>Por que viralizou:</strong> {analise.por_que_viralizou}</p>
              <p style={{ margin: '8px 0 0' }}><strong>Tema dominante:</strong> {analise.tema_dominante} · {(analise.scripts || []).length} scripts gerados</p>
            </div>
          ) : null}
        </article>
      </section>

      <section className="section">
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
          <input className="input" placeholder="Buscar por hook, tese, tema…" value={q} onChange={(e) => setQ(e.target.value)} style={{ maxWidth: 320 }} />
          <button className={cls === 'todas' ? 'primaryButton' : 'secondaryLink'} style={{ minHeight: 38, padding: '0 14px' }} onClick={() => setCls('todas')}>todas ({items.length})</button>
          {classes.map((c) => (
            <button key={c.classe_ivs} className={cls === c.classe_ivs ? 'primaryButton' : 'secondaryLink'} style={{ minHeight: 38, padding: '0 14px' }} onClick={() => setCls(c.classe_ivs)}>{c.classe_ivs} ({c.n})</button>
          ))}
        </div>

        <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit,minmax(320px,1fr))' }}>
          {vis.map((r) => (
            <article key={r.codigo} className="card" style={{ display: 'grid', gap: 14 }}>
              <div className="rowTop">
                <span className="badge badgeDark">{r.codigo}</span>
                {r.classe_ivs ? <span className="badge">{r.classe_ivs}</span> : null}
              </div>
              <div style={{ display: 'grid', gap: 8 }}>
                <strong style={{ fontSize: 15, lineHeight: 1.45 }}>{r.hook_base || r.tese_central || '—'}</strong>
                {r.tese_central ? <p className="muted small" style={{ margin: 0 }}>{r.tese_central}</p> : null}
                {r.objecao_principal ? <p className="muted small" style={{ margin: 0 }}><em>Objeção:</em> {r.objecao_principal}</p> : null}
              </div>
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                {r.mecanismo ? <span className="badge">{r.mecanismo}</span> : null}
                {r.plataforma ? <span className="badge badgeDark">{r.plataforma}</span> : null}
                {(r.referencias || []).map((refItem) => (
                  <a key={refItem.url} href={refItem.url} target="_blank" rel="noreferrer" className="badge badgeDark">▶ {refItem.tipo}</a>
                ))}
              </div>
              {r.ideia_prompt ? <div className="resultBox"><strong>Prompt-base:</strong> {r.ideia_prompt.slice(0, 220)}</div> : null}
              {r.fonte_raw ? (
                <details>
                  <summary className="muted small" style={{ cursor: 'pointer' }}>ver conteúdo original</summary>
                  <pre style={{ whiteSpace: 'pre-wrap', fontSize: 11, maxHeight: 240, overflow: 'auto', marginTop: 8, opacity: 0.88 }}>{r.fonte_raw}</pre>
                </details>
              ) : null}
            </article>
          ))}
          {vis.length === 0 ? <div className="empty">Nenhum roteiro encontrado para esse filtro.</div> : null}
        </div>
      </section>
    </div>
  )
}
