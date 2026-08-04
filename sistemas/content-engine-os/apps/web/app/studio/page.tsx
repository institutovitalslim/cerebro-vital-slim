import { fetchJson } from '../api'
import { AdvancedCreativeStudioForm } from '../components/forms'

type StackStatus = {
  llm_primary: string
  llm_fallback: string
  llm_live: boolean
  auth_provider: string
  database_provider: string
  storage_provider: string
  supabase: { configured: boolean }
}

type Summary = {
  counts: { sources: number; themes: number; opportunities: number; briefings: number; creative_jobs: number; strategy_intakes: number; assets: number; calendar_entries: number }
}

const pillars = [
  {
    title: 'Reaproveitamento inteligente',
    text: 'Um vídeo, uma consulta ou um insight precisa render vários criativos com ângulos, hooks e públicos diferentes.',
  },
  {
    title: 'Direção para o médico',
    text: 'O produto não pode obrigar o médico a pensar como agência. Ele precisa sugerir o que fazer agora.',
  },
  {
    title: 'Conteúdo com função',
    text: 'Cada peça deve nascer com papel claro: atrair, educar, quebrar objeção ou converter.',
  },
]

export default async function StudioPage() {
  const [stack, summary] = await Promise.all([
    fetchJson<StackStatus>('/platform/stack'),
    fetchJson<Summary>('/dashboard/summary?tenant_slug=demo'),
  ])

  return (
    <div>
      <header className="pageHeader heroHeader">
        <div>
          <p className="eyebrow">Studio premium</p>
          <h2 className="pageTitle">Criar conteúdo como produto, não como improviso</h2>
          <p className="muted">
            Este estúdio está sendo desenhado para dar aos médicos uma sensação de clareza, direção e velocidade muito superior à de agências caras que entregam material genérico.
          </p>
        </div>
        <div className="heroCallout">
          <span className="badge">Engine principal</span>
          <strong>{stack.llm_primary}</strong>
          <p className="muted" style={{ margin: 0 }}>
            Auth: {stack.auth_provider} · Banco: {stack.database_provider} · Storage: {stack.storage_provider}
          </p>
          <p className="muted" style={{ margin: 0 }}>
            Live: {stack.llm_live ? 'sim' : 'não'} · Fallback: {stack.llm_fallback}
          </p>
        </div>
      </header>

      <section className="grid cards">
        {pillars.map((item) => (
          <article key={item.title} className="card">
            <h3>{item.title}</h3>
            <p className="muted">{item.text}</p>
          </article>
        ))}
      </section>

      <section className="section grid" style={{ gridTemplateColumns: '1fr 1fr' }}>
        <AdvancedCreativeStudioForm />
        <article className="card">
          <h3>Como o Studio deve se comportar</h3>
          <div className="tableLike">
            <div className="row"><span className="muted">1. Receber tema, público e objetivo em linguagem humana.</span></div>
            <div className="row"><span className="muted">2. Sugerir peça principal com ângulo claro.</span></div>
            <div className="row"><span className="muted">3. Derivar hooks, públicos e reaproveitamentos.</span></div>
            <div className="row"><span className="muted">4. Passar por quality gate antes de virar produção final.</span></div>
          </div>
        </article>
      </section>

      <section className="section grid" style={{ gridTemplateColumns: '1fr 1fr' }}>
        <article className="card">
          <h3>Placar atual do workspace</h3>
          <div className="tableLike">
            <div className="row"><div className="rowTop"><strong>Fontes</strong><span className="badge">{summary.counts.sources}</span></div></div>
            <div className="row"><div className="rowTop"><strong>Temas</strong><span className="badge">{summary.counts.themes}</span></div></div>
            <div className="row"><div className="rowTop"><strong>Oportunidades</strong><span className="badge">{summary.counts.opportunities}</span></div></div>
            <div className="row"><div className="rowTop"><strong>Briefings</strong><span className="badge">{summary.counts.briefings}</span></div></div>
            <div className="row"><div className="rowTop"><strong>Jobs criativos</strong><span className="badge">{summary.counts.creative_jobs}</span></div></div>
            <div className="row"><div className="rowTop"><strong>Intakes estratégicos</strong><span className="badge">{summary.counts.strategy_intakes}</span></div></div>
            <div className="row"><div className="rowTop"><strong>Assets</strong><span className="badge">{summary.counts.assets}</span></div></div>
            <div className="row"><div className="rowTop"><strong>Calendário</strong><span className="badge">{summary.counts.calendar_entries}</span></div></div>
          </div>
        </article>
        <article className="card">
          <h3>Critérios do produto final</h3>
          <ul className="muted" style={{ paddingLeft: 18, marginBottom: 0 }}>
            <li>fricção mínima</li>
            <li>linguagem humana</li>
            <li>output premium</li>
            <li>reaproveitamento nativo</li>
            <li>aprendizagem com performance</li>
            <li>identidade superior ao padrão agência</li>
          </ul>
        </article>
      </section>
    </div>
  )
}
