import { fetchJson } from '../api'
import { EmptyState } from '../components/empty-state'

// dashboard vivo: sempre renderizar por requisição (nunca prerender estático no build)
export const dynamic = 'force-dynamic'

type AdsOverview = {
  window_days: number
  totals: {
    spend: string | number
    impressions: number
    reach: number
    clicks: number
    link_clicks: number
    messaging_starts: number
    leads: number
    custo_por_conversa: number | null
    from_date?: string | null
    to_date?: string | null
  }
  campaigns: {
    campaign_id: string
    campaign_name: string
    spend: string | number
    impressions: number
    clicks: number
    messaging_starts: number
    leads: number
    custo_por_conversa: string | number | null
    last_active: string
  }[]
  daily: { metric_date: string; spend: string | number; clicks: number; messaging_starts: number }[]
  google: {
    totals: { spend: string | number; impressions: number; clicks: number; conversions: string | number } | null
    campaigns: {
      campaign_id: string
      campaign_name: string
      channel_type: string
      spend: string | number
      clicks: number
      conversions: string | number
      cpa: string | number | null
      last_active: string
    }[]
  }
  readiness: { meta_ads: string; google_ads: string }
}

type AdsDecisao = {
  janela_dias: number
  medianas_canal: { meta: number | null; google: number | null }
  resumo: { verde: number; amarelo: number; vermelho: number }
  campanhas: {
    campaign_id: string
    campaign_name: string
    canal: 'meta' | 'google'
    tipo_resultado: string
    gasto: number
    gasto_ant: number
    resultado: number
    resultado_ant: number
    custo_res: number | null
    custo_res_ant: number | null
    semaforo: 'verde' | 'amarelo' | 'vermelho'
    motivos: string[]
    acao: string
    last_active: string
  }[]
}

const brl = (v: string | number | null | undefined) =>
  v == null ? '—' : Number(v).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
const num = (v: number | null | undefined) => (v == null ? '—' : Number(v).toLocaleString('pt-BR'))
const dia = (d: string) => new Date(`${d}T12:00:00`).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })

const SEMAFORO = {
  verde: { dot: '🟢', rotulo: 'Escalar', cor: '#2f9e63' },
  amarelo: { dot: '🟡', rotulo: 'Observar', cor: '#c9a227' },
  vermelho: { dot: '🔴', rotulo: 'Agir', cor: '#c0524d' },
} as const

export default async function Page() {
  const [data, decisao] = await Promise.all([
    fetchJson<AdsOverview>('/ads/overview?tenant_slug=demo&days=30').catch(() => null),
    fetchJson<AdsDecisao>('/ads/decisao?tenant_slug=demo&days=7').catch(() => null),
  ])
  const t = data?.totals

  return (
    <div className="dashboardRoot">
      <header className="pageHeader heroHeader">
        <div>
          <p className="eyebrow">Visão geral dos canais pagos</p>
          <h2 className="pageTitle">Ads &amp; canais pagos</h2>
          <p className="muted">Totais e ritmo diário dos canais. Para decidir e executar — criativo a criativo, termo a termo — use a Central de Tráfego.</p>
        </div>
      </header>

      <a href="/trafego" style={{ textDecoration: 'none' }}>
        <section className="featurePanel" style={{ marginBottom: 16, borderLeft: '3px solid #c9a227', cursor: 'pointer' }}>
          <div className="rowTop">
            <strong>🎯 Central de Tráfego — decisão e execução</strong>
            <span className="badge" style={{ background: '#c9a227', color: '#141210' }}>abrir →</span>
          </div>
          <p className="muted small" style={{ margin: '4px 0 0' }}>
            Fila de ações priorizada por dinheiro (negativar termos, pausar/escalar), análise de cada criativo com
            leads reais do WhatsApp por anúncio, termos de pesquisa do Google e lista de negativação pronta.
          </p>
        </section>
      </a>

      {decisao && decisao.campanhas.length ? (
        <section className="section">
          <div className="sectionHeaderInline">
            <div>
              <p className="eyebrow">Decisão de campanhas · últimos {decisao.janela_dias} dias vs {decisao.janela_dias} anteriores</p>
              <h3 className="sectionTitle">O que fazer com cada campanha</h3>
            </div>
            <span className="muted small">
              🟢 {decisao.resumo.verde} escalar · 🟡 {decisao.resumo.amarelo} observar · 🔴 {decisao.resumo.vermelho} agir
            </span>
          </div>
          <div className="tableLike">
            {decisao.campanhas.map((c) => {
              const s = SEMAFORO[c.semaforo]
              return (
                <div className="row" key={`${c.canal}-${c.campaign_id}`} style={{ borderLeft: `3px solid ${s.cor}`, paddingLeft: 12 }}>
                  <div className="rowTop">
                    <strong>
                      {s.dot} {c.campaign_name}
                      <span className="muted small" style={{ marginLeft: 8 }}>{c.canal === 'meta' ? 'Meta' : 'Google'}</span>
                    </strong>
                    <span className="badge" style={{ background: s.cor, color: '#fff' }}>{s.rotulo}: {c.acao}</span>
                  </div>
                  <span className="muted small">
                    {brl(c.gasto)} · {num(c.resultado)} {c.tipo_resultado}{c.resultado === 1 ? '' : 's'}
                    {c.custo_res != null ? ` · ${brl(c.custo_res)}/${c.tipo_resultado}` : ''}
                    {c.custo_res_ant != null ? ` (antes ${brl(c.custo_res_ant)})` : ''}
                  </span>
                  {c.motivos.map((m, i) => (
                    <span className="muted small" key={i} style={{ display: 'block' }}>· {m}</span>
                  ))}
                </div>
              )
            })}
          </div>
        </section>
      ) : null}

      {!data || !data.campaigns.length ? (
        <EmptyState title="Sem dados de campanha na janela" hint="A coleta roda todo dia às 06:50 (horário da Bahia). Se as campanhas estão ativas, os números aparecem aqui após a próxima coleta." />
      ) : (
        <>
          <section className="section metricGrid">
            <article className="metricCard">
              <span className="metricLabel">Investimento · {data.window_days}d</span>
              <strong className="metricValue">{brl(t?.spend)}</strong>
              <p className="muted small" style={{ margin: 0 }}>{t?.from_date ? `${dia(t.from_date)} a ${dia(t.to_date || t.from_date)}` : ''}</p>
            </article>
            <article className="metricCard">
              <span className="metricLabel">Conversas WhatsApp iniciadas</span>
              <strong className="metricValue">{num(t?.messaging_starts)}</strong>
              <p className="muted small" style={{ margin: 0 }}>custo por conversa: {brl(t?.custo_por_conversa)}</p>
            </article>
            <article className="metricCard">
              <span className="metricLabel">Cliques</span>
              <strong className="metricValue">{num(t?.clicks)}</strong>
              <p className="muted small" style={{ margin: 0 }}>{num(t?.link_clicks)} no link</p>
            </article>
            <article className="metricCard">
              <span className="metricLabel">Alcance pago</span>
              <strong className="metricValue">{num(t?.reach)}</strong>
              <p className="muted small" style={{ margin: 0 }}>{num(t?.impressions)} impressões</p>
            </article>
          </section>

          <section className="section">
            <div className="sectionHeaderInline">
              <div>
                <p className="eyebrow">Meta Ads</p>
                <h3 className="sectionTitle">Campanhas na janela</h3>
              </div>
              <span className="muted small">ordenadas por investimento</span>
            </div>
            <div className="tableLike">
              {data.campaigns.map((c) => (
                <div className="row" key={c.campaign_id}>
                  <div className="rowTop">
                    <strong>{c.campaign_name}</strong>
                    <span className="badge">{brl(c.spend)}</span>
                  </div>
                  <span className="muted small">
                    {num(c.clicks)} cliques · {num(c.messaging_starts)} conversas
                    {c.custo_por_conversa != null ? ` (${brl(c.custo_por_conversa)}/conversa)` : ''}
                    {Number(c.leads) > 0 ? ` · ${num(c.leads)} leads` : ''} · ativa até {dia(c.last_active)}
                  </span>
                </div>
              ))}
            </div>
          </section>

          <section className="section">
            <div className="sectionHeaderInline">
              <div>
                <p className="eyebrow">Ritmo diário</p>
                <h3 className="sectionTitle">Investimento e conversas por dia</h3>
              </div>
            </div>
            <div className="tableLike">
              {data.daily.slice(-14).reverse().map((d) => (
                <div className="row" key={d.metric_date}>
                  <div className="rowTop">
                    <strong>{dia(d.metric_date)}</strong>
                    <span className="badge">{brl(d.spend)}</span>
                  </div>
                  <span className="muted small">{num(d.clicks)} cliques · {num(d.messaging_starts)} conversas iniciadas</span>
                </div>
              ))}
            </div>
          </section>
        </>
      )}

      {data?.google?.totals && data.google.campaigns.length ? (
        <section className="section">
          <div className="sectionHeaderInline">
            <div>
              <p className="eyebrow">Google Ads</p>
              <h3 className="sectionTitle">Busca e PMax na janela</h3>
            </div>
            <span className="muted small">
              {brl(data.google.totals.spend)} · {num(data.google.totals.clicks)} cliques · {num(Number(data.google.totals.conversions))} conversões
            </span>
          </div>
          <div className="tableLike">
            {data.google.campaigns.map((c) => (
              <div className="row" key={c.campaign_id}>
                <div className="rowTop">
                  <strong>{c.campaign_name}</strong>
                  <span className="badge">{brl(c.spend)}</span>
                </div>
                <span className="muted small">
                  {c.channel_type === 'SEARCH' ? 'Pesquisa' : c.channel_type} · {num(c.clicks)} cliques · {num(Number(c.conversions))} conversões
                  {c.cpa != null ? ` (${brl(c.cpa)}/conversão)` : ''} · ativa até {dia(c.last_active)}
                </span>
              </div>
            ))}
          </div>
        </section>
      ) : null}

      <section className="splitSection" style={{ marginTop: 12 }}>
        <article className="featurePanel featurePanelDark">
          <span className="badge">Meta Ads</span>
          <strong style={{ fontSize: '1.02rem' }}>Conectado</strong>
          <p className="muted small" style={{ margin: 0 }}>{data?.readiness?.meta_ads || 'coleta diária via API oficial'}</p>
        </article>
        <article className="featurePanel featurePanelDark">
          <span className="badge">Google Ads</span>
          <strong style={{ fontSize: '1.02rem' }}>Conectado</strong>
          <p className="muted small" style={{ margin: 0 }}>{data?.readiness?.google_ads || 'coleta diária via API oficial (read-only)'}</p>
        </article>
      </section>
    </div>
  )
}
