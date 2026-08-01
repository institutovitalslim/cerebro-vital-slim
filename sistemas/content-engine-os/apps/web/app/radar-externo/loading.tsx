export default function RadarExternoLoading() {
  return (
    <div className="dashboardRoot radarRoot radarLoading" role="status" aria-live="polite" aria-busy="true">
      <header className="pageHeader heroHeader radarHero radarStateHero">
        <div className="radarHeroCopy">
          <p className="eyebrow">Inteligência externa governada</p>
          <h2 className="pageTitle">Carregando o Content Radar…</h2>
          <p className="heroText">Validando a sessão, a feature flag e as evidências observadas.</p>
        </div>
      </header>
      <section className="metricGrid radarMetrics" aria-hidden="true">
        {[0, 1, 2, 3].map((item) => <span className="metricCard radarSkeleton" key={item} />)}
      </section>
      <section className="radarStatePanel">
        <span className="radarLoadingLine">Aguarde. Nenhum estado vazio será exibido antes do fim da consulta.</span>
      </section>
    </div>
  )
}
