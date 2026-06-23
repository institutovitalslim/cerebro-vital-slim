'use client'

import { useEffect, useState } from 'react'

const api = process.env.NEXT_PUBLIC_API_BASE_URL || '/api'
type C = { id: string; format: string; destino: string | null; angulo_nome: string | null; title: string | null; status: string; assets: string[] }

const CONJUNTOS = ['1 · Baseline / oferta clara', '2 · Objeção: culpa / fracasso', "3 · Objeção: 'só mais uma dieta'", '4 · Barreira: preço / valor', '5 · Método / autoridade']

export default function Page() {
  const [items, setItems] = useState<C[]>([])
  useEffect(() => {
    const load = async () => {
      try {
        const r = await fetch(`${api}/generation/creatives?tenant_slug=demo&limit=200`, { cache: 'no-store' })
        const d = await r.json()
        setItems((d.items || []).filter((x: C) => x.status === 'aprovado'))
      } catch {}
    }
    load()
    const t = setInterval(load, 8000)
    return () => clearInterval(t)
  }, [])

  const feed = items.filter((c) => c.destino !== 'meta_ads')
  const meta = items.filter((c) => c.destino === 'meta_ads')
  const metaByAng = (nome: string) => items.filter((c) => c.destino === 'meta_ads' && c.angulo_nome === nome)

  const Thumb = (c: C) => (
    <div key={c.id} style={{ width: 76, aspectRatio: '4 / 5', borderRadius: 12, overflow: 'hidden', background: 'linear-gradient(180deg,#17120d,#0f0b07)', flexShrink: 0, border: '1px solid rgba(186,155,96,0.12)' }}>
      {c.assets[0] ? <img src={`${api}${c.assets[0]}`} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }} /> : null}
    </div>
  )

  return (
    <div className="dashboardRoot">
      <header className="pageHeader heroHeader">
        <div>
          <p className="eyebrow">Motor A · etapa 7</p>
          <h2 className="pageTitle">Planejamento de campanhas</h2>
          <p className="muted">Peças aprovadas, organizadas por destino. O motor já separa o que vira feed e o que entra em Meta Ads dentro da estrutura 5×3.</p>
        </div>
      </header>

      <section className="metricGrid">
        <article className="metricCard">
          <span className="metricLabel">Aprovadas</span>
          <strong className="metricValue">{items.length}</strong>
          <p className="muted small" style={{ margin: 0 }}>prontas para entrar em campanha ou calendário</p>
        </article>
        <article className="metricCard">
          <span className="metricLabel">Meta Ads</span>
          <strong className="metricValue">{meta.length}</strong>
          <p className="muted small" style={{ margin: 0 }}>criativos encaixados na estrutura de aquisição</p>
        </article>
        <article className="metricCard">
          <span className="metricLabel">Feed orgânico</span>
          <strong className="metricValue">{feed.length}</strong>
          <p className="muted small" style={{ margin: 0 }}>peças reservadas para autoridade e relacionamento</p>
        </article>
      </section>

      <section className="section">
        <div className="sectionHeaderInline">
          <div>
            <p className="eyebrow">Estrutura de mídia</p>
            <h3 className="sectionTitle">Meta Ads · 5 conjuntos × 3 criativos</h3>
          </div>
          <span className="muted small">meta ideal: 3 criativos aprovados por conjunto</span>
        </div>

        <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit,minmax(280px,1fr))' }}>
          {CONJUNTOS.map((nome) => {
            const cs = metaByAng(nome)
            return (
              <article key={nome} className="card" style={{ display: 'grid', gap: 12 }}>
                <div className="rowTop">
                  <strong style={{ fontSize: 14 }}>{nome}</strong>
                  <span className="badge">{cs.length}/3</span>
                </div>
                <div style={{ display: 'flex', gap: 10, minHeight: 86, flexWrap: 'wrap' }}>
                  {cs.length ? cs.map(Thumb) : <span className="muted small">Nenhuma aprovada neste conjunto.</span>}
                </div>
              </article>
            )
          })}
        </div>
      </section>

      <section className="section">
        <div className="sectionHeaderInline">
          <div>
            <p className="eyebrow">Orgânico</p>
            <h3 className="sectionTitle">Feed pronto para sequência editorial</h3>
          </div>
          <span className="muted small">{feed.length} aprovadas</span>
        </div>

        {feed.length ? (
          <div className="card" style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
            {feed.map(Thumb)}
          </div>
        ) : (
          <div className="empty">Nenhuma peça de feed aprovada ainda.</div>
        )}
      </section>

      <section className="featurePanel featurePanelDark">
        <span className="badge">Próximo passo</span>
        <p className="muted small" style={{ margin: 0 }}>Enviar peças aprovadas para o calendário com data, dono e status — e exportar os pacotes dos conjuntos para mídia paga.</p>
      </section>
    </div>
  )
}
