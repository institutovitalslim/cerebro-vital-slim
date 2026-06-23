import Link from 'next/link'
import { fetchJson } from '../api'

type SocialSelling = {
  profile: { profile_handle: string; metric_date: string | null; followers_count: number; following_count: number; posts_count: number; reach: number; impressions: number; profile_views: number; website_clicks: number; whatsapp_clicks: number; source: string }
  aggregate_30d: { likes: number; comments: number; saves: number; shares: number; profile_visits: number; follows: number; whatsapp_clicks: number; avg_engagement_rate: string | number; publications_tracked: number }
  by_status: { status: string; total: number }[]
  by_stage: { consciousness_stage: string; total: number; avg_fit_score: string | number }[]
  candidates: { id: string; public_handle: string; public_name: string | null; interaction_type: string; interaction_count: number; publication_url: string | null; last_interaction_at: string | null; consciousness_stage: string; fit_score: number; status: string; suggested_opening: string | null; guardrails: string[] }[]
  top_publications: { publication_external_id: string; publication_url: string | null; format: string | null; caption_excerpt: string | null; views: number; reach: number; likes: number; comments: number; saves: number; shares: number; follows: number; whatsapp_clicks: number; engagement_rate: string | number }[]
  governance: { mode: string; blocked: string[]; allowed: string[]; approval_required_for: string[] }
  playbook: string[]
}

async function safe<T>(p: Promise<T>, fallback: T): Promise<T> { try { return await p } catch { return fallback } }

export default async function SocialSellingPage() {
  const data = await safe<SocialSelling>(fetchJson('/social-selling/overview?tenant_slug=demo'), {
    profile: { profile_handle: '@dradaniely.freitas', metric_date: null, followers_count: 0, following_count: 0, posts_count: 0, reach: 0, impressions: 0, profile_views: 0, website_clicks: 0, whatsapp_clicks: 0, source: 'rapidapi_pending' },
    aggregate_30d: { likes: 0, comments: 0, saves: 0, shares: 0, profile_visits: 0, follows: 0, whatsapp_clicks: 0, avg_engagement_rate: 0, publications_tracked: 0 },
    by_status: [], by_stage: [], candidates: [], top_publications: [],
    governance: { mode: 'read_only_and_manual_outreach', blocked: [], allowed: [], approval_required_for: [] },
    playbook: [],
  })

  return (
    <div className="dashboardRoot">
      <header className="pageHeader heroHeader">
        <div>
          <p className="eyebrow">Social Selling</p>
          <h2 className="pageTitle">Busca ativa governada a partir de interações reais</h2>
          <p className="heroText">O módulo transforma seguidores e pessoas que interagiram em uma fila de consciência: quem demonstrou atenção, qual sinal deu e qual abordagem manual faz sentido.</p>
        </div>
        <div className="heroActions">
          <Link className="secondaryLink" href="/business-intelligence">Ver BI</Link>
          <Link className="secondaryLink" href="/stories-engine">Conectar Stories</Link>
        </div>
      </header>

      <section className="heroSurface">
        <div className="heroMain">
          <span className="badge">Perfil monitorado</span>
          <h3 className="sectionTitle">{data.profile.profile_handle}</h3>
          <p className="muted">Fonte planejada: RapidAPI. Modo atual: leitura, priorização e roteiro de abordagem. Nenhuma DM é enviada automaticamente.</p>
          <div className="heroActions">
            <Link className="primaryLink" href="/business-intelligence">Analisar publicações</Link>
            <Link className="secondaryLink" href="/fontes">Revisar fontes</Link>
          </div>
        </div>
        <div className="heroRail">
          <article className="heroMetricCard"><span className="metricLabel">Seguidores</span><strong className="metricValue">{data.profile.followers_count ?? 0}</strong><p className="muted small">última coleta: {data.profile.metric_date || 'pendente'}</p></article>
          <article className="heroMetricCard"><span className="metricLabel">Visitas ao perfil</span><strong className="metricValue">{data.profile.profile_views ?? 0}</strong><p className="muted small">sinal de interesse agregado</p></article>
          <article className="heroMetricCard"><span className="metricLabel">Cliques WhatsApp</span><strong className="metricValue">{data.profile.whatsapp_clicks ?? 0}</strong><p className="muted small">intenção de conversa</p></article>
        </div>
      </section>

      <section className="metricGrid">
        <article className="metricCard"><span className="metricLabel">Curtidas 30d</span><strong className="metricValue">{data.aggregate_30d.likes}</strong></article>
        <article className="metricCard"><span className="metricLabel">Comentários 30d</span><strong className="metricValue">{data.aggregate_30d.comments}</strong></article>
        <article className="metricCard"><span className="metricLabel">Salvamentos 30d</span><strong className="metricValue">{data.aggregate_30d.saves}</strong></article>
        <article className="metricCard"><span className="metricLabel">Compartilhamentos 30d</span><strong className="metricValue">{data.aggregate_30d.shares}</strong></article>
        <article className="metricCard"><span className="metricLabel">Novos follows atribuídos</span><strong className="metricValue">{data.aggregate_30d.follows}</strong></article>
      </section>

      <section className="splitSection">
        <article className="card" style={{ display: 'grid', gap: 14 }}>
          <div className="rowTop"><h3>Fila de oportunidades</h3><span className="badge">manual</span></div>
          {data.candidates.length ? (
            <div className="tableLike">
              {data.candidates.map((c) => (
                <div className="row" key={c.id}>
                  <div className="rowTop"><strong>{c.public_handle}</strong><span className="badge">score {c.fit_score}</span></div>
                  <span className="muted small">{c.interaction_type} · {c.interaction_count} interações · {c.consciousness_stage} · {c.status}</span>
                  {c.suggested_opening ? <p className="muted small" style={{ margin: 0 }}>{c.suggested_opening}</p> : null}
                </div>
              ))}
            </div>
          ) : <div className="empty">Ainda não há pessoas coletadas pela RapidAPI. Quando a ingestão entrar, aqui aparecerão perfis públicos que interagiram, classificados por sinal e consciência.</div>}
        </article>

        <article className="card" style={{ display: 'grid', gap: 14 }}>
          <div className="rowTop"><h3>Governança da abordagem</h3><span className="badge">sem automação</span></div>
          <div className="checkGrid">
            {data.playbook.map((item) => <div className="checkRow" key={item}><span className="checkDot" />{item}</div>)}
            <div className="checkRow"><span className="checkDot" />Enviar mensagem exige decisão humana; nada de disparo automático.</div>
          </div>
          <div className="resultBox">Bloqueado: {data.governance.blocked.join(', ') || 'auto_dm, bulk_message, diagnosis, promise_result'}</div>
        </article>
      </section>

      <section className="section grid" style={{ gridTemplateColumns: 'repeat(auto-fit,minmax(280px,1fr))' }}>
        <article className="card" style={{ display: 'grid', gap: 12 }}>
          <h3>Consciência dos potenciais leads</h3>
          {data.by_stage.length ? data.by_stage.map((s) => <div className="row" key={s.consciousness_stage}><div className="rowTop"><strong>{s.consciousness_stage}</strong><span className="badge">{s.total}</span></div><span className="muted small">score médio {s.avg_fit_score}</span></div>) : <p className="muted">Aguardando ingestão de interações.</p>}
        </article>
        <article className="card" style={{ display: 'grid', gap: 12 }}>
          <h3>Publicações que atraem interação</h3>
          {data.top_publications.length ? data.top_publications.map((p) => <div className="row" key={p.publication_external_id}><strong>{p.caption_excerpt || p.publication_external_id}</strong><span className="muted small">{p.likes} likes · {p.comments} comentários · {p.saves} saves · {p.shares} shares</span></div>) : <p className="muted">Aguardando métricas RapidAPI por publicação.</p>}
        </article>
      </section>
    </div>
  )
}
