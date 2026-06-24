import Link from 'next/link'
import { fetchJson } from '../api'

type Assessment = {
  id: string
  creative_id: string
  title?: string | null
  format?: string | null
  status: string
  risk_level: string
  score: number
  claims: { topic: string; matched_terms?: string[]; excerpt?: string }[]
  red_flags: { code: string; suggestion: string }[]
  evidence: { topic: string; title: string; year?: number; evidence_level?: string; link?: string; main_claim?: string }[]
  missing_sources: unknown[]
  fixes: string[]
  created_at: string
}

type Source = { topic?: string | null; title: string; authors?: string | null; year?: number | null; evidence_level?: string | null; main_claim?: string | null; link?: string | null }
type Pending = { id: string; title?: string | null; format: string; status: string; quality_score?: number | null; created_at: string }
type Overview = {
  phase: string
  mode: string
  summary: { assessments: number; high_risk: number; medium_risk: number; low_risk: number; avg_score: number }
  recent_assessments: Assessment[]
  pending_creatives: Pending[]
  scientific_sources: Source[]
  governance: Record<string, string | boolean>
}

const fallback: Overview = {
  phase: 'fase_5_scientific_compliance',
  mode: 'pre_publication_risk_gate',
  summary: { assessments: 0, high_risk: 0, medium_risk: 0, low_risk: 0, avg_score: 0 },
  recent_assessments: [],
  pending_creatives: [],
  scientific_sources: [],
  governance: { auto_publish: false, auto_dm: false, zapi_write: false },
}

async function safe<T>(promise: Promise<T>, fallbackValue: T): Promise<T> {
  try { return await promise } catch { return fallbackValue }
}

function RiskBadge({ risk }: { risk: string }) {
  const label = risk === 'high' ? 'alto risco' : risk === 'medium' ? 'risco médio' : 'baixo risco'
  return <span className={`badge ${risk === 'low' ? '' : 'badgeDark'}`}>{label}</span>
}

export default async function CompliancePage() {
  const data = await safe<Overview>(fetchJson('/compliance/overview?tenant_slug=demo'), fallback)
  return (
    <div className="dashboardRoot">
      <header className="pageHeader heroHeader">
        <div>
          <p className="eyebrow">Fase 5 · científico/compliance premium</p>
          <h2 className="pageTitle">Painel de compliance médico</h2>
          <p className="heroText">Classifica claims clínicos, exige evidência quando necessário, detecta promessa/diagnóstico/prescrição e bloqueia publicação de alto risco antes de sair para o calendário.</p>
        </div>
        <div className="heroActions">
          <Link className="secondaryLink" href="/banco-criativos">Revisar criativos</Link>
          <Link className="primaryButton" href="/calendario">Calendário</Link>
        </div>
      </header>

      <section className="metricGrid">
        <article className="metricCard"><span className="metricLabel">Avaliações</span><strong className="metricValue">{data.summary.assessments || 0}</strong><p className="muted small">criativos revisados</p></article>
        <article className="metricCard"><span className="metricLabel">Alto risco</span><strong className="metricValue">{data.summary.high_risk || 0}</strong><p className="muted small">bloqueia publicação</p></article>
        <article className="metricCard"><span className="metricLabel">Risco médio</span><strong className="metricValue">{data.summary.medium_risk || 0}</strong><p className="muted small">exige ajuste/fonte</p></article>
        <article className="metricCard"><span className="metricLabel">Score médio</span><strong className="metricValue">{Number(data.summary.avg_score || 0).toFixed(1)}</strong><p className="muted small">segurança editorial</p></article>
      </section>

      <section className="heroSurface commandHero">
        <div className="heroMain">
          <span className="badge">Gate antes da publicação</span>
          <h3 className="sectionTitle">Alto risco não avança para publicado.</h3>
          <p className="muted small">Promessa de resultado, diagnóstico público, prescrição/dose e antes/depois sem contexto entram como risco alto. Claims clínicos sem fonte entram como risco médio.</p>
        </div>
        <article className="featurePanel featurePanelDark">
          <span className="badge">Governança</span>
          <div className="checkGrid">
            <div className="checkRow"><span className="checkDot" />Sem promessa de resultado, cura ou garantia</div>
            <div className="checkRow"><span className="checkDot" />Sem diagnóstico ou prescrição em conteúdo público</div>
            <div className="checkRow"><span className="checkDot" />Claims de hormônios, GLP-1, tireoide, resistência insulínica etc. exigem fonte</div>
            <div className="checkRow"><span className="checkDot" />Disclaimer e CRM visíveis na legenda</div>
          </div>
        </article>
      </section>

      <section className="splitSection">
        <article className="featurePanel">
          <div className="sectionHeaderInline"><div><p className="eyebrow">Fila</p><h3 className="sectionTitle">Criativos pendentes de avaliação</h3></div><span className="badge">{data.pending_creatives.length}</span></div>
          {data.pending_creatives.length === 0 ? <p className="muted">Sem criativos pendentes de avaliação.</p> : <div className="tableLike">
            {data.pending_creatives.map((item) => (
              <div className="row" key={item.id}>
                <div className="rowTop"><strong>{item.title || item.format}</strong><span className="badge">{item.status}</span></div>
                <span className="muted small">{item.format} · score criativo {item.quality_score || 0}</span>
              </div>
            ))}
          </div>}
        </article>

        <article className="featurePanel">
          <div className="sectionHeaderInline"><div><p className="eyebrow">Base</p><h3 className="sectionTitle">Fontes científicas de apoio</h3></div><span className="badge">{data.scientific_sources.length}</span></div>
          <div className="tableLike">
            {data.scientific_sources.slice(0, 8).map((src, index) => (
              <div className="row" key={`${src.title}-${index}`}>
                <div className="rowTop"><strong>{src.title}</strong><span className="badge">{src.evidence_level || 'fonte'}</span></div>
                <span className="muted small">{src.topic || 'tema'} · {src.year || 's/d'} · {src.main_claim}</span>
              </div>
            ))}
          </div>
        </article>
      </section>

      <section className="section">
        <div className="sectionHeaderInline"><div><p className="eyebrow">Auditoria</p><h3 className="sectionTitle">Últimas avaliações</h3></div><span className="muted small">pré-publicação</span></div>
        {data.recent_assessments.length === 0 ? <div className="empty">Nenhuma avaliação ainda. Aprovar um criativo ou chamar o endpoint de assessment cria a primeira.</div> : <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit,minmax(340px,1fr))' }}>
          {data.recent_assessments.map((a) => (
            <article className="card" key={a.id} style={{ display: 'grid', gap: 12 }}>
              <div className="rowTop"><strong>{a.title || a.format || a.creative_id}</strong><RiskBadge risk={a.risk_level} /></div>
              <p className="muted small" style={{ margin: 0 }}>Status: {a.status} · score {Number(a.score || 0).toFixed(1)}</p>
              {a.claims?.length ? <div className="resultBox"><strong>Claims:</strong><br />{a.claims.map((c) => `${c.topic}: ${(c.matched_terms || []).join(', ')}`).join('\n')}</div> : null}
              {a.red_flags?.length ? <div className="resultBox"><strong>Red flags:</strong><br />{a.red_flags.map((f) => `${f.code}: ${f.suggestion}`).join('\n')}</div> : null}
              {a.evidence?.length ? <div className="resultBox"><strong>Evidências:</strong><br />{a.evidence.map((e) => `${e.title} (${e.year || 's/d'})`).join('\n')}</div> : null}
              <div className="resultBox"><strong>Ajustes:</strong><br />{(a.fixes || []).join('\n')}</div>
            </article>
          ))}
        </div>}
      </section>
    </div>
  )
}
