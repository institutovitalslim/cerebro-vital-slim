import Link from 'next/link'
import { fetchJson } from '../api'

type TopItem = {
  title: string
  format: string
  learning_score: number
  sprint_thesis?: string | null
  sprint_hook?: string | null
  origin_tag?: string | null
  metrics?: Record<string, number | string | null>
  conversion_hint?: { whatsapp_leads: number; appointments: number; saves: number; shares: number }
}

type Bucket = {
  dimension: string
  value: string
  count: number
  avg_score: number
  reach: number
  leads: number
  appointments: number
  examples: { title: string; score: number; status: string }[]
}

type Learning = {
  phase: string
  mode: string
  governance: { auto_publish: boolean; auto_dm: boolean; zapi_write: boolean; external_actions: string; note: string }
  summary: { measured_items: number; registered_publications?: number; metrics_pending: number; champions_ready?: number; diagnosis: string }
  winners: {
    top_items: TopItem[]
    by_format: Bucket[]
    by_hook: Bucket[]
    by_origin: Bucket[]
    by_cta: Bucket[]
    by_objection?: Bucket[]
    by_visual?: Bucket[]
    by_pillar?: Bucket[]
  }
  next_sprint_seed: { thesis: string; hook: string; objective: string; audience_stage: string; reason: string; champion_variables?: Record<string, string | null> }
  recommendations: string[]
}

const fallback: Learning = {
  phase: 'fase_3_performance_learning',
  mode: 'read_only_recommendation',
  governance: { auto_publish: false, auto_dm: false, zapi_write: false, external_actions: 'blocked_by_default', note: 'Aprendizado vira hipótese operacional.' },
  summary: { measured_items: 0, metrics_pending: 0, diagnosis: 'Ainda não há dados medidos.' },
  winners: { top_items: [], by_format: [], by_hook: [], by_origin: [], by_cta: [] },
  next_sprint_seed: {
    thesis: 'O corpo travado não é falta de força de vontade; é sinal de mecanismo metabólico não investigado.',
    hook: 'Por que fazer tudo certo pode não destravar seu corpo',
    objective: 'autoridade_e_conversa',
    audience_stage: 'consciente_da_dor',
    reason: 'Fallback seguro até haver métricas suficientes.',
  },
  recommendations: ['Registrar métricas das publicações para ativar recomendações reais.'],
}

async function safe<T>(promise: Promise<T>, fallbackValue: T): Promise<T> {
  try { return await promise } catch { return fallbackValue }
}

function BucketList({ title, items }: { title: string; items: Bucket[] }) {
  return (
    <article className="featurePanel">
      <div className="sectionHeaderInline">
        <div>
          <p className="eyebrow">Ranking</p>
          <h3 className="sectionTitle">{title}</h3>
        </div>
        <span className="badge">{items.length} sinais</span>
      </div>
      {items.length === 0 ? <p className="muted">Sem dados medidos ainda.</p> : (
        <div className="tableLike">
          {items.map((item) => (
            <div className="row" key={`${item.dimension}-${item.value}`}>
              <div className="rowTop">
                <strong>{item.value}</strong>
                <span className="badge">score {item.avg_score}</span>
              </div>
              <span className="muted small">{item.count} peça(s) · alcance {item.reach} · leads {item.leads} · agendamentos {item.appointments}</span>
              {item.examples?.length ? <p className="muted small" style={{ margin: '6px 0 0' }}>Ex.: {item.examples[0].title}</p> : null}
            </div>
          ))}
        </div>
      )}
    </article>
  )
}

export default async function AprendizadoPage() {
  const data = await safe<Learning>(fetchJson('/learning/insights?tenant_slug=demo'), fallback)
  const sprintHref = `/sprint-semanal?thesis=${encodeURIComponent(data.next_sprint_seed.thesis)}&objective=${encodeURIComponent(data.next_sprint_seed.objective)}&audience_stage=${encodeURIComponent(data.next_sprint_seed.audience_stage)}`

  return (
    <div className="dashboardRoot">
      <header className="pageHeader heroHeader">
        <div>
          <p className="eyebrow">Fase 3 · performance por variável</p>
          <h2 className="pageTitle">Aprendizado de performance</h2>
          <p className="heroText">Registra publicação vinculada ao criativo, importa métricas reais já coletadas e transforma hook, objeção, visual, CTA, pilar e formato em hipóteses para o próximo sprint. Não publica, não envia DM e não escreve em WhatsApp.</p>
        </div>
        <div className="heroActions">
          <Link className="secondaryLink" href="/calendario">Fechar métricas</Link>
          <Link className="primaryButton" href={sprintHref}>Abrir próximo sprint</Link>
        </div>
      </header>

      <section className="metricGrid">
        <article className="metricCard"><span className="metricLabel">Peças medidas</span><strong className="metricValue">{data.summary.measured_items}</strong><p className="muted small">base real do aprendizado</p></article>
        <article className="metricCard"><span className="metricLabel">Publicações registradas</span><strong className="metricValue">{data.summary.registered_publications || 0}</strong><p className="muted small">criativo → publicação</p></article>
        <article className="metricCard"><span className="metricLabel">Métricas pendentes</span><strong className="metricValue">{data.summary.metrics_pending}</strong><p className="muted small">publicadas sem fechamento</p></article>
        <article className="metricCard"><span className="metricLabel">Campeões prontos</span><strong className="metricValue">{data.summary.champions_ready || 0}</strong><p className="muted small">score interno ≥ 70</p></article>
      </section>

      <section className="heroSurface commandHero">
        <div className="heroMain">
          <span className="badge">Diagnóstico</span>
          <h3 className="sectionTitle">{data.summary.diagnosis}</h3>
          <div className="resultBox">
            <strong>Próxima tese sugerida:</strong>
            <p style={{ margin: '8px 0 0' }}>{data.next_sprint_seed.thesis}</p>
            <p className="muted small" style={{ margin: '8px 0 0' }}><strong>Hook:</strong> {data.next_sprint_seed.hook}</p>
            <p className="muted small" style={{ margin: '8px 0 0' }}>{data.next_sprint_seed.reason}</p>
            {data.next_sprint_seed.champion_variables ? (
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginTop: 10 }}>
                {Object.entries(data.next_sprint_seed.champion_variables).filter(([, value]) => Boolean(value)).map(([key, value]) => (
                  <span className="badge" key={key}>{key}: {value}</span>
                ))}
              </div>
            ) : null}
          </div>
        </div>
        <article className="featurePanel featurePanelDark">
          <span className="badge">Recomendações</span>
          <div className="checkGrid">
            {data.recommendations.map((item, index) => (
              <div className="row" key={index}>
                <strong>{index + 1}. {item}</strong>
              </div>
            ))}
          </div>
        </article>
      </section>

      <section className="splitSection">
        <BucketList title="Formatos vencedores" items={data.winners.by_format} />
        <BucketList title="Hooks vencedores" items={data.winners.by_hook} />
      </section>

      <section className="splitSection">
        <BucketList title="Objeções vencedoras" items={data.winners.by_objection || []} />
        <BucketList title="Visuais vencedores" items={data.winners.by_visual || []} />
      </section>

      <section className="splitSection">
        <BucketList title="Pilares vencedores" items={data.winners.by_pillar || []} />
        <BucketList title="CTAs" items={data.winners.by_cta} />
      </section>

      <section className="splitSection">
        <BucketList title="Origem / sprint tag" items={data.winners.by_origin} />
        <article className="featurePanel featurePanelDark">
          <span className="badge">Governança</span>
          <h3 className="sectionTitle">Importação sem ação externa</h3>
          <p className="muted small">A Fase 3 aceita métricas já obtidas por João/Meta/Instagram e registra no motor. Ela não publica, não puxa lead e não envia mensagem automaticamente.</p>
          <div className="resultBox">Endpoint: <strong>POST /api/learning/metrics-import</strong></div>
        </article>
      </section>

      <section className="section">
        <div className="sectionHeaderInline">
          <div>
            <p className="eyebrow">Peças líderes</p>
            <h3 className="sectionTitle">Top peças medidas</h3>
          </div>
          <span className="muted small">score interno ponderado</span>
        </div>
        {data.winners.top_items.length === 0 ? <div className="empty">Nenhuma peça medida ainda.</div> : (
          <div className="tableLike">
            {data.winners.top_items.map((item, index) => (
              <div className="row" key={`${item.title}-${index}`}>
                <div className="rowTop">
                  <strong>{index + 1}. {item.title}</strong>
                  <span className="badge">score {item.learning_score}</span>
                </div>
                <span className="muted small">{item.format} · {item.origin_tag || 'sem origem'} · leads {item.conversion_hint?.whatsapp_leads || 0} · agendamentos {item.conversion_hint?.appointments || 0}</span>
                {item.sprint_hook ? <div className="resultBox"><strong>Hook:</strong> {item.sprint_hook}</div> : null}
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  )
}
