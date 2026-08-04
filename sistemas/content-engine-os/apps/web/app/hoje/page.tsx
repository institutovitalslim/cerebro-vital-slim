import Link from 'next/link'
import { redirect } from 'next/navigation'

import { fetchJson } from '../api'
import { CardAcao } from '../components/ui/card-acao'
import { Chip } from '../components/ui/chip'
import { Kpi } from '../components/ui/kpi'
import { ESTADO_PECA } from '../components/ui/estados'

// ————— /hoje — "o que eu faço agora?" —————
// Página 100% servidor: NÃO calcula nada, só junta o que os endpoints já
// entregam prontos e leva a pessoa direto pro lugar certo com 1 clique.
// Erro de fonte = aviso visível (política: erro nunca vira zero silencioso).

export const dynamic = 'force-dynamic'

const apiPublico = process.env.NEXT_PUBLIC_API_BASE_URL || '/api'

// ————— tipos (só os campos que a página usa) —————

type Criativo = { id: string; format: string; title: string | null; status: string; assets: string[] }
type EntradaCalendario = {
  id: string; title: string; format: string | null; channel: string | null
  status: string; scheduled_for: string | null
}
type Acao = { tipo: string; canal: string; titulo: string; impacto_mensal: number | null; evidencia: string }
type FluxoDia = { periodo: string; contatos_novos: number }
type Cockpit = {
  resumo: { leads_engajados: number; leads_ctwa: number }
  acoes: Acao[]
  fluxo_leads: { por_dia: FluxoDia[] }
}
type Sugestao = {
  pilar: string; formato_sugerido: string; degrade: string
  item: {
    id: string; tipo: string; titulo: string; resumo: string | null
    hook: string | null; origem: string
  } | null
}
type BI = {
  social_profile?: { followers_count: number | null } | null
  follower_movement?: { delta_7d: number | null } | null
}

// ————— ajudantes —————

type Busca<T> = { dados: T | null; status: number | null }

async function busca<T>(path: string): Promise<Busca<T>> {
  try {
    return { dados: await fetchJson<T>(path), status: null }
  } catch (e) {
    const m = e instanceof Error ? e.message.match(/(\d{3})\s*$/) : null
    return { dados: null, status: m ? Number(m[1]) : 0 }
  }
}

const brl = (v: number | null | undefined) =>
  v == null ? '—' : Number(v).toLocaleString('pt-BR', {
    style: 'currency', currency: 'BRL', minimumFractionDigits: 0, maximumFractionDigits: 0,
  })

const num = (v: number | null | undefined) =>
  v == null ? '—' : Number(v).toLocaleString('pt-BR')

// dia no fuso da Bahia (o servidor roda em UTC)
const diaBahia = (d: string | Date) =>
  new Date(d).toLocaleDateString('en-CA', { timeZone: 'America/Bahia' })

const dataCurta = (d: string) =>
  new Date(d).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', timeZone: 'America/Bahia' })

const estadoDe = (status: string) =>
  ESTADO_PECA[status] || ESTADO_PECA[status.replace(/o$/, 'a')] ||
  { rotulo: status, emoji: '🧩', cor: 'var(--state-neutral)' }

const FORMATO_NOME: Record<string, string> = {
  reel: 'Reel', reels: 'Reel', carrossel: 'Carrossel', estatico: 'Estático', stories: 'Stories',
}

const CALENDARIO_STATUS: Record<string, string> = {
  planned: 'planejada', in_review: 'em revisão', approved: 'aprovada',
  aprovado_para_publicar: 'aprovada', scheduled: 'agendada',
}

// entrada já publicada/medida não entra no "publicar hoje"
const JA_FOI = new Set(['published', 'publicado', 'metrics_pending', 'medido', 'cancelled', 'cancelado'])

function Aviso({ children }: { children: React.ReactNode }) {
  return <div className="empty">⚠️ {children}</div>
}

// ————— página —————

export default async function Page() {
  const [criativos, calendario, cockpit, sugestao, bi] = await Promise.all([
    busca<{ items: Criativo[] }>('/generation/creatives?tenant_slug=demo&limit=60'),
    busca<{ items: EntradaCalendario[] }>('/calendar/entries?tenant_slug=demo'),
    busca<Cockpit>('/ads/cockpit?tenant_slug=demo&days=30'),
    busca<Sugestao>('/ideias/sugestao_do_dia?tenant_slug=demo'),
    busca<BI>('/bi/overview?tenant_slug=demo'),
  ])

  if ([criativos, calendario, cockpit, sugestao, bi].some((r) => r.status === 401)) {
    redirect('/login')
  }

  // ✅ revisar: peças com arte pronta esperando um sim ou não
  const fila = (criativos.dados?.items || []).filter((c) => c.status === 'renderizado')
  const filaAds = fila.filter((c) => (c as unknown as { destino?: string | null }).destino === 'meta_ads').length
  const filaOrganico = fila.length - filaAds

  // 📅 publicar: entradas com data até hoje que ainda não saíram
  const hoje = diaBahia(new Date())
  const pendentes = (calendario.dados?.items || [])
    .filter((e) => e.scheduled_for && !JA_FOI.has(e.status) && diaBahia(e.scheduled_for) <= hoje)
    .sort((a, b) => (a.scheduled_for! < b.scheduled_for! ? -1 : 1))

  // 🎯 tráfego: as 3 ações que mais devolvem dinheiro (já vêm ordenadas por R$)
  const acoes = (cockpit.dados?.acoes || []).slice(0, 3)

  // 💡 sugestão do dia
  const s = sugestao.dados
  const item = s?.item || null
  let linkProduzir = '/criar'
  if (s && item) {
    const qs = new URLSearchParams({ source: 'ideias', formato: s.formato_sugerido || 'reel' })
    if (item.tipo) qs.set('tipo', item.tipo)
    if (item.titulo) qs.set('titulo', item.titulo)
    if (item.hook) qs.set('hook', item.hook)
    linkProduzir = `/criar?${qs.toString()}`
  }

  // pulso do rodapé
  const ultimoDia = cockpit.dados?.fluxo_leads?.por_dia?.at(-1) || null
  const seguidores = bi.dados?.social_profile?.followers_count ?? null
  const delta7 = bi.dados?.follower_movement?.delta_7d ?? null

  return (
    <div className="dashboardRoot">
      <header className="pageHeader heroHeader">
        <div>
          <p className="eyebrow">Seu dia</p>
          <h2 className="pageTitle">O que eu faço agora?</h2>
          <p className="heroText">
            Tudo o que precisa da sua atenção hoje, em uma tela só: o que revisar,
            o que publicar, o que ajustar nos anúncios e o que criar. Cada bloco
            leva direto pro lugar onde a coisa acontece.
          </p>
        </div>
        <div className="heroActions">
          <a className="secondaryLink" href="/hoje">↻ Atualizar</a>
        </div>
      </header>

      {/* ✅ Revisar */}
      <section className="featurePanel">
        <div className="sectionHeaderInline">
          <div>
            <p className="eyebrow">✅ Revisar</p>
            <h3 className="sectionTitle">
              {fila.length > 0
                ? `${fila.length} ${fila.length === 1 ? 'peça esperando' : 'peças esperando'} seu sim`
                : 'Peças esperando seu sim'}
            </h3>
            {fila.length > 0 ? (
              <p className="muted small" style={{ margin: '2px 0 0' }}>
                🌱 {filaOrganico} orgânica{filaOrganico === 1 ? '' : 's'} (feed/perfil) · 📣 {filaAds} para anúncio
              </p>
            ) : null}
          </div>
          <Link className="secondaryLink" href="/banco-criativos">Ver a fila inteira →</Link>
        </div>
        {criativos.status != null ? (
          <Aviso>Não consegui carregar a fila de peças agora. Atualize a página; se continuar, o banco de criativos pode estar fora do ar.</Aviso>
        ) : fila.length === 0 ? (
          <div className="empty">Nada esperando decisão. Que tal <Link href="/criar">criar algo novo</Link>?</div>
        ) : (
          <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(130px, 1fr))', gap: 12 }}>
            {fila.slice(0, 4).map((c) => {
              const estado = estadoDe(c.status)
              const retrato = c.format === 'reels' || c.format === 'stories'
              return (
                <Link key={c.id} href="/banco-criativos" className="card" style={{ padding: 8, display: 'grid', gap: 8 }}>
                  <div style={{ aspectRatio: retrato ? '9 / 16' : '4 / 5', borderRadius: 12, overflow: 'hidden',
                    background: 'linear-gradient(180deg,#17120d,#0f0b07)', border: '1px solid rgba(212,168,60,0.12)' }}>
                    {c.assets[0] ? (
                      <img src={`${apiPublico}${c.assets[0]}`} alt={c.title || 'peça para revisar'}
                        style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                    ) : (
                      <div className="muted small" style={{ display: 'grid', placeItems: 'center', height: '100%', padding: 10, textAlign: 'center' }}>
                        {estado.emoji} {estado.rotulo}
                      </div>
                    )}
                  </div>
                  <Chip cor={estado.cor}>{estado.emoji} {estado.rotulo}</Chip>
                  <span className="muted small">{(c as { destino?: string | null }).destino === 'meta_ads' ? '📣 anúncio' : '🌱 orgânico'}</span>
                  <p className="muted small" style={{ margin: 0 }}>{c.title || FORMATO_NOME[c.format] || c.format}</p>
                </Link>
              )
            })}
          </div>
        )}
      </section>

      {/* 📅 Publicar hoje */}
      <section className="featurePanel">
        <div className="sectionHeaderInline">
          <div>
            <p className="eyebrow">📅 Publicar hoje</p>
            <h3 className="sectionTitle">
              {pendentes.length > 0
                ? `${pendentes.length} ${pendentes.length === 1 ? 'publicação combinada' : 'publicações combinadas'} até hoje`
                : 'Publicações combinadas para hoje'}
            </h3>
          </div>
          <Link className="secondaryLink" href="/calendario">Abrir calendário →</Link>
        </div>
        {calendario.status != null ? (
          <Aviso>Não consegui carregar o calendário agora. Atualize a página; se continuar, veja direto o <Link href="/calendario">calendário</Link>.</Aviso>
        ) : pendentes.length === 0 ? (
          <div className="empty">Nada agendado para hoje e nada atrasado. Calendário em dia 🎉</div>
        ) : (
          <div style={{ display: 'grid', gap: 10 }}>
            {pendentes.slice(0, 5).map((e) => {
              const dia = diaBahia(e.scheduled_for!)
              const atrasada = dia < hoje
              return (
                <CardAcao
                  key={e.id}
                  emoji={atrasada ? '⏰' : '📅'}
                  cor={atrasada ? 'var(--state-bad)' : 'var(--state-good)'}
                  titulo={e.title}
                  sub={[FORMATO_NOME[e.format || ''] || e.format, e.channel, CALENDARIO_STATUS[e.status] || e.status]
                    .filter(Boolean).join(' · ')}
                  direita={<Chip cor={atrasada ? 'var(--state-bad)' : 'var(--state-good)'}>
                    {atrasada ? `atrasada — era ${dataCurta(e.scheduled_for!)}` : 'é hoje'}
                  </Chip>}
                  href="/calendario"
                />
              )
            })}
            {pendentes.length > 5 ? (
              <p className="muted small" style={{ margin: 0 }}>
                …e mais {pendentes.length - 5} no <Link href="/calendario">calendário</Link>.
              </p>
            ) : null}
          </div>
        )}
      </section>

      {/* 🎯 Tráfego */}
      <section className="featurePanel">
        <div className="sectionHeaderInline">
          <div>
            <p className="eyebrow">🎯 Tráfego</p>
            <h3 className="sectionTitle">O que mais devolve dinheiro se você fizer hoje</h3>
          </div>
          <Link className="secondaryLink" href="/trafego">Abrir central de tráfego →</Link>
        </div>
        {cockpit.status != null ? (
          <Aviso>Não consegui falar com a central de tráfego agora. Atualize a página ou abra a <Link href="/trafego">central</Link> direto.</Aviso>
        ) : acoes.length === 0 ? (
          <div className="empty">Nenhuma ação pendente nos anúncios. Campanhas rodando sem alerta 🎉</div>
        ) : (
          <div style={{ display: 'grid', gap: 10 }}>
            {acoes.map((a, i) => (
              <CardAcao
                key={`${a.tipo}-${i}`}
                emoji={a.canal === 'google' ? '🔎' : '📣'}
                cor="var(--state-warn)"
                titulo={a.titulo}
                sub={a.evidencia}
                direita={a.impacto_mensal != null && a.impacto_mensal > 0
                  ? <Chip cor="var(--state-warn)">até {brl(a.impacto_mensal)}/mês</Chip>
                  : undefined}
                href="/trafego"
              />
            ))}
          </div>
        )}
      </section>

      {/* 💡 Criar hoje */}
      <section className="featurePanel">
        <div className="sectionHeaderInline">
          <div>
            <p className="eyebrow">💡 Criar hoje</p>
            <h3 className="sectionTitle">A sugestão do dia, pronta para produzir</h3>
          </div>
          <Link className="secondaryLink" href="/ideias">Ver todas as ideias →</Link>
        </div>
        {sugestao.status != null ? (
          <Aviso>Não consegui buscar a sugestão do dia. Atualize a página ou escolha uma ideia na <Link href="/ideias">fila de ideias</Link>.</Aviso>
        ) : !s || !item ? (
          <div className="empty">Ainda não há ideias na fila para sugerir. Cadastre temas ou fontes e a sugestão aparece aqui.</div>
        ) : (
          <CardAcao emoji="💡" cor="var(--state-good)" titulo={item.titulo}
            sub={item.hook ? `Gancho: ${item.hook}` : item.resumo || undefined}>
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center', marginTop: 10 }}>
              <Chip cor="var(--state-neutral)">tema do dia: {s.pilar}</Chip>
              <Chip cor="var(--state-neutral)">formato: {FORMATO_NOME[s.formato_sugerido] || s.formato_sugerido}</Chip>
              <span className="muted small">vinda de: {item.origem}</span>
            </div>
            <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', alignItems: 'center', marginTop: 12 }}>
              <Link className="primaryButton" style={{ padding: '10px 18px' }} href={linkProduzir}>▶ Produzir agora</Link>
              <span className="muted small">🌱 {s.degrade}</span>
            </div>
          </CardAcao>
        )}
      </section>

      {/* pulso do dia */}
      <section className="featurePanel">
        <div className="sectionHeaderInline">
          <div>
            <p className="eyebrow">🫀 Pulso</p>
            <h3 className="sectionTitle">Como o motor está respirando</h3>
          </div>
        </div>
        <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(190px, 1fr))', gap: 14 }}>
          {cockpit.status != null ? (
            <Aviso>Sem dados de leads agora — a central de tráfego não respondeu. Atualize a página.</Aviso>
          ) : (
            <>
              <Kpi
                rotulo="Pessoas novas no WhatsApp"
                valor={ultimoDia ? num(ultimoDia.contatos_novos) : '—'}
                sub={ultimoDia ? `no dia ${dataCurta(ultimoDia.periodo)}` : 'ainda sem registro diário'}
                cor="var(--state-good)"
              />
              <Kpi
                rotulo="Conversas com real interesse"
                valor={num(cockpit.dados?.resumo?.leads_engajados)}
                sub="últimos 30 dias, vindas de anúncio"
                cor="var(--state-good)"
              />
            </>
          )}
          {bi.status != null ? (
            <Aviso>Sem número de seguidores agora — o painel de BI não respondeu. Atualize a página.</Aviso>
          ) : (
            <Kpi
              rotulo="Seguidores no Instagram"
              valor={num(seguidores)}
              sub={delta7 != null ? `${delta7 >= 0 ? '+' : ''}${num(delta7)} nos últimos 7 dias` : 'variação ainda sem histórico'}
              cor="var(--state-warn)"
            />
          )}
        </div>
      </section>
    </div>
  )
}
