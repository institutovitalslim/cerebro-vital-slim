'use client'

import { FormEvent, useEffect, useState } from 'react'

const publicApi = process.env.NEXT_PUBLIC_API_BASE_URL || '/api'

async function postJson(path: string, body: unknown) {
  const response = await fetch(`${publicApi}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!response.ok) throw new Error(`Erro ao enviar ${path}`)
  return response.json()
}

async function postForm(path: string, formData: FormData) {
  const response = await fetch(`${publicApi}${path}`, {
    method: 'POST',
    body: formData,
  })
  if (!response.ok) throw new Error(`Erro ao enviar ${path}`)
  return response.json()
}

export function QuickSourceForm() {
  const [loading, setLoading] = useState(false)
  const [done, setDone] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [purposes, setPurposes] = useState<{ chave: string; label: string; descricao?: string }[]>([])
  const [fin, setFin] = useState('')
  const [showAdd, setShowAdd] = useState(false)
  const [novoLabel, setNovoLabel] = useState('')
  const [novoDesc, setNovoDesc] = useState('')

  async function carregar() {
    try {
      const r = await fetch(`${publicApi}/sources/purposes?tenant_slug=demo`, { cache: 'no-store' })
      const d = await r.json()
      const its = d.items || []
      setPurposes(its)
      setFin((cur) => cur || (its[0] ? its[0].chave : ''))
    } catch { /* */ }
  }
  useEffect(() => { carregar() }, [])

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const form = event.currentTarget
    const fd = new FormData(form)
    setLoading(true); setError(null); setDone(null)
    try {
      const result = await postJson('/sources', {
        tenant_slug: 'demo', network: fd.get('network'), label: fd.get('label'),
        handle_or_url: fd.get('handle_or_url'), active: true, finalidade: fin, objetivo: fd.get('objetivo'),
      })
      setDone(`Fonte criada: ${result.label}`)
      form.reset()
    } catch { setError('Não consegui salvar a fonte agora.') } finally { setLoading(false) }
  }

  async function addPurpose() {
    if (!novoLabel.trim()) return
    try {
      const r = await postJson('/sources/purposes', { tenant_slug: 'demo', label: novoLabel, descricao: novoDesc })
      setNovoLabel(''); setNovoDesc(''); setShowAdd(false)
      await carregar(); setFin(r.chave)
    } catch { setError('Não consegui criar o propósito.') }
  }

  const hint = (purposes.find((pp) => pp.chave === fin) || {}).descricao
  return (
    <form className="formCard" onSubmit={onSubmit}>
      <div className="formHeader"><h3>Adicionar fonte</h3><p className="muted">Cadastre um perfil ou site e diga PRA QUE ele serve no nosso ecossistema.</p></div>
      <input name="label" placeholder="Nome da fonte" className="input" required />
      <input name="network" placeholder="instagram, youtube, pubmed..." className="input" required />
      <input name="handle_or_url" placeholder="@perfil ou URL" className="input" required />
      <label className="muted small">Finalidade — como o sistema vai usar</label>
      <select className="input" value={fin} onChange={(e) => setFin(e.target.value)}>
        {purposes.map((pp) => <option key={pp.chave} value={pp.chave}>{pp.label}</option>)}
      </select>
      {hint ? <p className="muted small" style={{ margin: '-2px 0 2px', opacity: 0.85 }}>→ {hint}</p> : null}
      <button type="button" className="secondaryLink" style={{ width: 'fit-content', fontSize: 13 }} onClick={() => setShowAdd((v) => !v)}>{showAdd ? '− fechar' : '+ Novo propósito de fonte'}</button>
      {showAdd ? (
        <div style={{ display: 'grid', gap: 6, border: '1px solid rgba(186,155,96,.3)', borderRadius: 10, padding: 10 }}>
          <input className="input" placeholder="Nome do propósito (ex.: Receitas & nutrição)" value={novoLabel} onChange={(e) => setNovoLabel(e.target.value)} />
          <input className="input" placeholder="Como o sistema deve usar (descrição curta)" value={novoDesc} onChange={(e) => setNovoDesc(e.target.value)} />
          <button type="button" className="primaryButton" style={{ padding: '6px 12px', fontSize: 13 }} onClick={addPurpose} disabled={!novoLabel.trim()}>Criar propósito</button>
        </div>
      ) : null}
      <input name="objetivo" placeholder="Objetivo desta fonte (ex.: ângulos de emagrecimento que viralizam)" className="input" />
      <button className="primaryButton" disabled={loading}>{loading ? 'Salvando...' : 'Salvar fonte'}</button>
      {done ? <span className="successText">{done}</span> : null}
      {error ? <span className="errorText">{error}</span> : null}
    </form>
  )
}

export function QuickThemeForm() {
  const [loading, setLoading] = useState(false)
  const [done, setDone] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const formData = new FormData(event.currentTarget)
    setLoading(true); setError(null); setDone(null)
    try {
      const result = await postJson('/themes', {
        tenant_slug: 'demo', theme: formData.get('theme'), objective: formData.get('objective'),
        format_targets: String(formData.get('format_targets') || '').split(',').map((v) => v.trim()).filter(Boolean), notes: formData.get('notes'),
      })
      setDone(`Tema criado: ${result.theme}`)
      event.currentTarget.reset()
    } catch { setError('Não consegui salvar o tema agora.') } finally { setLoading(false) }
  }
  return <form className="formCard" onSubmit={onSubmit}><div className="formHeader"><h3>Novo tema</h3><p className="muted">Transforme uma dor real do cliente em produção organizada.</p></div><input name="theme" placeholder="Tema central" className="input" required /><input name="objective" placeholder="Objetivo do conteúdo" className="input" required /><input name="format_targets" placeholder="reel, carrossel, stories" className="input" /><textarea name="notes" placeholder="Contexto, objeções, observações" className="textarea" rows={4} /><button className="primaryButton" disabled={loading}>{loading ? 'Salvando...' : 'Salvar tema'}</button>{done ? <span className="successText">{done}</span> : null}{error ? <span className="errorText">{error}</span> : null}</form>
}

export function QuickCreativeForm() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const formData = new FormData(event.currentTarget)
    setLoading(true); setError(null); setResult(null)
    try {
      const response = await postJson('/generation/creative', {
        tenant_slug: 'demo', title: formData.get('title'), audience: formData.get('audience'), objective: formData.get('objective'), format: formData.get('format'),
      })
      setResult(JSON.stringify(response.payload, null, 2))
    } catch { setError('Não consegui gerar o criativo agora.') } finally { setLoading(false) }
  }
  return <form className="formCard" onSubmit={onSubmit}><div className="formHeader"><h3>Gerar peça rápida</h3><p className="muted">Use quando quiser validar um ângulo antes de escalar.</p></div><input name="title" placeholder="Título ou promessa central" className="input" required /><input name="audience" placeholder="Público principal" className="input" required /><input name="objective" placeholder="Objetivo do criativo" className="input" required /><select name="format" className="input" defaultValue="reel"><option value="reel">Reel</option><option value="carrossel">Carrossel</option><option value="stories">Stories</option><option value="post_estatico">Post estático</option></select><button className="primaryButton" disabled={loading}>{loading ? 'Gerando...' : 'Gerar criativo'}</button>{result ? <pre className="resultBox">{result}</pre> : null}{error ? <span className="errorText">{error}</span> : null}</form>
}

export function StrategyIntakeForm() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); const formData = new FormData(event.currentTarget); setLoading(true); setError(null); setResult(null)
    try {
      const response = await postJson('/intake/strategy', {
        tenant_slug: 'demo', clinic_name: formData.get('clinic_name'), specialty: formData.get('specialty'), city: formData.get('city'), audience: formData.get('audience'), main_offer: formData.get('main_offer'), primary_pain: formData.get('primary_pain'), desired_outcome: formData.get('desired_outcome'), authority_assets: String(formData.get('authority_assets') || '').split(',').map((v) => v.trim()).filter(Boolean), constraints: String(formData.get('constraints') || '').split(',').map((v) => v.trim()).filter(Boolean),
      })
      setResult(JSON.stringify(response.payload, null, 2))
    } catch { setError('Não consegui montar o intake estratégico agora.') } finally { setLoading(false) }
  }
  return <form className="formCard" onSubmit={onSubmit}><div className="formHeader"><h3>Intake estratégico</h3><p className="muted">Capte o núcleo da clínica para o sistema já sugerir pilares, objeções e primeiros passos.</p></div><input name="clinic_name" placeholder="Nome da clínica" className="input" required /><input name="specialty" placeholder="Especialidade" className="input" required /><input name="city" placeholder="Cidade / região" className="input" required /><input name="audience" placeholder="Público principal" className="input" required /><input name="main_offer" placeholder="Oferta principal" className="input" required /><textarea name="primary_pain" placeholder="Dor principal do paciente" className="textarea" rows={3} required /><textarea name="desired_outcome" placeholder="Resultado desejado" className="textarea" rows={2} required /><input name="authority_assets" placeholder="Autoridade disponível: entrevistas, aulas, consultas gravadas..." className="input" /><input name="constraints" placeholder="Restrições: compliance, linguagem, proibições..." className="input" /><button className="primaryButton" disabled={loading}>{loading ? 'Processando...' : 'Gerar base estratégica'}</button>{result ? <pre className="resultBox">{result}</pre> : null}{error ? <span className="errorText">{error}</span> : null}</form>
}

export function AdvancedCreativeStudioForm() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<string | null>(null)
  const [review, setReview] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); const formData = new FormData(event.currentTarget); setLoading(true); setError(null); setResult(null); setReview(null)
    try {
      const payload = { tenant_slug: 'demo', core_theme: formData.get('core_theme'), audience: formData.get('audience'), objective: formData.get('objective'), angle: formData.get('angle'), format: formData.get('format'), hook_style: formData.get('hook_style'), cta: formData.get('cta') }
      const response = await postJson('/generation/advanced', payload)
      const structured = response.payload.structured || {}
      setResult(JSON.stringify(structured, null, 2))
      const reviewResponse = await postJson('/quality/review', { content_type: payload.format, niche: 'medical', objective: payload.objective, content_body: `${structured.hook || ''} ${structured.development || ''}`, cta: structured.cta || payload.cta })
      setReview(JSON.stringify(reviewResponse, null, 2))
    } catch { setError('Não consegui gerar e revisar a peça avançada agora.') } finally { setLoading(false) }
  }
  return <form className="formCard" onSubmit={onSubmit}><div className="formHeader"><h3>Studio avançado</h3><p className="muted">Gera peça com ângulo, reaproveitamento e uma primeira revisão de risco/compliance.</p></div><input name="core_theme" placeholder="Tema central" className="input" required /><input name="audience" placeholder="Público principal" className="input" required /><input name="objective" placeholder="Objetivo do criativo" className="input" required /><select name="angle" className="input" defaultValue="reframe_de_culpa"><option value="reframe_de_culpa">reframe_de_culpa</option><option value="quebra_de_mito">quebra_de_mito</option><option value="mecanismo_clinico">mecanismo_clinico</option><option value="prova_clinica">prova_clinica</option></select><select name="format" className="input" defaultValue="reel"><option value="reel">Reel</option><option value="carrossel">Carrossel</option><option value="stories">Stories</option><option value="post_estatico">Post estático</option></select><select name="hook_style" className="input" defaultValue="mecanismo"><option value="mecanismo">mecanismo</option><option value="dor">dor</option><option value="objeção">objeção</option><option value="autoridade">autoridade</option></select><input name="cta" placeholder="CTA filtrando público qualificado" className="input" /><button className="primaryButton" disabled={loading}>{loading ? 'Criando...' : 'Gerar peça premium'}</button>{result ? <pre className="resultBox">{result}</pre> : null}{review ? <pre className="resultBox">{review}</pre> : null}{error ? <span className="errorText">{error}</span> : null}</form>
}

export function AssetUploadForm() {
  const [loading, setLoading] = useState(false)
  const [done, setDone] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); const target = event.currentTarget; const formData = new FormData(target); setLoading(true); setError(null); setDone(null)
    try {
      formData.append('tenant_slug', 'demo')
      const response = await postForm('/assets/upload', formData)
      setDone(`Asset salvo: ${response.title}`)
      target.reset()
    } catch { setError('Não consegui enviar o asset agora.') } finally { setLoading(false) }
  }
  return <form className="formCard" onSubmit={onSubmit}><div className="formHeader"><h3>Biblioteca de assets</h3><p className="muted">Suba vídeos, imagens, PDFs e referências para alimentar a máquina.</p></div><input name="title" placeholder="Título do asset" className="input" required /><select name="asset_kind" className="input" defaultValue="reference"><option value="reference">reference</option><option value="video_raw">video_raw</option><option value="image_raw">image_raw</option><option value="proof">proof</option><option value="brand">brand</option></select><input name="tags" placeholder="tags separadas por vírgula" className="input" /><input name="file" type="file" className="input" required /><button className="primaryButton" disabled={loading}>{loading ? 'Enviando...' : 'Salvar asset'}</button>{done ? <span className="successText">{done}</span> : null}{error ? <span className="errorText">{error}</span> : null}</form>
}

export function CalendarEntryForm() {
  const [loading, setLoading] = useState(false)
  const [done, setDone] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); const formData = new FormData(event.currentTarget); setLoading(true); setError(null); setDone(null)
    try {
      const response = await postJson('/calendar/entries', {
        tenant_slug: 'demo', title: formData.get('title'), format: formData.get('format'), channel: formData.get('channel'), objective: formData.get('objective'), status: formData.get('status'), scheduled_for: formData.get('scheduled_for') || null, notes: formData.get('notes'),
      })
      setDone(`Entrada criada: ${response.title}`)
      event.currentTarget.reset()
    } catch { setError('Não consegui criar a entrada do calendário agora.') } finally { setLoading(false) }
  }
  return <form className="formCard" onSubmit={onSubmit}><div className="formHeader"><h3>Calendário editorial</h3><p className="muted">Planeje produção, aprovação e publicação no próprio cockpit.</p></div><input name="title" placeholder="Título da peça" className="input" required /><select name="format" className="input" defaultValue="reel"><option value="reel">Reel</option><option value="carrossel">Carrossel</option><option value="stories">Stories</option><option value="post_estatico">Post estático</option></select><select name="channel" className="input" defaultValue="instagram"><option value="instagram">Instagram</option><option value="facebook">Facebook</option><option value="youtube">YouTube</option><option value="tiktok">TikTok</option></select><input name="objective" placeholder="Objetivo" className="input" /><select name="status" className="input" defaultValue="planned"><option value="planned">planned</option><option value="in_review">in_review</option><option value="approved">approved</option><option value="published">published</option></select><input name="scheduled_for" type="datetime-local" className="input" /><textarea name="notes" placeholder="Observações operacionais" className="textarea" rows={3} /><button className="primaryButton" disabled={loading}>{loading ? 'Salvando...' : 'Criar entrada'}</button>{done ? <span className="successText">{done}</span> : null}{error ? <span className="errorText">{error}</span> : null}</form>
}
