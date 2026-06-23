import Link from 'next/link'
import { fetchJson } from '../api'

type BIOverview = {
  creatives: { total_creatives: number; approved: number; ready_review: number; changes_requested: number; avg_quality_score: string | number }
  by_format: { format: string; total: number; approved: number }[]
  stories: { stories_sequences: number; stories_approved: number; stories_changes_requested: number }
  funnel: { story_clicks: number; qualified_dms: number; leads: number; appointments: number }
  recent_stories: { title: string; sequence_type: string; objective: string; status: string; created_at: string }[]
  calendar: { title: string; format: string; channel: string; objective: string | null; status: string; scheduled_for: string | null }[]
  sources: { network: string; total: number }[]
  rapidapi_instagram: { profile: string; collector: string; source: string; mode: string; status: string; next_step: string; pii_policy: string }
  content_score: number
  diagnosis: { status_label: string; priority: string; next_actions: string[] }
}

async function safe<T>(p: Promise<T>, fallback: T): Promise<T> {
  try { return await p } catch { return fallback }
}

export default async function BIPage() {
  const data = await safe<BIOverview>(fetchJson('/bi/overview?tenant_slug=demo'), {
    creatives: { total_creatives: 0, approved: 0, ready_review: 0, changes_requested: 0, avg_quality_score: 0 },
    by_format: [], stories: { stories_sequences: 0, stories_approved: 0, stories_changes_requested: 0 },
    funnel: { story_clicks: 0, qualified_dms: 0, leads: 0, appointments: 0 },
    recent_stories: [], calendar: [], sources: [],
    rapidapi_instagram: { profile: '@dradaniely.freitas', collector: 'João', source: 'RapidAPI', mode: 'read_only_planned', status: 'pendente', next_step: 'Criar ingestão diária', pii_policy: 'Sem PII' },
    content_score: 0,
    diagnosis: { status_label: 'BI em estruturação', priority: 'Conectar dados reais.', next_actions: [] },
  })

  return (
    <div className="dashboardRoot">
      <header className="pageHeader heroHeader">
        <div>
          <p className="eyebrow">BI · Business Intelligence</p>
          <h2 className="pageTitle">Centro de inteligência de conteúdo e autoridade</h2>
          <p className="heroText">
            O BI transforma criação em decisão: o que gerou atenção, conversa, lead, agendamento e autoridade — sem depender de achismo.
          </p>
        </div>
      </header>

      <section className="heroSurface">
        <div className="heroMain">
          <span className="badge">Prioridade do dia</span>
          <h3 className="sectionTitle">{data.diagnosis.priority}</h3>
          <p className="muted">Score operacional: {data.content_score}. Esse score prioriza aprovação, stories aprovados, DMs, leads e agendamentos — não vaidade.</p>
          <div className="heroActions">
            <Link className="primaryLink" href="/criar">Gerar família de conteúdo</Link>
            <Link className="secondaryLink" href="/banco-criativos">Revisar criativos</Link>
            <Link className="secondaryLink" href="/stories-engine">Abrir Stories Engine</Link>
          </div>
        </div>
        <div className="heroRail">
          <article className="heroMetricCard"><span className="metricLabel">Criativos</span><strong className="metricValue">{data.creatives.total_creatives}</strong><p className="muted small">{data.creatives.approved} aprovados · {data.creatives.ready_review} prontos para revisar</p></article>
          <article className="heroMetricCard"><span className="metricLabel">Stories</span><strong className="metricValue">{data.stories.stories_sequences}</strong><p className="muted small">{data.stories.stories_approved} aprovadas · {data.stories.stories_changes_requested} com ajustes</p></article>
          <article className="heroMetricCard"><span className="metricLabel">Agendamentos atribuídos</span><strong className="metricValue">{data.funnel.appointments}</strong><p className="muted small">{data.funnel.leads} leads · {data.funnel.qualified_dms} DMs qualificadas</p></article>
        </div>
      </section>

      <section className="splitSection">
        <article className="card" style={{ display: 'grid', gap: 14 }}>
          <div className="rowTop"><h3>RapidAPI Instagram · Dra. Daniely</h3><span className="badge">próxima integração</span></div>
          <div className="resultBox">
            {`Perfil: ${data.rapidapi_instagram.profile}
Operador: ${data.rapidapi_instagram.collector}
Fonte: ${data.rapidapi_instagram.source}
Modo: ${data.rapidapi_instagram.mode}
Status: ${data.rapidapi_instagram.status}`}
          </div>
          <p className="muted small" style={{ margin: 0 }}>{data.rapidapi_instagram.pii_policy}</p>
          <p className="muted small" style={{ margin: 0 }}><strong>Próximo passo:</strong> {data.rapidapi_instagram.next_step}</p>
        </article>

        <article className="card" style={{ display: 'grid', gap: 14 }}>
          <div className="rowTop"><h3>Funil de conteúdo</h3><span className="badge">story → conversa</span></div>
          <div className="metricGrid">
            <div className="resultBox"><strong>Cliques</strong><br />{data.funnel.story_clicks}</div>
            <div className="resultBox"><strong>DMs qualificadas</strong><br />{data.funnel.qualified_dms}</div>
            <div className="resultBox"><strong>Leads</strong><br />{data.funnel.leads}</div>
            <div className="resultBox"><strong>Agendamentos</strong><br />{data.funnel.appointments}</div>
          </div>
        </article>
      </section>

      <section className="section grid" style={{ gridTemplateColumns: 'repeat(auto-fit,minmax(280px,1fr))' }}>
        <article className="card" style={{ display: 'grid', gap: 12 }}>
          <h3>Performance por formato</h3>
          <div className="tableLike">
            {data.by_format.length ? data.by_format.map((row) => <div className="row" key={row.format}><div className="rowTop"><strong>{row.format}</strong><span className="badge">{row.approved}/{row.total}</span></div><span className="muted small">aprovados / total</span></div>) : <p className="muted">Sem criativos ainda.</p>}
          </div>
        </article>
        <article className="card" style={{ display: 'grid', gap: 12 }}>
          <h3>Stories recentes</h3>
          <div className="tableLike">
            {data.recent_stories.length ? data.recent_stories.map((row) => <div className="row" key={`${row.title}-${row.created_at}`}><strong>{row.title}</strong><span className="muted small">{row.sequence_type} · {row.objective} · {row.status}</span></div>) : <p className="muted">Sem sequências recentes.</p>}
          </div>
        </article>
        <article className="card" style={{ display: 'grid', gap: 12 }}>
          <h3>Próximas ações do BI</h3>
          <div className="checkGrid">
            {data.diagnosis.next_actions.map((action) => <div className="checkRow" key={action}><span className="checkDot" />{action}</div>)}
          </div>
        </article>
      </section>
    </div>
  )
}
