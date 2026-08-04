import { fetchJson } from '../api'
import { EmptyState } from '../components/empty-state'

type Theme = { id: string; theme: string; objective: string; format_targets: string[]; created_at: string }

export default async function TemasPage() {
  const data = await fetchJson<{ items: Theme[] }>('/themes?tenant_slug=demo')
  return (
    <div>
      <header className="pageHeader">
        <p className="eyebrow">Temas</p>
        <h2 className="pageTitle">Temas manuais e linhas editoriais</h2>
        <p className="muted">Entrada estratégica para transformar demanda do time em lote de criativos.</p>
      </header>
      {data.items.length === 0 ? (
        <EmptyState title="Nenhum tema cadastrado" hint="Temas são linhas editoriais que viram lotes de criativos. Comece pelo radar de sinais ou crie conteúdo direto." ctas={[{href:"/criar",label:"Criar conteúdo",primary:true},{href:"/fontes",label:"Ver sinais"}]} />
      ) : (
        <div className="tableLike">
          {data.items.map((item) => (
            <div key={item.id} className="row">
              <div className="rowTop"><strong>{item.theme}</strong><span className="badge">{item.format_targets?.join(' · ') || 'sem formato'}</span></div>
              <span className="muted">Objetivo: {item.objective}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
