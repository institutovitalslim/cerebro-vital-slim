'use client'

import { useEffect, useState } from 'react'

const api = process.env.NEXT_PUBLIC_API_BASE_URL || '/api'

type Creative = { id: string; format: string; title: string | null; status: string; assets: string[] }
type Metrics = Record<string, number | string | boolean | null>

const FIELDS: [string, string][] = [
  ['retencao_3s_pct', 'Retenção 3s (%)'],
  ['tempo_medio_seg', 'Tempo médio assistido (s)'],
  ['conclusao_pct', 'Taxa de conclusão (%)'],
  ['reach', 'Alcance'],
  ['shares', 'Compartilhamentos / envios'],
  ['saves', 'Salvamentos'],
  ['replays', 'Replays'],
  ['comentarios', 'Comentários (total)'],
  ['comentarios_qualificados', 'Comentários qualificados'],
  ['profile_clicks', 'Cliques no perfil'],
  ['follows', 'Seguidores ganhos'],
  ['whatsapp_leads', 'Leads no WhatsApp'],
  ['likes', 'Likes'],
  ['skip_rate_pct', 'Pular em 1-2s / skip (%)'],
]

// Indicadores que o sistema coleta sozinho do Instagram (POST /generation/campeoes/importar)
const AUTO_FIELDS: [string, string][] = [
  ['reach', 'Alcance'],
  ['views', 'Views'],
  ['likes', 'Likes'],
  ['comentarios', 'Comentários'],
  ['shares', 'Compartilhamentos'],
  ['saves', 'Salvamentos'],
  ['tempo_medio_seg', 'Tempo médio (s)'],
  ['profile_clicks', 'Cliques no perfil'],
  ['follows', 'Follows'],
  ['whatsapp_leads', 'Leads WhatsApp'],
]

const STRATEGY_FIELDS: [string, string, string][] = [
  ['seo_social_intent', 'SEO social / intenção de busca', 'Ex.: por que não consigo emagrecer mesmo fazendo dieta'],
  ['send_save_reason', 'Motivo de envio/salvamento', 'Ex.: amiga que se culpa por não ter força de vontade'],
  ['expected_intent_signal', 'Sinal de intenção esperado', 'Ex.: DM “me vi aqui”, envio, salvar, WhatsApp'],
  ['quality_metric', 'Métrica principal de qualidade', 'Ex.: dm_util, lead_util, envio, retencao'],
]
const FRACO_LABEL: Record<string, string> = {
  ret: 'retenção 3s', tempo: 'tempo médio', concl: 'conclusão', shares: 'compartilhamentos',
  saves: 'salvamentos', replays: 'replays', coment: 'comentários qualificados', clicks: 'cliques no perfil',
  follows: 'follows', leads: 'leads WhatsApp',
}

export default function CampeoesPage() {
  const [items, setItems] = useState<Creative[]>([])
  const [sel, setSel] = useState<Creative | null>(null)
  const [vals, setVals] = useState<Metrics>({})
  const [raw, setRaw] = useState<Metrics | null>(null)
  const [res, setRes] = useState<{ viral_score: number; breakdown: { fracos: string[] }; analise: string } | null>(null)
  const [loading, setLoading] = useState(false)
  const [importando, setImportando] = useState(false)
  const [importMsg, setImportMsg] = useState<{ ok: boolean; texto: string } | null>(null)

  useEffect(() => {
    fetch(`${api}/generation/creatives?tenant_slug=demo&limit=60`, { cache: 'no-store' })
      .then((r) => r.json()).then((d) => setItems((d.items || []).filter((c: Creative) => c.assets.length > 0)))
      .catch(() => {})
  }, [])

  async function abrir(c: Creative) {
    setSel(c); setRes(null); setVals({}); setRaw(null)
    try {
      const r = await fetch(`${api}/generation/creatives/${c.id}/metrics`, { cache: 'no-store' })
      const d = await r.json()
      if (d.metrics) {
        setRaw(d.metrics as Metrics)
        const m: Metrics = {}
        FIELDS.forEach(([k]) => { m[k] = d.metrics[k] })
        STRATEGY_FIELDS.forEach(([k]) => { m[k] = d.metrics[k] })
        m.trial_reel = Boolean(d.metrics.trial_reel)
        setVals(m)
        if (d.metrics.viral_score != null) setRes({ viral_score: d.metrics.viral_score, breakdown: { fracos: [] }, analise: d.metrics.analise || '' })
      }
    } catch { /* */ }
  }

  async function importar() {
    setImportando(true); setImportMsg(null)
    try {
      const r = await fetch(`${api}/generation/campeoes/importar?tenant_slug=demo`, { method: 'POST' })
      if (!r.ok) throw new Error(String(r.status))
      const d = await r.json()
      const extra = d.sem_dados ? ` · ${d.sem_dados} vinculada(s) ainda sem métricas coletadas` : ''
      setImportMsg({
        ok: true,
        texto: d.vinculadas === 0
          ? 'Nenhuma peça publicada com post do Instagram vinculado ainda — publique pelo calendário para ligar peça e post.'
          : `${d.importados} peça(s) preenchidas com métricas reais do Instagram${extra}.`,
      })
      if (sel) abrir(sel)
    } catch {
      setImportMsg({ ok: false, texto: 'Falha ao importar do Instagram — a API não respondeu. Nada foi alterado; tente de novo.' })
    } finally { setImportando(false) }
  }

  async function analisar() {
    if (!sel) return
    setLoading(true)
    try {
      const body: Record<string, number | string | boolean> = {}
      FIELDS.forEach(([k]) => { if (vals[k] != null && vals[k] !== '') body[k] = Number(vals[k]) })
      STRATEGY_FIELDS.forEach(([k]) => { if (vals[k] != null && vals[k] !== '') body[k] = String(vals[k]) })
      body.trial_reel = Boolean(vals.trial_reel)
      const r = await fetch(`${api}/generation/creatives/${sel.id}/metrics`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
      })
      setRes(await r.json())
    } catch { /* */ } finally { setLoading(false) }
  }

  const scoreColor = (s: number) => (s >= 70 ? '#7CCB8E' : s >= 45 ? '#E0B871' : '#D98A8A')

  const isAuto = raw?.origem === 'auto'
  const autoPreenchidos = isAuto ? AUTO_FIELDS.filter(([k]) => raw?.[k] != null) : []
  const autoKeys = new Set(autoPreenchidos.map(([k]) => k))
  const formFields = FIELDS.filter(([k]) => !autoKeys.has(k))

  return (
    <div className="dashboardRoot">
      <header className="pageHeader heroHeader">
        <div>
          <p className="eyebrow">O pódio dos criativos</p>
          <h2 className="pageTitle">Análise de performance & criativos campeões</h2>
          <p className="muted">
            O sistema puxa sozinho o que o Instagram já entrega (alcance, views, likes, comentários, envios, salvamentos)
            das peças publicadas e calcula o <strong>viral score</strong> com os sinais disponíveis. Os indicadores privados
            (retenção 3s, tempo médio…) entram como complemento manual — os campeões realimentam a próxima rodada.
          </p>
        </div>
        <div style={{ display: 'grid', gap: 8, justifyItems: 'end', alignContent: 'start' }}>
          <button className="primaryButton" onClick={importar} disabled={importando}>
            {importando ? 'Importando…' : '⤵ Importar métricas do Instagram'}
          </button>
          {importMsg ? (
            <p className="small" style={{ margin: 0, maxWidth: 340, textAlign: 'right', color: importMsg.ok ? 'var(--state-good, #7CCB8E)' : 'var(--state-bad, #D98A8A)' }}>
              {importMsg.texto}
            </p>
          ) : null}
        </div>
      </header>

      <section className="section grid" style={{ gridTemplateColumns: '300px 1fr', gap: 22, alignItems: 'start' }}>
        <div>
          <div className="sectionHeaderInline"><h3 className="sectionTitle" style={{ fontSize: '1rem' }}>Peças</h3></div>
          <div style={{ display: 'grid', gap: 8, maxHeight: '72vh', overflow: 'auto' }}>
            {items.map((c) => (
              <button key={c.id} onClick={() => abrir(c)} className="card" style={{ display: 'flex', gap: 10, alignItems: 'center', textAlign: 'left', cursor: 'pointer', border: sel?.id === c.id ? '1px solid #D4A83C' : undefined, padding: 8 }}>
                <img src={`${api}${c.assets[0]}`} alt="" style={{ width: 40, height: 50, objectFit: 'cover', borderRadius: 6 }} />
                <span className="small">{(c.title || c.format || '').replace(/\*/g, '').slice(0, 40)}</span>
              </button>
            ))}
          </div>
        </div>

        <div>
          {!sel ? <p className="muted">Selecione uma peça para analisar a performance.</p> : (
            <div style={{ display: 'grid', gap: 16 }}>
              {isAuto && autoPreenchidos.length > 0 ? (
                <article className="card" style={{ display: 'grid', gap: 12 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                    <h3 style={{ margin: 0, fontSize: '1rem' }}>Métricas reais do Instagram</h3>
                    <span className="badge" style={{ background: 'rgba(124,203,142,.16)', color: 'var(--state-good, #7CCB8E)' }}>auto</span>
                    {raw?.updated_at ? (
                      <span className="muted small">importadas em {new Date(String(raw.updated_at)).toLocaleDateString('pt-BR')}</span>
                    ) : null}
                  </div>
                  <div style={{ display: 'flex', gap: 18, flexWrap: 'wrap' }}>
                    {autoPreenchidos.map(([k, label]) => (
                      <div key={k} style={{ textAlign: 'center', minWidth: 84 }}>
                        <strong style={{ fontSize: '1.25rem', lineHeight: 1.1 }}>{Number(raw?.[k]).toLocaleString('pt-BR')}</strong>
                        <p className="muted small" style={{ margin: '2px 0 0' }}>
                          {label} <span className="badge" style={{ fontSize: 9, padding: '1px 5px', verticalAlign: 'middle' }}>auto</span>
                        </p>
                      </div>
                    ))}
                  </div>
                  <p className="muted small" style={{ margin: 0 }}>
                    Última coleta do post publicado — sem digitação. Complete abaixo só o que o Instagram não expõe por API.
                  </p>
                </article>
              ) : null}

              <details className="formCard" open={!isAuto}>
                <summary style={{ cursor: 'pointer', fontWeight: 600 }}>
                  {isAuto ? 'Complementar manualmente (retenção 3s, tempo médio, conclusão…)' : 'Registrar indicadores manualmente'}
                </summary>
                <div className="formHeader" style={{ marginTop: 12 }}>
                  <h3>Indicadores (Instagram + WhatsApp)</h3>
                  <p className="muted small">{isAuto ? 'Os campos importados do Instagram já estão preenchidos acima — aqui entram só os privados.' : 'Ordem = peso no algoritmo (ranking IVS).'}</p>
                </div>
                <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit,minmax(170px,1fr))', gap: 8 }}>
                  {formFields.map(([k, label]) => (
                    <div key={k} style={{ display: 'grid', gap: 2 }}>
                      <label className="muted small">{label}</label>
                      <input className="input" type="number" value={(vals[k] as number | null) ?? ''} onChange={(e) => setVals((v) => ({ ...v, [k]: e.target.value === '' ? null : Number(e.target.value) }))} />
                    </div>
                  ))}
                </div>
                <div className="formHeader" style={{ marginTop: 16 }}><h3>Estratégia Instagram 2026</h3><p className="muted small">Campos obrigatórios para julgar busca, retenção, envio e intenção real — não vaidade.</p></div>
                <label className="muted small" style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                  <input type="checkbox" checked={Boolean(vals.trial_reel)} onChange={(e) => setVals((v) => ({ ...v, trial_reel: e.target.checked }))} /> Trial Reel / laboratório antes de escalar
                </label>
                <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit,minmax(220px,1fr))', gap: 8 }}>
                  {STRATEGY_FIELDS.map(([k, label, placeholder]) => (
                    <div key={k} style={{ display: 'grid', gap: 2 }}>
                      <label className="muted small">{label}</label>
                      <input className="input" value={String(vals[k] ?? '')} placeholder={placeholder} onChange={(e) => setVals((v) => ({ ...v, [k]: e.target.value }))} />
                    </div>
                  ))}
                </div>
                <button className="primaryButton" onClick={analisar} disabled={loading} style={{ marginTop: 12 }}>{loading ? 'Analisando…' : 'Calcular score & analisar melhorias'}</button>
              </details>

              {res ? (
                <article className="card" style={{ display: 'grid', gap: 12 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                    <div style={{ textAlign: 'center' }}>
                      <strong style={{ fontSize: '2.4rem', color: scoreColor(res.viral_score), lineHeight: 1 }}>{res.viral_score}</strong>
                      <p className="muted small" style={{ margin: 0 }}>viral score{isAuto ? ' (sinais disponíveis)' : ''}</p>
                    </div>
                    {res.breakdown?.fracos?.length ? (
                      <div>
                        <p className="muted small" style={{ margin: 0 }}>Sinais mais fracos:</p>
                        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginTop: 4 }}>
                          {res.breakdown.fracos.map((f) => <span key={f} className="badge badgeDark">{FRACO_LABEL[f] || f}</span>)}
                        </div>
                      </div>
                    ) : null}
                  </div>
                  {res.analise ? <div className="resultBox" style={{ whiteSpace: 'pre-wrap', fontSize: 13, lineHeight: 1.5 }}>{res.analise}</div> : null}
                </article>
              ) : null}
            </div>
          )}
        </div>
      </section>
    </div>
  )
}
