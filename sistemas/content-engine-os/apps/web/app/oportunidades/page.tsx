import { fetchJson } from '../api'
import { EmptyState } from '../components/empty-state'

type Opportunity = { id: string; title: string; angle: string; score: number; source_type: string; status: string }

export default async function OportunidadesPage() {
  const data = await fetchJson<{ items: Opportunity[] }>('/opportunities?tenant_slug=demo')
  return (
    <div>
      <header className="pageHeader">
        <p className="eyebrow">Oportunidades</p>
        <h2 className="pageTitle">Fila de oportunidades editoriais</h2>
        <p className="muted">Sinais transformados em tese, ângulo e prioridade de execução.</p>
      </header>
      {data.items.length === 0 ? (
        <EmptyState title="Nenhuma oportunidade ainda" hint="Sinais do radar viram teses priorizadas aqui. Rode o radar de sinais ou registre um tema para gerar oportunidades." ctas={[{href:"/fontes",label:"Radar de sinais",primary:true},{href:"/criar",label:"Abrir Estúdio"}]} />
      ) : (
        <div className="tableLike">
          {data.items.map((item) => (
            <div key={item.id} className="row">
              <div className="rowTop"><strong>{item.title}</strong><span className="badge">Score {item.score}</span></div>
              <span className="muted">Ângulo: {item.angle} · Origem: {item.source_type} · Status: {item.status}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
