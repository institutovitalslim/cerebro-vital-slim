import Link from 'next/link'
import { fetchJson } from '../api'

type BIOverview = {
  creatives: { total_creatives: number; approved: number; ready_review: number; changes_requested: number; avg_quality_score: string | number }
  by_format: { format: string; total: number; approved: number }[]
  stories: { stories_sequences: number; stories_approved: number; stories_changes_requested: number }
  funnel: { story_clicks: number; qualified_dms: number; leads: number; appointments: number }
  recent_stories: { title: string; sequence_type: string; objective: string; status: string; created_at: string }[]
  calendar: { title: string; format: string; channel: string; objective: string | null; status: string; scheduled_for: string | null; metrics_pending?: boolean; origin_tag?: string | null }[]
  editorial_flow: { approved_to_publish: number; metrics_pending: number; measured: number }
  sources: { network: string; total: number }[]
  rapidapi_instagram: { profile: string; collector: string; source: string; mode: string; status: string; next_step: string; pii_policy: string }
  social_profile: { profile_handle: string; followers_count: number; profile_views: number; whatsapp_clicks: number }
  follower_movement: {
    latest: { metric_date: string; followers_count: number; net_change: number; day_span: number } | null
    delta_7d: number | null
    delta_30d: number | null
    series: { metric_date: string; followers_count: number; net_change: number; day_span: number }[]
    days_tracked: number
  }
  social_aggregate_30d: { likes: number; comments: number; saves: number; shares: number; follows: number; publications_tracked: number }
  social_selling: { total_interactors: number; candidates: number; approved_for_manual_outreach: number; avg_fit_score: string | number }
  content_score: number
  diagnosis: { status_label: string; priority: string; next_actions: string[] }
}

async function safe<T>(p: Promise<T>, fallback: T): Promise<T> {
  try { return await p } catch { return fallback }
}

const signed = (n: number | null | undefined) => (n == null ? '—' : n > 0 ? `+${n}` : `${n}`)
const deltaColor = (n: number | null | undefined) =>
  n == null || n === 0 ? 'var(--muted)' : n < 0 ? 'var(--danger)' : 'var(--accent-hi)'

export default async function BIPage() {
  const data = await safe<BIOverview>(fetchJson('/bi/overview?tenant_slug=demo'), {
    creatives: { total_creatives: 0, approved: 0, ready_review: 0, changes_requested: 0, avg_quality_score: 0 },
    by_format: [], stories: { stories_sequences: 0, stories_approved: 0, stories_changes_requested: 0 },
    funnel: { story_clicks: 0, qualified_dms: 0, leads: 0, appointments: 0 },
    recent_stories: [], calendar: [], editorial_flow: { approved_to_publish: 0, metrics_pending: 0, measured: 0 }, sources: [],
    rapidapi_instagram: { profile: '@dradaniely.freitas', collector: 'João', source: 'RapidAPI', mode: 'read_only_planned', status: 'pendente', next_step: 'Criar ingestão diária', pii_policy: 'Sem PII' },
    social_profile: { profile_handle: '@dradaniely.freitas', followers_count: 0, profile_views: 0, whatsapp_clicks: 0 },
    follower_movement: { latest: null, delta_7d: 0, delta_30d: 0, series: [], days_tracked: 0 },
    social_aggregate_30d: { likes: 0, comments: 0, saves: 0, shares: 0, follows: 0, publications_tracked: 0 },
    social_selling: { total_interactors: 0, candidates: 0, approved_for_manual_outreach: 0, avg_fit_score: 0 },
    content_score: 0,
    diagnosis: { status_label: 'BI em estruturação', priority: 'Conectar dados reais.', next_actions: [] },
  })

  return (
    <div className="dashboardRoot">
      <header className="pageHeader heroHeader">
        <div>
          <p className="eyebrow">Instagram & funil</p>
          <h2 className="pageTitle">O que o conteúdo está gerando de verdade</h2>
          <p className="heroText">
            Aqui a criação vira decisão: o que gerou atenção, conversa, lead e agendamento — sem depender de achismo.
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
            <Link className="secondaryLink" href="/social-selling">Abrir Social Selling</Link>
          </div>
        </div>
        <div className="heroRail">
          <article className="heroMetricCard"><span className="metricLabel">Criativos</span><strong className="metricValue">{data.creatives.total_creatives}</strong><p className="muted small">{data.creatives.approved} aprovados · {data.creatives.ready_review} prontos para revisar</p></article>
          <article className="heroMetricCard"><span className="metricLabel">Stories</span><strong className="metricValue">{data.stories.stories_sequences}</strong><p className="muted small">{data.stories.stories_approved} aprovadas · {data.stories.stories_changes_requested} com ajustes</p></article>
          <article className="heroMetricCard"><span className="metricLabel">Agendamentos atribuídos</span><strong className="metricValue">{data.funnel.appointments}</strong><p className="muted small">{data.funnel.leads} leads · {data.funnel.qualified_dms} DMs qualificadas</p></article>
        </div>
      </section>


      <section className="metricGrid">
        <article className="metricCard"><span className="metricLabel">Seguidores</span><strong className="metricValue">{data.social_profile.followers_count || 0}</strong><p className="muted small">perfil {data.social_profile.profile_handle}</p></article>
        <article className="metricCard"><span className="metricLabel">Interatores mapeados</span><strong className="metricValue">{data.social_selling.total_interactors || 0}</strong><p className="muted small">{data.social_selling.candidates || 0} candidatos em triagem</p></article>
        <article className="metricCard"><span className="metricLabel">Sinais 30d</span><strong className="metricValue">{(data.social_aggregate_30d.likes || 0) + (data.social_aggregate_30d.comments || 0) + (data.social_aggregate_30d.saves || 0) + (data.social_aggregate_30d.shares || 0)}</strong><p className="muted small">likes + comentários + saves + shares</p></article>
        <article className="metricCard"><span className="metricLabel">WhatsApp pelo perfil</span><strong className="metricValue">{data.social_profile.whatsapp_clicks || 0}</strong><p className="muted small">sinal agregado de intenção</p></article>
        <article className="metricCard"><span className="metricLabel">Métricas pendentes</span><strong className="metricValue">{data.editorial_flow.metrics_pending || 0}</strong><p className="muted small">publicadas aguardando aprendizado</p></article>
      </section>

      <section className="section">
        <div className="sectionHeaderInline">
          <div>
            <p className="eyebrow">Movimento de seguidores</p>
            <h3 className="sectionTitle">Ganhou ou perdeu seguidores (líquido por dia)</h3>
          </div>
          <span className="muted small">saldo real da contagem oficial · {data.follower_movement.days_tracked} dias monitorados</span>
        </div>
        {data.follower_movement.latest ? (
          <>
            <section className="metricGrid" style={{ marginTop: 8 }}>
              <article className="metricCard">
                <span className="metricLabel">{data.follower_movement.latest.day_span > 1 ? 'Desde a última coleta' : 'Ontem'}</span>
                <strong className="metricValue" style={{ color: deltaColor(data.follower_movement.latest.net_change) }}>
                  {signed(data.follower_movement.latest.net_change)}
                </strong>
                <p className="muted small">
                  total: {data.follower_movement.latest.followers_count} seguidores
                  {data.follower_movement.latest.day_span > 1 ? ` · acumulado de ${data.follower_movement.latest.day_span} dias` : ''}
                </p>
              </article>
              <article className="metricCard">
                <span className="metricLabel">Últimos 7 dias</span>
                <strong className="metricValue" style={{ color: deltaColor(data.follower_movement.delta_7d) }}>
                  {signed(data.follower_movement.delta_7d)}
                </strong>
                <p className="muted small">{data.follower_movement.delta_7d == null ? 'histórico insuficiente' : 'saldo líquido da semana'}</p>
              </article>
              <article className="metricCard">
                <span className="metricLabel">Últimos 30 dias</span>
                <strong className="metricValue" style={{ color: deltaColor(data.follower_movement.delta_30d) }}>
                  {signed(data.follower_movement.delta_30d)}
                </strong>
                <p className="muted small">{data.follower_movement.delta_30d == null ? 'histórico insuficiente' : 'saldo líquido do mês'}</p>
              </article>
            </section>
            <div className="tableLike" style={{ marginTop: 12 }}>
              {data.follower_movement.series.map((d) => (
                <div className="row" key={d.metric_date}>
                  <div className="rowTop">
                    <strong>{new Date(`${d.metric_date}T12:00:00`).toLocaleDateString('pt-BR', { weekday: 'short', day: '2-digit', month: '2-digit' })}</strong>
                    <span className="badge" style={{ color: deltaColor(d.net_change) }}>{signed(d.net_change)}</span>
                  </div>
                  <span className="muted small">
                    {d.followers_count} seguidores no total
                    {d.day_span > 1 ? ` · variação acumulada de ${d.day_span} dias (houve dia sem coleta)` : ''}
                  </span>
                </div>
              ))}
            </div>
            <p className="muted small" style={{ marginTop: 10 }}>
              Este é o <strong>saldo líquido</strong> (quem entrou menos quem saiu), da contagem oficial do Instagram. Um dia negativo significa que houve mais quem deixou de seguir do que quem passou a seguir. A <strong>identidade</strong> de quem deixou de seguir não é fornecida pelo Instagram a nenhuma ferramenta — apps que prometem isso mostram inferência, não dado real.
            </p>
          </>
        ) : (
          <div className="empty">Ainda coletando o histórico diário. O saldo aparece a partir do segundo dia de coleta (todo dia às 06:10, horário da Bahia).</div>
        )}
      </section>

      <section className="splitSection">
        <article className="card" style={{ display: 'grid', gap: 14 }}>
          <div className="rowTop"><h3>Coleta do Instagram · Dra. Daniely</h3><span className="badge">próxima integração</span></div>
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
