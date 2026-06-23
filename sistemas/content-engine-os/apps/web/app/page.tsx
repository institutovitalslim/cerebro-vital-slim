import Link from 'next/link'
import { fetchJson } from './api'

type Summary = { counts?: Record<string, number> }
type Creative = { status: string; format: string }
type BI = {
  content_score?: number
  creatives?: { total_creatives: number; approved: number; ready_review: number; changes_requested: number }
  stories?: { stories_sequences: number; stories_approved: number; stories_changes_requested: number }
  funnel?: { story_clicks: number; qualified_dms: number; leads: number; appointments: number }
  diagnosis?: { priority: string; next_actions: string[] }
}

async function safe<T>(p: Promise<T>, fallback: T): Promise<T> {
  try { return await p } catch { return fallback }
}

const lanes = [
  {
    label: '01 · Inteligência',
    title: 'Encontre o sinal certo',
    desc: 'Fontes, BI, roteiros e dores reais antes de criar qualquer coisa.',
    href: '/business-intelligence',
    cta: 'Abrir BI',
    checks: ['perfil da Dra. via RapidAPI', 'fontes e benchmarks', 'roteiros e objeções'],
  },
  {
    label: '02 · Produção',
    title: 'Crie família, não peça solta',
    desc: 'Uma tese vira reel, carrossel, stories, anúncio e variações testáveis.',
    href: '/criar',
    cta: 'Criar família',
    checks: ['hook', 'objeção', 'visual', 'CTA'],
  },
  {
    label: '03 · Aprovação',
    title: 'Aprove ou peça ajuste',
    desc: 'Tudo passa por revisão visual/compliance antes de calendário ou mídia.',
    href: '/banco-criativos',
    cta: 'Revisar fila',
    checks: ['aprovar', 'solicitar alterações', 'baixar pacote'],
  },
  {
    label: '04 · Aprendizado',
    title: 'Meça e realimente',
    desc: 'Performance vira próximo ciclo: campeões, stories, calendário e anúncio.',
    href: '/criativos-campeoes',
    cta: 'Ver campeões',
    checks: ['retenção', 'DM útil', 'lead', 'agendamento'],
  },
]

export default async function HomePage() {
  const [summary, creativesResp, bi] = await Promise.all([
    safe<Summary>(fetchJson<Summary>('/dashboard/summary?tenant_slug=demo'), {}),
    safe<{ items: Creative[] }>(fetchJson('/generation/creatives?tenant_slug=demo&limit=200'), { items: [] }),
    safe<BI>(fetchJson('/bi/overview?tenant_slug=demo'), {}),
  ])
  const creatives = creativesResp.items || []
  const counts = summary.counts || {}
  const readyReview = bi.creatives?.ready_review ?? creatives.filter((c) => c.status === 'renderizado').length
  const approved = bi.creatives?.approved ?? creatives.filter((c) => c.status === 'aprovado').length
  const totalCreatives = bi.creatives?.total_creatives ?? creatives.length
  const stories = bi.stories?.stories_sequences ?? 0
  const appointments = bi.funnel?.appointments ?? 0
  const priority = bi.diagnosis?.priority || 'Escolher uma tese central, criar uma família completa e aprovar antes de publicar.'

  return (
    <div className="dashboardRoot">
      <section className="heroSurface commandHero">
        <div className="heroMain">
          <span className="badge">Cockpit executivo</span>
          <div>
            <p className="eyebrow">Sistema operacional de autoridade</p>
            <h2 className="heroTitle">Conteúdo que nasce com estratégia e morre em aprendizado.</h2>
          </div>
          <p className="heroText">
            O fluxo agora é único: sinal → tese → família de conteúdo → aprovação → publicação → BI → próxima rodada. O usuário não precisa adivinhar onde ir.
          </p>
          <div className="commandNext">
            <span className="metricLabel">Próxima melhor ação</span>
            <strong>{priority}</strong>
          </div>
          <div className="heroActions">
            <Link href="/business-intelligence" className="primaryLink">Começar pelo BI</Link>
            <Link href="/criar" className="secondaryLink">Criar família agora</Link>
            <Link href="/banco-criativos" className="secondaryLink">Aprovar fila</Link>
          </div>
        </div>

        <div className="heroRail">
          <article className="heroMetricCard"><span className="metricLabel">Score do motor</span><strong className="metricValue">{bi.content_score ?? 0}</strong><p className="muted small">soma ponderada de aprovação, conversas e conversões</p></article>
          <article className="heroMetricCard"><span className="metricLabel">Fila para revisar</span><strong className="metricValue">{readyReview}</strong><p className="muted small">peças prontas que precisam de decisão humana</p></article>
          <article className="heroMetricCard"><span className="metricLabel">Aprovados</span><strong className="metricValue">{approved}</strong><p className="muted small">criativos liberados para calendário, orgânico ou mídia</p></article>
        </div>
      </section>

      <section className="section">
        <div className="sectionHeaderInline">
          <div>
            <p className="eyebrow">Fluxo principal</p>
            <h3 className="sectionTitle">O caminho que o usuário deve seguir</h3>
          </div>
          <span className="muted small">sem página solta, sem dúvida operacional</span>
        </div>
        <div className="flowRail">
          {lanes.map((lane) => (
            <Link key={lane.href} href={lane.href} className="flowCard">
              <span className="badge badgeDark">{lane.label}</span>
              <h3>{lane.title}</h3>
              <p className="muted small">{lane.desc}</p>
              <div className="checkGrid">
                {lane.checks.map((check) => <div className="checkRow" key={check}><span className="checkDot" />{check}</div>)}
              </div>
              <span className="secondaryLink">{lane.cta} →</span>
            </Link>
          ))}
        </div>
      </section>

      <section className="metricGrid">
        <article className="metricCard"><span className="metricLabel">Criativos totais</span><strong className="metricValue">{totalCreatives}</strong><p className="muted small">famílias e peças geradas no sistema</p></article>
        <article className="metricCard"><span className="metricLabel">Stories</span><strong className="metricValue">{stories}</strong><p className="muted small">sequências com handoff Clara e tracking</p></article>
        <article className="metricCard"><span className="metricLabel">Agendamentos atribuídos</span><strong className="metricValue">{appointments}</strong><p className="muted small">conversões agregadas por conteúdo</p></article>
        <article className="metricCard"><span className="metricLabel">Calendário</span><strong className="metricValue">{counts.calendar_entries ?? 0}</strong><p className="muted small">entradas editoriais programadas</p></article>
      </section>

      <section className="splitSection">
        <article className="card" style={{ display: 'grid', gap: 14 }}>
          <div className="rowTop"><h3>Modo de uso recomendado</h3><span className="badge">1 tese → 1 família</span></div>
          <div className="checkGrid">
            <div className="checkRow"><span className="checkDot" />Escolha uma tese com base no BI ou radar.</div>
            <div className="checkRow"><span className="checkDot" />Gere uma família: reel, carrossel, stories e anúncio.</div>
            <div className="checkRow"><span className="checkDot" />Aprove ou peça alterações; nada entra no calendário sem revisão.</div>
            <div className="checkRow"><span className="checkDot" />Publique, registre performance e realimente campeões.</div>
          </div>
        </article>
        <article className="card" style={{ display: 'grid', gap: 14 }}>
          <div className="rowTop"><h3>Atalhos de decisão</h3><span className="badge">operacional</span></div>
          <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit,minmax(160px,1fr))' }}>
            <Link className="secondaryLink" href="/fontes">Cadastrar fonte</Link>
            <Link className="secondaryLink" href="/stories-engine">Criar stories</Link>
            <Link className="secondaryLink" href="/planejamento">Planejar campanha</Link>
            <Link className="secondaryLink" href="/calendario">Calendário</Link>
          </div>
        </article>
      </section>
    </div>
  )
}
