'use client'

import { useEffect, useState } from 'react'
import { EmptyState } from '../components/empty-state'
import { Chip } from '../components/ui/chip'

const api = process.env.NEXT_PUBLIC_API_BASE_URL || '/api'
type C = { id: string; format: string; destino: string | null; angulo_nome: string | null; title: string | null; status: string; assets: string[] }

// Nomes EXATOS dos ângulos (ANGULOS_META da API) — o encaixe por conjunto é igualdade estrita.
const CONJUNTOS = [
  { nome: '1 · Baseline / oferta clara', curto: '1 · Baseline' },
  { nome: '2 · Objeção: culpa / fracasso', curto: '2 · Culpa' },
  { nome: "3 · Objeção: medo de ser 'só mais uma dieta'", curto: '3 · Só mais uma dieta' },
  { nome: '4 · Barreira: preço / valor percebido', curto: '4 · Preço' },
  { nome: '5 · Método / autoridade', curto: '5 · Método' },
]

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
  const metaByAng = (nome: string) => meta.filter((c) => c.angulo_nome === nome)
  const nomesConjuntos = CONJUNTOS.map((x) => x.nome)
  const metaSemConjunto = meta.filter((c) => !nomesConjuntos.includes(c.angulo_nome || ''))

  const Thumb = (c: C) => (
    <div key={c.id} style={{ width: 76, aspectRatio: '4 / 5', borderRadius: 12, overflow: 'hidden', background: 'linear-gradient(180deg,#17120d,#0f0b07)', flexShrink: 0, border: '1px solid rgba(212,168,60,0.12)' }}>
      {c.assets[0] ? <img src={`${api}${c.assets[0]}`} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }} /> : null}
    </div>
  )

  // Peça de anúncio: miniatura + download do pacote (ZIP com assets + copy + checklist de subida).
  const PecaAds = (c: C) => (
    <div key={c.id} style={{ display: 'flex', gap: 10, alignItems: 'center', minWidth: 0 }}>
      {Thumb(c)}
      <div style={{ display: 'grid', gap: 6, minWidth: 0, flex: 1 }}>
        <span className="muted small" style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={c.title || undefined}>{c.title || 'Sem título'}</span>
        <a className="secondaryLink" style={{ minHeight: 34, padding: '0 12px', fontSize: '0.78rem' }} href={`${api}/publishing/pacote-ads/${c.id}?tenant_slug=demo`}>📦 Baixar pacote do anúncio</a>
      </div>
    </div>
  )

  return (
    <div className="dashboardRoot">
      <header className="pageHeader heroHeader">
        <div>
          <p className="eyebrow">Anúncios prontos para subir</p>
          <h2 className="pageTitle">Planejamento de campanhas</h2>
          <p className="muted">Peças aprovadas, organizadas por destino. O motor já separa o que vira feed e o que entra em Meta Ads dentro da estrutura 5×3.</p>
        </div>
      </header>

      <section className="card" style={{ display: 'flex', gap: 10, flexWrap: 'wrap', alignItems: 'center' }}>
        <span className="muted small" style={{ marginRight: 4 }}>Criativos prontos por conjunto:</span>
        {CONJUNTOS.map(({ nome, curto }) => {
          const n = metaByAng(nome).length
          const cor = n >= 3 ? 'var(--state-good)' : n > 0 ? 'var(--state-warn)' : 'var(--state-bad)'
          return <Chip key={nome} cor={cor}>{`${curto} · ${n}/3`}</Chip>
        })}
      </section>

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
          {CONJUNTOS.map(({ nome }) => {
            const cs = metaByAng(nome)
            return (
              <article key={nome} className="card" style={{ display: 'grid', gap: 12 }}>
                <div className="rowTop">
                  <strong style={{ fontSize: 14 }}>{nome}</strong>
                  <span className="badge">{cs.length}/3</span>
                </div>
                <div style={{ display: 'grid', gap: 10, minHeight: 86, alignContent: 'start' }}>
                  {cs.length ? cs.map(PecaAds) : <span className="muted small">Nenhuma aprovada neste conjunto.</span>}
                </div>
              </article>
            )
          })}
        </div>

        {metaSemConjunto.length ? (
          <article className="card" style={{ display: 'grid', gap: 12 }}>
            <div className="rowTop">
              <strong style={{ fontSize: 14 }}>Meta Ads sem conjunto definido</strong>
              <span className="badge">{metaSemConjunto.length}</span>
            </div>
            <p className="muted small" style={{ margin: 0 }}>Peças aprovadas para anúncio que vieram sem ângulo salvo — o checklist do pacote pede para definir o conjunto na subida.</p>
            <div style={{ display: 'grid', gap: 10 }}>{metaSemConjunto.map(PecaAds)}</div>
          </article>
        ) : null}
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
          <EmptyState title="Nenhuma peça de feed aprovada" hint="Aprove peças no Banco de Criativos para planejá-las no calendário editorial." ctas={[{href:"/banco-criativos",label:"Aprovar criativos",primary:true},{href:"/calendario",label:"Calendário"}]} />
        )}
      </section>

      <section className="featurePanel featurePanelDark">
        <span className="badge">Handoff pronto</span>
        <p className="muted small" style={{ margin: 0 }}>Cada peça de Meta Ads baixa o pacote completo (assets + copy nos 3 campos + checklist de subida com UTM). Próximo passo: enviar as peças de feed para o calendário com data, dono e status.</p>
      </section>
    </div>
  )
}
