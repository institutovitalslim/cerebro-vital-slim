import { InteligenciaCriativa } from '../components/inteligencia'
import { EmptyState } from '../components/empty-state'
import { fetchJson } from '../api'
import { QuickSourceForm } from '../components/forms'
import { SinaisVirais } from '../components/sinais'

type Source = { id: string; network: string; label: string; handle_or_url: string; active: boolean; created_at: string; finalidade?: string | null; objetivo?: string | null }

const NETWORK_COPY: Record<string, string> = {
  instagram: 'Repertório de reels, hooks e narrativas concorrentes.',
  youtube: 'Fontes long-form para extração de temas e autoridade.',
  pubmed: 'Base científica para sustentação de tese e mecanismo.',
}

const FINALIDADE_LABEL: Record<string, string> = {
  viral: '🎯 Conteúdo viral', cientifica: '🔬 Científica', dores_objecoes: '💬 Dores & objeções',
  concorrente: '⚔ Concorrente', tendencias: '📈 Tendências', institucional: '★ Marca', outro: 'Outro',
}

export default async function FontesPage() {
  const data = await fetchJson<{ items: Source[] }>('/sources?tenant_slug=demo')
  const items = data.items || []
  const purp = await fetchJson<{ items: { chave: string; label: string }[] }>('/sources/purposes?tenant_slug=demo').catch(() => ({ items: [] as { chave: string; label: string }[] }))
  const labelMap: Record<string, string> = Object.fromEntries((purp.items || []).map((x) => [x.chave, x.label]))

  return (
    <div className="dashboardRoot">
      <header className="pageHeader heroHeader">
        <div>
          <p className="eyebrow">De onde vêm as boas ideias</p>
          <h2 className="pageTitle">Fontes & sinais</h2>
          <p className="muted">
            Aqui mora o radar do sistema: perfis, canais e bases científicas que abastecem o conteúdo com
            ganchos, provas e respostas às objeções das pacientes.
          </p>
        </div>
      </header>

      <section className="section metricGrid">
        <article className="metricCard">
          <span className="metricLabel">Fontes monitoradas</span>
          <strong className="metricValue">{items.length}</strong>
          <p className="muted small" style={{ margin: 0 }}>ativas para benchmark e inspiração operacional</p>
        </article>
        <article className="metricCard">
          <span className="metricLabel">Cobertura</span>
          <strong className="metricValue">{new Set(items.map((item) => item.network)).size || 0}</strong>
          <p className="muted small" style={{ margin: 0 }}>redes ou bases diferentes alimentando o cockpit</p>
        </article>
      </section>

      <section className="splitSection">
        <QuickSourceForm />

        <article className="featurePanel featurePanelDark">
          <span className="badge">Critério IVS</span>
          <div>
            <h3 style={{ marginTop: 0, marginBottom: 8 }}>O que entra como fonte boa</h3>
            <p className="muted small" style={{ margin: 0 }}>
              Fonte boa não é só perfil bonito. Ela precisa render mecanismo, objeção, pauta ou prova reaproveitável.
            </p>
          </div>
          <div className="checkGrid">
            <div className="checkRow"><span className="checkDot" />Hook claro ou padrão narrativo replicável</div>
            <div className="checkRow"><span className="checkDot" />Dor real do avatar mestre do IVS</div>
            <div className="checkRow"><span className="checkDot" />Capacidade de virar reel, carrossel ou anúncio</div>
            <div className="checkRow"><span className="checkDot" />Base segura para compliance e posicionamento</div>
          </div>
        </article>
      </section>

      <section className="section">
        <div className="sectionHeaderInline">
          <div>
            <p className="eyebrow">Biblioteca ativa</p>
            <h3 className="sectionTitle">Fontes cadastradas</h3>
          </div>
          <span className="muted small">cada fonte abastece repertório, benchmark e testes</span>
        </div>

        {items.length === 0 ? (
          <EmptyState title="Nenhuma fonte cadastrada" hint="Fontes alimentam o radar de sinais que vira tese e criativo. Use o formulário acima para adicionar perfis, blogs ou termos." />
        ) : (
          <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit,minmax(280px,1fr))' }}>
            {items.map((item) => (
              <article key={item.id} className="card" style={{ display: 'grid', gap: 14 }}>
                <div className="rowTop">
                  <div>
                    <strong style={{ fontSize: '1.02rem' }}>{item.label}</strong>
                    <p className="muted small" style={{ margin: '6px 0 0' }}>{NETWORK_COPY[item.network] || 'Fonte cadastrada para alimentar o radar do sistema.'}</p>
                  </div>
                  <span className="badge">{item.network}</span>
                </div>
                <div className="resultBox" style={{ padding: 14 }}>
                  {item.handle_or_url}
                </div>
                {(item.finalidade || item.objetivo) ? (
                  <div style={{ display: 'grid', gap: 4 }}>
                    {item.finalidade ? <span className="badge badgeDark" style={{ width: 'fit-content' }}>{labelMap[item.finalidade] || FINALIDADE_LABEL[item.finalidade] || item.finalidade}</span> : null}
                    {item.objetivo ? <p className="muted small" style={{ margin: 0 }}>{item.objetivo}</p> : null}
                  </div>
                ) : null}
                <div className="rowTop">
                  <span className={`badge ${item.active ? '' : 'badgeDark'}`}>{item.active ? 'ativa' : 'pausada'}</span>
                  <span className="muted small">{new Date(item.created_at).toLocaleDateString('pt-BR')}</span>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>
      <InteligenciaCriativa />
      <SinaisVirais />
    </div>
  )
}