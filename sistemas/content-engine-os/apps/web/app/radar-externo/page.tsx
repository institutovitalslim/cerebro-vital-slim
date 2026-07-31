import Link from 'next/link'
import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'
import { revalidatePath } from 'next/cache'

import { apiBase, fetchJson } from '../api'

export const dynamic = 'force-dynamic'

const SOURCE_KINDS = ['approved', 'candidate', 'excluded', 'own_account', 'thematic_search'] as const
const SIGNAL_STATES = ['insufficient', 'normal', 'signal', 'outlier', 'breakout'] as const

type SourceKind = (typeof SOURCE_KINDS)[number]
type SignalState = (typeof SIGNAL_STATES)[number]
type GovernanceResult = 'ok' | '403' | '409' | '422' | '503' | 'error'

type ReverseEngineering = {
  why_it_may_have_worked?: string
  pattern?: string
  adaptation_to_instituto_vital_slim?: string
  suggested_hook?: string | null
}

type ComparisonPost = {
  content_item_id: string
  external_id: string
  url?: string | null
  metric_value: number
}

type ExternalItem = {
  id: string
  source_profile: string
  actual_source_profile?: string | null
  source_network: string
  external_id: string
  url?: string | null
  canonical_format: string
  caption_excerpt?: string | null
  reverse_engineering?: ReverseEngineering
  source_kind: SourceKind
  baseline_id?: string | null
  candidate_snapshot_id?: string | null
  algorithm_version?: string | null
  cutoff_at?: string | null
  metric_basis?: string | null
  metric_value?: number | null
  sample_count?: number | null
  median_value?: number | null
  maturity?: 'insufficient' | 'provisional' | 'target' | null
  performance_ratio?: number | null
  signal_state?: SignalState | null
  reason?: string | null
  comparison_posts?: ComparisonPost[]
  eligible_for_ideation: boolean
}

type RadarSource = {
  id: string
  network: string
  canonical_key: string
  display_name?: string | null
  source_kind: SourceKind
  active: boolean
  decision_reason?: string | null
}

type Overview = {
  feature_enabled: boolean
  version: string
  mode: 'observed_metrics_only'
  summary: {
    total_items: number
    candidate_items: number
    governed_items: number
    eligible_items: number
    last_ingest_at?: string | null
  }
  top_items: ExternalItem[]
  sources: RadarSource[]
  thresholds: { outlier: number; breakout: number; minimum_sample: number; target_sample: number }
}

type LoadResult =
  | { state: 'ready'; data: Overview }
  | { state: 'unauthorized' }
  | { state: 'forbidden' }
  | { state: 'error'; message: string }

const sourceLabels: Record<SourceKind, string> = {
  approved: 'Fonte aprovada',
  candidate: 'Candidata · prévia',
  excluded: 'Excluída',
  own_account: 'Conta própria',
  thematic_search: 'Busca temática',
}

const signalLabels: Record<SignalState, string> = {
  insufficient: 'Amostra insuficiente',
  normal: 'Dentro do padrão',
  signal: 'Sinal inicial',
  outlier: 'Outlier',
  breakout: 'Breakout',
}

const metricLabels: Record<string, string> = {
  views: 'visualizações',
  plays: 'reproduções',
  reach: 'alcance',
  public_interactions: 'interações públicas',
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function requiredString(value: unknown, field: string): string {
  if (typeof value !== 'string' || !value.trim()) throw new Error(`Contrato inválido: ${field}`)
  return value
}

function optionalString(value: unknown): string | null | undefined {
  return value == null ? value as null | undefined : typeof value === 'string' ? value : undefined
}

function finiteNumber(value: unknown, field: string, nullable = false): number | null {
  if (nullable && value == null) return null
  if (typeof value !== 'number' || !Number.isFinite(value)) throw new Error(`Contrato inválido: ${field}`)
  return value
}

function nonNegativeNumber(value: unknown, field: string): number {
  const number = finiteNumber(value, field) as number
  if (number < 0) throw new Error(`Contrato inválido: ${field}`)
  return number
}

function isSourceKind(value: unknown): value is SourceKind {
  return typeof value === 'string' && (SOURCE_KINDS as readonly string[]).includes(value)
}

function isSignalState(value: unknown): value is SignalState {
  return typeof value === 'string' && (SIGNAL_STATES as readonly string[]).includes(value)
}

function safeExternalUrl(value: unknown): string | null {
  if (typeof value !== 'string') return null
  try {
    const url = new URL(value)
    return url.protocol === 'http:' || url.protocol === 'https:' ? url.toString() : null
  } catch {
    return null
  }
}

function parseReverseEngineering(value: unknown): ReverseEngineering | undefined {
  if (!isRecord(value)) return undefined
  return {
    why_it_may_have_worked: optionalString(value.why_it_may_have_worked) || undefined,
    pattern: optionalString(value.pattern) || undefined,
    adaptation_to_instituto_vital_slim: optionalString(value.adaptation_to_instituto_vital_slim) || undefined,
    suggested_hook: optionalString(value.suggested_hook),
  }
}

function parseComparison(value: unknown, index: number): ComparisonPost {
  if (!isRecord(value)) throw new Error(`Contrato inválido: comparison_posts[${index}]`)
  return {
    content_item_id: requiredString(value.content_item_id, `comparison_posts[${index}].content_item_id`),
    external_id: requiredString(value.external_id, `comparison_posts[${index}].external_id`),
    url: safeExternalUrl(value.url),
    metric_value: finiteNumber(value.metric_value, `comparison_posts[${index}].metric_value`) as number,
  }
}

function parseItem(value: unknown, index: number): ExternalItem {
  if (!isRecord(value) || !isSourceKind(value.source_kind)) throw new Error(`Contrato inválido: top_items[${index}]`)
  if (value.signal_state != null && !isSignalState(value.signal_state)) throw new Error(`Contrato inválido: top_items[${index}].signal_state`)
  const maturity = value.maturity
  if (maturity != null && !['insufficient', 'provisional', 'target'].includes(String(maturity))) {
    throw new Error(`Contrato inválido: top_items[${index}].maturity`)
  }
  const comparisons = value.comparison_posts == null ? [] : value.comparison_posts
  if (!Array.isArray(comparisons)) throw new Error(`Contrato inválido: top_items[${index}].comparison_posts`)
  return {
    id: requiredString(value.id, `top_items[${index}].id`),
    source_profile: requiredString(value.source_profile, `top_items[${index}].source_profile`),
    actual_source_profile: optionalString(value.actual_source_profile),
    source_network: requiredString(value.source_network, `top_items[${index}].source_network`),
    external_id: requiredString(value.external_id, `top_items[${index}].external_id`),
    url: safeExternalUrl(value.url),
    canonical_format: requiredString(value.canonical_format, `top_items[${index}].canonical_format`),
    caption_excerpt: optionalString(value.caption_excerpt),
    reverse_engineering: parseReverseEngineering(value.reverse_engineering),
    source_kind: value.source_kind,
    baseline_id: optionalString(value.baseline_id),
    candidate_snapshot_id: optionalString(value.candidate_snapshot_id),
    algorithm_version: optionalString(value.algorithm_version),
    cutoff_at: optionalString(value.cutoff_at),
    metric_basis: optionalString(value.metric_basis),
    metric_value: finiteNumber(value.metric_value, `top_items[${index}].metric_value`, true),
    sample_count: finiteNumber(value.sample_count, `top_items[${index}].sample_count`, true),
    median_value: finiteNumber(value.median_value, `top_items[${index}].median_value`, true),
    maturity: maturity as ExternalItem['maturity'],
    performance_ratio: finiteNumber(value.performance_ratio, `top_items[${index}].performance_ratio`, true),
    signal_state: value.signal_state as SignalState | null | undefined,
    reason: optionalString(value.reason),
    comparison_posts: comparisons.map(parseComparison),
    eligible_for_ideation: value.eligible_for_ideation === true,
  }
}

function parseSource(value: unknown, index: number): RadarSource {
  if (!isRecord(value) || !isSourceKind(value.source_kind) || typeof value.active !== 'boolean') {
    throw new Error(`Contrato inválido: sources[${index}]`)
  }
  return {
    id: requiredString(value.id, `sources[${index}].id`),
    network: requiredString(value.network, `sources[${index}].network`),
    canonical_key: requiredString(value.canonical_key, `sources[${index}].canonical_key`),
    display_name: optionalString(value.display_name),
    source_kind: value.source_kind,
    active: value.active,
    decision_reason: optionalString(value.decision_reason),
  }
}

function parseOverview(value: unknown): Overview {
  if (!isRecord(value) || typeof value.feature_enabled !== 'boolean' || value.mode !== 'observed_metrics_only') {
    throw new Error('Contrato inválido: overview')
  }
  if (!isRecord(value.summary) || !isRecord(value.thresholds) || !Array.isArray(value.top_items) || !Array.isArray(value.sources)) {
    throw new Error('Contrato inválido: estrutura do overview')
  }
  return {
    feature_enabled: value.feature_enabled,
    version: requiredString(value.version, 'version'),
    mode: value.mode,
    summary: {
      total_items: nonNegativeNumber(value.summary.total_items, 'summary.total_items'),
      candidate_items: nonNegativeNumber(value.summary.candidate_items, 'summary.candidate_items'),
      governed_items: nonNegativeNumber(value.summary.governed_items, 'summary.governed_items'),
      eligible_items: nonNegativeNumber(value.summary.eligible_items, 'summary.eligible_items'),
      last_ingest_at: optionalString(value.summary.last_ingest_at),
    },
    top_items: value.top_items.slice(0, 50).map(parseItem),
    sources: value.sources.map(parseSource),
    thresholds: {
      outlier: nonNegativeNumber(value.thresholds.outlier, 'thresholds.outlier'),
      breakout: nonNegativeNumber(value.thresholds.breakout, 'thresholds.breakout'),
      minimum_sample: nonNegativeNumber(value.thresholds.minimum_sample, 'thresholds.minimum_sample'),
      target_sample: nonNegativeNumber(value.thresholds.target_sample, 'thresholds.target_sample'),
    },
  }
}

function asText(value: string | string[] | undefined): string {
  return Array.isArray(value) ? value[0] || '' : value || ''
}

function formatNumber(value: number | null | undefined): string {
  if (value == null || !Number.isFinite(value)) return 'não observado'
  return new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 1 }).format(value)
}

function formatDate(value?: string | null): string {
  if (!value) return 'ainda não registrada'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return 'data não disponível'
  return new Intl.DateTimeFormat('pt-BR', { dateStyle: 'short', timeStyle: 'short', timeZone: 'America/Bahia' }).format(date)
}

function signalTone(state?: SignalState | null): string {
  if (state === 'breakout') return 'radarSignalBreakout'
  if (state === 'outlier') return 'radarSignalOutlier'
  if (state === 'signal') return 'radarSignalEarly'
  if (state === 'normal') return 'radarSignalNormal'
  return 'radarSignalInsufficient'
}

function buildStudioHref(item: ExternalItem, radarVersion: string): string {
  const reverse = item.reverse_engineering || {}
  const routeByFormat: Record<string, string> = {
    reel: '/producao/reels',
    carousel: '/producao/carrosseis',
    post: '/producao/estaticos',
    story: '/criar',
  }
  const route = routeByFormat[item.canonical_format] || '/criar'
  const originTag = item.baseline_id ? `radar:${item.id}:${item.baseline_id}` : `radar:${item.id}`
  const qs = new URLSearchParams({
    source: 'radar',
    thesis: reverse.adaptation_to_instituto_vital_slim || item.caption_excerpt || '',
    hook: reverse.suggested_hook || '',
    origin_tag: originTag,
    objective: 'prova_e_metodo',
    formato: item.canonical_format,
    radar_item_id: item.id,
    radar_external_id: item.external_id,
    radar_baseline_id: item.baseline_id || '',
    radar_snapshot_id: item.candidate_snapshot_id || '',
    radar_cutoff_at: item.cutoff_at || '',
    radar_algorithm_version: item.algorithm_version || radarVersion,
  })
  return `${route}?${qs.toString()}`
}

async function loadOverview(): Promise<LoadResult> {
  try {
    const raw = await fetchJson<unknown>('/external-learning/overview?tenant_slug=demo')
    return { state: 'ready', data: parseOverview(raw) }
  } catch (error) {
    const message = error instanceof Error ? error.message : ''
    const status = Number(message.match(/(\d{3})\s*$/)?.[1] || 0)
    if (status === 401) return { state: 'unauthorized' }
    if (status === 403) return { state: 'forbidden' }
    return { state: 'error', message: message.startsWith('Contrato inválido') ? 'A resposta da API não passou pela validação de segurança.' : 'A API do radar não respondeu corretamente.' }
  }
}

async function updateSourceGovernance(formData: FormData): Promise<void> {
  'use server'

  const sourceId = String(formData.get('source_id') || '').trim()
  const sourceKind = String(formData.get('source_kind') || '').trim()
  const reason = String(formData.get('reason') || '').trim()
  if (!/^[a-zA-Z0-9-]{1,80}$/.test(sourceId) || !isSourceKind(sourceKind) || reason.length < 3 || reason.length > 1000) {
    redirect('/radar-externo?governanca=422#fontes-radar')
  }

  let status = 0
  try {
    const cookie = (await cookies()).toString()
    const response = await fetch(`${apiBase}/external-learning/sources/${encodeURIComponent(sourceId)}?tenant_slug=demo`, {
      method: 'PATCH',
      cache: 'no-store',
      headers: { 'Content-Type': 'application/json', ...(cookie ? { cookie } : {}) },
      body: JSON.stringify({ source_kind: sourceKind, reason }),
    })
    status = response.status
  } catch {
    redirect('/radar-externo?governanca=error#fontes-radar')
  }

  if (status === 401) redirect('/login')
  if (status === 403 || status === 409 || status === 422 || status === 503) {
    redirect(`/radar-externo?governanca=${status}#fontes-radar`)
  }
  if (status < 200 || status >= 300) redirect('/radar-externo?governanca=error#fontes-radar')
  revalidatePath('/radar-externo')
  redirect('/radar-externo?governanca=ok#fontes-radar')
}

function StatePage({
  eyebrow,
  title,
  description,
  tone = 'neutral',
  children,
}: {
  eyebrow: string
  title: string
  description: string
  tone?: 'neutral' | 'error'
  children: React.ReactNode
}) {
  return (
    <div className="dashboardRoot radarRoot">
      <header className="pageHeader heroHeader radarHero radarStateHero">
        <div className="radarHeroCopy">
          <p className="eyebrow">{eyebrow}</p>
          <h2 className="pageTitle">{title}</h2>
          <p className="heroText">{description}</p>
        </div>
      </header>
      <section className={`radarStatePanel ${tone === 'error' ? 'radarStateError' : ''}`} role={tone === 'error' ? 'alert' : 'status'} aria-live="polite">
        {children}
      </section>
    </div>
  )
}

function GovernanceFeedback({ result }: { result: GovernanceResult | '' }) {
  if (!result) return null
  const messages: Record<GovernanceResult, { tone: 'ok' | 'error'; text: string }> = {
    ok: { tone: 'ok', text: 'Decisão salva. A fonte e a trilha de auditoria foram atualizadas.' },
    '403': { tone: 'error', text: 'A decisão não foi salva. Somente uma pessoa com papel owner pode alterar a governança.' },
    '409': { tone: 'error', text: 'A decisão não foi salva. Resolva a busca temática para uma fonte real antes de aprová-la.' },
    '422': { tone: 'error', text: 'Revise o novo estado e escreva uma justificativa entre 3 e 1.000 caracteres.' },
    '503': { tone: 'error', text: 'A decisão não foi salva porque o Radar está desativado neste ambiente.' },
    error: { tone: 'error', text: 'Não foi possível salvar a decisão. Tente novamente sem alterar os dados informados.' },
  }
  const message = messages[result]
  return <div className={`radarGovernanceFeedback is-${message.tone}`} role={message.tone === 'error' ? 'alert' : 'status'} aria-live="polite">{message.text}</div>
}

function SourceGovernance({ sources, result = '' }: { sources: RadarSource[]; result?: GovernanceResult | '' }) {
  return (
    <section className="section radarSourcesSection" id="fontes-radar" aria-labelledby="fontes-radar-titulo">
      <div className="sectionHeaderInline">
        <div>
          <p className="eyebrow">Governança no Radar</p>
          <h3 className="sectionTitle" id="fontes-radar-titulo">Fontes registradas</h3>
          <p className="muted small radarSectionIntro">Apenas owner pode decidir. Toda mudança exige justificativa e é gravada na trilha de auditoria.</p>
        </div>
        <span className="badge" aria-label={`${sources.length} fontes registradas`}>{sources.length} fontes</span>
      </div>
      <GovernanceFeedback result={result} />
      {sources.length === 0 ? (
        <div className="radarInlineEmpty" role="status">Nenhuma fonte foi registrada no Radar. A coleta governada precisa cadastrar uma fonte antes da primeira decisão.</div>
      ) : (
        <div className="radarSourceGrid">
          {sources.map((source) => {
            const name = source.display_name || source.canonical_key
            const allowedTargets = SOURCE_KINDS.filter((kind) => kind !== source.source_kind && !(source.source_kind === 'thematic_search' && (kind === 'approved' || kind === 'own_account')))
            return (
              <article className={`radarSourceCard source-${source.source_kind} ${source.active ? '' : 'isInactive'}`} key={source.id}>
                <div className="radarCardTop">
                  <strong>{name}</strong>
                  <span className={`radarActivity ${source.active ? 'isActive' : 'isInactive'}`}>{source.active ? 'Ativa' : 'Inativa'}</span>
                </div>
                <div className="radarPillRow">
                  <span className="stateChip">{sourceLabels[source.source_kind]}</span>
                  <span className="badge badgeDark">{source.network}</span>
                </div>
                <span className="muted small">{source.canonical_key}</span>
                <p><strong>Justificativa atual:</strong> {source.decision_reason || 'sem justificativa registrada'}</p>
                {source.active ? (
                  <details className="radarGovernanceDetails">
                    <summary aria-label={`Alterar governança da fonte ${name}`}>Alterar governança</summary>
                    <form action={updateSourceGovernance} className="radarGovernanceForm">
                      <input type="hidden" name="source_id" value={source.id} />
                      <label>
                        <span>Novo estado para {name}</span>
                        <select className="input" name="source_kind" required defaultValue="">
                          <option value="" disabled>Selecione uma decisão</option>
                          {allowedTargets.map((kind) => <option value={kind} key={kind}>{sourceLabels[kind]}</option>)}
                        </select>
                      </label>
                      <label>
                        <span>Justificativa da decisão</span>
                        <textarea className="textarea" name="reason" minLength={3} maxLength={1000} required rows={3} placeholder="Registre a evidência e o motivo da mudança." />
                      </label>
                      <button className="secondaryButton" type="submit" aria-label={`Salvar decisão de governança para ${name}`}>Salvar decisão</button>
                    </form>
                  </details>
                ) : (
                  <span className="radarDisabledAction">Fonte inativa · nenhuma ação disponível</span>
                )}
              </article>
            )
          })}
        </div>
      )}
    </section>
  )
}

export default async function RadarExternoPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>
}) {
  const [result, params] = await Promise.all([loadOverview(), searchParams])

  if (result.state === 'unauthorized') {
    return <StatePage eyebrow="Sessão necessária" title="Entre para consultar o Radar." description="Os sinais externos e as decisões de fonte pertencem ao workspace autenticado."><Link className="primaryButton" href="/login">Entrar no Content Engine OS</Link></StatePage>
  }
  if (result.state === 'forbidden') {
    return <StatePage eyebrow="Acesso restrito" title="Seu perfil não pode abrir este Radar." description="A sessão existe, mas não tem acesso ao workspace solicitado. Nenhum dado foi exibido."><Link className="secondaryLink" href="/hoje">Voltar ao cockpit</Link></StatePage>
  }
  if (result.state === 'error') {
    return <StatePage eyebrow="Radar indisponível" title="Não foi possível carregar os sinais." description={result.message} tone="error"><p>Nenhum erro foi convertido em zero e nenhum empty state foi exibido.</p><Link className="primaryButton" href="/radar-externo">Tentar carregar novamente</Link></StatePage>
  }

  const data = result.data
  if (!data.feature_enabled) {
    return <StatePage eyebrow="Rollout controlado" title="Content Radar v1 está desativado." description="A feature flag está desligada neste ambiente. Não há dados, métricas ou oportunidades para interpretar nesta tela."><Link className="secondaryLink" href="/hoje">Voltar ao cockpit</Link></StatePage>
  }

  const governanceParam = asText(params.governanca)
  const governanceResult: GovernanceResult | '' = ['ok', '403', '409', '422', '503', 'error'].includes(governanceParam) ? governanceParam as GovernanceResult : ''

  if (data.top_items.length === 0) {
    return (
      <div className="dashboardRoot radarRoot">
        <header className="pageHeader heroHeader radarHero radarStateHero">
          <div className="radarHeroCopy">
            <div className="radarStatusLine"><span className="radarLiveDot isOn" aria-hidden /><span>Radar v1 ativo neste ambiente</span></div>
            <p className="eyebrow">Base sem observações</p>
            <h2 className="pageTitle">Ainda não há conteúdo externo observado.</h2>
            <p className="heroText">O Radar está disponível, mas a coleta ainda não entregou itens. Nenhum número foi estimado para preencher a tela.</p>
          </div>
          <div className="heroActions"><Link className="primaryButton" href="/radar-externo">Atualizar observações</Link></div>
        </header>
        <section className="radarStatePanel" role="status" aria-live="polite">
          <strong>Zero itens observados.</strong>
          <p>Aguarde a próxima coleta governada. Quando houver evidência pública, até os 50 itens prioritários aparecerão aqui.</p>
        </section>
        <SourceGovernance sources={data.sources} result={governanceResult} />
      </div>
    )
  }

  const queryText = asText(params.q).trim().slice(0, 120)
  const q = queryText.toLocaleLowerCase('pt-BR')
  const sourceParam = asText(params.fonte)
  const sourceKind: SourceKind | '' = isSourceKind(sourceParam) ? sourceParam : ''
  const signalParam = asText(params.sinal)
  const signalState: SignalState | '' = isSignalState(signalParam) ? signalParam : ''

  const filteredItems = data.top_items.filter((item) => {
    const searchable = `${item.source_profile} ${item.caption_excerpt || ''} ${item.reverse_engineering?.pattern || ''}`.toLocaleLowerCase('pt-BR')
    return (!q || searchable.includes(q)) && (!sourceKind || item.source_kind === sourceKind) && (!signalState || item.signal_state === signalState)
  })
  const eligibleItems = filteredItems.filter((item) => item.eligible_for_ideation)
  const showAll = asText(params.todos) === '1'
  const visibleItems = showAll ? filteredItems : filteredItems.slice(0, 12)
  const viewQuery = new URLSearchParams()
  if (queryText) viewQuery.set('q', queryText)
  if (sourceKind) viewQuery.set('fonte', sourceKind)
  if (signalState) viewQuery.set('sinal', signalState)
  const showAllQuery = new URLSearchParams(viewQuery)
  showAllQuery.set('todos', '1')

  return (
    <div className="dashboardRoot radarRoot">
      <header className="pageHeader heroHeader radarHero">
        <div className="radarHeroCopy">
          <div className="radarStatusLine"><span className="radarLiveDot isOn" aria-hidden /><span>Radar v1 ativo neste ambiente</span></div>
          <p className="eyebrow">Inteligência externa governada</p>
          <h2 className="pageTitle">Sinal real, não score decorativo.</h2>
          <p className="heroText">O radar compara métricas públicas observadas com posts do mesmo perfil, formato e base métrica. Quando o dado não existe, ele mostra que não existe — sem estimar visualizações, alcance ou sucesso.</p>
        </div>
        <div className="heroActions">
          <a className="secondaryLink" href="#fontes-radar">Gerenciar fontes deste Radar</a>
          <Link className="primaryButton" href="/ideias">Abrir fila de ideias</Link>
        </div>
      </header>

      <section className="metricGrid radarMetrics" aria-label="Resumo do radar">
        <article className="metricCard"><span className="metricLabel">Itens observados</span><strong className="metricValue">{formatNumber(data.summary.total_items)}</strong><p className="muted small">excluídos não entram neste total</p></article>
        <article className="metricCard"><span className="metricLabel">Base governada</span><strong className="metricValue">{formatNumber(data.summary.governed_items)}</strong><p className="muted small">fontes aprovadas + conta própria</p></article>
        <article className="metricCard"><span className="metricLabel">Em prévia</span><strong className="metricValue">{formatNumber(data.summary.candidate_items)}</strong><p className="muted small">candidatas não promovem conteúdo sozinhas</p></article>
        <article className="metricCard radarMetricPrimary"><span className="metricLabel">Elegíveis para ideação</span><strong className="metricValue">{formatNumber(data.summary.eligible_items)}</strong><p className="muted small">outlier ou breakout em fonte aprovada</p></article>
      </section>

      <section className="radarMethod" aria-label="Como o sinal é calculado">
        <div><p className="eyebrow">Verdade operacional</p><h3 className="sectionTitle">O que precisa acontecer para um post subir</h3></div>
        <ol className="radarMethodSteps">
          <li><span>01</span><strong>Métrica observada</strong><small>views, plays, alcance ou interações públicas — nunca um substituto inventado.</small></li>
          <li><span>02</span><strong>Comparação justa</strong><small>mesmo perfil, mesmo formato, mesma base métrica e só dados disponíveis até o corte.</small></li>
          <li><span>03</span><strong>Mediana rastreável</strong><small>mínimo de {data.thresholds.minimum_sample} comparáveis; maturidade completa em {data.thresholds.target_sample}.</small></li>
          <li><span>04</span><strong>Sinal acionável</strong><small>outlier a partir de {data.thresholds.outlier}×; breakout a partir de {data.thresholds.breakout}×.</small></li>
        </ol>
        <p className="radarTimestamp">Última observação registrada: <strong>{formatDate(data.summary.last_ingest_at)}</strong></p>
      </section>

      <section className="section radarEligibleSection" aria-labelledby="radar-elegiveis">
        <div className="sectionHeaderInline"><div><p className="eyebrow">Fila segura</p><h3 className="sectionTitle" id="radar-elegiveis">Pode virar hipótese de conteúdo</h3></div><span className="badge">{eligibleItems.length} nesta visão</span></div>
        {eligibleItems.length === 0 ? (
          <div className="radarInlineEmpty" role="status"><strong>Nenhum item passou pelos gates nesta visão.</strong><span>Isso é um resultado válido. O radar não fabrica oportunidade para preencher espaço.</span></div>
        ) : (
          <div className="radarEligibleGrid">
            {eligibleItems.slice(0, 6).map((item) => (
              <article className={`radarEvidenceCard ${signalTone(item.signal_state)}`} key={`eligible-${item.id}`}>
                <div className="radarCardTop"><span className="stateChip">{signalLabels[item.signal_state || 'insufficient']}</span><strong>{formatNumber(item.performance_ratio)}× a mediana</strong></div>
                <h4>@{item.source_profile.replace(/^@/, '')}</h4>
                <p>{item.caption_excerpt || 'Legenda não observada pelo coletor.'}</p>
                <div className="radarEvidenceStrip"><span>{metricLabels[item.metric_basis || ''] || item.metric_basis || 'base ausente'}</span><strong>{formatNumber(item.metric_value)}</strong><span>mediana {formatNumber(item.median_value)}</span><span>n={item.sample_count ?? 0}</span></div>
                <Link className="primaryButton" href={buildStudioHref(item, data.version)} aria-label={`Levar hipótese de @${item.source_profile.replace(/^@/, '')} ao Estúdio`}>Levar como hipótese ao Estúdio</Link>
              </article>
            ))}
          </div>
        )}
      </section>

      <section className="section" aria-labelledby="radar-observados">
        <div className="sectionHeaderInline radarToolbarHeader">
          <div><p className="eyebrow">Evidências · top 50</p><h3 className="sectionTitle" id="radar-observados">Conteúdos observados</h3><p className="muted small radarSectionIntro">Esta visão recebe no máximo os 50 itens prioritários por atualização da API.</p></div>
          <span className="muted small radarCount" role="status" aria-live="polite" aria-atomic="true">{visibleItems.length} visíveis · {filteredItems.length} correspondem aos filtros</span>
        </div>
        <form className="radarToolbar" method="get" action="/radar-externo" aria-label="Filtrar conteúdos observados">
          <label><span>Buscar</span><input className="input" name="q" defaultValue={queryText} maxLength={120} placeholder="perfil, legenda ou padrão" /></label>
          <label><span>Governança</span><select className="input" name="fonte" defaultValue={sourceKind}><option value="">Todas as fontes visíveis</option><option value="approved">Aprovadas</option><option value="own_account">Conta própria</option><option value="candidate">Candidatas</option><option value="thematic_search">Busca temática</option></select></label>
          <label><span>Sinal</span><select className="input" name="sinal" defaultValue={signalState}><option value="">Todos os estados</option><option value="breakout">Breakout</option><option value="outlier">Outlier</option><option value="signal">Sinal inicial</option><option value="normal">Dentro do padrão</option><option value="insufficient">Amostra insuficiente</option></select></label>
          <button className="secondaryButton" type="submit">Aplicar filtros</button>
          {(q || sourceKind || signalState) ? <Link className="secondaryLink" href="/radar-externo">Limpar filtros</Link> : null}
        </form>

        {filteredItems.length === 0 ? (
          <div className="radarInlineEmpty" role="status" aria-live="polite"><strong>Nenhum item corresponde aos filtros.</strong><span>Ajuste a busca; nenhum registro oculto foi convertido em zero.</span><Link className="secondaryLink" href="/radar-externo">Limpar filtros e ver os itens</Link></div>
        ) : (
          <div className="radarEvidenceGrid">
            {visibleItems.map((item) => {
              const state = item.signal_state || 'insufficient'
              const reverse = item.reverse_engineering || {}
              const comparisons = item.comparison_posts || []
              const profileName = item.source_kind === 'thematic_search' ? `Busca: ${item.source_profile}` : `@${item.source_profile.replace(/^@/, '')}`
              return (
                <article className={`radarEvidenceCard ${signalTone(state)}`} key={item.id}>
                  <div className="radarCardTop"><div className="radarPillRow"><span className="stateChip">{sourceLabels[item.source_kind]}</span><span className="badge badgeDark">{item.canonical_format || 'formato não classificado'}</span></div><span className="radarSignalLabel">{signalLabels[state]}</span></div>
                  <div><p className="eyebrow">{item.source_network}</p><h4>{profileName}</h4>{item.source_kind === 'thematic_search' && !item.actual_source_profile ? <small className="radarUnknown">Perfil real não identificado pelo coletor</small> : null}</div>
                  <p className="radarCaption">{item.caption_excerpt || 'Legenda não observada pelo coletor.'}</p>
                  <dl className="radarEvidenceDefinition"><div><dt>Base métrica</dt><dd>{item.metric_basis ? metricLabels[item.metric_basis] || item.metric_basis : 'não disponível'}</dd></div><div><dt>Valor observado</dt><dd>{formatNumber(item.metric_value)}</dd></div><div><dt>Mediana comparável</dt><dd>{formatNumber(item.median_value)}</dd></div><div><dt>Desempenho relativo</dt><dd>{item.performance_ratio == null ? 'não calculado' : `${formatNumber(item.performance_ratio)}×`}</dd></div><div><dt>Amostra</dt><dd>{item.sample_count == null ? 'não calculada' : `${formatNumber(item.sample_count)} posts`}</dd></div><div><dt>Maturidade</dt><dd>{item.maturity === 'target' ? 'completa' : item.maturity === 'provisional' ? 'provisória' : 'insuficiente'}</dd></div></dl>
                  {item.reason ? <p className="radarReason"><strong>Por que não sobe:</strong> {item.reason}</p> : null}
                  <details className="radarDetails"><summary>Ver base de comparação</summary>{comparisons.length === 0 ? <p>Não há posts comparáveis registrados para este corte.</p> : <ul>{comparisons.map((post) => <li key={post.content_item_id}>{post.url ? <a href={post.url} target="_blank" rel="noreferrer" aria-label={`Abrir post comparável ${post.external_id} em nova aba`}>#{post.external_id}</a> : <span>#{post.external_id}</span>}<strong>{formatNumber(post.metric_value)}</strong></li>)}</ul>}</details>
                  <div className="radarHypothesis"><span>Hipótese editorial — não validação</span><p>{reverse.why_it_may_have_worked || 'Ainda sem hipótese de mecanismo registrada.'}</p>{reverse.adaptation_to_instituto_vital_slim ? <p><strong>Adaptação:</strong> {reverse.adaptation_to_instituto_vital_slim}</p> : null}</div>
                  <div className="radarCardActions">{item.eligible_for_ideation ? <Link className="primaryButton" href={buildStudioHref(item, data.version)} aria-label={`Usar ${profileName} como hipótese no Estúdio`}>Usar como hipótese</Link> : <span className="radarDisabledAction">{item.source_kind === 'candidate' ? 'Aguarda aprovação da fonte' : 'Aguarda evidência suficiente'}</span>}{item.url ? <a className="secondaryLink" href={item.url} target="_blank" rel="noreferrer" aria-label={`Abrir referência de ${profileName} em nova aba`}>Abrir referência</a> : null}</div>
                </article>
              )
            })}
          </div>
        )}
        {filteredItems.length > 12 ? <div className="radarPaginationGate">{showAll ? <Link className="secondaryLink" href={`/radar-externo${viewQuery.size ? `?${viewQuery}` : ''}`}>Mostrar só os 12 prioritários</Link> : <><span>Mostrando os 12 itens mais relevantes para reduzir ruído operacional.</span><Link className="secondaryLink" href={`/radar-externo?${showAllQuery}`}>Ver todos os {filteredItems.length} deste top 50</Link></>}</div> : null}
      </section>

      <SourceGovernance sources={data.sources} result={governanceResult} />
    </div>
  )
}
