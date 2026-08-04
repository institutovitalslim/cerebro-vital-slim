import { fetchJson } from '../api'
import { AssetUploadForm, CalendarEntryForm, StrategyIntakeForm, AdvancedCreativeStudioForm } from '../components/forms'

type WorkflowData = {
  workflow: {
    completion_ratio: number
    completed_steps: number
    total_steps: number
    next_stage: { title: string; description: string; target: string }
    stages: Array<{ key: string; title: string; description: string; done: boolean; target: string }>
  }
}

type AdvisorData = {
  advisor: {
    status_label: string
    diagnosis: string
    priority: string
    next_actions: string[]
    quick_wins: string[]
    warning: string
  }
  engine: { mode: string; model: string }
}

export default async function OperacaoPage() {
  const [workflowData, advisorData] = await Promise.all([
    fetchJson<WorkflowData>('/workflow/state?tenant_slug=demo'),
    fetchJson<AdvisorData>('/dashboard/advisor?tenant_slug=demo'),
  ])

  const progress = Math.round(workflowData.workflow.completion_ratio * 100)

  return (
    <div className="dashboardRoot">
      <section className="heroSurface">
        <div className="heroMain">
          <p className="eyebrow">Operação unificada</p>
          <h1 className="heroTitle">A jornada inteira da máquina de conteúdo em um só lugar.</h1>
          <p className="heroText">
            Em vez de navegar por telas soltas, a equipe consegue ver aqui o estágio da operação,
            o próximo gargalo e o que precisa acontecer para sair de repertório para publicação.
          </p>
          <div className="heroActions">
            <a className="primaryLink" href={workflowData.workflow.next_stage.target}>Atacar próximo passo</a>
            <a className="secondaryLink" href="/">Voltar para visão geral</a>
          </div>
        </div>

        <div className="heroRail">
          <div className="heroMetricCard">
            <span className="metricLabel">Progresso da operação</span>
            <strong>{progress}% concluído</strong>
            <p className="muted">{workflowData.workflow.completed_steps} de {workflowData.workflow.total_steps} blocos operacionais ativos.</p>
          </div>
          <div className="heroMetricCard">
            <span className="metricLabel">Próximo passo</span>
            <strong>{workflowData.workflow.next_stage.title}</strong>
            <p className="muted">{workflowData.workflow.next_stage.description}</p>
          </div>
          <div className="heroMetricCard">
            <span className="metricLabel">Advisor live</span>
            <strong>{advisorData.advisor.status_label}</strong>
            <p className="muted">{advisorData.engine.mode} · {advisorData.engine.model}</p>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="sectionHeaderInline">
          <div>
            <p className="eyebrow">Pipeline</p>
            <h2 className="sectionTitle">Fluxo operacional</h2>
          </div>
        </div>
        <div className="metricGrid">
          {workflowData.workflow.stages.map((stage) => (
            <article key={stage.key} className="metricCard">
              <span className="metricLabel">{stage.done ? 'Concluído' : 'Pendente'}</span>
              <strong>{stage.title}</strong>
              <p className="muted small">{stage.description}</p>
              <a className="secondaryLink" href={stage.target}>Abrir etapa</a>
            </article>
          ))}
        </div>
      </section>

      <section className="section splitSection">
        <article className="featurePanel featurePanelDark">
          <p className="eyebrow">Diagnóstico</p>
          <h3>{advisorData.advisor.priority}</h3>
          <p className="muted">{advisorData.advisor.diagnosis}</p>
          <div className="checkGrid">
            {advisorData.advisor.next_actions.map((item) => (
              <div key={item} className="checkRow"><span className="checkDot" />{item}</div>
            ))}
          </div>
        </article>
        <article className="featurePanel">
          <p className="eyebrow">Quick wins</p>
          <h3>Ganhos rápidos para destravar produção</h3>
          <div className="tableLike compactRows">
            {advisorData.advisor.quick_wins.map((item) => (
              <div key={item} className="row"><strong>{item}</strong></div>
            ))}
            <div className="row"><strong>Aviso</strong><span className="muted">{advisorData.advisor.warning}</span></div>
          </div>
        </article>
      </section>

      <section className="section">
        <div className="sectionHeaderInline">
          <div>
            <p className="eyebrow">Ação</p>
            <h2 className="sectionTitle">Execute sem sair do fluxo</h2>
          </div>
        </div>
        <div className="grid tripleGrid">
          <StrategyIntakeForm />
          <AssetUploadForm />
          <CalendarEntryForm />
        </div>
      </section>

      <section className="section">
        <AdvancedCreativeStudioForm />
      </section>
    </div>
  )
}
