'use client'

import { FormEvent, useEffect, useMemo, useState } from 'react'

const api = process.env.NEXT_PUBLIC_API_BASE_URL || '/api'

type ContentFormat = {
  key: string
  name: string
  description: string
  best_for: string[]
  objection_targets: string[]
  default_structure: string[]
  motion_notes: string
  prompt_bias: string
  compliance_notes: string
}

type MotionPreset = Record<string, { label: string; description: string }>
type ScreenFormats = Record<string, { label: string; aspect_ratio: string; recommended?: boolean }>

type MotionOptions = {
  content_formats: ContentFormat[]
  motion_presets: MotionPreset
  screen_formats: ScreenFormats
  duration_presets: { key: string; label: string; duration_seconds: number; blocks_count: number }[]
  content_strategies: string[]
  voiceovers: string[]
  workflow: string[]
}

type PlanBlock = {
  block_index: number
  narration_text: string
  scene: string
  motion: string
  audio: string
  visual_prompt: string
}

type MotionPlan = {
  title: string
  topic: string
  thesis: string
  objective: string
  objection: string
  content_format: string
  content_format_name: string
  content_strategy: string
  screen_format: string
  aspect_ratio: string
  duration_seconds: number
  blocks_count: number
  visual_preset_label: string
  hook_question: string
  through_line_object: string
  payoff: string
  blocks: PlanBlock[]
  caption: string
  cta: string
  compliance_notes: string[]
  quality_scores_estimados: Record<string, number>
  approval_status: string
  patient_send_ready: boolean
}

const objectiveLabels: Record<string, string> = {
  educacao_autoridade: 'Educação + autoridade',
  alcance: 'Alcance',
  conversao: 'Conversão',
  objecao: 'Quebra de objeção',
  remarketing: 'Remarketing',
}

const objectionLabels: Record<string, string> = {
  ja_tentei_de_tudo: 'Já tentei de tudo',
  o_problema_sou_eu: 'O problema sou eu',
  isso_e_normal_da_idade: 'Isso é normal da idade',
  medo_de_julgamento: 'Medo de julgamento',
  preco_sem_valor_percebido: 'Preço sem valor percebido',
}

function labelize(value: string) {
  return value.replaceAll('_', ' ')
}

export default function Page() {
  const [options, setOptions] = useState<MotionOptions | null>(null)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState('')
  const [plan, setPlan] = useState<MotionPlan | null>(null)
  const [projectId, setProjectId] = useState('')
  const [form, setForm] = useState({
    topic: 'Por que emagrecer não é o mesmo que manter?',
    objective: 'educacao_autoridade',
    objection: 'ja_tentei_de_tudo',
    content_format: 'mito_que_prende',
    content_strategy: 'loop_previsao',
    screen_format: 'reels',
    duration_seconds: 60,
    visual_preset: 'ivs_mixed_media_medico_premium',
    voiceover: 'documental_feminina_pt_br',
    source_examples_summary: 'Exemplos associados ao formato serão usados apenas para abstrair ritmo, gancho e mecanismo — sem copiar.',
  })

  useEffect(() => {
    fetch(`${api}/motion-videos/options`, { credentials: 'include', cache: 'no-store' })
      .then((r) => {
        if (!r.ok) throw new Error(`options ${r.status}`)
        return r.json()
      })
      .then(setOptions)
      .catch((err) => setError(`Não consegui carregar opções: ${err.message}`))
      .finally(() => setLoading(false))
  }, [])

  const selectedFormat = useMemo(
    () => options?.content_formats.find((item) => item.key === form.content_format),
    [options, form.content_format],
  )

  async function submit(event: FormEvent) {
    event.preventDefault()
    setGenerating(true)
    setError('')
    setPlan(null)
    setProjectId('')
    try {
      const response = await fetch(`${api}/motion-videos/plan`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tenant_slug: 'demo', ...form }),
      })
      const data = await response.json()
      if (!response.ok) throw new Error(data?.detail || `plan ${response.status}`)
      setPlan(data.payload)
      setProjectId(data.id)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao gerar plano')
    } finally {
      setGenerating(false)
    }
  }

  return (
    <div className="dashboardRoot motionStudio">
      <header className="pageHeader heroHeader motionHero">
        <div>
          <p className="eyebrow">Produção · Motion Videos</p>
          <h2 className="pageTitle">Higgsfield Studio para motion graphics IVS</h2>
          <p className="heroText">
            Transforme tema, roteiro ou tese em um plano de vídeo motion graphics com formato short-form,
            objeção, estratégia narrativa, prompts por bloco e gate de compliance — sem gastar crédito nesta fase.
          </p>
        </div>
        <div className="motionHeroPanel">
          <span className="badge">Plan-only</span>
          <strong>Geração paga bloqueada por gate</strong>
          <p className="muted small">Primeiro planejamos roteiro/prompts. Higgsfield só entra após aprovação explícita.</p>
        </div>
      </header>

      <section className="motionFlow cardLike">
        {(options?.workflow || ['Objetivo', 'Objeção', 'Formato de conteúdo', 'Vídeos de exemplo', 'Estratégia Narrativa', 'Prompts Higgsfield']).map((step, index) => (
          <div key={step} className="motionFlowStep">
            <span>{String(index + 1).padStart(2, '0')}</span>
            <strong>{step}</strong>
          </div>
        ))}
      </section>

      {loading ? <p className="muted">Carregando biblioteca de formatos...</p> : null}
      {error ? <div className="errorBox">{error}</div> : null}

      <section className="motionGrid">
        <form className="formCard motionForm" onSubmit={submit}>
          <div className="formHeader">
            <p className="eyebrow">Brief guiado</p>
            <h3>1 · Escolha estratégia antes do prompt</h3>
            <p className="muted">Padrão: tema/roteiro + objeção + content_format + exemplos + estratégia + motion preset.</p>
          </div>

          <label>
            Tema ou roteiro
            <textarea
              value={form.topic}
              onChange={(e) => setForm({ ...form, topic: e.target.value })}
              rows={3}
              required
            />
          </label>

          <div className="twoCols">
            <label>
              Objetivo
              <select value={form.objective} onChange={(e) => setForm({ ...form, objective: e.target.value })}>
                {Object.entries(objectiveLabels).map(([key, label]) => <option key={key} value={key}>{label}</option>)}
              </select>
            </label>
            <label>
              Objeção principal
              <select value={form.objection} onChange={(e) => setForm({ ...form, objection: e.target.value })}>
                {Object.entries(objectionLabels).map(([key, label]) => <option key={key} value={key}>{label}</option>)}
              </select>
            </label>
          </div>

          <label>
            Formato de conteúdo short-form
            <select value={form.content_format} onChange={(e) => setForm({ ...form, content_format: e.target.value })}>
              {(options?.content_formats || []).map((item) => <option key={item.key} value={item.key}>{item.name}</option>)}
            </select>
          </label>

          {selectedFormat ? (
            <div className="formatInsight">
              <strong>{selectedFormat.name}</strong>
              <p>{selectedFormat.description}</p>
              <small>{selectedFormat.motion_notes}</small>
            </div>
          ) : null}

          <label>
            Vídeos de exemplo / referência de mecanismo
            <textarea
              value={form.source_examples_summary}
              onChange={(e) => setForm({ ...form, source_examples_summary: e.target.value })}
              rows={3}
            />
          </label>

          <div className="twoCols">
            <label>
              Estratégia narrativa
              <select value={form.content_strategy} onChange={(e) => setForm({ ...form, content_strategy: e.target.value })}>
                {(options?.content_strategies || []).map((item) => <option key={item} value={item}>{labelize(item)}</option>)}
              </select>
            </label>
            <label>
              Formato de tela
              <select value={form.screen_format} onChange={(e) => setForm({ ...form, screen_format: e.target.value })}>
                {Object.entries(options?.screen_formats || {}).map(([key, item]) => <option key={key} value={key}>{item.label} · {item.aspect_ratio}</option>)}
              </select>
            </label>
          </div>

          <div className="twoCols">
            <label>
              Duração
              <select
                value={form.duration_seconds}
                onChange={(e) => setForm({ ...form, duration_seconds: Number(e.target.value) })}
              >
                {(options?.duration_presets || []).map((item) => <option key={item.key} value={item.duration_seconds}>{item.label} · {item.duration_seconds}s</option>)}
              </select>
            </label>
            <label>
              Estilo visual
              <select value={form.visual_preset} onChange={(e) => setForm({ ...form, visual_preset: e.target.value })}>
                {Object.entries(options?.motion_presets || {}).map(([key, item]) => <option key={key} value={key}>{item.label}</option>)}
              </select>
            </label>
          </div>

          <button className="primaryButton" type="submit" disabled={generating}>
            {generating ? 'Gerando plano...' : 'Gerar plano Motion Video sem gasto'}
          </button>
        </form>

        <aside className="motionPreview cardLike">
          <p className="eyebrow">Preview estratégico</p>
          {!plan ? (
            <>
              <h3>O plano aparecerá aqui</h3>
              <p className="muted">A saída inclui tese, objeto-metáfora, blocos de 10s, prompts Higgsfield, score e compliance.</p>
              <div className="motionEmptyRatio">9:16 / 16:9 / 4:5</div>
            </>
          ) : (
            <>
              <span className="badge">{plan.approval_status}</span>
              <h3>{plan.title}</h3>
              <p className="muted"><strong>Tese:</strong> {plan.thesis}</p>
              <div className="scoreGrid">
                {Object.entries(plan.quality_scores_estimados).map(([key, value]) => (
                  <div key={key} className="scoreCard">
                    <span>{labelize(key)}</span>
                    <strong>{value}</strong>
                  </div>
                ))}
              </div>
              <div className="motionMeta">
                <span>{plan.aspect_ratio}</span>
                <span>{plan.duration_seconds}s</span>
                <span>{plan.blocks_count} blocos</span>
                <span>{plan.content_format_name}</span>
              </div>
              <p><strong>Hook:</strong> {plan.hook_question}</p>
              <p><strong>Objeto-metáfora:</strong> {plan.through_line_object}</p>
              <p><strong>Payoff:</strong> {plan.payoff}</p>
              {projectId ? <p className="small muted">Projeto salvo: <code>{projectId}</code></p> : null}
            </>
          )}
        </aside>
      </section>

      {plan ? (
        <section className="section">
          <div className="sectionHeader">
            <p className="eyebrow">Roteiro + prompts</p>
            <h3 className="sectionTitle">Blocos Higgsfield</h3>
          </div>
          <div className="motionBlocks">
            {plan.blocks.map((block) => (
              <article key={block.block_index} className="motionBlock cardLike">
                <span className="badge badgeDark">Bloco {block.block_index}</span>
                <h4>{block.narration_text}</h4>
                <p><strong>Scene:</strong> {block.scene}</p>
                <p><strong>Motion:</strong> {block.motion}</p>
                <details>
                  <summary>Prompt Higgsfield completo</summary>
                  <pre>{block.visual_prompt}</pre>
                </details>
              </article>
            ))}
          </div>
        </section>
      ) : null}
    </div>
  )
}
