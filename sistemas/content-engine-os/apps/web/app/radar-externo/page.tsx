import Link from 'next/link'
import { fetchJson } from '../api'

type ExternalItem = {
  id: string
  source_profile: string
  source_network: string
  external_id: string
  url?: string | null
  format?: string | null
  caption_excerpt?: string | null
  opportunity_score: number
  source: string
  reverse_engineering?: {
    why_it_worked?: string
    pattern?: string
    avatar_pillar?: string
    adaptation_to_ivs?: string
    suggested_hook?: string
    suggested_formats?: string[]
    compliance_notes?: string[]
  }
}

type Pattern = { pattern_key: string; pattern_type: string; label: string; score: number; examples?: { hook?: string; score?: number; profile?: string }[] }
type Opportunity = { title: string; angle: string; score: number; source_type: string; status: string }
type Overview = {
  phase: string
  mode: string
  summary: { total_items: number; profiles: number; avg_score: number; last_ingest_at?: string | null }
  top_items: ExternalItem[]
  patterns: Pattern[]
  opportunities: Opportunity[]
  governance: Record<string, string | boolean>
  next_step: string
}

const fallback: Overview = {
  phase: 'fase_4_external_reverse_engineering',
  mode: 'read_only_learning',
  summary: { total_items: 0, profiles: 0, avg_score: 0, last_ingest_at: null },
  top_items: [],
  patterns: [],
  opportunities: [],
  governance: { auto_publish: false, auto_dm: false, zapi_write: false },
  next_step: 'Rodar ingestão governada para alimentar oportunidades.',
}

async function safe<T>(promise: Promise<T>, fallbackValue: T): Promise<T> {
  try { return await promise } catch { return fallbackValue }
}

export default async function RadarExternoPage() {
  const data = await safe<Overview>(fetchJson('/external-learning/overview?tenant_slug=demo'), fallback)
  return (
    <div className="dashboardRoot">
      <header className="pageHeader heroHeader">
        <div>
          <p className="eyebrow">Fase 4 · fonte externa read-only</p>
          <h2 className="pageTitle">Radar externo & engenharia reversa</h2>
          <p className="heroText">Ingere sinais públicos via RapidAPI/manual, identifica padrões vencedores e transforma em oportunidades originais para o IVS. Não publica, não envia DM e não copia conteúdo externo literalmente.</p>
        </div>
        <div className="heroActions">
          <Link className="secondaryLink" href="/fontes">Gerenciar fontes</Link>
          <Link className="primaryButton" href="/sprint-semanal">Abrir Sprint</Link>
        </div>
      </header>

      <section className="metricGrid">
        <article className="metricCard"><span className="metricLabel">Sinais ingeridos</span><strong className="metricValue">{data.summary.total_items || 0}</strong><p className="muted small">idempotente por fonte + external_id</p></article>
        <article className="metricCard"><span className="metricLabel">Perfis cobertos</span><strong className="metricValue">{data.summary.profiles || 0}</strong><p className="muted small">fontes externas monitoradas</p></article>
        <article className="metricCard"><span className="metricLabel">Score médio</span><strong className="metricValue">{Number(data.summary.avg_score || 0).toFixed(1)}</strong><p className="muted small">oportunidade editorial</p></article>
        <article className="metricCard"><span className="metricLabel">Modo</span><strong className="metricValue" style={{ fontSize: 24 }}>read-only</strong><p className="muted small">sem ação externa automática</p></article>
      </section>

      <section className="heroSurface commandHero">
        <div className="heroMain">
          <span className="badge">Próximo passo</span>
          <h3 className="sectionTitle">{data.next_step}</h3>
          <p className="muted small">Última ingestão: {data.summary.last_ingest_at ? new Date(data.summary.last_ingest_at).toLocaleString('pt-BR') : 'ainda não registrada'}</p>
        </div>
        <article className="featurePanel featurePanelDark">
          <span className="badge">Governança</span>
          <div className="checkGrid">
            <div className="checkRow"><span className="checkDot" />RapidAPI/manual permitido; sem bypass de scraper</div>
            <div className="checkRow"><span className="checkDot" />Não copiar texto externo literalmente</div>
            <div className="checkRow"><span className="checkDot" />Claims clínicos exigem revisão</div>
            <div className="checkRow"><span className="checkDot" />Sem DM, Z-API ou publicação automática</div>
          </div>
        </article>
      </section>

      <section className="splitSection">
        <article className="featurePanel">
          <div className="sectionHeaderInline"><div><p className="eyebrow">Biblioteca viva</p><h3 className="sectionTitle">Padrões vencedores</h3></div><span className="badge">{data.patterns.length}</span></div>
          {data.patterns.length === 0 ? <p className="muted">Sem padrões ingeridos ainda.</p> : <div className="tableLike">
            {data.patterns.map((p) => (
              <div className="row" key={p.pattern_key}>
                <div className="rowTop"><strong>{p.pattern_type} · {p.label}</strong><span className="badge">score {Number(p.score).toFixed(1)}</span></div>
                <span className="muted small">{p.pattern_key}</span>
                {p.examples?.[0]?.hook ? <p className="muted small" style={{ margin: '6px 0 0' }}>Ex.: {p.examples[0].hook}</p> : null}
              </div>
            ))}
          </div>}
        </article>

        <article className="featurePanel">
          <div className="sectionHeaderInline"><div><p className="eyebrow">Ranking</p><h3 className="sectionTitle">Oportunidades criadas</h3></div><span className="badge">{data.opportunities.length}</span></div>
          {data.opportunities.length === 0 ? <p className="muted">Nenhuma oportunidade criada ainda.</p> : <div className="tableLike">
            {data.opportunities.map((o, index) => (
              <div className="row" key={`${o.title}-${index}`}>
                <div className="rowTop"><strong>{o.title}</strong><span className="badge">score {Number(o.score).toFixed(1)}</span></div>
                <span className="muted small">{o.angle}</span>
              </div>
            ))}
          </div>}
        </article>
      </section>

      <section className="section">
        <div className="sectionHeaderInline"><div><p className="eyebrow">Engenharia reversa</p><h3 className="sectionTitle">Conteúdos externos campeões</h3></div><span className="muted small">adaptar padrão, não copiar peça</span></div>
        {data.top_items.length === 0 ? <div className="empty">Rode a ingestão para popular o radar.</div> : <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit,minmax(320px,1fr))' }}>
          {data.top_items.map((item) => (
            <article className="card" key={item.id} style={{ display: 'grid', gap: 12 }}>
              <div className="rowTop"><strong>{item.source_profile}</strong><span className="badge">score {Number(item.opportunity_score).toFixed(1)}</span></div>
              <p className="muted small" style={{ margin: 0 }}>{item.caption_excerpt}</p>
              <div className="resultBox"><strong>Por que funcionou:</strong><br />{item.reverse_engineering?.why_it_worked || 'Padrão em análise.'}</div>
              <div className="resultBox"><strong>Adaptação IVS:</strong><br />{item.reverse_engineering?.adaptation_to_ivs || 'Transformar em tese original IVS.'}</div>
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                <span className="badge">{item.format || 'conteúdo'}</span>
                <span className="badge badgeDark">{item.reverse_engineering?.pattern || 'padrão'}</span>
                <span className="badge badgeDark">{item.reverse_engineering?.avatar_pillar || 'avatar'}</span>
              </div>
              {item.url ? <Link className="secondaryLink" href={item.url}>Abrir referência</Link> : null}
            </article>
          ))}
        </div>}
      </section>
    </div>
  )
}
