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
  const [res, setRes] = useState<{ viral_score: number; breakdown: { fracos: string[] }; analise: string } | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetch(`${api}/generation/creatives?tenant_slug=demo&limit=60`, { cache: 'no-store' })
      .then((r) => r.json()).then((d) => setItems((d.items || []).filter((c: Creative) => c.assets.length > 0)))
      .catch(() => {})
  }, [])

  async function abrir(c: Creative) {
    setSel(c); setRes(null); setVals({})
    try {
      const r = await fetch(`${api}/generation/creatives/${c.id}/metrics`, { cache: 'no-store' })
      const d = await r.json()
      if (d.metrics) {
        const m: Metrics = {}
        FIELDS.forEach(([k]) => { m[k] = d.metrics[k] })
        STRATEGY_FIELDS.forEach(([k]) => { m[k] = d.metrics[k] })
        m.trial_reel = Boolean(d.metrics.trial_reel)
        setVals(m)
        if (d.metrics.viral_score != null) setRes({ viral_score: d.metrics.viral_score, breakdown: { fracos: [] }, analise: d.metrics.analise || '' })
      }
    } catch { /* */ }
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

  return (
    <div className="dashboardRoot">
      <header className="pageHeader heroHeader">
        <div>
          <p className="eyebrow">Motor A · etapa 8 (posterior)</p>
          <h2 className="pageTitle">Análise de performance & criativos campeões</h2>
          <p className="muted">
            Após postar, registre os indicadores reais (Instagram + WhatsApp) de cada peça. O sistema calcula o
            <strong> viral score</strong> ponderado pela rubrica IVS e sugere melhorias — os campeões realimentam a próxima rodada.
          </p>
        </div>
      </header>

      <section className="section grid" style={{ gridTemplateColumns: '300px 1fr', gap: 22, alignItems: 'start' }}>
        <div>
          <div className="sectionHeaderInline"><h3 className="sectionTitle" style={{ fontSize: '1rem' }}>Peças</h3></div>
          <div style={{ display: 'grid', gap: 8, maxHeight: '72vh', overflow: 'auto' }}>
            {items.map((c) => (
              <button key={c.id} onClick={() => abrir(c)} className="card" style={{ display: 'flex', gap: 10, alignItems: 'center', textAlign: 'left', cursor: 'pointer', border: sel?.id === c.id ? '1px solid #B6945B' : undefined, padding: 8 }}>
                <img src={`${api}${c.assets[0]}`} alt="" style={{ width: 40, height: 50, objectFit: 'cover', borderRadius: 6 }} />
                <span className="small">{(c.title || c.format || '').replace(/\*/g, '').slice(0, 40)}</span>
              </button>
            ))}
          </div>
        </div>

        <div>
          {!sel ? <p className="muted">Selecione uma peça para analisar a performance.</p> : (
            <div style={{ display: 'grid', gap: 16 }}>
              <article className="formCard">
                <div className="formHeader"><h3>Indicadores (Instagram + WhatsApp)</h3><p className="muted small">Ordem = peso no algoritmo (ranking IVS).</p></div>
                <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit,minmax(170px,1fr))', gap: 8 }}>
                  {FIELDS.map(([k, label]) => (
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
              </article>

              {res ? (
                <article className="card" style={{ display: 'grid', gap: 12 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                    <div style={{ textAlign: 'center' }}>
                      <strong style={{ fontSize: '2.4rem', color: scoreColor(res.viral_score), lineHeight: 1 }}>{res.viral_score}</strong>
                      <p className="muted small" style={{ margin: 0 }}>viral score</p>
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
