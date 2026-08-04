import { fetchJson } from '../api'

type Job = { id: string; format: string; status: string; output_payload: Record<string, unknown>; created_at: string }

export default async function JobsPage() {
  const data = await fetchJson<{ items: Job[] }>('/generation/creative-jobs?tenant_slug=demo')
  return (
    <div>
      <header className="pageHeader">
        <p className="eyebrow">Jobs criativos</p>
        <h2 className="pageTitle">Histórico inicial de geração</h2>
        <p className="muted">Fila persistida dos outputs criativos já produzidos pelo sistema.</p>
      </header>
      {data.items.length === 0 ? (
        <div className="empty">Nenhum job criativo foi gerado ainda.</div>
      ) : (
        <div className="tableLike">
          {data.items.map((item) => (
            <div key={item.id} className="row">
              <div className="rowTop"><strong>{item.format}</strong><span className="badge">{item.status}</span></div>
              {'engine_model' in item.output_payload ? (
                <span className="muted">Engine: {String(item.output_payload.engine_model || 'n/d')} · modo: {String(item.output_payload.engine_mode || 'n/d')}</span>
              ) : null}
              <pre style={{ margin: 0, whiteSpace: 'pre-wrap', color: '#5f554d', fontSize: 13 }}>{JSON.stringify(item.output_payload, null, 2)}</pre>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
