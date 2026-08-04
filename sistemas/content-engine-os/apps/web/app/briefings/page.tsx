import { fetchJson } from '../api'
import { EmptyState } from '../components/empty-state'

type Briefing = { id: string; title: string; thesis: string; mechanism: string; cta: string }

export default async function BriefingsPage() {
  const data = await fetchJson<{ items: Briefing[] }>('/briefings?tenant_slug=demo')
  return (
    <div>
      <header className="pageHeader">
        <p className="eyebrow">Briefings</p>
        <h2 className="pageTitle">Briefings prontos para produção</h2>
        <p className="muted">Base operacional para reels, carrosséis, stories, anúncios e variações.</p>
      </header>
      {data.items.length === 0 ? (
        <EmptyState title="Nenhum briefing ainda" hint="Briefings são a base pronta para produzir reels, carrosséis e anúncios a partir de uma tese." ctas={[{href:"/criar",label:"Criar conteúdo",primary:true},{href:"/banco-roteiros",label:"Banco de roteiros"}]} />
      ) : (
        <div className="tableLike">
          {data.items.map((item) => (
            <div key={item.id} className="row">
              <div className="rowTop"><strong>{item.title}</strong><span className="badge">Briefing</span></div>
              <span className="muted">{item.thesis}</span>
              <span className="muted">Mecanismo: {item.mechanism}</span>
              <span className="muted">CTA: {item.cta}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
