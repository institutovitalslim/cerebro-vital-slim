'use client'

import { FormEvent, useEffect, useState } from 'react'

import { StoryboardPanel } from './storyboard'

const api = process.env.NEXT_PUBLIC_API_BASE_URL || '/api'

export type Creative = {
  id: string
  format: string
  destino: string | null
  network: string
  title: string | null
  caption: string | null
  hashtags: string[] | null
  angulo_nome: string | null
  angulo_ivs?: string | null
  hook_tipo?: string | null
  objecao_alvo?: string | null
  quebra_objecao?: string | null
  visual_tipo?: string | null
  cta_tipo?: string | null
  destino_criativo?: string | null
  hypothesis?: string | null
  status: string
  quality_score: number | null
  assets: string[]
  created_at: string
  feedback?: string | null
  reel_status?: string | null
  reel_url?: string | null
}

const FORMATOS = ['carrossel', 'reels', 'stories', 'estatico']
const OBJETIVOS = ['atração', 'identificação', 'educação', 'conversão', 'desejo', 'retenção']
const ANGULOS_META: [string, string][] = [
  ['baseline', '1 · Baseline / oferta clara'],
  ['culpa', '2 · Objeção: culpa / fracasso'],
  ['so_dieta', "3 · Objeção: 'só mais uma dieta'"],
  ['preco', '4 · Barreira: preço / valor'],
  ['metodo', '5 · Método / autoridade'],
]
const HOOKS = ['identificacao', 'mecanismo', 'contraste', 'mito', 'pergunta_direta']
const VISUAIS = ['dra_camera', 'broll_rotina', 'prova_metodo', 'texto_premium']
const CTAS = ['salvar_compartilhar', 'pre_avaliacao', 'whatsapp_qualificado', 'agendamento']
const OBJECOES = ['ja_tentei_de_tudo', 'so_mais_uma_dieta', 'preco_valor', 'sem_tempo', 'hormonios_metabolismo']
export const STATUS_LABEL: Record<string, string> = {
  gerado: 'Gerando arte…',
  renderizado: 'Pronto p/ revisar',
  aprovado: 'Aprovado ✓',
  publicado: 'Publicado · métrica pendente',
  render_erro: 'Erro no render',
  pausado_formato: 'Pausado',
  ajustes_solicitados: 'Ajustes solicitados ✎',
}
export const is45 = (f: string) => f === 'carrossel' || f === 'estatico'

async function listar(format?: string): Promise<Creative[]> {
  try {
    const qs = new URLSearchParams({ tenant_slug: 'demo', limit: '60' })
    if (format) qs.set('format', format)
    const r = await fetch(`${api}/generation/creatives?${qs.toString()}`, { cache: 'no-store' })
    const d = await r.json()
    return d.items || []
  } catch {
    return []
  }
}

export function FormGerar({ defaultFormato = 'carrossel', lockFormato = false }: { defaultFormato?: string; lockFormato?: boolean } = {}) {
  const [modo, setModo] = useState<'single' | 'matrix'>('single')
  const [formato, setFormato] = useState(defaultFormato)
  const [objetivo, setObjetivo] = useState('educação')
  const [destino, setDestino] = useState('feed')
  const [angulo, setAngulo] = useState('baseline')
  const [hookTipo, setHookTipo] = useState('identificacao')
  const [objecaoAlvo, setObjecaoAlvo] = useState('ja_tentei_de_tudo')
  const [visualTipo, setVisualTipo] = useState('dra_camera')
  const [ctaTipo, setCtaTipo] = useState('pre_avaliacao')
  const [matrixName, setMatrixName] = useState('Ciclo modular IVS')
  const [matrixAngulos, setMatrixAngulos] = useState('culpa,so_dieta,metodo')
  const [matrixHooks, setMatrixHooks] = useState('identificacao,mecanismo,contraste')
  const [matrixObjecoes, setMatrixObjecoes] = useState('ja_tentei_de_tudo')
  const [matrixCtas, setMatrixCtas] = useState('pre_avaliacao,whatsapp_qualificado')
  const [matrixVisuais, setMatrixVisuais] = useState('dra_camera,broll_rotina')
  const [tema, setTema] = useState('')
  const [briefing, setBriefing] = useState<{ thesis: string; hook: string; originTag: string; source: string; pillar: string; audienceStage: string; objective: string } | null>(null)
  const [loading, setLoading] = useState(false)
  const [msg, setMsg] = useState<string | null>(null)
  const [recent, setRecent] = useState<Creative[]>([])

  useEffect(() => {
    if (typeof window === 'undefined') return
    const qs = new URLSearchParams(window.location.search)
    if (qs.get('source') !== 'weekly-sprint') return
    const thesis = qs.get('thesis') || ''
    const hook = qs.get('hook') || ''
    const originTag = qs.get('origin_tag') || ''
    const source = qs.get('source') || ''
    const objective = qs.get('objective') || ''
    const pillar = qs.get('pillar') || ''
    const audienceStage = qs.get('audience_stage') || ''
    const nextTema = [thesis, hook ? `Hook: ${hook}` : '', originTag ? `Origem: ${originTag}` : ''].filter(Boolean).join('\n')
    if (nextTema) setTema(nextTema)
    if (objective === 'captacao_qualificada') setObjetivo('conversão')
    if (objective === 'educacao_de_mercado') setObjetivo('educação')
    if (objective === 'prova_e_metodo') setObjetivo('desejo')
    if (hook.toLowerCase().includes('mito') || hook.toLowerCase().includes('mentira')) setHookTipo('mito')
    if (hook.toLowerCase().includes('?') || hook.toLowerCase().includes('por que')) setHookTipo('pergunta_direta')
    if (originTag || thesis || hook) setBriefing({ thesis, hook, originTag, source, pillar, audienceStage, objective })
  }, [])

  async function load() {
    setRecent((await listar(lockFormato ? defaultFormato : undefined)).slice(0, 8))
  }
  useEffect(() => {
    load()
    const t = setInterval(load, 5000)
    return () => clearInterval(t)
  }, [])

  async function gerar(e: FormEvent) {
    e.preventDefault()
    setLoading(true)
    setMsg(null)
    try {
      const csv = (s: string) => s.split(',').map((x) => x.trim()).filter(Boolean)
      if (modo === 'matrix') {
        const angulos = csv(matrixAngulos); const hooks = csv(matrixHooks); const objecoes = csv(matrixObjecoes); const ctas = csv(matrixCtas); const visuais = csv(matrixVisuais)
        const total = angulos.length * hooks.length * objecoes.length * ctas.length * visuais.length
        if (total > 36) throw new Error('matrix_limit')
        const r = await fetch(`${api}/generation/matrix`, {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ tenant_slug: 'demo', name: matrixName, formato, objetivo, rede: 'instagram', destino, tema: tema || null, angulos, hooks, objecoes, ctas, visuais }),
        })
        if (!r.ok) throw new Error()
        const d = await r.json()
        setMsg(`Matriz criada: ${d.created}/${d.requested} variações. Acompanhe no Banco de criativos.`)
        load(); return
      }
      const body: Record<string, unknown> = {
        tenant_slug: 'demo', formato, objetivo, rede: 'instagram', tema: tema || null,
        hook_tipo: hookTipo, objecao_alvo: objecaoAlvo, visual_tipo: visualTipo, cta_tipo: ctaTipo,
      }
      if (briefing) {
        body.source = briefing.source
        body.thesis = briefing.thesis
        body.pillar = briefing.pillar
        body.audience_stage = briefing.audienceStage
        body.origin_tag = briefing.originTag
        body.hook = briefing.hook
      }
      if (formato === 'carrossel') {
        body.destino = destino
        if (destino === 'meta_ads') body.angulo = angulo
      }
      const r = await fetch(`${api}/generation/orchestrate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      if (!r.ok) throw new Error()
      const d = await r.json()
      setMsg(`Peça gerada (score ${d.quality_score}). Renderizando… acompanhe no Banco de criativos.`)
      load()
    } catch {
      setMsg('Não consegui gerar agora. Confira se a matriz tem no máximo 36 variações e tente de novo.')
    } finally {
      setLoading(false)
    }
  }

  const countCsv = (s: string) => s.split(',').map((x) => x.trim()).filter(Boolean).length
  const matrixTotal = countCsv(matrixAngulos) * countCsv(matrixHooks) * countCsv(matrixObjecoes) * countCsv(matrixCtas) * countCsv(matrixVisuais)

  return (
    <section className="section grid" style={{ gridTemplateColumns: 'minmax(320px, 420px) minmax(0, 1fr)', gap: 24, alignItems: 'start' }}>
      <form className="formCard" onSubmit={gerar}>
        <div className="formHeader">
          <span className="badge">Etapa 5</span>
          <h3>Nova peça</h3>
          <p className="muted">Reels puxam atenção. Carrossel constrói autoridade. Modo matriz transforma criativo em segmentação.</p>
        </div>

        {briefing ? (
          <div className="resultBox briefingBox">
            <span className="metricLabel">Briefing herdado do Sprint Semanal</span>
            {briefing.thesis ? <p><strong>Tese:</strong> {briefing.thesis}</p> : null}
            {briefing.hook ? <p><strong>Hook:</strong> {briefing.hook}</p> : null}
            {briefing.originTag ? <p><strong>Origem:</strong> {briefing.originTag}</p> : null}
            <p className="muted small">Revise antes de gerar. Nada é publicado automaticamente.</p>
          </div>
        ) : null}

        <div className="resultBox briefingBox">
          <span className="metricLabel">Rodapé obrigatório de toda legenda</span>
          <p>Dra Daniely Freitas<br />Médica, Farmacêutica e Professora de Medicina<br />CRM-BA 27.588<br />(Este conteúdo tem caráter meramente educativo e não substitui uma consulta médica.)</p>
        </div>

        <label className="muted small">Modo</label>
        <select className="input" value={modo} onChange={(e) => setModo(e.target.value as 'single' | 'matrix')}>
          <option value="single">Peça única</option>
          <option value="matrix">Matriz de teste</option>
        </select>

        <label className="muted small">Formato</label>
        {lockFormato ? (
          <div className="resultBox"><strong>{formato}</strong><br /><span className="muted small">Formato travado para este módulo de produção.</span></div>
        ) : (
          <select className="input" value={formato} onChange={(e) => setFormato(e.target.value)}>
            {FORMATOS.map((f) => (
              <option key={f} value={f}>{f}</option>
            ))}
          </select>
        )}

        {formato === 'carrossel' ? (
          <>
            <label className="muted small">Destino do carrossel</label>
            <select className="input" value={destino} onChange={(e) => setDestino(e.target.value)}>
              <option value="feed">Feed — salvar/compartilhar + autoridade</option>
              <option value="meta_ads">Meta Ads — leads p/ agendamento</option>
            </select>

            {destino === 'meta_ads' ? (
              <>
                <label className="muted small">Conjunto / ângulo (estrutura 5×3)</label>
                <select className="input" value={angulo} onChange={(e) => setAngulo(e.target.value)}>
                  {ANGULOS_META.map(([k, l]) => (
                    <option key={k} value={k}>{l}</option>
                  ))}
                </select>
              </>
            ) : null}
          </>
        ) : null}

        <label className="muted small">Objetivo</label>
        <select className="input" value={objetivo} onChange={(e) => setObjetivo(e.target.value)}>
          {OBJETIVOS.map((o) => (
            <option key={o} value={o}>{o}</option>
          ))}
        </select>

        {modo === 'single' ? <div style={{ border: '1px solid rgba(186,155,96,.18)', borderRadius: 14, padding: 12, display: 'grid', gap: 10 }}>
          <div>
            <span className="badge badgeDark">Hipótese criativa</span>
            <p className="muted small" style={{ margin: '6px 0 0' }}>Campos usados para filtrar performance depois: hook, objeção, visual e CTA.</p>
          </div>
          <label className="muted small">Hook</label>
          <select className="input" value={hookTipo} onChange={(e) => setHookTipo(e.target.value)}>{HOOKS.map((h) => <option key={h} value={h}>{h}</option>)}</select>
          <label className="muted small">Objeção-alvo</label>
          <select className="input" value={objecaoAlvo} onChange={(e) => setObjecaoAlvo(e.target.value)}>{OBJECOES.map((o) => <option key={o} value={o}>{o}</option>)}</select>
          <label className="muted small">Visual</label>
          <select className="input" value={visualTipo} onChange={(e) => setVisualTipo(e.target.value)}>{VISUAIS.map((v) => <option key={v} value={v}>{v}</option>)}</select>
          <label className="muted small">CTA</label>
          <select className="input" value={ctaTipo} onChange={(e) => setCtaTipo(e.target.value)}>{CTAS.map((c) => <option key={c} value={c}>{c}</option>)}</select>
        </div> : (
          <div style={{ border: '1px solid rgba(186,155,96,.22)', borderRadius: 14, padding: 12, display: 'grid', gap: 10 }}>
            <div>
              <span className="badge badgeDark">Matriz modular</span>
              <p className="muted small" style={{ margin: '6px 0 0' }}>Use vírgulas para combinar variáveis. Limite inicial: 36 variações por ciclo.</p>
            </div>
            <input className="input" placeholder="Nome do ciclo" value={matrixName} onChange={(e) => setMatrixName(e.target.value)} />
            <label className="muted small">Ângulos</label>
            <input className="input" value={matrixAngulos} onChange={(e) => setMatrixAngulos(e.target.value)} />
            <label className="muted small">Hooks</label>
            <input className="input" value={matrixHooks} onChange={(e) => setMatrixHooks(e.target.value)} />
            <label className="muted small">Objeções</label>
            <input className="input" value={matrixObjecoes} onChange={(e) => setMatrixObjecoes(e.target.value)} />
            <label className="muted small">CTAs</label>
            <input className="input" value={matrixCtas} onChange={(e) => setMatrixCtas(e.target.value)} />
            <label className="muted small">Visuais</label>
            <input className="input" value={matrixVisuais} onChange={(e) => setMatrixVisuais(e.target.value)} />
            <div className="resultBox" style={{ borderColor: matrixTotal > 36 ? 'rgba(255,90,90,.45)' : 'rgba(186,155,96,.35)' }}>
              {countCsv(matrixAngulos)} ângulos × {countCsv(matrixHooks)} hooks × {countCsv(matrixObjecoes)} objeções × {countCsv(matrixCtas)} CTAs × {countCsv(matrixVisuais)} visuais = <strong>{matrixTotal}</strong> variações
              <p className="muted small" style={{ margin: '6px 0 0' }}>Sem promessa de resultado, prazo, cura ou emagrecimento garantido. Tudo segue para revisão humana.</p>
            </div>
          </div>
        )}

        <label className="muted small">Tema / briefing</label>
        <textarea className="textarea" placeholder="ex: tireoide lenta e queda de cabelo na mulher 45+" value={tema} onChange={(e) => setTema(e.target.value)} />

        <button className="primaryButton" disabled={loading || (modo === 'matrix' && matrixTotal > 36)}>{loading ? 'Gerando…' : modo === 'matrix' ? 'Gerar matriz' : 'Gerar peça'}</button>
        {msg ? <span className="successText">{msg}</span> : null}
      </form>

      <div className="section" style={{ gap: 14 }}>
        <div className="sectionHeaderInline">
          <div>
            <p className="eyebrow">Fila viva</p>
            <h3 className="sectionTitle">Últimas peças</h3>
          </div>
          <a className="secondaryLink" href="/banco-criativos">Ver banco completo</a>
        </div>

        <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit,minmax(180px,1fr))', gap: 14 }}>
          {recent.map((c) => (
            <a key={c.id} href="/banco-criativos" className="card" style={{ padding: 10, display: 'grid', gap: 10 }}>
              <div style={{ aspectRatio: is45(c.format) ? '4 / 5' : '9 / 16', background: 'linear-gradient(180deg,#17120d,#0f0b07)', borderRadius: 14, overflow: 'hidden', border: '1px solid rgba(186,155,96,0.12)' }}>
                {c.assets[0] ? (
                  <img src={`${api}${c.assets[0]}`} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                ) : (
                  <div className="muted small" style={{ display: 'grid', placeItems: 'center', height: '100%', padding: 14, textAlign: 'center' }}>{STATUS_LABEL[c.status] || c.status}</div>
                )}
              </div>
              <div style={{ display: 'grid', gap: 6 }}>
                <span className="badge badgeDark">{c.format}</span>
                <p className="muted small" style={{ margin: 0 }}>{STATUS_LABEL[c.status] || c.status}</p>
              </div>
            </a>
          ))}
          {recent.length === 0 ? <div className="empty">Nenhuma peça ainda.</div> : null}
        </div>
      </div>
    </section>
  )
}

export function Galeria() {
  const [items, setItems] = useState<Creative[]>([])
  const [filtro, setFiltro] = useState('todos')
  const [fAngulo, setFAngulo] = useState('todos')
  const [fHook, setFHook] = useState('todos')
  const [fObjecao, setFObjecao] = useState('todos')
  const [fVisual, setFVisual] = useState('todos')
  const [fCta, setFCta] = useState('todos')
  const [sel, setSel] = useState<Creative | null>(null)
  const [idx, setIdx] = useState(0)
  const [melhoria, setMelhoria] = useState('')
  const [slideFeedback, setSlideFeedback] = useState<Record<string, string>>({})
  const [regen, setRegen] = useState<string | null>(null)
  const [statusMsg, setStatusMsg] = useState<string | null>(null)

  async function load() {
    const its = await listar()
    setItems(its)
    setSel((cur) => (cur ? its.find((x) => x.id === cur.id) || cur : cur))
  }

  useEffect(() => {
    load()
    const t = setInterval(load, 5000)
    return () => clearInterval(t)
  }, [])

  async function aprovar(id: string) {
    const r = await fetch(`${api}/generation/creatives/${id}/approve`, { method: 'POST' })
    const d = await r.json().catch(() => ({}))
    setStatusMsg(d.calendar_entry ? 'Peça aprovada e enviada ao Calendário Editorial.' : 'Peça aprovada.')
    load()
  }

  function feedbackKey(id: string, slideIndex: number) {
    return `${id}:${slideIndex}`
  }

  function feedbackAtual(c: Creative) {
    const porSlide = c.assets
      .map((_, i) => ({ slide: i + 1, text: (slideFeedback[feedbackKey(c.id, i)] || '').trim() }))
      .filter((x) => x.text)
      .map((x) => `Slide ${x.slide}: ${x.text}`)
    const geral = melhoria.trim() ? [`Geral: ${melhoria.trim()}`] : []
    return [...porSlide, ...geral].join('\n')
  }

  async function solicitarMelhorias(id: string) {
    const creative = sel && sel.id === id ? sel : items.find((x) => x.id === id)
    const texto = creative ? feedbackAtual(creative) : melhoria.trim()
    if (!texto.trim()) return
    await fetch(`${api}/generation/creatives/${id}/feedback`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ texto }),
    })
    setRegen(id)
    try { await fetch(`${api}/generation/creatives/${id}/regerar`, { method: 'POST' }) } finally { setRegen(null) }
    setMelhoria('')
    setSlideFeedback((cur) => Object.fromEntries(Object.entries(cur).filter(([k]) => !k.startsWith(`${id}:`))))
    await load()
  }

  async function regerar(id: string) {
    setRegen(id)
    try { await fetch(`${api}/generation/creatives/${id}/regerar`, { method: 'POST' }) } catch { /* */ }
    setRegen(null)
    load()
  }

  function baixarTodos(c: Creative) {
    c.assets.forEach((a, i) => {
      const l = document.createElement('a')
      l.href = `${api}${a}`
      l.download = `${c.format}_${String(i + 1).padStart(2, '0')}.png`
      document.body.appendChild(l)
      l.click()
      l.remove()
    })
  }

  const unique = (key: keyof Creative) => Array.from(new Set(items.map((x) => x[key]).filter(Boolean) as string[])).sort()
  const vis = items.filter((c) => {
    if (!(filtro === 'todos' || (filtro === 'aprovados' ? c.status === 'aprovado' : c.format === filtro))) return false
    if (fAngulo !== 'todos' && c.angulo_ivs !== fAngulo) return false
    if (fHook !== 'todos' && c.hook_tipo !== fHook) return false
    if (fObjecao !== 'todos' && c.objecao_alvo !== fObjecao) return false
    if (fVisual !== 'todos' && c.visual_tipo !== fVisual) return false
    if (fCta !== 'todos' && c.cta_tipo !== fCta) return false
    return true
  })

  return (
    <>
      <section className="section">
        <div className="sectionHeaderInline">
          <div>
            <p className="eyebrow">Curadoria</p>
            <h3 className="sectionTitle">Biblioteca viva de criativos</h3>
          </div>
          <span className="muted small">{vis.length} peças · atualização automática</span>
        </div>

        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          {['todos', 'aprovados', 'carrossel', 'reels', 'stories', 'estatico'].map((f) => (
            <button key={f} className={f === filtro ? 'primaryButton' : 'secondaryLink'} style={{ minHeight: 38, padding: '0 14px' }} onClick={() => setFiltro(f)}>
              {f}
            </button>
          ))}
        </div>
        {statusMsg ? <span className="successText">{statusMsg}</span> : null}

        <div className="card" style={{ padding: 12, display: 'grid', gap: 10 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', gap: 10, alignItems: 'center', flexWrap: 'wrap' }}>
            <span className="badge badgeDark">Filtros de hipótese</span>
            <button className="secondaryLink" onClick={() => { setFAngulo('todos'); setFHook('todos'); setFObjecao('todos'); setFVisual('todos'); setFCta('todos') }}>Limpar variáveis</button>
          </div>
          <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit,minmax(160px,1fr))', gap: 8 }}>
            <select className="input" value={fAngulo} onChange={(e) => setFAngulo(e.target.value)}><option value="todos">Todos ângulos</option>{unique('angulo_ivs').map((v) => <option key={v} value={v}>{v}</option>)}</select>
            <select className="input" value={fHook} onChange={(e) => setFHook(e.target.value)}><option value="todos">Todos hooks</option>{unique('hook_tipo').map((v) => <option key={v} value={v}>{v}</option>)}</select>
            <select className="input" value={fObjecao} onChange={(e) => setFObjecao(e.target.value)}><option value="todos">Todas objeções</option>{unique('objecao_alvo').map((v) => <option key={v} value={v}>{v}</option>)}</select>
            <select className="input" value={fVisual} onChange={(e) => setFVisual(e.target.value)}><option value="todos">Todos visuais</option>{unique('visual_tipo').map((v) => <option key={v} value={v}>{v}</option>)}</select>
            <select className="input" value={fCta} onChange={(e) => setFCta(e.target.value)}><option value="todos">Todos CTAs</option>{unique('cta_tipo').map((v) => <option key={v} value={v}>{v}</option>)}</select>
          </div>
        </div>

        {vis.length === 0 ? <div className="empty">Nenhuma peça aqui ainda. Gere em “Criação de criativos”.</div> : null}

        <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit,minmax(230px,1fr))', gap: 18 }}>
          {vis.map((c) => (
            <article key={c.id} className="card" style={{ padding: 12, display: 'grid', gap: 12 }}>
              <div
                onClick={() => {
                  setSel(c)
                  setIdx(0)
                }}
                title="Revisar todos os slides"
                style={{
                  position: 'relative',
                  cursor: 'pointer',
                  aspectRatio: is45(c.format) ? '4 / 5' : '9 / 16',
                  background: 'linear-gradient(180deg,#17120d,#0f0b07)',
                  borderRadius: 16,
                  overflow: 'hidden',
                  border: '1px solid rgba(186,155,96,0.12)',
                }}
              >
                {c.format === 'reels' && c.reel_url ? (
                  <video src={`${api}${c.reel_url}`} muted playsInline preload="metadata" poster={c.assets[0] ? `${api}${c.assets[0]}` : undefined} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                ) : c.assets[0] ? (
                  <img src={`${api}${c.assets[0]}`} alt={c.title || ''} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                ) : (
                  <div className="muted small" style={{ display: 'grid', placeItems: 'center', height: '100%', textAlign: 'center', padding: 12 }}>{STATUS_LABEL[c.status] || c.status}</div>
                )}
                {c.format === 'reels' ? <span className="badge badgeDark" style={{ position: 'absolute', bottom: 10, left: 10 }}>{c.reel_url ? '▶ reel' : '🎬 storyboard'}</span> : null}
                {c.assets.length > 1 ? <span className="badge badgeDark" style={{ position: 'absolute', top: 10, right: 10 }}>{c.assets.length} slides</span> : null}
                {c.status === 'aprovado' ? <span className="badge" style={{ position: 'absolute', top: 10, left: 10 }}>Aprovado</span> : null}
              </div>

              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                <span className="badge">{c.format}</span>
                {c.destino === 'meta_ads' ? <span className="badge badgeDark">Meta Ads</span> : null}
                {c.angulo_nome ? <span className="badge badgeDark">{c.angulo_nome}</span> : null}
                {c.objecao_alvo ? <span className="badge badgeDark">Obj: {c.objecao_alvo}</span> : null}
                {c.hook_tipo ? <span className="badge badgeDark">Hook: {c.hook_tipo}</span> : null}
                {c.visual_tipo ? <span className="badge badgeDark">Visual: {c.visual_tipo}</span> : null}
                {c.cta_tipo ? <span className="badge badgeDark">CTA: {c.cta_tipo}</span> : null}
                {c.quality_score != null ? <span className="badge">score {c.quality_score}</span> : null}
              </div>

              <div style={{ display: 'grid', gap: 6 }}>
                <p style={{ margin: 0, fontWeight: 600, fontSize: 14, lineHeight: 1.45 }}>{(c.title || '').replace(/\*/g, '') || '—'}</p>
                <p className="muted small" style={{ margin: 0 }}>{STATUS_LABEL[c.status] || c.status}</p>
              </div>

              <button className="primaryButton" style={{ width: '100%' }} onClick={() => { setSel(c); setIdx(0) }} disabled={c.assets.length === 0}>
                Revisar e aprovar
              </button>
            </article>
          ))}
        </div>
      </section>

      {sel ? (
        <div onClick={() => setSel(null)} style={{ position: 'fixed', inset: 0, background: 'rgba(5,3,2,.88)', backdropFilter: 'blur(10px)', zIndex: 50, display: 'grid', placeItems: 'center', padding: 24 }}>
          <div onClick={(e) => e.stopPropagation()} className="card" style={{ maxWidth: 1120, width: '100%', maxHeight: '92vh', overflow: 'auto', display: 'grid', gridTemplateColumns: 'minmax(0,1fr) 360px', gap: 22 }}>
            <div>
              <div style={{ aspectRatio: is45(sel.format) ? '4 / 5' : '9 / 16', background: 'linear-gradient(180deg,#17120d,#0f0b07)', borderRadius: 18, overflow: 'hidden', display: 'grid', placeItems: 'center', maxHeight: '72vh', border: '1px solid rgba(186,155,96,0.12)' }}>
                {sel.assets[idx] ? <img src={`${api}${sel.assets[idx]}`} alt="" style={{ width: '100%', height: '100%', objectFit: 'contain' }} /> : <span className="muted">renderizando…</span>}
              </div>
              {sel.assets.length > 1 ? (
                <div style={{ display: 'flex', gap: 8, marginTop: 12, overflowX: 'auto', paddingBottom: 4 }}>
                  {sel.assets.map((a, i) => (
                    <img
                      key={a}
                      src={`${api}${a}`}
                      onClick={() => setIdx(i)}
                      style={{ width: 62, height: 78, objectFit: 'cover', borderRadius: 10, cursor: 'pointer', flexShrink: 0, border: i === idx ? '2px solid #b6945b' : '2px solid rgba(255,255,255,0.06)' }}
                    />
                  ))}
                </div>
              ) : null}
              {sel.format === 'reels' ? <StoryboardPanel cid={sel.id} /> : null}
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 12 }}>
                <span className="badge badgeDark">{sel.format}{sel.destino === 'meta_ads' ? ' · Meta Ads' : ''}</span>
                <button className="secondaryLink" onClick={() => setSel(null)}>Fechar</button>
              </div>
              <div style={{ display: 'grid', gap: 8 }}>
                <strong style={{ fontSize: '1.05rem', lineHeight: 1.4 }}>{(sel.title || '').replace(/\*/g, '')}</strong>
                <p className="muted small" style={{ margin: 0 }}>Slide {idx + 1} de {Math.max(sel.assets.length, 1)}</p>
                {sel.angulo_nome ? <p className="muted small" style={{ margin: 0 }}>Conjunto Meta Ads: {sel.angulo_nome}</p> : null}
                <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                  {sel.angulo_ivs ? <span className="badge badgeDark">Ângulo: {sel.angulo_ivs}</span> : null}
                  {sel.objecao_alvo ? <span className="badge badgeDark">Objeção: {sel.objecao_alvo}</span> : null}
                  {sel.hook_tipo ? <span className="badge badgeDark">Hook: {sel.hook_tipo}</span> : null}
                  {sel.visual_tipo ? <span className="badge badgeDark">Visual: {sel.visual_tipo}</span> : null}
                  {sel.cta_tipo ? <span className="badge badgeDark">CTA: {sel.cta_tipo}</span> : null}
                </div>
                {sel.hypothesis ? <div className="resultBox"><strong className="muted small">Hipótese do criativo</strong><p className="small" style={{ margin: '4px 0 0', whiteSpace: 'pre-wrap' }}>{sel.hypothesis}</p></div> : null}
              </div>
              {sel.caption ? <div className="resultBox">{sel.caption}</div> : null}
              {sel.hashtags && sel.hashtags.length ? <p className="muted small" style={{ margin: 0 }}>{sel.hashtags.join(' ')}</p> : null}
              {sel.feedback ? (
                <div className="resultBox" style={{ borderColor: 'rgba(186,155,96,.4)' }}>
                  <strong className="muted small">Melhorias solicitadas</strong>
                  <p className="small" style={{ margin: '4px 0 0', whiteSpace: 'pre-wrap' }}>{sel.feedback}</p>
                  <button className="primaryButton" style={{ marginTop: 8, padding: '6px 12px', fontSize: 13 }} onClick={() => regerar(sel.id)} disabled={regen === sel.id}>{regen === sel.id ? 'Regerando…' : 'Regerar com base na melhoria'}</button>
                </div>
              ) : null}
              <div style={{ marginTop: 'auto', display: 'flex', flexDirection: 'column', gap: 10 }}>
                {sel.status === 'aprovado' ? (
                  <span className="badge">Aprovado ✓</span>
                ) : sel.assets.length > 0 ? (
                  <button className="primaryButton" onClick={() => aprovar(sel.id)}>Aprovar peça</button>
                ) : null}
                {sel.assets.length > 0 ? <button className="secondaryLink" onClick={() => baixarTodos(sel)}>Baixar {sel.assets.length > 1 ? `todos (${sel.assets.length})` : 'imagem'}</button> : null}
                <div style={{ borderTop: '1px solid rgba(255,255,255,.08)', paddingTop: 10, display: 'grid', gap: 8 }}>
                  <label className="muted small">Correção do slide {idx + 1}</label>
                  <textarea
                    className="textarea"
                    placeholder={`Ex.: no slide ${idx + 1}, trocar a imagem, ajustar título, mudar CTA…`}
                    value={slideFeedback[feedbackKey(sel.id, idx)] || ''}
                    onChange={(e) => setSlideFeedback((cur) => ({ ...cur, [feedbackKey(sel.id, idx)]: e.target.value }))}
                    style={{ minHeight: 76 }}
                  />
                  <label className="muted small">Correção geral da peça (opcional)</label>
                  <textarea className="textarea" placeholder="Ex.: manter tom mais premium, reduzir texto de todos os slides…" value={melhoria} onChange={(e) => setMelhoria(e.target.value)} style={{ minHeight: 64 }} />
                  {feedbackAtual(sel) ? <div className="resultBox"><strong className="muted small">Correções acumuladas antes de regerar</strong><br />{feedbackAtual(sel)}</div> : null}
                  <button className="secondaryLink" onClick={() => solicitarMelhorias(sel.id)} disabled={!feedbackAtual(sel) || regen === sel.id}>{regen === sel.id ? 'Aplicando correções…' : 'Enviar correções e regerar peça'}</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : null}
    </>
  )
}
