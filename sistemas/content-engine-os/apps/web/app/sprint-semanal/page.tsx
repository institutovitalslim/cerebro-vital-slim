'use client'

import Link from 'next/link'
import { FormEvent, useEffect, useState } from 'react'

import { apiBase } from '../api'

type FamilyItem = {
  format: string
  role: string
  hook: string
  hook_variations?: string[]
  hook_test_minimum?: number
  output: string
  cta: string
  metric: string
  production_url: string
  origin_tag: string
}

type Pillar = { pillar: string; label: string; thesis: string; objection: string; promise_safe: string }
type Overview = {
  priority: string
  creatives: { total_creatives: number; ready_review: number; approved: number; changes_requested: number }
  stories: { stories: number; stories_approved: number }
  funnel: { appointments: number; leads: number; qualified_dms: number }
  pillars: Pillar[]
  default_plan: { thesis: string; pillar: string; objective: string; audience_stage: string; family: FamilyItem[] }
  governance: { mode: string; blocked: string[]; requires_human_approval: string[] }
}

type Plan = {
  thesis: string
  pillar: string
  objective: string
  audience_stage: string
  family: FamilyItem[]
  approval_flow: string[]
  governance: { external_actions: string; notes: string }
}

const fallback: Overview = {
  priority: 'Escolha uma tese semanal e crie a família completa antes de aprovar/publicar.',
  creatives: { total_creatives: 0, ready_review: 0, approved: 0, changes_requested: 0 },
  stories: { stories: 0, stories_approved: 0 },
  funnel: { appointments: 0, leads: 0, qualified_dms: 0 },
  pillars: [],
  default_plan: { thesis: 'O corpo travado não é falta de força de vontade; é sinal de mecanismo metabólico não investigado.', pillar: 'emagrecimento_metabolico', objective: 'autoridade_e_conversa', audience_stage: 'consciente_da_dor', family: [] },
  governance: { mode: 'plan_only', blocked: ['auto_publish', 'auto_dm'], requires_human_approval: ['publicar', 'enviar_mensagem'] },
}

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const r = await fetch(`${apiBase}${path}`, { cache: 'no-store', ...init })
  if (!r.ok) throw new Error(`${path}: ${r.status}`)
  return r.json()
}

function productionHref(item: FamilyItem, plan: Pick<Plan, 'thesis' | 'pillar' | 'objective' | 'audience_stage'> | Overview['default_plan']) {
  const qs = new URLSearchParams({
    source: 'weekly-sprint',
    thesis: plan.thesis,
    pillar: plan.pillar,
    objective: plan.objective,
    audience_stage: plan.audience_stage,
    origin_tag: item.origin_tag,
    format: item.format,
    hook: item.hook,
  })
  return `${item.production_url}?${qs.toString()}`
}

export default function SprintSemanalPage() {
  const [overview, setOverview] = useState<Overview>(fallback)
  const [plan, setPlan] = useState<Plan | null>(null)
  const [thesis, setThesis] = useState(fallback.default_plan.thesis)
  const [pillar, setPillar] = useState(fallback.default_plan.pillar)
  const [objective, setObjective] = useState('autoridade_e_conversa')
  const [stage, setStage] = useState('consciente_da_dor')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchJson<Overview>('/weekly-command/overview?tenant_slug=demo')
      .then((data) => {
        setOverview(data)
        setPlan({ ...data.default_plan, approval_flow: [], governance: { external_actions: 'blocked_by_default', notes: 'Plano inicial.' } })
        setThesis(data.default_plan.thesis)
        setPillar(data.default_plan.pillar)
      })
      .catch(() => setError('Não consegui carregar o comando semanal agora. Usando fallback seguro.'))
  }, [])

  async function gerarPlano(e: FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const next = await fetchJson<Plan>('/weekly-command/family-plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tenant_slug: 'demo', thesis, pillar, objective, audience_stage: stage }),
      })
      setPlan(next)
    } catch {
      setError('Falha ao gerar plano. Nada foi publicado ou enviado.')
    } finally {
      setLoading(false)
    }
  }

  const family = plan?.family || overview.default_plan.family || []
  const activePlan = plan || overview.default_plan

  return (
    <div className="dashboardRoot">
      <header className="pageHeader heroHeader">
        <div>
          <p className="eyebrow">Fase 2 · Sprint Semanal</p>
          <h2 className="pageTitle">Uma tese vira uma família inteira de autoridade</h2>
          <p className="heroText">Comece pela decisão estratégica da semana, gere a família de formatos e só depois siga para produção, aprovação e aprendizado.</p>
        </div>
        <div className="heroActions">
          <Link className="secondaryLink" href="/business-intelligence">Ver BI</Link>
          <Link className="secondaryLink" href="/banco-criativos">Aprovar fila</Link>
        </div>
      </header>

      <section className="heroSurface commandHero">
        <div className="heroMain">
          <span className="badge">Comando da semana</span>
          <h3 className="sectionTitle">{overview.priority}</h3>
          <p className="heroText">Este módulo não publica, não envia DM e não escreve em WhatsApp. Ele organiza a tese e direciona a produção.</p>
          <div className="commandNext">
            <span className="metricLabel">Próxima ação em 10 segundos</span>
            <strong>Validar a tese, escolher o hook vencedor do Reels e abrir a produção por formato.</strong>
            <p className="muted small">Fluxo: BI → tese semanal → família completa → revisão humana → calendário → aprendizado.</p>
          </div>
          <div className="metricGrid">
            <article className="metricCard"><span className="metricLabel">Para revisar</span><strong className="metricValue">{overview.creatives.ready_review}</strong></article>
            <article className="metricCard"><span className="metricLabel">Aprovados</span><strong className="metricValue">{overview.creatives.approved}</strong></article>
            <article className="metricCard"><span className="metricLabel">Stories</span><strong className="metricValue">{overview.stories.stories}</strong></article>
            <article className="metricCard"><span className="metricLabel">Leads 30d</span><strong className="metricValue">{overview.funnel.leads}</strong></article>
          </div>
        </div>
        <form className="formCard" onSubmit={gerarPlano}>
          <div className="formHeader">
            <span className="badge badgeDark">Tese central</span>
            <h3>Definir sprint</h3>
            <p className="muted small">Escolha a tese antes de criar qualquer peça.</p>
          </div>
          <label className="muted small">Pilar</label>
          <select className="input" value={pillar} onChange={(e) => {
            setPillar(e.target.value)
            const p = overview.pillars.find((x) => x.pillar === e.target.value)
            if (p) setThesis(p.thesis)
          }}>
            {overview.pillars.length ? overview.pillars.map((p) => <option key={p.pillar} value={p.pillar}>{p.label}</option>) : <option value={pillar}>Emagrecimento metabólico</option>}
          </select>
          <label className="muted small">Tese da semana</label>
          <textarea className="textarea" value={thesis} onChange={(e) => setThesis(e.target.value)} />
          <label className="muted small">Objetivo</label>
          <select className="input" value={objective} onChange={(e) => setObjective(e.target.value)}>
            <option value="autoridade_e_conversa">Autoridade + conversa</option>
            <option value="captacao_qualificada">Captação qualificada</option>
            <option value="educacao_de_mercado">Educação de mercado</option>
            <option value="prova_e_metodo">Prova + método</option>
          </select>
          <label className="muted small">Consciência do público</label>
          <select className="input" value={stage} onChange={(e) => setStage(e.target.value)}>
            <option value="frio">Frio</option>
            <option value="consciente_da_dor">Consciente da dor</option>
            <option value="consciente_da_solucao">Consciente da solução</option>
            <option value="quase_pronto">Quase pronto</option>
          </select>
          <button className="primaryButton" disabled={loading || thesis.trim().length < 6}>{loading ? 'Gerando…' : 'Gerar família semanal'}</button>
          {error ? <p className="errorText">{error}</p> : null}
        </form>
      </section>

      <section className="section">
        <div className="sectionHeaderInline">
          <div>
            <p className="eyebrow">Família da tese</p>
            <h3 className="sectionTitle">Criar uma vez, distribuir por função</h3>
          </div>
          <span className="muted small">{family.length} formatos guiados</span>
        </div>
        <div className="flowRail">
          {family.map((item) => (
            <article className="flowCard" key={item.origin_tag}>
              <span className="badge badgeDark">{item.format}</span>
              <h3>{item.role}</h3>
              <p className="muted small"><strong>Hook principal:</strong> {item.hook}</p>
              {item.hook_variations?.length ? (
                <div className="hookStack">
                  <span className="metricLabel">Hooks para teste</span>
                  {item.hook_variations.map((hook, index) => (
                    <p className="hookLine" key={`${item.origin_tag}-hook-${index}`}><strong>{index + 1}.</strong> {hook}</p>
                  ))}
                </div>
              ) : null}
              <p className="muted small"><strong>Saída:</strong> {item.output}</p>
              <p className="muted small"><strong>CTA:</strong> {item.cta}</p>
              <p className="muted small"><strong>Métrica:</strong> {item.metric}</p>
              <div className="resultBox">{item.origin_tag}</div>
              <Link className="secondaryLink" href={productionHref(item, activePlan)}>Abrir produção com briefing →</Link>
            </article>
          ))}
        </div>
      </section>

      <section className="splitSection">
        <article className="card" style={{ display: 'grid', gap: 12 }}>
          <h3>Fluxo de aprovação</h3>
          <div className="checkGrid">
            {(plan?.approval_flow?.length ? plan.approval_flow : ['Gerar peças por formato', 'Revisar no Banco de Criativos', 'Aprovar ou pedir alteração', 'Planejar calendário', 'Medir no BI']).map((x) => <div className="checkRow" key={x}><span className="checkDot" />{x}</div>)}
          </div>
        </article>
        <article className="card" style={{ display: 'grid', gap: 12 }}>
          <h3>Governança</h3>
          <p className="muted">Bloqueado por padrão: {overview.governance.blocked.join(', ')}</p>
          <p className="muted">Exige humano: {overview.governance.requires_human_approval.join(', ')}</p>
        </article>
      </section>
    </div>
  )
}
