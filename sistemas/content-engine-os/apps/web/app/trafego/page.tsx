'use client'

import { useEffect, useMemo, useRef, useState } from 'react'

// ————— Central de Tráfego v3 —————
// Filosofia: linguagem que uma criança de 12 anos entende, hierarquia da BM
// (campanha → conjunto → anúncio) e toda tarefa executável em 1 clique.

const api = process.env.NEXT_PUBLIC_API_BASE_URL || '/api'

type Acao = {
  tipo: string; canal: string; titulo: string; impacto_mensal: number | null
  evidencia: string; conflito: string | null
  itens: { termo: string; gasto?: number; cliques?: number; conv?: number; campanha?: string; grupo?: string
    categoria?: string; motivo?: string }[]
  passos: string[]
}
type TermoIA = { termo: string; categoria: string; motivo: string
  campanha: string | null; grupo: string | null; gasto: number; cliques: number }
type Criativo = {
  ad_id: string; ad_name: string | null; campaign_name: string | null; adset_name: string | null
  gasto: number; conversas: number; freq: number | null; thumbnail_url: string | null
  body: string | null; leads_ctwa: number; leads_engajados: number; leads_frios: number
  custo_lead_engajado: number | null; hook_rate: number | null
  instagram_permalink: string | null
  veredito: 'escalar' | 'observar' | 'revisar' | 'pausar'; motivos: string[]
  roteiros_count: number
}
type Roteiro = { titulo: string; hook_3s: string; hooks_alternativos?: string[]
  estrutura: string[]; cta: string; por_que_funciona: string }
type PadraoViral = { codigo: string; classe: string | null; mecanismo: string | null; hook_base: string | null }
type Kw = { campaign_name: string; ad_group_name: string; keyword: string; match_type: string
  kw_status?: string | null; negativada?: boolean; gasto: number; cliques: number; conv: number; cpa: number | null }
type GAd = { campaign_name: string; ad_group_name: string; ad_id: string
  headlines: string[] | null; gasto: number; cliques: number; conv: number; cpa: number | null }
type Termo = { term: string; gasto: number; cliques: number; conv: number
  campaign_name: string; ad_group_name?: string }
type Lead = { phone: string; sender_name: string | null; first_ts: string; ad_title: string | null
  source_id: string; msgs_7d: number; first_text: string | null; conversa_amostra: string | null }
type FluxoPeriodo = { periodo: string; contatos_ativos: number; contatos_novos: number
  msgs_inbound: number; ctwa_leads: number
  fonte_anuncio_ig: number; fonte_anuncio_fb: number; fonte_site_google: number
  fonte_indicacao: number; fonte_outros: number }
type DiaSerie = { dia: string; gasto: number; conversas: number; leads: number; engajados: number }
type Cockpit = {
  janela_dias: number
  resumo: { acoes_total: number; desperdicio_mensal_estimado: number
    mediana_custo_lead_engajado: number | null; leads_ctwa: number; leads_engajados: number }
  acoes: Acao[]; criativos: Criativo[]; termos_negativar: Termo[]; termos_incluir: Termo[]
  termos_negativar_ia: TermoIA[]; negativas_frase: TermoIA[]
  sentinela: { gerada_em: string | null; desatualizada: boolean } | null
  keywords: Kw[]; google_anuncios: GAd[]; leads_recentes: Lead[]
  serie_diaria: DiaSerie[]; gasto_total: number; conversas_total: number
  fluxo_leads: { por_dia: FluxoPeriodo[]; por_semana: FluxoPeriodo[]; por_mes: FluxoPeriodo[] }
  dados_atualizados_em: string | null
}

const brl = (v: number | null | undefined, cents = true) =>
  v == null ? '—' : Number(v).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL',
    minimumFractionDigits: cents ? 2 : 0, maximumFractionDigits: cents ? 2 : 0 })

const C = {
  verde: '#2f9e63', amarelo: '#c9a227', vermelho: '#c0524d',
  fundo: 'rgba(255,255,255,.04)', borda: 'rgba(255,255,255,.09)', ouro: '#c9a227',
}

// ————— peças visuais básicas —————

function Chip({ cor, children }: { cor: string; children: React.ReactNode }) {
  return (
    <span style={{ background: cor, color: '#fff', borderRadius: 99, padding: '3px 12px',
      fontSize: '.75rem', fontWeight: 700, whiteSpace: 'nowrap' }}>{children}</span>
  )
}

function Barra({ valor, max, cor }: { valor: number; max: number; cor: string }) {
  const pct = max > 0 ? Math.max(2, Math.round((valor / max) * 100)) : 0
  return (
    <div style={{ background: 'rgba(255,255,255,.07)', borderRadius: 99, height: 8, width: '100%' }}>
      <div style={{ width: `${pct}%`, height: 8, borderRadius: 99, background: cor }} />
    </div>
  )
}

function BotaoCopiar({ texto, rotulo }: { texto: string; rotulo: string }) {
  const [ok, setOk] = useState(false)
  return (
    <button
      type="button"
      onClick={async () => {
        await navigator.clipboard.writeText(texto)
        setOk(true)
        setTimeout(() => setOk(false), 2500)
      }}
      style={{ background: ok ? C.verde : C.ouro, color: ok ? '#fff' : '#141210', border: 'none',
        borderRadius: 10, padding: '10px 18px', fontWeight: 800, fontSize: '.9rem',
        cursor: 'pointer', whiteSpace: 'nowrap' }}>
      {ok ? '✓ Copiado!' : `📋 ${rotulo}`}
    </button>
  )
}

function CopiarMini({ texto }: { texto: string }) {
  const [ok, setOk] = useState(false)
  return (
    <button
      type="button"
      title={`copiar ${texto}`}
      onClick={async (e) => {
        e.preventDefault()
        e.stopPropagation()
        await navigator.clipboard.writeText(texto)
        setOk(true)
        setTimeout(() => setOk(false), 1800)
      }}
      style={{ background: ok ? C.verde : 'rgba(255,255,255,.08)', color: ok ? '#fff' : 'inherit',
        border: `1px solid ${ok ? C.verde : C.borda}`, borderRadius: 8, padding: '3px 9px',
        fontSize: '.75rem', cursor: 'pointer', flexShrink: 0 }}>
      {ok ? '✓' : '📋'}
    </button>
  )
}

// copia termos num formato de correspondência específico do Google Ads
function CopiarFmt({ texto, rotulo }: { texto: string; rotulo: string }) {
  const [ok, setOk] = useState(false)
  return (
    <button
      type="button"
      title={`copiar como ${rotulo}`}
      onClick={async (e) => {
        e.preventDefault()
        e.stopPropagation()
        await navigator.clipboard.writeText(texto)
        setOk(true)
        setTimeout(() => setOk(false), 1800)
      }}
      style={{ background: ok ? C.verde : 'rgba(255,255,255,.08)', color: ok ? '#fff' : 'inherit',
        border: `1px solid ${ok ? C.verde : C.borda}`, borderRadius: 8, padding: '3px 8px',
        fontSize: '.72rem', cursor: 'pointer', flexShrink: 0, whiteSpace: 'nowrap' }}>
      {ok ? '✓' : rotulo}
    </button>
  )
}

function CopiarFormatos({ termos }: { termos: string[] }) {
  return (
    <span style={{ display: 'inline-flex', gap: 4, alignItems: 'center', flexWrap: 'wrap' }}>
      <CopiarFmt rotulo="[exata]" texto={termos.map((t) => `[${t}]`).join('\n')} />
      <CopiarFmt rotulo={'"frase"'} texto={termos.map((t) => `"${t}"`).join('\n')} />
      <CopiarFmt rotulo="ampla" texto={termos.join('\n')} />
    </span>
  )
}

function Seta({ aberto }: { aberto: boolean }) {
  return <span style={{ display: 'inline-block', transition: 'transform .15s',
    transform: aberto ? 'rotate(90deg)' : 'none', marginRight: 8, opacity: .6 }}>▶</span>
}

// ————— página —————

// trava global: evita duas varreduras da Sentinela ao mesmo tempo (remounts)
let sentinelaEmVoo = false

export default function Page() {
  const [d, setD] = useState<Cockpit | null>(null)
  const [erro, setErro] = useState(false)
  const [dias, setDias] = useState(30)
  const [aba, setAba] = useState<'hoje' | 'campanhas' | 'palavras' | 'leads'>('hoje')
  const [atualizando, setAtualizando] = useState(false)
  const [heroDetalhe, setHeroDetalhe] = useState<Criativo | null>(null)
  // janela atual sempre fresca p/ callbacks longos (atualizar/sentinela levam minutos)
  const diasRef = useRef(dias)
  useEffect(() => { diasRef.current = dias }, [dias])

  const carregar = (n: number) => {
    setErro(false)
    fetch(`${api}/ads/cockpit?tenant_slug=demo&days=${n}`, { credentials: 'include', cache: 'no-store' })
      .then((r) => { if (!r.ok) throw new Error(String(r.status)); return r.json() })
      .then(setD)
      .catch(() => setErro(true))
  }

  async function atualizarDados() {
    if (atualizando) return
    setAtualizando(true)
    try {
      const r = await fetch(`${api}/ads/atualizar`, { method: 'POST', credentials: 'include' })
      if (!r.ok) throw new Error(String(r.status))
      carregar(diasRef.current)
    } catch { /* mantém dados atuais */ }
    setAtualizando(false)
  }

  useEffect(() => { setD(null); carregar(dias) }, [dias])

  // dados com mais de 6h ao abrir a página → atualiza sozinho
  useEffect(() => {
    if (!d?.dados_atualizados_em || atualizando) return
    const idadeH = (Date.now() - new Date(d.dados_atualizados_em).getTime()) / 3.6e6
    if (idadeH > 6) void atualizarDados()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [d?.dados_atualizados_em])

  // há pesquisas mais novas que a última varredura da Sentinela → IA reavalia sozinha
  useEffect(() => {
    if (!d?.sentinela?.desatualizada || sentinelaEmVoo) return
    sentinelaEmVoo = true
    fetch(`${api}/ads/sentinela?tenant_slug=demo`, { method: 'POST', credentials: 'include' })
      .then((r) => { if (r.ok) carregar(diasRef.current) })
      .catch(() => {})
      .finally(() => { sentinelaEmVoo = false })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [d?.sentinela?.desatualizada])

  const abas = [
    { id: 'hoje', rotulo: '✅ O que fazer hoje', badge: d?.acoes.length },
    { id: 'campanhas', rotulo: '📣 Campanhas', badge: undefined },
    { id: 'palavras', rotulo: '🔎 Palavras do Google', badge: d ? d.termos_negativar.length + d.termos_incluir.length + (d.termos_negativar_ia?.length || 0) : undefined },
    { id: 'leads', rotulo: '💬 Leads', badge: d?.leads_recentes.length },
  ] as const

  return (
    <div className="dashboardRoot">
      <header className="pageHeader heroHeader">
        <div>
          <p className="eyebrow">Tráfego pago · Meta + Google</p>
          <h2 className="pageTitle">Central de Tráfego</h2>
        </div>
        <div style={{ display: 'flex', gap: 6, alignItems: 'center', flexWrap: 'wrap' }}>
          {[7, 14, 30].map((n) => (
            <button key={n} type="button" onClick={() => setDias(n)}
              style={{ background: dias === n ? C.ouro : 'transparent', color: dias === n ? '#141210' : 'inherit',
                border: `1px solid ${dias === n ? C.ouro : C.borda}`, borderRadius: 10,
                padding: '7px 14px', fontWeight: 700, cursor: 'pointer' }}>
              {n} dias
            </button>
          ))}
          <button type="button" onClick={atualizarDados} disabled={atualizando}
            title="Busca agora os dados mais recentes na Meta, no Google e no WhatsApp (~1-2 min)"
            style={{ background: atualizando ? 'rgba(47,158,99,.35)' : C.verde, color: '#fff',
              border: 'none', borderRadius: 10, padding: '7px 14px', fontWeight: 800,
              cursor: atualizando ? 'wait' : 'pointer' }}>
            {atualizando ? '⏳ Atualizando…' : '🔄 Atualizar dados'}
          </button>
          {d?.dados_atualizados_em ? (
            <span className="muted small">
              dados de {new Date(d.dados_atualizados_em).toLocaleString('pt-BR', {
                day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })}
            </span>
          ) : null}
        </div>
      </header>

      {erro ? (
        <section className="featurePanel"><strong>Não consegui carregar os dados.</strong>
          <p className="muted small">Recarregue a página; se persistir, as coletas rodam de manhã (06:50–07:05).</p>
        </section>
      ) : !d ? (
        <section className="featurePanel"><p className="muted">Carregando os números das campanhas…</p></section>
      ) : (
        <>
          <Hero d={d} onAbrirMelhor={setHeroDetalhe} />
          <nav style={{ display: 'flex', gap: 8, margin: '18px 0 14px', flexWrap: 'wrap' }}>
            {abas.map((a) => (
              <button key={a.id} type="button" onClick={() => setAba(a.id)}
                style={{ background: aba === a.id ? 'rgba(201,162,39,.16)' : C.fundo,
                  border: `1px solid ${aba === a.id ? C.ouro : C.borda}`,
                  color: 'inherit', borderRadius: 12, padding: '10px 18px', fontWeight: 700,
                  fontSize: '.95rem', cursor: 'pointer' }}>
                {a.rotulo}{a.badge ? ` (${a.badge})` : ''}
              </button>
            ))}
          </nav>
          {aba === 'hoje' && <AbaHoje d={d} />}
          {aba === 'campanhas' && <AbaCampanhas d={d} />}
          {aba === 'palavras' && <AbaPalavras d={d} />}
          {aba === 'leads' && <AbaLeads d={d} />}
          {heroDetalhe ? (
            <ModalCriativo c={heroDetalhe} onClose={() => setHeroDetalhe(null)}
              mediana={d.resumo.mediana_custo_lead_engajado} />
          ) : null}
        </>
      )}
    </div>
  )
}

// ————— faixa de cima: KPIs grandes + gráfico de evolução —————

function Kpi({ rotulo, valor, sub, cor }: { rotulo: string; valor: string; sub?: string; cor?: string }) {
  return (
    <article style={{ background: C.fundo, borderRadius: 14, padding: '14px 16px', textAlign: 'center',
      border: `1px solid ${cor ? cor + '66' : C.borda}`,
      boxShadow: cor ? `inset 0 0 24px ${cor}14` : undefined }}>
      <p style={{ margin: 0, fontSize: '.7rem', textTransform: 'uppercase', letterSpacing: '.08em', opacity: .6 }}>{rotulo}</p>
      <p style={{ margin: '4px 0 0', fontWeight: 800, fontSize: '1.45rem', color: cor || 'inherit' }}>{valor}</p>
      {sub ? <p className="muted small" style={{ margin: '2px 0 0' }}>{sub}</p> : null}
    </article>
  )
}

function Hero({ d, onAbrirMelhor }: { d: Cockpit; onAbrirMelhor: (c: Criativo) => void }) {
  const melhor = d.criativos.filter((c) => c.custo_lead_engajado != null && c.leads_engajados >= 3)
    .sort((a, b) => (a.custo_lead_engajado! - b.custo_lead_engajado!))[0]
  const taxaEng = d.resumo.leads_ctwa ? Math.round((d.resumo.leads_engajados / d.resumo.leads_ctwa) * 100) : null
  return (
    <>
      <section style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 10 }}>
        <Kpi rotulo="Investido na janela" valor={brl(d.gasto_total, false)} sub="Meta + Google" />
        <Kpi rotulo="Conversas iniciadas" valor={String(d.conversas_total)} sub="WhatsApp via anúncio" />
        <Kpi rotulo="Leads bons" valor={String(d.resumo.leads_engajados)} cor={C.verde}
          sub={taxaEng != null ? `${taxaEng}% dos que chegam conversam` : undefined} />
        <Kpi rotulo="R$ por lead bom" valor={brl(d.resumo.mediana_custo_lead_engajado)} cor={C.ouro}
          sub="mediana dos anúncios" />
        <Kpi rotulo="Indo para o lixo" valor={`${brl(d.resumo.desperdicio_mensal_estimado, false)}/mês`}
          cor={C.vermelho} sub={`recuperável em ${d.resumo.acoes_total} ações`} />
        {melhor ? (
          <div onClick={() => onAbrirMelhor(melhor)} style={{ cursor: 'pointer' }}
            title="Ver o anúncio e gerar variações do campeão">
            <article style={{ background: C.fundo, borderRadius: 14, padding: '10px 12px',
              border: `1px solid ${C.verde}88`, boxShadow: `inset 0 0 24px ${C.verde}14`,
              display: 'flex', gap: 10, alignItems: 'center', height: '100%' }}>
              {melhor.thumbnail_url ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img src={melhor.thumbnail_url} alt="" width={52} height={52}
                  style={{ borderRadius: 10, objectFit: 'cover', flexShrink: 0 }} />
              ) : <span style={{ fontSize: '1.6rem' }}>🏆</span>}
              <div style={{ minWidth: 0 }}>
                <p style={{ margin: 0, fontSize: '.7rem', textTransform: 'uppercase',
                  letterSpacing: '.08em', opacity: .6 }}>Melhor anúncio</p>
                <p style={{ margin: '2px 0 0', fontWeight: 800, fontSize: '1.15rem', color: C.verde }}>
                  {brl(melhor.custo_lead_engajado)}/lead
                </p>
                <p className="muted small" style={{ margin: 0, overflow: 'hidden',
                  textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {(melhor.ad_name || '').slice(0, 24)} · 🏆 gerar variações →
                </p>
              </div>
            </article>
          </div>
        ) : (
          <Kpi rotulo="Melhor anúncio" valor="—" sub="sem vencedor na janela" />
        )}
      </section>
      {d.serie_diaria.length >= 5 ? <GraficoEvolucao serie={d.serie_diaria} /> : null}
    </>
  )
}

function GraficoEvolucao({ serie }: { serie: DiaSerie[] }) {
  const [hover, setHover] = useState<number | null>(null)
  const W = 900, H = 220, PAD_L = 56, PAD_R = 40, PAD_B = 30, PAD_T = 14
  const maxGasto = Math.max(...serie.map((s) => s.gasto), 1)
  const maxLeads = Math.max(...serie.map((s) => s.engajados), 1)
  const x = (i: number) => PAD_L + (i * (W - PAD_L - PAD_R)) / Math.max(serie.length - 1, 1)
  const yG = (v: number) => H - PAD_B - (v / maxGasto) * (H - PAD_B - PAD_T - 16)
  const yL = (v: number) => H - PAD_B - (v / maxLeads) * (H - PAD_B - PAD_T - 16)
  const linhaGasto = serie.map((s, i) => `${i ? 'L' : 'M'}${x(i).toFixed(1)},${yG(s.gasto).toFixed(1)}`).join(' ')
  const areaGasto = `${linhaGasto} L${x(serie.length - 1).toFixed(1)},${H - PAD_B} L${PAD_L},${H - PAD_B} Z`
  const linhaLeads = serie.map((s, i) => `${i ? 'L' : 'M'}${x(i).toFixed(1)},${yL(s.engajados).toFixed(1)}`).join(' ')
  const rot = (d: string) => new Date(`${d}T12:00:00`).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })
  // marcas de data: ~1 a cada 4-5 dias, sempre primeira e última
  const passo = Math.max(1, Math.round(serie.length / 7))
  const marcas = serie.map((_, i) => i).filter((i) => i % passo === 0 || i === serie.length - 1)
  // grades horizontais de valor (4 divisões)
  const grades = [0.25, 0.5, 0.75, 1]

  function onMove(e: React.MouseEvent<SVGSVGElement>) {
    const rect = e.currentTarget.getBoundingClientRect()
    const px = ((e.clientX - rect.left) / rect.width) * W
    const i = Math.round(((px - PAD_L) / (W - PAD_L - PAD_R)) * (serie.length - 1))
    setHover(i >= 0 && i < serie.length ? i : null)
  }

  const hv = hover != null ? serie[hover] : null
  return (
    <section style={{ background: C.fundo, border: `1px solid ${C.borda}`, borderRadius: 14,
      padding: '12px 14px', marginTop: 10 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 8 }}>
        <strong className="small">Evolução diária — passe o mouse para os valores exatos</strong>
        <span className="muted small">
          <span style={{ color: C.ouro }}>▬</span> investimento&nbsp;&nbsp;
          <span style={{ color: C.verde }}>▬</span> leads bons&nbsp;&nbsp;
          <span style={{ color: 'rgba(255,255,255,.4)' }}>▬</span> conversas
        </span>
      </div>
      <div style={{ position: 'relative' }}>
        <svg viewBox={`0 0 ${W} ${H}`} style={{ width: '100%', height: 'auto', display: 'block' }}
          onMouseMove={onMove} onMouseLeave={() => setHover(null)}>
          {grades.map((f, i) => (
            <g key={i}>
              <line x1={PAD_L} x2={W - PAD_R} y1={yG(maxGasto * f)} y2={yG(maxGasto * f)}
                stroke="rgba(255,255,255,.07)" strokeWidth={1} />
              <text x={PAD_L - 6} y={yG(maxGasto * f) + 4} fontSize={10}
                fill="rgba(201,162,39,.7)" textAnchor="end">{brl(maxGasto * f, false)}</text>
              <text x={W - PAD_R + 6} y={yL(maxLeads * f) + 4} fontSize={10}
                fill="rgba(47,158,99,.8)" textAnchor="start">{Math.round(maxLeads * f)}</text>
            </g>
          ))}
          <path d={areaGasto} fill="rgba(201,162,39,.12)" />
          <path d={linhaGasto} fill="none" stroke={C.ouro} strokeWidth={2.5} strokeLinejoin="round" />
          <path d={linhaLeads} fill="none" stroke={C.verde} strokeWidth={2.5} strokeLinejoin="round" />
          {serie.map((s, i) => (
            <g key={i}>
              {s.engajados > 0 ? <circle cx={x(i)} cy={yL(s.engajados)} r={3} fill={C.verde} /> : null}
              <circle cx={x(i)} cy={yG(s.gasto)} r={2.5} fill={C.ouro} />
            </g>
          ))}
          {marcas.map((i) => (
            <text key={i} x={x(i)} y={H - 8} fontSize={10.5} fill="rgba(255,255,255,.5)"
              textAnchor={i === 0 ? 'start' : i === serie.length - 1 ? 'end' : 'middle'}>
              {rot(serie[i].dia)}
            </text>
          ))}
          {hover != null ? (
            <line x1={x(hover)} x2={x(hover)} y1={PAD_T} y2={H - PAD_B}
              stroke="rgba(255,255,255,.35)" strokeWidth={1} strokeDasharray="3 3" />
          ) : null}
        </svg>
        {hv ? (
          <div style={{ position: 'absolute', top: 6,
            left: `${Math.min(78, Math.max(2, (x(hover!) / W) * 100))}%`,
            background: '#1b1712', border: `1px solid ${C.borda}`, borderRadius: 10,
            padding: '8px 12px', pointerEvents: 'none', whiteSpace: 'nowrap', zIndex: 5,
            boxShadow: '0 6px 18px rgba(0,0,0,.5)' }}>
            <p className="small" style={{ margin: 0, fontWeight: 800 }}>
              {new Date(`${hv.dia}T12:00:00`).toLocaleDateString('pt-BR', { weekday: 'short', day: '2-digit', month: '2-digit' })}
            </p>
            <p className="small" style={{ margin: '2px 0 0', color: C.ouro }}>investimento: <strong>{brl(hv.gasto)}</strong></p>
            <p className="small" style={{ margin: 0, color: C.verde }}>leads bons: <strong>{hv.engajados}</strong> (de {hv.leads} cliques)</p>
            <p className="small" style={{ margin: 0, opacity: .8 }}>conversas: {hv.conversas}</p>
          </div>
        ) : null}
      </div>
    </section>
  )
}

// ————— aba 1: o que fazer hoje —————

const MATCH_PT: Record<string, string> = { EXACT: 'exata', PHRASE: 'frase', BROAD: 'ampla' }

const CAT_ROTULO: Record<string, string> = {
  outro_medico: '🧑‍⚕️ outro médico', concorrente: '🏢 concorrente',
  gratuito_sus_plano: '🆓 grátis/SUS/plano', outra_cidade: '📍 outra cidade',
  emprego_curso: '🎓 emprego/curso', fora_de_escopo: '🚷 fora do escopo',
}

const ACAO_VISUAL: Record<string, { emoji: string; cor: string; frase: string }> = {
  negativar: { emoji: '🚫', cor: C.vermelho, frase: 'Bloquear pesquisas que só gastam' },
  negativar_ia: { emoji: '🛡️', cor: C.vermelho, frase: 'A IA achou pesquisas que não são seu paciente' },
  pausar_keyword: { emoji: '⏸️', cor: C.vermelho, frase: 'Pausar palavra que não traz cliente' },
  pausar_criativo: { emoji: '⏸️', cor: C.vermelho, frase: 'Pausar anúncio que não funciona' },
  keyword_nova: { emoji: '➕', cor: C.verde, frase: 'Adicionar palavra que traz cliente' },
  novo_criativo: { emoji: '🎬', cor: C.ouro, frase: 'Fazer versão nova do anúncio campeão' },
}

function AbaHoje({ d }: { d: Cockpit }) {
  const [aberta, setAberta] = useState<number | null>(0)
  if (!d.acoes.length) {
    return <section className="featurePanel"><strong>🎉 Nada urgente hoje.</strong>
      <p className="muted small">Nenhum vazamento relevante detectado na janela.</p></section>
  }
  return (
    <section style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      <p className="muted" style={{ margin: '0 0 4px' }}>
        Em ordem do que economiza mais dinheiro. Clique numa tarefa para ver o porquê e executar.
      </p>
      {d.acoes.map((a, i) => {
        const v = ACAO_VISUAL[a.tipo] || { emoji: '•', cor: C.ouro, frase: a.tipo }
        const listaCopia = a.itens.length
          ? a.itens.map((it) => `[${it.termo}]`).join('\n')
          : null
        const abertaEsta = aberta === i
        return (
          <article key={i} className="featurePanel"
            style={{ borderLeft: `4px solid ${v.cor}`, cursor: 'pointer' }}
            onClick={() => setAberta(abertaEsta ? null : i)}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
              <span style={{ fontSize: '1.5rem' }}>{v.emoji}</span>
              <div style={{ flex: 1, minWidth: 220 }}>
                <strong style={{ fontSize: '1.02rem' }}>{i + 1}. {a.titulo}</strong>
                <p className="muted small" style={{ margin: '2px 0 0' }}>{v.frase} · {a.canal === 'meta' ? 'Meta (Instagram/Facebook)' : 'Google'}</p>
              </div>
              {a.impacto_mensal ? (
                <div style={{ textAlign: 'right' }}>
                  <strong style={{ color: v.cor, fontSize: '1.15rem' }}>{brl(a.impacto_mensal, false)}</strong>
                  <p className="muted small" style={{ margin: 0 }}>economia/mês</p>
                </div>
              ) : null}
              <Seta aberto={abertaEsta} />
            </div>
            {abertaEsta ? (
              <div style={{ marginTop: 12, paddingTop: 12, borderTop: `1px solid ${C.borda}` }}
                onClick={(e) => e.stopPropagation()}>
                <p style={{ margin: '0 0 8px' }}><strong>Por quê:</strong> {a.evidencia}</p>
                {a.conflito ? (
                  <p style={{ margin: '0 0 8px', color: C.amarelo }}><strong>⚠ Cuidado:</strong> {a.conflito}</p>
                ) : null}
                {a.itens.length ? (
                  <div style={{ background: 'rgba(0,0,0,.25)', borderRadius: 10, padding: 12, margin: '8px 0' }}>
                    {a.itens.slice(0, 10).map((it, j) => (
                      <div key={j} style={{ padding: '5px 0', borderBottom: '1px solid rgba(255,255,255,.05)' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 10, fontSize: '.88rem' }}>
                          <span style={{ display: 'flex', alignItems: 'center', gap: 8, minWidth: 0, flexWrap: 'wrap' }}>
                            {it.categoria ? <CopiarFormatos termos={[it.termo]} /> : <CopiarMini texto={`[${it.termo}]`} />}
                            <code style={{ overflowWrap: 'anywhere', whiteSpace: 'normal' }}>{it.termo}</code>
                            {it.categoria ? (
                              <span style={{ background: 'rgba(192,82,77,.18)', border: '1px solid rgba(192,82,77,.45)',
                                borderRadius: 99, padding: '1px 9px', fontSize: '.72rem', whiteSpace: 'nowrap' }}>
                                {CAT_ROTULO[it.categoria] || it.categoria}
                              </span>
                            ) : null}
                          </span>
                          <span className="muted" style={{ whiteSpace: 'nowrap' }}>
                            {it.gasto != null ? brl(it.gasto) : ''}{it.conv ? ` · ${it.conv} clientes` : it.cliques ? ` · ${it.cliques} cliques, 0 clientes` : ''}
                          </span>
                        </div>
                        {it.motivo ? (
                          <p className="muted small" style={{ margin: '2px 0 0' }}>💡 {it.motivo}</p>
                        ) : null}
                        {it.campanha ? (
                          <p className="muted small" style={{ margin: '2px 0 0' }}>
                            👉 colocar em: 📣 {it.campanha}{it.grupo ? <> › 📁 <strong>{it.grupo}</strong></> : ' (nível da campanha)'}
                          </p>
                        ) : null}
                      </div>
                    ))}
                    {a.itens.length > 10 ? <p className="muted small" style={{ margin: '4px 0 0' }}>+ {a.itens.length - 10} itens (o botão copia todos)</p> : null}
                  </div>
                ) : null}
                <div style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap', marginTop: 8 }}>
                  {a.tipo === 'negativar_ia' && a.itens.length ? (
                    <span style={{ display: 'inline-flex', gap: 6, alignItems: 'center', flexWrap: 'wrap' }}>
                      <strong className="small">📋 Copiar {a.itens.length === 1 ? 'o termo' : `os ${a.itens.length} termos`} como:</strong>
                      <CopiarFormatos termos={a.itens.map((it) => it.termo)} />
                    </span>
                  ) : listaCopia ? <BotaoCopiar texto={listaCopia} rotulo={`Copiar ${a.itens.length} ${a.itens.length === 1 ? 'termo' : 'termos'}`} /> : null}
                  <details onClick={(e) => e.stopPropagation()}>
                    <summary className="muted small" style={{ cursor: 'pointer' }}>👣 onde clicar, passo a passo</summary>
                    <ol className="small" style={{ margin: '6px 0 0 18px' }}>
                      {a.passos.map((p, j) => (<li key={j} style={{ marginBottom: 3 }}>{p}</li>))}
                    </ol>
                  </details>
                </div>
              </div>
            ) : null}
          </article>
        )
      })}
    </section>
  )
}

// ————— aba 2: campanhas estilo BM (campanha → conjunto → anúncio) —————

const VEREDITO_CHIP: Record<string, { rotulo: string; cor: string }> = {
  escalar: { rotulo: '🟢 pôr mais verba', cor: C.verde },
  observar: { rotulo: '⚪ deixar rodando', cor: '#6f6a61' },
  revisar: { rotulo: '🟡 melhorar', cor: C.amarelo },
  pausar: { rotulo: '🔴 pausar', cor: C.vermelho },
}

function AbaCampanhas({ d }: { d: Cockpit }) {
  const [canal, setCanal] = useState<'meta' | 'google'>('meta')
  const [modo, setModo] = useState<'cards' | 'lista'>('cards')
  return (
    <section>
      <div style={{ display: 'flex', gap: 8, marginBottom: 12, flexWrap: 'wrap', alignItems: 'center' }}>
        {(['meta', 'google'] as const).map((c) => (
          <button key={c} type="button" onClick={() => setCanal(c)}
            style={{ background: canal === c ? 'rgba(201,162,39,.16)' : C.fundo, color: 'inherit',
              border: `1px solid ${canal === c ? C.ouro : C.borda}`, borderRadius: 10,
              padding: '8px 18px', fontWeight: 700, cursor: 'pointer' }}>
            {c === 'meta' ? '📱 Meta (Instagram/Facebook)' : '🔎 Google'}
          </button>
        ))}
        {canal === 'meta' ? (
          <div style={{ marginLeft: 'auto', display: 'flex', gap: 6 }}>
            {(['cards', 'lista'] as const).map((m) => (
              <button key={m} type="button" onClick={() => setModo(m)}
                style={{ background: modo === m ? C.fundo : 'transparent', color: 'inherit',
                  border: `1px solid ${modo === m ? C.ouro : C.borda}`, borderRadius: 8,
                  padding: '6px 12px', fontSize: '.82rem', cursor: 'pointer' }}>
                {m === 'cards' ? '🖼 Cards' : '📊 Lista'}
              </button>
            ))}
          </div>
        ) : null}
      </div>
      {canal === 'meta'
        ? (modo === 'cards' ? <CardsMeta d={d} /> : <ArvoreMeta d={d} />)
        : <ArvoreGoogle d={d} />}
    </section>
  )
}

// ————— cards visuais estilo Seguify: o criativo é o herói —————

function Tile({ rotulo, valor, tom, seta }: {
  rotulo: string; valor: string; tom?: 'bom' | 'ruim' | 'neutro'; seta?: 'cima' | 'baixo'
}) {
  const cor = tom === 'bom' ? C.verde : tom === 'ruim' ? C.vermelho : 'inherit'
  return (
    <div style={{ background: 'rgba(0,0,0,.30)', borderRadius: 10, padding: '8px 10px',
      border: `1px solid ${tom === 'bom' ? 'rgba(47,158,99,.35)' : tom === 'ruim' ? 'rgba(192,82,77,.35)' : C.borda}` }}>
      <p style={{ margin: 0, fontSize: '.62rem', textTransform: 'uppercase', letterSpacing: '.07em', opacity: .55 }}>{rotulo}</p>
      <p style={{ margin: '2px 0 0', fontWeight: 800, fontSize: '.98rem', color: cor }}>
        {valor}{seta ? <span style={{ fontSize: '.8rem', marginLeft: 4 }}>{seta === 'cima' ? '↗' : '↘'}</span> : null}
      </p>
    </div>
  )
}

function CardsMeta({ d }: { d: Cockpit }) {
  const [detalhe, setDetalhe] = useState<Criativo | null>(null)
  const [filtro, setFiltro] = useState<'todos' | 'escalar' | 'problema'>('todos')
  const mediana = d.resumo.mediana_custo_lead_engajado
  const lista = d.criativos.filter((c) =>
    filtro === 'todos' ? true
      : filtro === 'escalar' ? c.veredito === 'escalar'
      : c.veredito === 'revisar' || c.veredito === 'pausar')
  const ordenada = [...lista].sort((a, b) => b.gasto - a.gasto)

  return (
    <div>
      <div style={{ display: 'flex', gap: 6, marginBottom: 12 }}>
        {([['todos', 'Todos'], ['escalar', '🟢 Vencedores'], ['problema', '🔴 Com problema']] as const).map(([id, rot]) => (
          <button key={id} type="button" onClick={() => setFiltro(id)}
            style={{ background: filtro === id ? C.fundo : 'transparent', color: 'inherit',
              border: `1px solid ${filtro === id ? C.ouro : C.borda}`, borderRadius: 99,
              padding: '5px 14px', fontSize: '.82rem', cursor: 'pointer' }}>{rot}</button>
        ))}
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: 14 }}>
        {ordenada.map((c) => {
          const v = VEREDITO_CHIP[c.veredito]
          const custoBom = c.custo_lead_engajado != null && mediana
            ? (c.custo_lead_engajado <= mediana ? 'bom' : c.custo_lead_engajado >= 1.5 * mediana ? 'ruim' : 'neutro')
            : 'neutro'
          const hookTom = c.hook_rate == null ? 'neutro' : c.hook_rate >= 0.25 ? 'bom' : c.hook_rate < 0.15 ? 'ruim' : 'neutro'
          return (
            <article key={c.ad_id}
              style={{ background: C.fundo, border: `1px solid ${C.borda}`, borderRadius: 14,
                overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
              <div style={{ position: 'relative', aspectRatio: '4 / 3', background: '#0d0b09' }}>
                {c.thumbnail_url ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={c.thumbnail_url} alt=""
                    style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                ) : (
                  <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center',
                    justifyContent: 'center', fontSize: '2rem', opacity: .3 }}>🖼</div>
                )}
                <span style={{ position: 'absolute', top: 8, left: 8, background: 'rgba(0,0,0,.65)',
                  borderRadius: 6, padding: '2px 8px', fontSize: '.66rem', fontWeight: 800,
                  letterSpacing: '.06em' }}>
                  {(c as unknown as { object_type?: string }).object_type === 'VIDEO' || c.hook_rate != null ? 'VÍDEO' : 'ANÚNCIO'}
                </span>
                <span style={{ position: 'absolute', top: 8, right: 8 }}>
                  <Chip cor={v.cor}>{v.rotulo}</Chip>
                </span>
              </div>
              <div style={{ padding: '10px 12px', display: 'flex', flexDirection: 'column', gap: 8, flex: 1 }}>
                <div>
                  <p style={{ margin: 0, fontWeight: 700, fontSize: '.9rem', overflow: 'hidden',
                    textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{c.ad_name || c.ad_id}</p>
                  <p className="muted small" style={{ margin: 0, overflow: 'hidden',
                    textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{c.campaign_name}</p>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 6 }}>
                  <Tile rotulo="Investido" valor={brl(c.gasto, false)} />
                  <Tile rotulo="Leads bons" valor={String(c.leads_engajados)}
                    tom={c.leads_engajados > 0 ? 'bom' : c.gasto >= 50 ? 'ruim' : 'neutro'} />
                  <Tile rotulo="R$ / lead bom"
                    valor={c.custo_lead_engajado != null ? brl(c.custo_lead_engajado, false) : '—'}
                    tom={custoBom} seta={custoBom === 'bom' ? 'cima' : custoBom === 'ruim' ? 'baixo' : undefined} />
                  <Tile rotulo="Prendem no vídeo"
                    valor={c.hook_rate != null ? `${Math.round(c.hook_rate * 100)}%` : '—'}
                    tom={hookTom} seta={hookTom === 'bom' ? 'cima' : hookTom === 'ruim' ? 'baixo' : undefined} />
                </div>
                <p className="muted small" style={{ margin: 0 }}>
                  💬 {c.conversas} conversas · 🔥 {c.leads_engajados} · 🧊 {c.leads_frios}
                  {c.freq != null ? ` · 👁 ${c.freq.toFixed(1)}x` : ''}
                </p>
                {c.roteiros_count > 0 ? (
                  <p className="small" style={{ margin: 0, color: C.verde, fontWeight: 700 }}>
                    🎬 roteiros prontos para gravar
                  </p>
                ) : null}
                <button type="button" onClick={() => setDetalhe(c)}
                  style={{ marginTop: 'auto', background: 'transparent', border: `1px solid ${C.ouro}`,
                    color: C.ouro, borderRadius: 10, padding: '8px 0', fontWeight: 700,
                    fontSize: '.85rem', cursor: 'pointer' }}>
                  ✨ Raio-X do anúncio
                </button>
              </div>
            </article>
          )
        })}
      </div>
      {detalhe ? <ModalCriativo c={detalhe} onClose={() => setDetalhe(null)} mediana={mediana} /> : null}
    </div>
  )
}

function ModalCriativo({ c, onClose, mediana }: { c: Criativo; onClose: () => void; mediana: number | null }) {
  const v = VEREDITO_CHIP[c.veredito]
  return (
    <div onClick={onClose}
      style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,.65)', zIndex: 60,
        display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 18 }}>
      <article onClick={(e) => e.stopPropagation()}
        style={{ maxWidth: 640, width: '100%', maxHeight: '88vh', overflow: 'auto',
          background: '#17140f', border: `1px solid ${C.borda}`, borderRadius: 16, padding: 18 }}>
        <div style={{ display: 'flex', gap: 14, alignItems: 'flex-start' }}>
          {c.thumbnail_url ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={c.thumbnail_url} alt="" width={120} height={120}
              style={{ borderRadius: 12, objectFit: 'cover', flexShrink: 0 }} />
          ) : null}
          <div style={{ flex: 1, minWidth: 0 }}>
            <p style={{ margin: 0, fontWeight: 800 }}>{c.ad_name || c.ad_id}</p>
            <p className="muted small" style={{ margin: '2px 0 8px' }}>{c.campaign_name} › {c.adset_name}</p>
            <Chip cor={v.cor}>{v.rotulo}</Chip>
          </div>
          <button type="button" onClick={onClose}
            style={{ background: 'none', border: 'none', color: 'inherit', fontSize: '1.3rem', cursor: 'pointer' }}>✕</button>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: 8, margin: '16px 0' }}>
          <Tile rotulo="Investido" valor={brl(c.gasto, false)} />
          <Tile rotulo="Conversas" valor={String(c.conversas)} />
          <Tile rotulo="Leads bons (≥3 msgs)" valor={String(c.leads_engajados)}
            tom={c.leads_engajados > 0 ? 'bom' : 'ruim'} />
          <Tile rotulo="Leads frios" valor={String(c.leads_frios)}
            tom={c.leads_frios > c.leads_engajados ? 'ruim' : 'neutro'} />
          <Tile rotulo="R$ por lead bom"
            valor={c.custo_lead_engajado != null ? brl(c.custo_lead_engajado) : '—'}
            tom={c.custo_lead_engajado != null && mediana
              ? (c.custo_lead_engajado <= mediana ? 'bom' : 'ruim') : 'neutro'} />
          <Tile rotulo="Prendem no vídeo (15s+)"
            valor={c.hook_rate != null ? `${Math.round(c.hook_rate * 100)}%` : '—'}
            tom={c.hook_rate == null ? 'neutro' : c.hook_rate >= 0.25 ? 'bom' : c.hook_rate < 0.15 ? 'ruim' : 'neutro'} />
          <Tile rotulo="Mesma pessoa viu" valor={c.freq != null ? `${c.freq.toFixed(1)}x` : '—'}
            tom={c.freq != null && c.freq >= 3.5 ? 'ruim' : 'neutro'} />
        </div>

        <div style={{ background: 'rgba(0,0,0,.25)', borderRadius: 12, padding: 14, marginBottom: 12 }}>
          <p style={{ margin: '0 0 6px', fontWeight: 800 }}>✨ Diagnóstico</p>
          {c.motivos.length ? c.motivos.map((m, i) => (
            <p key={i} className="small" style={{ margin: '0 0 4px' }}>• {m}</p>
          )) : (
            <p className="small" style={{ margin: 0 }}>
              Rodando dentro do esperado — sem alerta na janela. Mantenha e compare com os vencedores.
            </p>
          )}
        </div>

        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', marginBottom: 12 }}>
          {c.instagram_permalink ? (
            <a href={c.instagram_permalink} target="_blank" rel="noreferrer"
              style={{ background: 'rgba(255,255,255,.08)', border: `1px solid ${C.borda}`,
                color: 'inherit', borderRadius: 10, padding: '9px 16px', fontWeight: 700,
                fontSize: '.86rem', textDecoration: 'none' }}>
              ▶ Ver o anúncio no Instagram
            </a>
          ) : null}
          <SecaoRoteiros c={c} />
        </div>

        {c.body ? (
          <details>
            <summary className="muted small" style={{ cursor: 'pointer' }}>📝 ver o texto do anúncio</summary>
            <p className="muted small" style={{ whiteSpace: 'pre-wrap', margin: '6px 0 0' }}>{c.body}</p>
          </details>
        ) : null}
      </article>
    </div>
  )
}

function SecaoRoteiros({ c }: { c: Criativo }) {
  const [estado, setEstado] = useState<'parado' | 'gerando' | 'pronto' | 'erro'>('parado')
  const [roteiros, setRoteiros] = useState<Roteiro[]>([])
  const [padroes, setPadroes] = useState<PadraoViral[]>([])
  const [geradoEm, setGeradoEm] = useState<string | null>(null)

  // roteiros já gerados ficam salvos — carrega ao abrir o Raio-X
  useEffect(() => {
    if (!c.roteiros_count) return
    fetch(`${api}/ads/roteiros_salvos?ad_id=${encodeURIComponent(c.ad_id)}&tenant_slug=demo`,
      { credentials: 'include', cache: 'no-store' })
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => {
        if (d?.roteiros?.length) {
          setRoteiros(d.roteiros); setPadroes(d.padroes || [])
          setGeradoEm(d.gerado_em || null); setEstado('pronto')
        }
      })
      .catch(() => {})
  }, [c.ad_id, c.roteiros_count])

  async function gerar() {
    setEstado('gerando')
    try {
      const r = await fetch(`${api}/ads/roteiros?ad_id=${encodeURIComponent(c.ad_id)}&tenant_slug=demo&days=30`,
        { method: 'POST', credentials: 'include' })
      if (!r.ok) throw new Error(String(r.status))
      const d = await r.json()
      setRoteiros(d.roteiros || [])
      setPadroes(d.padroes || [])
      setGeradoEm(new Date().toISOString())
      setEstado('pronto')
    } catch {
      setEstado('erro')
    }
  }

  const textoRoteiro = (r: Roteiro) =>
    `${r.titulo}\n\nHOOK (3s): ${r.hook_3s}` +
    (r.hooks_alternativos?.length
      ? `\n\nHOOKS ALTERNATIVOS (mesma abertura, escolha 1):\n${r.hooks_alternativos.map((h, i) => `${i + 1}. ${h}`).join('\n')}`
      : '') +
    `\n\nESTRUTURA:\n${r.estrutura.map((e, i) => `${i + 1}. ${e}`).join('\n')}\n\nCTA: ${r.cta}`

  return (
    <>
      <button type="button" onClick={gerar} disabled={estado === 'gerando'}
        style={{ background: estado === 'gerando' ? 'rgba(201,162,39,.35)' : C.ouro,
          color: '#141210', border: 'none', borderRadius: 10, padding: '9px 16px',
          fontWeight: 800, fontSize: '.86rem', cursor: estado === 'gerando' ? 'wait' : 'pointer' }}>
        {estado === 'gerando' ? '⏳ Escrevendo roteiros… (~1 min)'
          : estado === 'pronto' ? '🔄 Gerar nova versão'
          : c.veredito === 'escalar' ? '🏆 Gerar variações do campeão'
          : '🎬 Gerar roteiros para regravar'}
      </button>
      {geradoEm && estado === 'pronto' ? (
        <span className="muted small" style={{ alignSelf: 'center' }}>
          salvos · gerados em {new Date(geradoEm).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })}
        </span>
      ) : null}
      {estado === 'erro' ? (
        <p className="small" style={{ color: C.vermelho, width: '100%', margin: 0 }}>
          Não consegui gerar agora — tente de novo em instantes.
        </p>
      ) : null}
      {estado === 'pronto' && roteiros.length ? (
        <div style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: 10, marginTop: 4 }}>
          {padroes.length ? (
            <div style={{ background: 'rgba(201,162,39,.08)', border: `1px solid rgba(201,162,39,.3)`,
              borderRadius: 12, padding: 12 }}>
              <p style={{ margin: '0 0 6px', fontWeight: 800, fontSize: '.85rem' }}>
                🧬 Padrões de viralização aplicados (da biblioteca de virais minerados)
              </p>
              {padroes.map((p, i) => (
                <p key={i} className="muted small" style={{ margin: '0 0 4px' }}>
                  <strong>{(p.classe || 'padrão').replace(/_/g, ' ')}</strong>
                  {p.mecanismo ? ` · ${p.mecanismo.replace(/_/g, ' ')}` : ''} — hook validado: “{(p.hook_base || '').slice(0, 110)}…”
                </p>
              ))}
            </div>
          ) : null}
          <p className="muted small" style={{ margin: 0 }}>
            3 opções escritas em cima do diagnóstico deste anúncio — escolha uma e grave:
          </p>
          {roteiros.map((r, i) => (
            <div key={i} style={{ background: 'rgba(0,0,0,.28)', borderRadius: 12, padding: 14,
              border: `1px solid ${C.borda}` }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', gap: 10, alignItems: 'flex-start' }}>
                <strong className="small">🎬 Opção {i + 1} · {r.titulo}</strong>
                <BotaoCopiar texto={textoRoteiro(r)} rotulo="Copiar roteiro" />
              </div>
              <p className="small" style={{ margin: '8px 0 6px', display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                <span style={{ color: C.ouro, fontWeight: 800 }}>HOOK (3s):</span> “{r.hook_3s}”
                <CopiarMini texto={r.hook_3s} />
              </p>
              {r.hooks_alternativos?.length ? (
                <div style={{ margin: '0 0 8px' }}>
                  <p className="muted small" style={{ margin: '0 0 4px' }}>hooks alternativos para a mesma abertura:</p>
                  {r.hooks_alternativos.map((h, j) => (
                    <p key={j} className="small" style={{ margin: '0 0 3px', display: 'flex', gap: 8, alignItems: 'center' }}>
                      <CopiarMini texto={h} />
                      <span style={{ overflowWrap: 'anywhere' }}>“{h}”</span>
                    </p>
                  ))}
                </div>
              ) : null}
              <ol className="small" style={{ margin: '0 0 6px 18px' }}>
                {r.estrutura.map((e, j) => (<li key={j} style={{ marginBottom: 2 }}>{e}</li>))}
              </ol>
              <p className="small" style={{ margin: '0 0 6px' }}>
                <span style={{ color: C.verde, fontWeight: 800 }}>CTA:</span> {r.cta}
              </p>
              <p className="muted small" style={{ margin: 0, fontStyle: 'italic' }}>{r.por_que_funciona}</p>
            </div>
          ))}
        </div>
      ) : null}
    </>
  )
}

function LinhaCabecalho({ cols }: { cols: string[] }) {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'minmax(200px,2fr) 130px 110px 110px 130px 150px',
      gap: 10, padding: '6px 12px', fontSize: '.72rem', textTransform: 'uppercase',
      letterSpacing: '.06em', opacity: .55 }}>
      {cols.map((c, i) => (<span key={i} style={{ textAlign: i === 0 ? 'left' : 'right' }}>{c}</span>))}
    </div>
  )
}

function Linha({ nivel, aberta, onClick, nome, sub, gasto, maxGasto, col3, col4, col5, chip, thumb }: {
  nivel: 0 | 1 | 2; aberta?: boolean; onClick?: () => void; nome: string; sub?: string
  gasto: number; maxGasto: number; col3: string; col4: string; col5: string
  chip?: { rotulo: string; cor: string } | null; thumb?: string | null
}) {
  return (
    <div onClick={onClick}
      style={{ display: 'grid', gridTemplateColumns: 'minmax(200px,2fr) 130px 110px 110px 130px 150px',
        gap: 10, alignItems: 'center', padding: '10px 12px',
        paddingLeft: 12 + nivel * 26, cursor: onClick ? 'pointer' : 'default',
        background: nivel === 0 ? C.fundo : 'transparent',
        borderRadius: 10, border: nivel === 0 ? `1px solid ${C.borda}` : 'none',
        borderBottom: nivel > 0 ? `1px solid rgba(255,255,255,.05)` : undefined }}>
      <div style={{ display: 'flex', alignItems: 'center', minWidth: 0 }}>
        {onClick ? <Seta aberto={!!aberta} /> : <span style={{ width: 20 }} />}
        {thumb ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={thumb} alt="" width={34} height={34}
            style={{ borderRadius: 6, objectFit: 'cover', marginRight: 8, flexShrink: 0 }} />
        ) : null}
        <div style={{ minWidth: 0 }}>
          <p title={nome} style={{ margin: 0, fontWeight: nivel === 0 ? 700 : 500,
            fontSize: nivel === 0 ? '.95rem' : '.88rem', overflowWrap: 'anywhere' }}>{nome}</p>
          {sub ? <p className="muted small" title={sub} style={{ margin: 0, overflowWrap: 'anywhere' }}>{sub}</p> : null}
        </div>
      </div>
      <div>
        <p style={{ margin: '0 0 3px', textAlign: 'right', fontWeight: 600, fontSize: '.88rem' }}>{brl(gasto, false)}</p>
        <Barra valor={gasto} max={maxGasto} cor={C.ouro} />
      </div>
      <p style={{ margin: 0, textAlign: 'right', fontSize: '.88rem' }}>{col3}</p>
      <p style={{ margin: 0, textAlign: 'right', fontSize: '.88rem' }}>{col4}</p>
      <p style={{ margin: 0, textAlign: 'right', fontSize: '.88rem', fontWeight: 600 }}>{col5}</p>
      <div style={{ textAlign: 'right' }}>{chip ? <Chip cor={chip.cor}>{chip.rotulo}</Chip> : null}</div>
    </div>
  )
}

function ArvoreMeta({ d }: { d: Cockpit }) {
  const [abertas, setAbertas] = useState<Record<string, boolean>>({})
  const [detalhe, setDetalhe] = useState<Criativo | null>(null)
  const mediana = d.resumo.mediana_custo_lead_engajado
  const arvore = useMemo(() => {
    const camps: Record<string, { gasto: number; conversas: number; eng: number; sets: Record<string, Criativo[]> }> = {}
    for (const c of d.criativos) {
      const camp = camps[c.campaign_name || '—'] ||= { gasto: 0, conversas: 0, eng: 0, sets: {} }
      camp.gasto += c.gasto; camp.conversas += c.conversas; camp.eng += c.leads_engajados
      ;(camp.sets[c.adset_name || '—'] ||= []).push(c)
    }
    return camps
  }, [d])
  const maxGasto = Math.max(...Object.values(arvore).map((c) => c.gasto), 1)

  return (
    <div>
      <p className="muted small" style={{ margin: '0 0 8px' }}>
        Clique na campanha para abrir os conjuntos; no conjunto, para ver cada anúncio. Clique no anúncio para o raio-x.
      </p>
      <LinhaCabecalho cols={['Campanha / conjunto / anúncio', 'Investido', 'Conversas', 'Leads bons', 'R$ por lead bom', 'O que fazer']} />
      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        {Object.entries(arvore).sort((a, b) => b[1].gasto - a[1].gasto).map(([campNome, camp]) => {
          const kCamp = `c:${campNome}`
          const custoCamp = camp.eng ? camp.gasto / camp.eng : null
          return (
            <div key={kCamp}>
              <Linha nivel={0} aberta={abertas[kCamp]} nome={campNome} gasto={camp.gasto} maxGasto={maxGasto}
                col3={String(camp.conversas)} col4={String(camp.eng)} col5={custoCamp ? brl(custoCamp) : '—'}
                chip={null}
                onClick={() => setAbertas((s) => ({ ...s, [kCamp]: !s[kCamp] }))} />
              {abertas[kCamp] ? Object.entries(camp.sets).map(([setNome, ads]) => {
                const kSet = `${kCamp}|s:${setNome}`
                const gastoSet = ads.reduce((s, a) => s + a.gasto, 0)
                const engSet = ads.reduce((s, a) => s + a.leads_engajados, 0)
                return (
                  <div key={kSet}>
                    <Linha nivel={1} aberta={abertas[kSet]} nome={`📦 ${setNome}`} gasto={gastoSet} maxGasto={maxGasto}
                      col3={String(ads.reduce((s, a) => s + a.conversas, 0))} col4={String(engSet)}
                      col5={engSet ? brl(gastoSet / engSet) : '—'} chip={null}
                      onClick={() => setAbertas((s) => ({ ...s, [kSet]: !s[kSet] }))} />
                    {abertas[kSet] ? ads.sort((a, b) => b.gasto - a.gasto).map((c) => (
                      <Linha key={c.ad_id} nivel={2} nome={c.ad_name || c.ad_id}
                        sub={c.motivos[0] || undefined} thumb={c.thumbnail_url}
                        gasto={c.gasto} maxGasto={maxGasto} col3={String(c.conversas)}
                        col4={String(c.leads_engajados)}
                        col5={c.custo_lead_engajado != null ? brl(c.custo_lead_engajado) : '—'}
                        chip={VEREDITO_CHIP[c.veredito]}
                        onClick={() => setDetalhe(c)} />
                    )) : null}
                  </div>
                )
              }) : null}
            </div>
          )
        })}
      </div>

      {detalhe ? <ModalCriativo c={detalhe} onClose={() => setDetalhe(null)} mediana={mediana} /> : null}
    </div>
  )
}

function ArvoreGoogle({ d }: { d: Cockpit }) {
  const [abertas, setAbertas] = useState<Record<string, boolean>>({})
  const arvore = useMemo(() => {
    const camps: Record<string, { gasto: number; conv: number; grupos: Record<string, { kws: Kw[]; ads: GAd[] }> }> = {}
    for (const k of d.keywords) {
      const camp = camps[k.campaign_name || '—'] ||= { gasto: 0, conv: 0, grupos: {} }
      camp.gasto += k.gasto; camp.conv += k.conv
      const g = camp.grupos[k.ad_group_name || '—'] ||= { kws: [], ads: [] }
      g.kws.push(k)
    }
    for (const a of d.google_anuncios) {
      const camp = camps[a.campaign_name || '—'] ||= { gasto: 0, conv: 0, grupos: {} }
      const g = camp.grupos[a.ad_group_name || '—'] ||= { kws: [], ads: [] }
      g.ads.push(a)
    }
    return camps
  }, [d])
  const maxGasto = Math.max(...Object.values(arvore).map((c) => c.gasto), 1)

  return (
    <div>
      <p className="muted small" style={{ margin: '0 0 8px' }}>
        Campanha → grupo → palavras e anúncios. Palavra vermelha = gastou e não trouxe ninguém.
      </p>
      <LinhaCabecalho cols={['Campanha / grupo / palavra', 'Investido', 'Cliques', 'Clientes', 'R$ por cliente', 'Situação']} />
      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        {Object.entries(arvore).sort((a, b) => b[1].gasto - a[1].gasto).map(([campNome, camp]) => {
          const kCamp = `g:${campNome}`
          return (
            <div key={kCamp}>
              <Linha nivel={0} aberta={abertas[kCamp]} nome={campNome} gasto={camp.gasto} maxGasto={maxGasto}
                col3="" col4={camp.conv ? camp.conv.toFixed(0) : '0'}
                col5={camp.conv ? brl(camp.gasto / camp.conv) : '—'}
                chip={camp.conv === 0 && camp.gasto > 50 ? { rotulo: '🔴 sem clientes', cor: C.vermelho } : null}
                onClick={() => setAbertas((s) => ({ ...s, [kCamp]: !s[kCamp] }))} />
              {abertas[kCamp] ? Object.entries(camp.grupos).map(([gNome, g]) => {
                const kG = `${kCamp}|${gNome}`
                const gastoG = g.kws.reduce((s, k) => s + k.gasto, 0)
                const convG = g.kws.reduce((s, k) => s + k.conv, 0)
                return (
                  <div key={kG}>
                    <Linha nivel={1} aberta={abertas[kG]} nome={`📁 ${gNome}`} gasto={gastoG} maxGasto={maxGasto}
                      col3={String(g.kws.reduce((s, k) => s + k.cliques, 0))} col4={convG.toFixed(0)}
                      col5={convG ? brl(gastoG / convG) : '—'} chip={null}
                      onClick={() => setAbertas((s) => ({ ...s, [kG]: !s[kG] }))} />
                    {abertas[kG] ? (
                      <>
                        {g.kws.sort((a, b) => b.gasto - a.gasto).map((k, i) => (
                          <Linha key={i} nivel={2} nome={`🔑 ${k.keyword}`}
                            sub={`${(MATCH_PT[k.match_type] || k.match_type || '').toLowerCase()}${(k.kw_status || 'ENABLED') !== 'ENABLED' ? ' · pausada' : ''}${k.negativada ? ' · negativada' : ''}`}
                            gasto={k.gasto} maxGasto={maxGasto} col3={String(k.cliques)}
                            col4={k.conv ? k.conv.toFixed(1) : '0'} col5={k.cpa != null ? brl(k.cpa) : '—'}
                            chip={k.negativada
                              ? { rotulo: '🚫 já negativada', cor: '#6f6a61' }
                              : (k.kw_status || 'ENABLED') !== 'ENABLED'
                              ? { rotulo: '⏸ já pausada', cor: '#6f6a61' }
                              : k.conv === 0 && k.gasto >= 30
                              ? { rotulo: '🔴 pausar', cor: C.vermelho }
                              : k.conv > 0 ? { rotulo: '🟢 traz cliente', cor: C.verde } : null} />
                        ))}
                        {g.ads.map((a, i) => (
                          <Linha key={`ad${i}`} nivel={2} nome={`📝 ${(a.headlines || []).slice(0, 2).join(' · ') || a.ad_id}`}
                            sub="anúncio de texto" gasto={a.gasto} maxGasto={maxGasto} col3={String(a.cliques)}
                            col4={a.conv ? a.conv.toFixed(1) : '0'} col5={a.cpa != null ? brl(a.cpa) : '—'} chip={null} />
                        ))}
                      </>
                    ) : null}
                  </div>
                )
              }) : null}
            </div>
          )
        })}
      </div>
    </div>
  )
}

// ————— aba 3: palavras do Google (copiar e colar) —————

function agruparPorGrupo(termos: Termo[]) {
  const camps: Record<string, Record<string, Termo[]>> = {}
  for (const t of termos) {
    const c = camps[t.campaign_name || '—'] ||= {}
    ;(c[t.ad_group_name || '—'] ||= []).push(t)
  }
  return camps
}

function PainelTermos({ titulo, sub, cor, termos, rotuloBotao, extra }: {
  titulo: string; sub: string; cor: string; termos: Termo[]
  rotuloBotao: string; extra: (t: Termo) => string
}) {
  const chave = (t: Termo) => `${t.campaign_name}|${t.ad_group_name}|${t.term}`
  const [sel, setSel] = useState<Record<string, boolean>>(
    () => Object.fromEntries(termos.map((t) => [chave(t), true])))
  const grupos = useMemo(() => agruparPorGrupo(termos), [termos])
  const totalSel = termos.filter((t) => sel[chave(t)]).length

  return (
    <article className="featurePanel" style={{ borderTop: `3px solid ${cor}` }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 10, marginBottom: 6 }}>
        <div>
          <strong style={{ fontSize: '1.02rem' }}>{titulo}</strong>
          <p className="muted small" style={{ margin: '2px 0 0' }}>{sub}</p>
        </div>
        <span className="badge">{totalSel} marcados</span>
      </div>
      {termos.length ? Object.entries(grupos).map(([campNome, gruposDaCamp]) => (
        <div key={campNome} style={{ marginTop: 12 }}>
          <p style={{ margin: '0 0 4px', fontWeight: 800, fontSize: '.85rem', opacity: .85 }}>📣 {campNome}</p>
          {Object.entries(gruposDaCamp).map(([grupoNome, lista]) => {
            const selecionados = lista.filter((t) => sel[chave(t)])
            return (
              <div key={grupoNome} style={{ background: 'rgba(0,0,0,.22)', borderRadius: 12,
                padding: '10px 12px', marginBottom: 10, border: `1px solid ${C.borda}` }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  gap: 10, marginBottom: 4, flexWrap: 'wrap' }}>
                  <strong className="small">📁 {grupoNome}</strong>
                  <BotaoCopiar rotulo={`${rotuloBotao} deste grupo (${selecionados.length})`}
                    texto={selecionados.map((t) => `[${t.term}]`).join('\n')} />
                </div>
                {lista.map((t) => (
                  <label key={chave(t)} style={{ display: 'flex', alignItems: 'center', gap: 10,
                    padding: '6px 2px', borderBottom: '1px solid rgba(255,255,255,.05)', cursor: 'pointer' }}>
                    <input type="checkbox" checked={!!sel[chave(t)]}
                      onChange={() => setSel((s) => ({ ...s, [chave(t)]: !s[chave(t)] }))} />
                    <span style={{ flex: 1, fontSize: '.92rem', overflowWrap: 'anywhere' }}>{t.term}</span>
                    <span className="muted small" style={{ whiteSpace: 'nowrap' }}>{extra(t)}</span>
                    <CopiarMini texto={`[${t.term}]`} />
                  </label>
                ))}
              </div>
            )
          })}
        </div>
      )) : (<p className="muted small" style={{ marginTop: 8 }}>nada encontrado na janela</p>)}
      <p className="muted small" style={{ margin: '6px 0 0' }}>
        Fluxo: abra o grupo de anúncios no Google Ads → Palavras-chave negativas (ou Palavras-chave) →
        cole a lista do grupo de uma vez. Formato <code>[termo]</code> = correspondência exata.
      </p>
    </article>
  )
}

function SentinelaPalavras({ d }: { d: Cockpit }) {
  const [descartados, setDescartados] = useState<Record<string, boolean>>({})
  const descartar = (t: TermoIA, nivel: 'exata' | 'frase') => {
    setDescartados((s) => ({ ...s, [`${t.termo}|${nivel}`]: true }))
    fetch(`${api}/ads/sentinela_descartar?tenant_slug=demo&nivel=${nivel}&termo=${encodeURIComponent(t.termo)}`,
      { method: 'POST', credentials: 'include' }).catch(() => {})
  }
  const itens = (d.termos_negativar_ia || []).filter((t) => !descartados[`${t.termo}|exata`])
  const frases = (d.negativas_frase || []).filter((t) => !descartados[`${t.termo}|frase`])
  const carimbo = d.sentinela?.gerada_em
    ? new Date(d.sentinela.gerada_em).toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })
    : null
  if (!itens.length && !frases.length) {
    return (
      <section className="featurePanel" style={{ borderTop: `3px solid ${C.verde}`, marginBottom: 14 }}>
        <strong style={{ fontSize: '1.02rem' }}>🛡️ Sentinela de termos (IA)</strong>
        <p className="muted small" style={{ margin: '4px 0 0' }}>
          Nenhuma pesquisa fora do alvo pendente — cada pesquisa nova (nome de outro médico, grátis/SUS,
          outra cidade, emprego/curso…) é avaliada sozinha a cada atualização de dados.
          {carimbo ? ` Última varredura: ${carimbo}.` : d.sentinela?.desatualizada ? ' Primeira varredura rodando em segundo plano…' : ''}
        </p>
      </section>
    )
  }
  const porCat: Record<string, TermoIA[]> = {}
  for (const t of itens) (porCat[t.categoria] = porCat[t.categoria] || []).push(t)
  return (
    <section className="featurePanel" style={{ borderTop: `3px solid ${C.vermelho}`, marginBottom: 14 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 10, flexWrap: 'wrap' }}>
        <div>
          <strong style={{ fontSize: '1.02rem' }}>🛡️ Sentinela de termos (IA) — pesquisas que roubam sua verba</strong>
          <p className="muted small" style={{ margin: '2px 0 0' }}>
            A IA lê TODAS as pesquisas novas (mesmo com gasto pequeno) e separa quem procura outra coisa.
            Negative na conta e elas somem daqui na próxima atualização.{carimbo ? ` Última varredura: ${carimbo}.` : ''}
          </p>
        </div>
        {itens.length ? (
          <span style={{ display: 'inline-flex', gap: 6, alignItems: 'center', flexWrap: 'wrap' }}>
            <strong className="small">📋 Copiar todos ({itens.length}) como:</strong>
            <CopiarFormatos termos={itens.map((t) => t.termo)} />
          </span>
        ) : null}
      </div>
      {Object.entries(porCat).map(([cat, lista]) => (
        <div key={cat} style={{ background: 'rgba(0,0,0,.22)', borderRadius: 12, padding: '10px 12px',
          marginTop: 10, border: `1px solid ${C.borda}` }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 10, marginBottom: 4, flexWrap: 'wrap' }}>
            <strong className="small">{CAT_ROTULO[cat] || cat} ({lista.length})</strong>
            <span style={{ display: 'inline-flex', gap: 6, alignItems: 'center', flexWrap: 'wrap' }}>
              <span className="muted small">copiar como:</span>
              <CopiarFormatos termos={lista.map((t) => t.termo)} />
            </span>
          </div>
          {lista.map((t, i) => (
            <div key={i} style={{ padding: '6px 2px', borderBottom: '1px solid rgba(255,255,255,.05)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                <CopiarFormatos termos={[t.termo]} />
                <span style={{ flex: 1, minWidth: 160, fontSize: '.92rem', overflowWrap: 'anywhere' }}>{t.termo}</span>
                <span className="muted small" style={{ whiteSpace: 'nowrap' }}>
                  {t.gasto ? `${brl(t.gasto)} · ` : ''}{t.cliques || 0} cliques
                </span>
                <button type="button" title="não negativar — tirar esta sugestão da fila"
                  onClick={() => descartar(t, 'exata')}
                  style={{ background: 'transparent', color: 'inherit', border: `1px solid ${C.borda}`,
                    borderRadius: 8, padding: '3px 9px', fontSize: '.75rem', cursor: 'pointer', flexShrink: 0 }}>
                  ✕
                </button>
              </div>
              <p className="muted small" style={{ margin: '2px 0 0 40px' }}>
                💡 {t.motivo}{t.campanha ? <> · visto em 📣 {t.campanha}{t.grupo ? ` › 📁 ${t.grupo}` : ''}</> : null}
              </p>
            </div>
          ))}
        </div>
      ))}
      {frases.length ? (
        <div style={{ background: 'rgba(0,0,0,.22)', borderRadius: 12, padding: '10px 12px',
          marginTop: 10, border: `1px solid ${C.borda}` }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 10, marginBottom: 4, flexWrap: 'wrap' }}>
            <strong className="small">🧱 Negativar como FRASE na conta toda ({frases.length})</strong>
            <BotaoCopiar rotulo={`Copiar (${frases.length})`} texto={frases.map((t) => `"${t.termo}"`).join('\n')} />
          </div>
          {frases.map((t, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '5px 2px',
              borderBottom: '1px solid rgba(255,255,255,.05)' }}>
              <CopiarMini texto={`"${t.termo}"`} />
              <code className="small">{t.termo}</code>
              <span className="muted small" style={{ flex: 1, overflowWrap: 'anywhere' }}>— {t.motivo}</span>
              <button type="button" title="não negativar — tirar esta sugestão da fila"
                onClick={() => descartar(t, 'frase')}
                style={{ background: 'transparent', color: 'inherit', border: `1px solid ${C.borda}`,
                  borderRadius: 8, padding: '3px 9px', fontSize: '.75rem', cursor: 'pointer', flexShrink: 0 }}>
                ✕
              </button>
            </div>
          ))}
          <p className="muted small" style={{ margin: '6px 0 0' }}>
            Formato <code>&quot;frase&quot;</code>: bloqueia qualquer pesquisa que contenha a palavra. Cole em
            Ferramentas → Listas de palavras-chave negativas (vale para todas as campanhas).
          </p>
        </div>
      ) : null}
      <p className="muted small" style={{ margin: '8px 0 0' }}>
        Fluxo: Google Ads → Palavras-chave → Palavras-chave negativas → + no nível da <strong>campanha</strong> (ou
        na lista de negativas da conta) → cole. Formatos: <code>[termo]</code> exata = bloqueia só a pesquisa
        idêntica · <code>&quot;termo&quot;</code> frase = bloqueia toda pesquisa que contenha essa sequência ·
        <code>termo</code> ampla = bloqueia qualquer pesquisa com todas essas palavras em qualquer ordem
        (a mais garantida para nomes de médicos e concorrentes).
      </p>
    </section>
  )
}

function AbaPalavras({ d }: { d: Cockpit }) {
  return (
    <>
      <SentinelaPalavras d={d} />
      <AnaliseEstrutural />
      <section className="splitSection">
        <PainelTermos titulo="🚫 Bloquear estas pesquisas" cor={C.vermelho}
          sub="gastaram seu dinheiro e não trouxeram nenhum cliente — organizadas por grupo, cole 1x em cada"
          termos={d.termos_negativar} rotuloBotao="Copiar"
          extra={(t) => `${brl(t.gasto)} · ${t.cliques} cliques`} />
        <PainelTermos titulo="➕ Apostar nestas pesquisas" cor={C.verde}
          sub="trouxeram cliente e ainda não são palavras-chave suas — já no grupo certo"
          termos={d.termos_incluir} rotuloBotao="Copiar"
          extra={(t) => `${t.conv.toFixed(1)} cliente(s) por ${brl(t.gasto)}`} />
      </section>
    </>
  )
}

// ————— análise estrutural (IA): novos grupos, keywords e copy de RSA —————

type AnaliseBusca = {
  resumo_executivo: string
  novos_grupos: { nome: string; campanha_destino: string; por_que: string; keywords: string[]
    termos_origem: string[]; titulos: string[]; descricoes: string[] }[]
  keywords_por_grupo: { campanha: string; grupo: string; adicionar: string[]; por_que: string }[]
  melhorias_anuncios: { campanha: string; grupo: string; problema: string
    titulos_novos: string[]; descricoes_novas: string[] }[]
}

function ListaCopiavel({ rotulo, itens }: { rotulo: string; itens: string[] }) {
  if (!itens.length) return null
  return (
    <div style={{ margin: '6px 0' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 8 }}>
        <strong className="small">{rotulo}</strong>
        <BotaoCopiar rotulo={`Copiar (${itens.length})`} texto={itens.join('\n')} />
      </div>
      {itens.map((x, i) => (
        <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '3px 0',
          borderBottom: '1px solid rgba(255,255,255,.05)' }}>
          <CopiarMini texto={x} />
          <span className="small" style={{ overflowWrap: 'anywhere' }}>{x}</span>
          <span className="muted small" style={{ marginLeft: 'auto', whiteSpace: 'nowrap' }}>{x.length} car.</span>
        </div>
      ))}
    </div>
  )
}

function AnaliseEstrutural() {
  const [estado, setEstado] = useState<'carregando' | 'vazio' | 'gerando' | 'pronto' | 'erro'>('carregando')
  const [analise, setAnalise] = useState<AnaliseBusca | null>(null)
  const [geradoEm, setGeradoEm] = useState<string | null>(null)

  useEffect(() => {
    fetch(`${api}/ads/analise_busca_salva?tenant_slug=demo`, { credentials: 'include', cache: 'no-store' })
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => {
        if (d?.analise) { setAnalise(d.analise); setGeradoEm(d.gerado_em || null); setEstado('pronto') }
        else setEstado('vazio')
      })
      .catch(() => setEstado('vazio'))
  }, [])

  async function gerar() {
    setEstado('gerando')
    try {
      const r = await fetch(`${api}/ads/analise_busca?tenant_slug=demo&days=30`,
        { method: 'POST', credentials: 'include' })
      if (!r.ok) throw new Error(String(r.status))
      const d = await r.json()
      setAnalise(d.analise); setGeradoEm(new Date().toISOString()); setEstado('pronto')
    } catch { setEstado('erro') }
  }

  return (
    <section className="featurePanel" style={{ borderTop: `3px solid ${C.ouro}`, marginBottom: 14 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
        <div>
          <strong style={{ fontSize: '1.02rem' }}>🧠 Análise estrutural das campanhas (IA)</strong>
          <p className="muted small" style={{ margin: '2px 0 0' }}>
            Lê os termos de busca reais e propõe: novos grupos de anúncios, keywords e títulos/descrições alinhados ao que as pessoas digitam
          </p>
        </div>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          {geradoEm ? <span className="muted small">gerada em {new Date(geradoEm).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })}</span> : null}
          <button type="button" onClick={gerar} disabled={estado === 'gerando' || estado === 'carregando'}
            style={{ background: estado === 'gerando' ? 'rgba(201,162,39,.35)' : C.ouro, color: '#141210',
              border: 'none', borderRadius: 10, padding: '9px 16px', fontWeight: 800, fontSize: '.86rem',
              cursor: estado === 'gerando' ? 'wait' : 'pointer' }}>
            {estado === 'gerando' ? '⏳ Analisando… (~2 min)' : analise ? '🔄 Refazer análise' : '🧠 Analisar agora'}
          </button>
        </div>
      </div>
      {estado === 'erro' ? <p className="small" style={{ color: C.vermelho }}>Falhou — tente de novo em instantes.</p> : null}
      {analise ? (
        <div style={{ marginTop: 12, display: 'flex', flexDirection: 'column', gap: 12 }}>
          <p className="small" style={{ background: 'rgba(201,162,39,.08)', border: '1px solid rgba(201,162,39,.3)',
            borderRadius: 10, padding: 12, margin: 0 }}>
            <strong>Resumo:</strong> {analise.resumo_executivo}
          </p>

          {analise.novos_grupos.length ? (
            <div>
              <p style={{ margin: '0 0 8px', fontWeight: 800 }}>🆕 Grupos de anúncios a criar ({analise.novos_grupos.length})</p>
              {analise.novos_grupos.map((g, i) => (
                <details key={i} style={{ background: 'rgba(0,0,0,.22)', borderRadius: 12, padding: '10px 14px', marginBottom: 8 }}>
                  <summary style={{ cursor: 'pointer', fontWeight: 700 }}>
                    📁 {g.nome} <span className="muted small">→ em {g.campanha_destino}</span>
                  </summary>
                  <p className="small" style={{ margin: '8px 0' }}><strong>Por quê:</strong> {g.por_que}</p>
                  <p className="muted small" style={{ margin: '0 0 6px' }}>
                    Baseado nas buscas reais: {g.termos_origem.map((t) => `“${t}”`).join(', ')}
                  </p>
                  <ListaCopiavel rotulo="Keywords do grupo" itens={g.keywords} />
                  <ListaCopiavel rotulo="Títulos do anúncio (máx 30)" itens={g.titulos} />
                  <ListaCopiavel rotulo="Descrições (máx 90)" itens={g.descricoes} />
                </details>
              ))}
            </div>
          ) : null}

          {analise.keywords_por_grupo.length ? (
            <div>
              <p style={{ margin: '0 0 8px', fontWeight: 800 }}>➕ Keywords para grupos existentes</p>
              {analise.keywords_por_grupo.map((k, i) => (
                <div key={i} style={{ background: 'rgba(0,0,0,.22)', borderRadius: 12, padding: '10px 14px', marginBottom: 8 }}>
                  <p className="small" style={{ margin: '0 0 4px' }}>
                    <strong>📣 {k.campanha} › 📁 {k.grupo}</strong> — {k.por_que}
                  </p>
                  <ListaCopiavel rotulo="Adicionar" itens={k.adicionar} />
                </div>
              ))}
            </div>
          ) : null}

          {analise.melhorias_anuncios.length ? (
            <div>
              <p style={{ margin: '0 0 8px', fontWeight: 800 }}>✍️ Anúncios para reescrever</p>
              {analise.melhorias_anuncios.map((m, i) => (
                <details key={i} style={{ background: 'rgba(0,0,0,.22)', borderRadius: 12, padding: '10px 14px', marginBottom: 8 }}>
                  <summary style={{ cursor: 'pointer', fontWeight: 700 }}>
                    📣 {m.campanha} › 📁 {m.grupo}
                  </summary>
                  <p className="small" style={{ margin: '8px 0', color: C.amarelo }}><strong>Problema:</strong> {m.problema}</p>
                  <ListaCopiavel rotulo="Títulos novos (máx 30)" itens={m.titulos_novos} />
                  <ListaCopiavel rotulo="Descrições novas (máx 90)" itens={m.descricoes_novas} />
                </details>
              ))}
            </div>
          ) : null}
        </div>
      ) : estado === 'vazio' ? (
        <p className="muted small" style={{ margin: '10px 0 0' }}>
          Nenhuma análise gerada ainda — clique em “Analisar agora” (leva ~2 min, fica salva).
        </p>
      ) : null}
    </section>
  )
}

// ————— aba 4: leads (fluxo, agrupados por criativo, análise IA) —————

const tempLead = (m: number) => m >= 3
  ? { rotulo: '🔥 conversou bastante', cor: C.verde }
  : m <= 1 ? { rotulo: '🧊 clicou e sumiu', cor: C.vermelho }
  : { rotulo: '🌡 respondeu pouco', cor: C.amarelo }

function FluxoConversas({ d }: { d: Cockpit }) {
  const [periodo, setPeriodo] = useState<'por_dia' | 'por_semana' | 'por_mes'>('por_dia')
  const dados = d.fluxo_leads?.[periodo] || []
  const max = Math.max(...dados.map((x) => x.contatos_ativos || x.contatos_novos), 1)
  const rot = (p: string) => periodo === 'por_dia'
    ? new Date(`${p}T12:00:00`).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })
    : periodo === 'por_semana' ? `sem. ${p}` : p
  const tot = dados.reduce((s, x) => s + x.contatos_novos, 0)
  const totAtivos = dados.reduce((s, x) => s + (x.contatos_ativos || 0), 0)
  const totAds = dados.reduce((s, x) => s + x.ctwa_leads, 0)
  const fontesLinha = (x: FluxoPeriodo) => {
    const parts: string[] = []
    if (x.fonte_anuncio_ig) parts.push(`📱${x.fonte_anuncio_ig}`)
    if (x.fonte_anuncio_fb) parts.push(`📘${x.fonte_anuncio_fb}`)
    if (x.fonte_site_google) parts.push(`🔎${x.fonte_site_google}`)
    if (x.fonte_indicacao) parts.push(`🤝${x.fonte_indicacao}`)
    if (x.fonte_outros) parts.push(`❔${x.fonte_outros}`)
    return parts.join(' ')
  }
  const fontes = [
    { rotulo: '📱 Anúncio Instagram', n: dados.reduce((s, x) => s + (x.fonte_anuncio_ig || 0), 0), cor: C.verde },
    { rotulo: '📘 Anúncio Facebook', n: dados.reduce((s, x) => s + (x.fonte_anuncio_fb || 0), 0), cor: C.verde },
    { rotulo: '🔎 Site / Google', n: dados.reduce((s, x) => s + (x.fonte_site_google || 0), 0), cor: C.ouro },
    { rotulo: '🤝 Indicação', n: dados.reduce((s, x) => s + (x.fonte_indicacao || 0), 0), cor: '#7b68c9' },
    { rotulo: '❔ Outros / orgânico', n: dados.reduce((s, x) => s + (x.fonte_outros || 0), 0), cor: '#6f6a61' },
  ].filter((f) => f.n > 0)
  return (
    <section className="featurePanel" style={{ marginBottom: 14 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 10, flexWrap: 'wrap', marginBottom: 10 }}>
        <div>
          <strong style={{ fontSize: '1.02rem' }}>📈 Entrada de conversas no WhatsApp</strong>
          <p className="muted small" style={{ margin: '2px 0 0' }}>
            {totAtivos} conversas ativas no período · <strong>{tot} contatos novos</strong> · {totAds} cliques de anúncio
          </p>
          <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginTop: 6 }}>
            {fontes.map((f, i) => (
              <span key={i} style={{ background: 'rgba(0,0,0,.28)', border: `1px solid ${f.cor}55`,
                color: 'inherit', borderRadius: 99, padding: '3px 10px', fontSize: '.76rem' }}>
                {f.rotulo}: <strong style={{ color: f.cor }}>{f.n}</strong>
              </span>
            ))}
          </div>
        </div>
        <div style={{ display: 'flex', gap: 6 }}>
          {([['por_dia', 'Dia'], ['por_semana', 'Semana'], ['por_mes', 'Mês']] as const).map(([id, r]) => (
            <button key={id} type="button" onClick={() => setPeriodo(id)}
              style={{ background: periodo === id ? C.fundo : 'transparent', color: 'inherit',
                border: `1px solid ${periodo === id ? C.ouro : C.borda}`, borderRadius: 8,
                padding: '6px 14px', fontSize: '.84rem', fontWeight: 700, cursor: 'pointer' }}>{r}</button>
          ))}
        </div>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
        {(periodo === 'por_dia' ? dados.slice(-14) : dados).map((x, i) => (
          <div key={i} style={{ display: 'grid', gridTemplateColumns: '86px 1fr auto', gap: 10, alignItems: 'center' }}>
            <span className="muted small">{rot(x.periodo)}</span>
            <div style={{ background: 'rgba(255,255,255,.06)', borderRadius: 99, height: 16, position: 'relative' }}>
              <div style={{ width: `${Math.max(3, ((x.contatos_ativos || 0) / max) * 100)}%`, height: 16,
                borderRadius: 99, background: 'rgba(255,255,255,.14)' }} />
              <div style={{ width: `${Math.max(0, (x.contatos_novos / max) * 100)}%`, height: 16,
                borderRadius: 99, background: 'rgba(201,162,39,.55)', position: 'absolute', top: 0, left: 0 }} />
              <div style={{ width: `${Math.max(0, (((x.fonte_anuncio_ig || 0) + (x.fonte_anuncio_fb || 0)) / max) * 100)}%`,
                height: 16, borderRadius: 99, background: C.verde, position: 'absolute', top: 0, left: 0, opacity: .9 }} />
            </div>
            <span className="small" style={{ whiteSpace: 'nowrap' }}>
              {x.contatos_ativos || 0} ativas · <strong>{x.contatos_novos} novas</strong>
              <span className="muted"> ({fontesLinha(x) || '—'})</span>
            </span>
          </div>
        ))}
      </div>
      <p className="muted small" style={{ margin: '8px 0 0' }}>
        <span style={{ color: C.verde }}>▮</span> novas por anúncio · <span style={{ color: 'rgba(201,162,39,.9)' }}>▮</span> novas (todas as fontes) · <span style={{ opacity: .5 }}>▮</span> conversas ativas no dia
        &nbsp;·&nbsp; fontes: 📱 anúncio IG · 📘 anúncio FB · 🔎 site/Google · 🤝 indicação · ❔ outros
      </p>
    </section>
  )
}

type AnaliseConversas = {
  resumo_executivo: string
  por_criativo: { anuncio: string; ad_id?: string; thumbnail_url?: string | null
    campanha?: string | null; conjunto?: string | null
    qualidade_dos_leads: string; duvidas_comuns: string[]
    objecoes: string[]; recomendacao: string }[]
  vocabulario_dos_leads: string[]
  ideias_para_campanhas: { tipo: string; ideia: string; por_que: string }[]
}

type Pecas = {
  carrossel: { titulo_capa: string; slides: { titulo: string; texto: string }[]
    cta_final: string; copy_legenda: string }
  estatico: { headline: string; subtexto: string; copy_primaria: string
    titulo_anuncio: string; descricao_anuncio: string }
  video: { ganchos: string[]; estrutura: string[]; cta: string }
}

function BlocoPecas({ p }: { p: Pecas }) {
  const textoCarrossel = `CAPA: ${p.carrossel.titulo_capa}\n\n` +
    p.carrossel.slides.map((s, i) => `SLIDE ${i + 2} — ${s.titulo}\n${s.texto}`).join('\n\n') +
    `\n\nCTA: ${p.carrossel.cta_final}\n\nLEGENDA:\n${p.carrossel.copy_legenda}`
  const textoEstatico = `HEADLINE: ${p.estatico.headline}\nSUBTEXTO: ${p.estatico.subtexto}\n\n` +
    `COPY PRIMÁRIA:\n${p.estatico.copy_primaria}\n\nTÍTULO: ${p.estatico.titulo_anuncio}\nDESCRIÇÃO: ${p.estatico.descricao_anuncio}`
  const textoVideo = `GANCHOS (escolha 1):\n${p.video.ganchos.map((g, i) => `${i + 1}. ${g}`).join('\n')}\n\n` +
    `ROTEIRO:\n${p.video.estrutura.map((e, i) => `${i + 1}. ${e}`).join('\n')}\n\nCTA: ${p.video.cta}`
  return (
    <div style={{ display: 'grid', gap: 8, marginTop: 8 }}>
      <details style={{ background: 'rgba(0,0,0,.3)', borderRadius: 10, padding: '8px 12px' }}>
        <summary style={{ cursor: 'pointer', fontWeight: 700 }} className="small">
          🎠 Carrossel — “{p.carrossel.titulo_capa}”
        </summary>
        <div style={{ margin: '8px 0' }}><BotaoCopiar rotulo="Copiar carrossel completo" texto={textoCarrossel} /></div>
        {p.carrossel.slides.map((s, i) => (
          <p key={i} className="small" style={{ margin: '0 0 6px' }}>
            <strong>Slide {i + 2} · {s.titulo}:</strong> {s.texto}
          </p>
        ))}
        <p className="small" style={{ margin: 0, color: C.verde }}><strong>CTA:</strong> {p.carrossel.cta_final}</p>
      </details>
      <details style={{ background: 'rgba(0,0,0,.3)', borderRadius: 10, padding: '8px 12px' }}>
        <summary style={{ cursor: 'pointer', fontWeight: 700 }} className="small">
          🖼 Estático — “{p.estatico.headline}”
        </summary>
        <div style={{ margin: '8px 0' }}><BotaoCopiar rotulo="Copiar estático completo" texto={textoEstatico} /></div>
        <p className="small" style={{ margin: '0 0 4px' }}><strong>Na arte:</strong> {p.estatico.headline} — {p.estatico.subtexto}</p>
        <p className="small" style={{ margin: '0 0 4px' }}><strong>Copy:</strong> {p.estatico.copy_primaria}</p>
        <p className="muted small" style={{ margin: 0 }}>título: {p.estatico.titulo_anuncio} · descrição: {p.estatico.descricao_anuncio}</p>
      </details>
      <details style={{ background: 'rgba(0,0,0,.3)', borderRadius: 10, padding: '8px 12px' }}>
        <summary style={{ cursor: 'pointer', fontWeight: 700 }} className="small">
          🎬 Vídeo — 3 ganchos + roteiro
        </summary>
        <div style={{ margin: '8px 0' }}><BotaoCopiar rotulo="Copiar roteiro completo" texto={textoVideo} /></div>
        {p.video.ganchos.map((g, i) => (
          <p key={i} className="small" style={{ margin: '0 0 4px', display: 'flex', gap: 8, alignItems: 'center' }}>
            <CopiarMini texto={g} /><span style={{ color: C.ouro, fontWeight: 700 }}>Gancho {i + 1}:</span>
            <span style={{ overflowWrap: 'anywhere' }}>“{g}”</span>
          </p>
        ))}
        <ol className="small" style={{ margin: '6px 0 4px 18px' }}>
          {p.video.estrutura.map((e, i) => (<li key={i} style={{ marginBottom: 2 }}>{e}</li>))}
        </ol>
        <p className="small" style={{ margin: 0, color: C.verde }}><strong>CTA:</strong> {p.video.cta}</p>
      </details>
    </div>
  )
}

function IdeiaComPecas({ ideia, porQue, tipo, pecasSalvas }: {
  ideia: string; porQue: string; tipo: string; pecasSalvas: Pecas | null
}) {
  const [estado, setEstado] = useState<'parado' | 'gerando' | 'pronto' | 'erro'>(pecasSalvas ? 'pronto' : 'parado')
  const [pecas, setPecas] = useState<Pecas | null>(pecasSalvas)

  async function gerar() {
    setEstado('gerando')
    try {
      const qs = new URLSearchParams({ tenant_slug: 'demo', ideia, por_que: porQue })
      const r = await fetch(`${api}/ads/criar_pecas?${qs}`, { method: 'POST', credentials: 'include' })
      if (!r.ok) throw new Error(String(r.status))
      const d = await r.json()
      setPecas(d.pecas); setEstado('pronto')
    } catch { setEstado('erro') }
  }

  return (
    <div style={{ background: 'rgba(0,0,0,.22)', borderRadius: 12, padding: '10px 14px', marginBottom: 8 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 10, alignItems: 'flex-start', flexWrap: 'wrap' }}>
        <p className="small" style={{ margin: 0, flex: 1, minWidth: 200 }}>
          <span className="badge" style={{ marginRight: 8 }}>{tipo.replace(/_/g, ' ')}</span>
          <strong>{ideia}</strong>
        </p>
        <button type="button" onClick={gerar} disabled={estado === 'gerando'}
          style={{ background: estado === 'gerando' ? 'rgba(201,162,39,.35)' : C.ouro, color: '#141210',
            border: 'none', borderRadius: 10, padding: '7px 14px', fontWeight: 800, fontSize: '.8rem',
            cursor: estado === 'gerando' ? 'wait' : 'pointer', whiteSpace: 'nowrap' }}>
          {estado === 'gerando' ? '⏳ Criando… (~2 min)' : pecas ? '🔄 Recriar peças' : '🎨 Criar as peças'}
        </button>
      </div>
      <p className="muted small" style={{ margin: '4px 0 0' }}>{porQue}</p>
      {estado === 'erro' ? <p className="small" style={{ color: C.vermelho, margin: '6px 0 0' }}>Falhou — tente de novo.</p> : null}
      {pecas ? <BlocoPecas p={pecas} /> : null}
    </div>
  )
}

function AnaliseConversasIA() {
  const [estado, setEstado] = useState<'carregando' | 'vazio' | 'gerando' | 'pronto' | 'erro'>('carregando')
  const [analise, setAnalise] = useState<AnaliseConversas | null>(null)
  const [geradoEm, setGeradoEm] = useState<string | null>(null)
  const [pecasSalvas, setPecasSalvas] = useState<Record<string, Pecas>>({})

  useEffect(() => {
    fetch(`${api}/ads/analise_conversas_salva?tenant_slug=demo`, { credentials: 'include', cache: 'no-store' })
      .then((r) => (r.ok ? r.json() : null))
      .then((dd) => {
        if (dd?.analise) { setAnalise(dd.analise); setGeradoEm(dd.gerado_em || null); setEstado('pronto') }
        else setEstado('vazio')
      })
      .catch(() => setEstado('vazio'))
    fetch(`${api}/ads/pecas_salvas?tenant_slug=demo`, { credentials: 'include', cache: 'no-store' })
      .then((r) => (r.ok ? r.json() : null))
      .then((dd) => {
        if (dd?.pecas) {
          const m: Record<string, Pecas> = {}
          for (const p of dd.pecas) if (!m[p.ideia]) m[p.ideia] = p.pecas
          setPecasSalvas(m)
        }
      })
      .catch(() => {})
  }, [])

  async function gerar() {
    setEstado('gerando')
    try {
      const r = await fetch(`${api}/ads/analise_conversas?tenant_slug=demo&days=30`,
        { method: 'POST', credentials: 'include' })
      if (!r.ok) throw new Error(String(r.status))
      const dd = await r.json()
      setAnalise(dd.analise); setGeradoEm(new Date().toISOString()); setEstado('pronto')
    } catch { setEstado('erro') }
  }

  return (
    <section className="featurePanel" style={{ borderTop: `3px solid ${C.verde}`, marginBottom: 14 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
        <div>
          <strong style={{ fontSize: '1.02rem' }}>🗣 O que os leads estão dizendo (IA)</strong>
          <p className="muted small" style={{ margin: '2px 0 0' }}>
            Lê as conversas reais agrupadas por anúncio: dúvidas, objeções e o vocabulário deles — vira melhoria de campanha
          </p>
        </div>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          {geradoEm ? <span className="muted small">gerada em {new Date(geradoEm).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })}</span> : null}
          <button type="button" onClick={gerar} disabled={estado === 'gerando' || estado === 'carregando'}
            style={{ background: estado === 'gerando' ? 'rgba(47,158,99,.35)' : C.verde, color: '#fff',
              border: 'none', borderRadius: 10, padding: '9px 16px', fontWeight: 800, fontSize: '.86rem',
              cursor: estado === 'gerando' ? 'wait' : 'pointer' }}>
            {estado === 'gerando' ? '⏳ Lendo conversas… (~2 min)' : analise ? '🔄 Refazer análise' : '🗣 Analisar conversas'}
          </button>
        </div>
      </div>
      {estado === 'erro' ? <p className="small" style={{ color: C.vermelho }}>Falhou — tente de novo em instantes.</p> : null}
      {analise ? (
        <div style={{ marginTop: 12, display: 'flex', flexDirection: 'column', gap: 12 }}>
          <p className="small" style={{ background: 'rgba(47,158,99,.08)', border: '1px solid rgba(47,158,99,.3)',
            borderRadius: 10, padding: 12, margin: 0 }}>
            <strong>Resumo:</strong> {analise.resumo_executivo}
          </p>
          {analise.por_criativo.map((pc, i) => (
            <details key={i} style={{ background: 'rgba(0,0,0,.22)', borderRadius: 12, padding: '10px 14px' }}>
              <summary style={{ cursor: 'pointer', fontWeight: 700 }}>
                <span style={{ display: 'inline-flex', alignItems: 'center', gap: 10, verticalAlign: 'middle' }}>
                  {pc.thumbnail_url ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img src={pc.thumbnail_url} alt="" width={44} height={44}
                      style={{ borderRadius: 8, objectFit: 'cover' }} />
                  ) : '🎬'}
                  <span style={{ overflowWrap: 'anywhere' }}>
                    {pc.anuncio}
                    {pc.campanha ? (
                      <span className="muted small" style={{ display: 'block', fontWeight: 400 }}>
                        📣 {pc.campanha}{pc.conjunto ? ` › 📦 ${pc.conjunto}` : ''}
                      </span>
                    ) : null}
                  </span>
                </span>
              </summary>
              <p className="small" style={{ margin: '8px 0' }}><strong>Qualidade dos leads:</strong> {pc.qualidade_dos_leads}</p>
              {pc.duvidas_comuns.length ? (
                <p className="small" style={{ margin: '0 0 6px' }}><strong>Dúvidas comuns:</strong> {pc.duvidas_comuns.join(' · ')}</p>
              ) : null}
              {pc.objecoes.length ? (
                <p className="small" style={{ margin: '0 0 6px', color: C.amarelo }}><strong>Objeções:</strong> {pc.objecoes.join(' · ')}</p>
              ) : null}
              <p className="small" style={{ margin: 0, color: C.verde }}><strong>Recomendação:</strong> {pc.recomendacao}</p>
            </details>
          ))}
          {analise.vocabulario_dos_leads.length ? (
            <div style={{ background: 'rgba(0,0,0,.22)', borderRadius: 12, padding: '10px 14px' }}>
              <ListaCopiavel rotulo="🗣 Vocabulário dos leads (usar em copy e keywords)" itens={analise.vocabulario_dos_leads} />
            </div>
          ) : null}
          {analise.ideias_para_campanhas.length ? (
            <div>
              <p style={{ margin: '0 0 8px', fontWeight: 800 }}>💡 Ideias para as campanhas — clique e crie as peças</p>
              {analise.ideias_para_campanhas.map((id, i) => (
                <IdeiaComPecas key={i} ideia={id.ideia} porQue={id.por_que} tipo={id.tipo}
                  pecasSalvas={pecasSalvas[id.ideia] || null} />
              ))}
            </div>
          ) : null}
        </div>
      ) : estado === 'vazio' ? (
        <p className="muted small" style={{ margin: '10px 0 0' }}>Nenhuma análise ainda — clique em “Analisar conversas” (fica salva).</p>
      ) : null}
    </section>
  )
}

function AbaLeads({ d }: { d: Cockpit }) {
  const [aberto, setAberto] = useState<string | null>(null)
  const grupos = useMemo(() => {
    const g: Record<string, { titulo: string; leads: Lead[] }> = {}
    for (const L of d.leads_recentes) {
      const k = L.source_id || '—'
      ;(g[k] ||= { titulo: L.ad_title || k, leads: [] }).leads.push(L)
    }
    return Object.entries(g).sort((a, b) => b[1].leads.length - a[1].leads.length)
  }, [d])

  return (
    <section>
      <FluxoConversas d={d} />
      <AnaliseConversasIA />
      <p className="muted" style={{ margin: '0 0 10px' }}>
        Leads agrupados pelo anúncio que os trouxe — clique no anúncio para abrir as conversas.
      </p>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {grupos.map(([sid, g]) => {
          const eng = g.leads.filter((L) => L.msgs_7d >= 3).length
          const abertoEste = aberto === sid
          return (
            <article key={sid} className="featurePanel" style={{ padding: '12px 16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', gap: 10, flexWrap: 'wrap',
                cursor: 'pointer', alignItems: 'center' }}
                onClick={() => setAberto(abertoEste ? null : sid)}>
                <strong style={{ overflowWrap: 'anywhere' }}><Seta aberto={abertoEste} />🎬 {g.titulo}</strong>
                <span className="small" style={{ whiteSpace: 'nowrap' }}>
                  <strong>{g.leads.length}</strong> leads · <span style={{ color: C.verde }}>{eng} 🔥</span>
                </span>
              </div>
              {abertoEste ? (
                <div style={{ marginTop: 10, display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {g.leads.map((L, i) => {
                    const t = tempLead(L.msgs_7d)
                    return (
                      <div key={i} style={{ borderLeft: `3px solid ${t.cor}`, paddingLeft: 10 }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', gap: 10, flexWrap: 'wrap' }}>
                          <strong className="small">{L.sender_name || `${L.phone.slice(0, 4)}…${L.phone.slice(-4)}`}</strong>
                          <span style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                            <Chip cor={t.cor}>{t.rotulo} · {L.msgs_7d} msgs</Chip>
                            <span className="muted small">
                              {new Date(L.first_ts).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })}
                            </span>
                          </span>
                        </div>
                        {L.conversa_amostra || L.first_text ? (
                          <p className="small" style={{ margin: '4px 0 0', fontStyle: 'italic', opacity: .85, overflowWrap: 'anywhere' }}>
                            “{(L.conversa_amostra || L.first_text || '').slice(0, 260)}”
                          </p>
                        ) : null}
                      </div>
                    )
                  })}
                </div>
              ) : null}
            </article>
          )
        })}
      </div>
    </section>
  )
}
