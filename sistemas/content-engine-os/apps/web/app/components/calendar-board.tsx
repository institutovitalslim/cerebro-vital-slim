'use client'

import { FormEvent, useState } from 'react'

const api = process.env.NEXT_PUBLIC_API_BASE_URL || '/api'

export type CalendarEntry = {
  id: string
  title: string
  format: string
  channel: string
  objective: string | null
  status: string
  scheduled_for: string | null
  notes: string | null
  creative_id?: string | null
  origin_tag?: string | null
  sprint_thesis?: string | null
  sprint_hook?: string | null
  published_at?: string | null
  metrics?: Record<string, unknown> | null
  metrics_recorded_at?: string | null
  metrics_pending?: boolean
  quality_score?: number | string | null
}

export const STATUS_COPY: Record<string, string> = {
  planned: 'Em planejamento',
  in_review: 'Aguardando validação',
  approved: 'Pronta para publicar',
  aprovado_para_publicar: 'Aprovada para publicar',
  published: 'Publicada · métrica pendente',
  publicado: 'Publicada · métrica pendente',
  metrics_pending: 'Publicada · métrica pendente',
  medido: 'Métrica registrada',
}

async function postJson<T>(path: string, body: unknown, method = 'POST'): Promise<T> {
  const response = await fetch(`${api}${path}`, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!response.ok) throw new Error(`${path}: ${response.status}`)
  return response.json()
}

export function CalendarBoard({ initialItems }: { initialItems: CalendarEntry[] }) {
  const [items, setItems] = useState(initialItems)
  const [busy, setBusy] = useState<string | null>(null)
  const [msg, setMsg] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function reload() {
    const r = await fetch(`${api}/calendar/entries?tenant_slug=demo`, { cache: 'no-store' })
    const d = await r.json()
    setItems(d.items || [])
  }

  async function marcarPublicado(id: string) {
    setBusy(id); setMsg(null); setError(null)
    try {
      await postJson(`/calendar/entries/${id}/status`, { status: 'published' }, 'PATCH')
      await reload()
      setMsg('Peça marcada como publicada. Agora falta registrar a métrica quando houver dados.')
    } catch {
      setError('Não consegui marcar como publicada agora.')
    } finally {
      setBusy(null)
    }
  }

  async function salvarMetricas(event: FormEvent<HTMLFormElement>, id: string) {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const num = (name: string) => {
      const v = String(form.get(name) || '').trim()
      return v ? Number(v) : null
    }
    setBusy(id); setMsg(null); setError(null)
    try {
      await postJson(`/calendar/entries/${id}/metrics`, {
        reach: num('reach'),
        likes: num('likes'),
        comments: num('comments'),
        shares: num('shares'),
        saves: num('saves'),
        profile_clicks: num('profile_clicks'),
        whatsapp_leads: num('whatsapp_leads'),
        appointments: num('appointments'),
        notes: String(form.get('notes') || '').trim() || null,
      })
      await reload()
      setMsg('Métrica registrada. A peça saiu da fila pendente de aprendizado.')
    } catch {
      setError('Não consegui registrar as métricas agora.')
    } finally {
      setBusy(null)
    }
  }

  const published = items.filter((item) => ['published', 'publicado', 'metrics_pending'].includes(item.status)).length
  const metricsPending = items.filter((item) => item.metrics_pending || ['published', 'publicado', 'metrics_pending'].includes(item.status)).length
  const approved = items.filter((item) => ['approved', 'aprovado_para_publicar'].includes(item.status)).length

  return (
    <>
      <section className="metricGrid">
        <article className="metricCard">
          <span className="metricLabel">Fila editorial</span>
          <strong className="metricValue">{items.length}</strong>
          <p className="muted small" style={{ margin: 0 }}>entradas criadas no cockpit</p>
        </article>
        <article className="metricCard">
          <span className="metricLabel">Aprovadas para publicar</span>
          <strong className="metricValue">{approved}</strong>
          <p className="muted small" style={{ margin: 0 }}>vieram do Banco de Criativos</p>
        </article>
        <article className="metricCard">
          <span className="metricLabel">Publicadas</span>
          <strong className="metricValue">{published}</strong>
          <p className="muted small" style={{ margin: 0 }}>já transformadas em rotina real</p>
        </article>
        <article className="metricCard">
          <span className="metricLabel">Métrica pendente</span>
          <strong className="metricValue">{metricsPending}</strong>
          <p className="muted small" style={{ margin: 0 }}>precisam fechar aprendizado</p>
        </article>
      </section>

      {msg ? <div className="successText">{msg}</div> : null}
      {error ? <div className="errorText">{error}</div> : null}

      <section className="section">
        <div className="sectionHeaderInline">
          <div>
            <p className="eyebrow">Operação viva</p>
            <h3 className="sectionTitle">Fila editorial</h3>
          </div>
          <span className="muted small">aprovar → publicar → medir</span>
        </div>

        {items.length === 0 ? (
          <div className="empty">Nenhuma entrada editorial criada ainda.</div>
        ) : (
          <div className="tableLike">
            {items.map((item) => {
              const canPublish = ['approved', 'aprovado_para_publicar', 'planned', 'in_review'].includes(item.status)
              const shouldMeasure = item.metrics_pending || ['published', 'publicado', 'metrics_pending'].includes(item.status)
              return (
                <div key={item.id} className="row">
                  <div className="rowTop">
                    <div>
                      <strong>{item.title}</strong>
                      <p className="muted small" style={{ margin: '6px 0 0' }}>{item.format} · {item.channel} · {item.objective || 'sem objetivo definido'}</p>
                    </div>
                    <span className="badge">{STATUS_COPY[item.status] || item.status}</span>
                  </div>
                  <span className="muted">Agendamento: {item.scheduled_for ? new Date(item.scheduled_for).toLocaleString('pt-BR') : 'não definido'}</span>
                  {item.origin_tag || item.sprint_thesis || item.sprint_hook ? (
                    <div className="resultBox">
                      {item.origin_tag ? <p className="small" style={{ margin: 0 }}><strong>Origem:</strong> {item.origin_tag}</p> : null}
                      {item.sprint_thesis ? <p className="small" style={{ margin: '4px 0 0' }}><strong>Tese:</strong> {item.sprint_thesis}</p> : null}
                      {item.sprint_hook ? <p className="small" style={{ margin: '4px 0 0' }}><strong>Hook:</strong> {item.sprint_hook}</p> : null}
                    </div>
                  ) : item.notes ? <div className="resultBox">{item.notes}</div> : null}

                  <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                    {item.creative_id ? <a className="secondaryLink" href="/banco-criativos">Abrir criativo</a> : null}
                    {canPublish ? <button className="primaryButton" style={{ minHeight: 36, padding: '0 14px' }} disabled={busy === item.id} onClick={() => marcarPublicado(item.id)}>{busy === item.id ? 'Salvando…' : 'Marcar publicado'}</button> : null}
                  </div>

                  {shouldMeasure ? (
                    <form onSubmit={(event) => salvarMetricas(event, item.id)} className="resultBox" style={{ display: 'grid', gap: 8 }}>
                      <span className="metricLabel">Registrar métrica agregada</span>
                      <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit,minmax(120px,1fr))', gap: 8 }}>
                        <input className="input" name="reach" type="number" min="0" placeholder="Alcance" />
                        <input className="input" name="likes" type="number" min="0" placeholder="Curtidas" />
                        <input className="input" name="comments" type="number" min="0" placeholder="Comentários" />
                        <input className="input" name="shares" type="number" min="0" placeholder="Envios" />
                        <input className="input" name="saves" type="number" min="0" placeholder="Salvos" />
                        <input className="input" name="profile_clicks" type="number" min="0" placeholder="Cliques perfil" />
                        <input className="input" name="whatsapp_leads" type="number" min="0" placeholder="Leads WhatsApp" />
                        <input className="input" name="appointments" type="number" min="0" placeholder="Agendamentos" />
                      </div>
                      <textarea className="textarea" name="notes" placeholder="Aprendizado rápido: o que funcionou / o que ajustar" rows={2} />
                      <button className="secondaryLink" disabled={busy === item.id}>{busy === item.id ? 'Registrando…' : 'Salvar métrica e fechar aprendizado'}</button>
                    </form>
                  ) : null}

                  {item.metrics_recorded_at ? <span className="successText">Métrica registrada em {new Date(item.metrics_recorded_at).toLocaleString('pt-BR')}</span> : null}
                </div>
              )
            })}
          </div>
        )}
      </section>
    </>
  )
}
