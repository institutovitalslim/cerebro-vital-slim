'use client'

import { FormEvent, useEffect, useMemo, useState } from 'react'

type Story = {
  n: number
  funcao: string
  texto: string
  visual: string
  sticker: string
  objecao: string
  dm: string
  risco: 'baixo' | 'médio'
}

type Sequence = {
  tipo: string
  tese: string
  ctaPrincipal: string
  palavraChave: string
  stories: Story[]
}

type SavedSequence = {
  id: string
  title: string
  sequence_type: string
  objective: string
  main_objection: string
  story_count: number
  created_at: string
  performance_entries: number
  total_useful_dms: number
  total_leads: number
}

type WinnerSequence = SavedSequence & {
  total_views: number
  total_replies: number
  total_prints: number
  total_sticker_taps: number
  total_shares: number
  total_saves: number
  avg_retention_initial_pct: number | null
  learned_intent_signal: string | null
  winner_score: number
  useful_dm_rate: number | null
  lead_rate: number | null
  dominant_objection_learned: string | null
}

type VariationResponse = {
  source_title: string
  usage_note: string
  variations: { variant: string; focus: string; hook: string; cta: string; sticker: string; why: string }[]
}

const SEQUENCIAS = [
  ['espelho', 'Espelho · identificação emocional'],
  ['sem_culpa', 'Sem culpa · reframe de culpa'],
  ['bastidor', 'Bastidor clínico · confiança'],
  ['mito', 'Mito que trava · educação'],
  ['caixinha', 'Caixinha protegida · DM segura'],
  ['conversar', 'Pronta para conversar · intenção alta'],
]

const OBJETIVOS = [
  ['conexao', 'Conexão'],
  ['dm', 'Gerar DM'],
  ['pesquisa', 'Pesquisa/BI'],
  ['prova', 'Prova segura'],
  ['objecao', 'Quebrar objeção'],
  ['agenda', 'Ponte para agenda'],
]

const OBJECOES = [
  ['culpa', 'Culpa / falta de força de vontade'],
  ['vergonha', 'Vergonha de falar sobre corpo/peso'],
  ['julgamento', 'Medo de julgamento'],
  ['ja_tentei', 'Já tentei de tudo'],
  ['tempo', 'Falta de tempo/rotina difícil'],
  ['preco', 'Preço/valor'],
  ['distancia', 'Distância'],
  ['remedio', 'Medo de remédio ou dependência'],
  ['efeito_sanfona', 'Efeito sanfona'],
]

const MOMENTOS = [
  ['dor_fria', 'Dor fria · ainda observa em silêncio'],
  ['comparacao', 'Comparação · se mede por outras mulheres'],
  ['frustracao', 'Frustração · cansou de tentar'],
  ['decisao', 'Decisão · quer entender o caminho'],
  ['quase_pronta', 'Quase pronta · precisa de segurança'],
]

const ATIVOS = [
  ['texto', 'Texto premium simples'],
  ['dra', 'Vídeo curto da Dra. Daniely'],
  ['bastidor', 'Bastidor da clínica'],
  ['print', 'Print anonimizado/validado'],
  ['enquete', 'Enquete'],
  ['caixinha', 'Caixinha'],
  ['depoimento', 'Depoimento validado'],
]

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

async function getJson(path: string) {
  const response = await fetch(`${publicApi}${path}`, { cache: 'no-store' })
  if (!response.ok) throw new Error(`Erro ao buscar ${path}`)
  return response.json()
}

const labelOf = (items: string[][], value: string) => items.find(([v]) => v === value)?.[1] || value

function objectionLine(objecao: string) {
  const map: Record<string, string> = {
    culpa: 'Não é falta de força de vontade. Muitas vezes é um conjunto de rotina, corpo, emoção e estratégia errada.',
    vergonha: 'Você não precisa se expor para começar. Uma conversa segura já pode organizar o próximo passo.',
    julgamento: 'Cuidado clínico não começa com julgamento; começa com escuta, história e contexto.',
    ja_tentei: 'Quando várias tentativas falham, repetir mais forte a mesma lógica raramente resolve.',
    tempo: 'A melhor estratégia não é a perfeita: é a que cabe na rotina real sem destruir sua semana.',
    preco: 'Antes de pensar em valor, a paciente precisa entender se o caminho faz sentido para o caso dela.',
    distancia: 'O primeiro passo é entender se existe um caminho possível; depois a equipe orienta formato e viabilidade.',
    remedio: 'A avaliação existe para entender contexto e possibilidades, não para empurrar uma solução única.',
    efeito_sanfona: 'O foco não é só perder peso; é entender por que o corpo volta para o mesmo lugar.',
  }
  return map[objecao] || map.culpa
}

function ctaFor(objetivo: string, objecao: string) {
  if (objetivo === 'agenda') return ['orientação', 'Me manda “orientação” que nossa equipe te explica o próximo passo.']
  if (objetivo === 'dm') return ['me vi aqui', 'Se você se viu nessa sequência, me manda “me vi aqui”.']
  if (objetivo === 'pesquisa') return ['minha dificuldade', 'Me responde com uma palavra: rotina, ansiedade, fome ou vergonha.']
  if (objetivo === 'prova') return ['quero entender', 'Se quiser entender como avaliamos isso com segurança, me manda “quero entender”.']
  if (objetivo === 'objecao') return ['já tentei', objecao === 'ja_tentei' ? 'Me manda “já tentei” se essa parte pegou em você.' : 'Me manda “faz sentido” se essa objeção já apareceu para você.']
  return ['eu', 'Se esse story falou com você, responde só “eu”.']
}

function visualFor(ativo: string, index: number) {
  const map: Record<string, string[]> = {
    texto: ['Fundo IVS escuro + texto curto', 'Card printável', 'Fundo claro premium + frase única'],
    dra: ['Dra. Daniely olhando para câmera', 'Corte curto da Dra. com legenda grande', 'Frame natural da Dra. no consultório'],
    bastidor: ['Bastidor da clínica sem paciente identificável', 'Mesa/ambiente clínico premium', 'Detalhe de rotina da equipe'],
    print: ['Print anonimizado com tarja elegante', 'Resposta de DM sem nome/foto', 'Comentário validado e ocultado'],
    enquete: ['Story limpo com enquete central', 'Texto curto + sticker grande', 'Pergunta em destaque'],
    caixinha: ['Caixinha com texto acolhedor', 'Fundo minimalista + pergunta', 'Imagem calma + caixa de pergunta'],
    depoimento: ['Trecho validado sem promessa', 'Prova social segura', 'Depoimento contextualizado'],
  }
  const pool = map[ativo] || map.texto
  return pool[index % pool.length]
}

function buildSequence(input: {
  tema: string
  tipo: string
  objetivo: string
  objecao: string
  momento: string
  ativo: string
  quantidade: number
}): Sequence {
  const tema = input.tema.trim() || 'por que não é falta de força de vontade'
  const [palavraChave, ctaPrincipal] = ctaFor(input.objetivo, input.objecao)
  const objLine = objectionLine(input.objecao)
  const momento = labelOf(MOMENTOS, input.momento).split(' · ')[0].toLowerCase()
  const tipo = labelOf(SEQUENCIAS, input.tipo)
  const temaLower = tema.charAt(0).toLowerCase() + tema.slice(1)

  const base: Omit<Story, 'n'>[] = [
    {
      funcao: 'Hook',
      texto: `Talvez o problema não seja “${temaLower}”. Talvez seja tentar lidar com isso sozinha e se cobrar como se fosse simples.`,
      visual: visualFor(input.ativo, 0),
      sticker: 'Sticker de reação ou enquete “já senti isso / nunca falei disso”',
      objecao: 'Abre identificação sem culpar a paciente.',
      dm: '“nossa”, “sou eu”, “já senti isso”',
      risco: 'baixo',
    },
    {
      funcao: 'Espelho emocional',
      texto: `Tem mulher que olha no espelho e não vê só peso. Vê cansaço, comparação, frustração e a sensação de não se reconhecer mais.`,
      visual: 'Texto premium, sem imagem corporal sensível',
      sticker: 'Enquete: “isso pesa?” sim / muito',
      objecao: 'Normaliza a dor sem explorar insegurança.',
      dm: 'Relatos curtos de identificação',
      risco: 'baixo',
    },
    {
      funcao: 'Quebra de objeção',
      texto: objLine,
      visual: visualFor(input.ativo, 1),
      sticker: 'Prepare o print',
      objecao: labelOf(OBJECOES, input.objecao),
      dm: '“faz sentido”',
      risco: 'baixo',
    },
    {
      funcao: 'Contexto clínico',
      texto: `No IVS, antes de orientar, a gente olha história, exames, rotina, sono, ansiedade, tentativas anteriores e objetivo real.`,
      visual: input.ativo === 'dra' ? visualFor('dra', 2) : visualFor('bastidor', 0),
      sticker: 'Caixinha: “o que você já tentou?”',
      objecao: 'Mostra método, não promessa.',
      dm: 'Histórico de dietas/tentativas',
      risco: 'baixo',
    },
    {
      funcao: 'Pergunta de BI',
      texto: `Se você está em fase de ${momento}, qual parte mais te trava hoje?`,
      visual: visualFor('enquete', 0),
      sticker: 'Enquete: rotina / fome / ansiedade / vergonha',
      objecao: 'Transforma dor em dado operacional.',
      dm: 'Votos e respostas sobre trava principal',
      risco: 'baixo',
    },
    {
      funcao: 'Reframe',
      texto: `O ponto não é “tentar mais uma vez”. É entender por que as outras vezes ficaram pesadas demais para sustentar.`,
      visual: 'Card printável com uma frase central',
      sticker: 'Slider: quanto isso fez sentido?',
      objecao: 'Quebra “já tentei de tudo”.',
      dm: '“foi exatamente assim”',
      risco: 'baixo',
    },
    {
      funcao: 'Prova segura',
      texto: `A avaliação não existe para te encaixar numa fórmula. Existe para entender o seu ponto de partida e o que é possível construir com segurança.`,
      visual: input.ativo === 'print' ? visualFor('print', 1) : visualFor(input.ativo, 2),
      sticker: 'Reação com coração ou “quero entender”',
      objecao: 'Evita promessa de resultado e reforça cuidado.',
      dm: '“quero entender”',
      risco: 'baixo',
    },
    {
      funcao: 'Caixinha protegida',
      texto: `Se você nunca teve coragem de falar disso, pode começar sem se expor. Me manda sua maior dúvida em uma frase.`,
      visual: visualFor('caixinha', 0),
      sticker: 'Caixinha: “minha dúvida é…”',
      objecao: 'Quebra vergonha e medo de julgamento.',
      dm: 'Dúvidas privadas',
      risco: 'baixo',
    },
    {
      funcao: 'Resumo printável',
      texto: `Printa isso: culpa não organiza tratamento. Clareza, avaliação e acompanhamento organizam o próximo passo.`,
      visual: 'Card IVS claro/escuro, sem poluição',
      sticker: '“Volta e printa”',
      objecao: 'Consolida a tese da sequência.',
      dm: 'Prints, reações, respostas',
      risco: 'baixo',
    },
    {
      funcao: 'CTA principal',
      texto: ctaPrincipal,
      visual: 'CTA minimalista com botão/sticker de resposta',
      sticker: `DM com palavra-chave: ${palavraChave}`,
      objecao: 'Convida sem pressão e sem promessa.',
      dm: palavraChave,
      risco: input.objetivo === 'agenda' ? 'médio' : 'baixo',
    },
    {
      funcao: 'Follow-up',
      texto: `Vou responder primeiro quem mandou “${palavraChave}” porque assim a equipe entende melhor o que você precisa antes de qualquer orientação.`,
      visual: 'Bastidor leve da equipe/WhatsApp sem dados',
      sticker: 'Última chamada suave',
      objecao: 'Explica o motivo da DM e aumenta qualidade.',
      dm: palavraChave,
      risco: 'baixo',
    },
    {
      funcao: 'Fechamento comunitário',
      texto: `Se essa sequência ajudou uma mulher que vive se culpando em silêncio, encaminha para ela. Pode ser o primeiro respiro do dia.`,
      visual: 'Texto emocional, sem apelo agressivo',
      sticker: 'Compartilhar',
      objecao: 'Amplia alcance sem venda direta.',
      dm: 'Compartilhamentos e reações',
      risco: 'baixo',
    },
  ]

  const stories = base.slice(0, input.quantidade).map((story, index) => ({ ...story, n: index + 1 }))
  return {
    tipo,
    tese: `${tipo}: ${tema}. Sequência construída para partir da dor emocional, quebrar a objeção “${labelOf(OBJECOES, input.objecao)}” e conduzir para uma resposta privada segura.`,
    ctaPrincipal,
    palavraChave,
    stories,
  }
}

function formatSequence(seq: Sequence) {
  return [
    `Tipo: ${seq.tipo}`,
    `Tese: ${seq.tese}`,
    `CTA principal: ${seq.ctaPrincipal}`,
    '',
    ...seq.stories.flatMap((s) => [
      `Story ${s.n} — ${s.funcao}`,
      `Texto: ${s.texto}`,
      `Visual: ${s.visual}`,
      `Sticker/CTA: ${s.sticker}`,
      `Objeção quebrada: ${s.objecao}`,
      `DM esperada: ${s.dm}`,
      '',
    ]),
  ].join('\n')
}

export default function StoriesEnginePage() {
  const [tema, setTema] = useState('Não é falta de força de vontade')
  const [tipo, setTipo] = useState('sem_culpa')
  const [objetivo, setObjetivo] = useState('dm')
  const [objecao, setObjecao] = useState('culpa')
  const [momento, setMomento] = useState('frustracao')
  const [ativo, setAtivo] = useState('texto')
  const [quantidade, setQuantidade] = useState(10)
  const [seoIntent, setSeoIntent] = useState('por que não consigo emagrecer')
  const [sendSaveReason, setSendSaveReason] = useState('mandar para uma amiga que se culpa pelo peso')
  const [expectedSignal, setExpectedSignal] = useState('DM útil com identificação')
  const [qualityMetric, setQualityMetric] = useState('dm_util')
  const [generated, setGenerated] = useState<Sequence | null>(null)
  const [copied, setCopied] = useState(false)
  const [saving, setSaving] = useState(false)
  const [savedId, setSavedId] = useState<string | null>(null)
  const [saveMsg, setSaveMsg] = useState<string | null>(null)
  const [savedSequences, setSavedSequences] = useState<SavedSequence[]>([])
  const [perfMsg, setPerfMsg] = useState<string | null>(null)
  const [perfLoading, setPerfLoading] = useState(false)
  const [winners, setWinners] = useState<WinnerSequence[]>([])
  const [variation, setVariation] = useState<VariationResponse | null>(null)
  const [variationLoading, setVariationLoading] = useState<string | null>(null)

  const preview = useMemo(() => buildSequence({ tema, tipo, objetivo, objecao, momento, ativo, quantidade }), [tema, tipo, objetivo, objecao, momento, ativo, quantidade])

  function gerar(event: FormEvent) {
    event.preventDefault()
    setGenerated(preview)
    setCopied(false)
  }

  async function copiar() {
    const text = formatSequence(generated || preview)
    try {
      await navigator.clipboard.writeText(text)
      setCopied(true)
    } catch {
      setCopied(false)
    }
  }

  async function carregarSequencias() {
    try {
      const data = await getJson('/stories/sequences?tenant_slug=demo&limit=8')
      setSavedSequences(data.items || [])
    } catch {
      // mantém a tela funcional mesmo se a API estiver indisponível
    }
  }

  async function carregarWinners() {
    try {
      const data = await getJson('/stories/winners?tenant_slug=demo&limit=6')
      setWinners(data.items || [])
    } catch {
      setWinners([])
    }
  }

  useEffect(() => { void carregarSequencias(); void carregarWinners() }, [])

  async function salvarSequencia() {
    setSaving(true); setSaveMsg(null)
    try {
      const current = generated || preview
      const result = await postJson('/stories/sequences', {
        tenant_slug: 'demo',
        title: tema,
        sequence_type: tipo,
        objective: objetivo,
        main_objection: objecao,
        patient_moment: momento,
        support_asset: ativo,
        story_count: current.stories.length,
        payload: {
          sequence: current,
          inputs: { tema, tipo, objetivo, objecao, momento, ativo, quantidade },
          instagram_strategy: {
            seo_social_intent: seoIntent,
            send_save_reason: sendSaveReason,
            expected_intent_signal: expectedSignal,
            quality_metric: qualityMetric,
          },
        },
      })
      setSavedId(result.id)
      setSaveMsg('Sequência salva no banco.')
      await carregarSequencias()
      await carregarWinners()
    } catch {
      setSaveMsg('Não consegui salvar agora.')
    } finally {
      setSaving(false)
    }
  }

  async function registrarPerformance(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const form = event.currentTarget
    const fd = new FormData(form)
    const sequenceId = String(fd.get('sequence_id') || savedId || '')
    if (!sequenceId) { setPerfMsg('Salve ou selecione uma sequência antes.'); return }
    const intOrNull = (name: string) => {
      const raw = String(fd.get(name) || '').trim()
      return raw ? Number(raw) : null
    }
    setPerfLoading(true); setPerfMsg(null)
    try {
      await postJson('/stories/performance', {
        tenant_slug: 'demo',
        sequence_id: sequenceId,
        posted_at: fd.get('posted_at') || null,
        views: intOrNull('views'),
        replies: intOrNull('replies'),
        useful_dms: intOrNull('useful_dms'),
        leads: intOrNull('leads'),
        prints: intOrNull('prints'),
        sticker_taps: intOrNull('sticker_taps'),
        shares: intOrNull('shares'),
        saves: intOrNull('saves'),
        retention_initial_pct: intOrNull('retention_initial_pct'),
        avg_watch_time_sec: intOrNull('avg_watch_time_sec'),
        intent_signal: fd.get('intent_signal') || null,
        quality_metric: fd.get('quality_metric') || null,
        send_save_reason: fd.get('send_save_reason') || null,
        dominant_objection: fd.get('dominant_objection') || null,
        best_story: intOrNull('best_story'),
        worst_story: intOrNull('worst_story'),
        decision: fd.get('decision') || 'adaptar',
        notes: fd.get('notes') || null,
      })
      setPerfMsg('Performance registrada.')
      form.reset()
      await carregarSequencias()
      await carregarWinners()
    } catch {
      setPerfMsg('Não consegui registrar performance agora.')
    } finally {
      setPerfLoading(false)
    }
  }

  async function gerarVariacoes(sequenceId: string) {
    setVariationLoading(sequenceId); setVariation(null)
    try {
      const data = await postJson(`/stories/sequences/${sequenceId}/ab-variations?tenant_slug=demo`, {})
      setVariation(data)
    } catch {
      setVariation({ source_title: 'Erro', usage_note: 'Não consegui gerar variações agora.', variations: [] })
    } finally {
      setVariationLoading(null)
    }
  }

  const seq = generated || preview

  return (
    <div className="dashboardRoot">
      <header className="pageHeader heroHeader">
        <p className="eyebrow">Motor A · Stories</p>
        <h2 className="pageTitle">Stories Connection Engine IVS</h2>
        <p className="heroText">
          Gerador funcional de sequências de Stories: tema, objeção, objetivo e momento emocional entram; o sistema devolve textos, stickers, visual sugerido, quebra de objeção e DM esperada.
        </p>
      </header>

      <section className="section grid" style={{ gridTemplateColumns: 'minmax(320px, 430px) minmax(0, 1fr)', gap: 24, alignItems: 'start' }}>
        <form className="formCard" onSubmit={gerar}>
          <div className="formHeader">
            <span className="badge">Gerador funcional</span>
            <h3>Nova sequência</h3>
            <p className="muted">A sequência nasce da objeção da paciente, não de um dispositivo aleatório.</p>
          </div>

          <label className="muted small">Tema central</label>
          <input className="input" value={tema} onChange={(e) => setTema(e.target.value)} placeholder="Ex.: Não é falta de força de vontade" />

          <label className="muted small">Tipo de sequência</label>
          <select className="input" value={tipo} onChange={(e) => setTipo(e.target.value)}>
            {SEQUENCIAS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
          </select>

          <label className="muted small">Objetivo</label>
          <select className="input" value={objetivo} onChange={(e) => setObjetivo(e.target.value)}>
            {OBJETIVOS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
          </select>

          <label className="muted small">Objeção principal</label>
          <select className="input" value={objecao} onChange={(e) => setObjecao(e.target.value)}>
            {OBJECOES.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
          </select>

          <label className="muted small">Momento da paciente</label>
          <select className="input" value={momento} onChange={(e) => setMomento(e.target.value)}>
            {MOMENTOS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
          </select>

          <label className="muted small">Ativo de apoio</label>
          <select className="input" value={ativo} onChange={(e) => setAtivo(e.target.value)}>
            {ATIVOS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
          </select>

          <label className="muted small">Quantidade de stories: {quantidade}</label>
          <input className="input" type="range" min="8" max="12" value={quantidade} onChange={(e) => setQuantidade(Number(e.target.value))} />

          <div className="formHeader" style={{ marginTop: 10 }}>
            <span className="badge">Instagram 2026</span>
            <p className="muted small">Busca, retenção, envio/salvamento e intenção real entram antes de postar.</p>
          </div>
          <label className="muted small">SEO social / intenção de busca</label>
          <input className="input" value={seoIntent} onChange={(e) => setSeoIntent(e.target.value)} placeholder="Ex.: efeito sanfona, emagrecimento com exames" />
          <label className="muted small">Motivo para salvar/enviar</label>
          <input className="input" value={sendSaveReason} onChange={(e) => setSendSaveReason(e.target.value)} placeholder="Ex.: mandar para amiga que vive se culpando" />
          <label className="muted small">Sinal de intenção esperado</label>
          <input className="input" value={expectedSignal} onChange={(e) => setExpectedSignal(e.target.value)} placeholder="Ex.: DM útil, salvar, envio, WhatsApp" />
          <label className="muted small">Métrica principal de qualidade</label>
          <select className="input" value={qualityMetric} onChange={(e) => setQualityMetric(e.target.value)}>
            <option value="dm_util">DM útil</option>
            <option value="lead_util">Lead útil</option>
            <option value="envio">Envio/compartilhamento</option>
            <option value="retencao">Retenção inicial</option>
            <option value="salvamento">Salvamento</option>
          </select>

          <button className="primaryButton">Gerar sequência</button>
          <button type="button" className="secondaryLink" onClick={copiar} style={{ width: 'fit-content' }}>Copiar sequência completa</button>
          <button type="button" className="primaryButton" onClick={salvarSequencia} disabled={saving}>{saving ? 'Salvando...' : 'Salvar no banco'}</button>
          {copied ? <span className="successText">Sequência copiada.</span> : null}
          {saveMsg ? <span className={saveMsg.includes('salva') ? 'successText' : 'errorText'}>{saveMsg}</span> : null}
        </form>

        <article className="card">
          <div className="rowTop">
            <div>
              <span className="badge">{seq.tipo}</span>
              <h3>Sequência pronta</h3>
            </div>
            <span className="badge badgeDark">CTA: {seq.palavraChave}</span>
          </div>
          <p className="muted">{seq.tese}</p>
          <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit,minmax(180px,1fr))', gap: 8, marginBottom: 14 }}>
            <div className="resultBox"><strong className="muted small">SEO social</strong><p className="small" style={{ margin: '4px 0 0' }}>{seoIntent}</p></div>
            <div className="resultBox"><strong className="muted small">Motivo de envio</strong><p className="small" style={{ margin: '4px 0 0' }}>{sendSaveReason}</p></div>
            <div className="resultBox"><strong className="muted small">Sinal esperado</strong><p className="small" style={{ margin: '4px 0 0' }}>{expectedSignal}</p></div>
            <div className="resultBox"><strong className="muted small">Métrica norte</strong><p className="small" style={{ margin: '4px 0 0' }}>{qualityMetric}</p></div>
          </div>
          <div className="tableLike">
            {seq.stories.map((story) => (
              <div className="row" key={`${story.n}-${story.funcao}`}>
                <div className="rowTop"><strong>Story {story.n} · {story.funcao}</strong><span className="badge">risco {story.risco}</span></div>
                <span>{story.texto}</span>
                <span className="muted"><strong>Visual:</strong> {story.visual}</span>
                <span className="muted"><strong>Sticker/CTA:</strong> {story.sticker}</span>
                <span className="muted"><strong>Quebra de objeção:</strong> {story.objecao}</span>
                <span className="muted"><strong>DM esperada:</strong> {story.dm}</span>
              </div>
            ))}
          </div>
        </article>
      </section>

      <section className="section grid" style={{ gridTemplateColumns: 'repeat(3, minmax(0, 1fr))' }}>
        <article className="card">
          <h3>Por que supera o Stories 10x</h3>
          <p className="muted">O módulo não sorteia dispositivos. Ele cruza avatar, dor emocional, objeção, intenção, visual e handoff.</p>
        </article>
        <article className="card">
          <h3>Compliance embutido</h3>
          <p className="muted">Sem promessa de quilos, prazo ou cura. A copy usa avaliação, contexto, possibilidade e orientação.</p>
        </article>
        <article className="card">
          <h3>Aprendizado operacional</h3>
          <p className="muted">Cada sequência pode registrar replies, DMs úteis, objeção dominante e decisão: repetir, adaptar ou descartar.</p>
        </article>
      </section>

      <section className="section grid" style={{ gridTemplateColumns: 'minmax(0, 1fr) minmax(320px, 440px)', gap: 24, alignItems: 'start' }}>
        <article className="card">
          <div className="rowTop"><h3>Sequências salvas</h3><span className="badge">banco + aprendizado</span></div>
          <div className="tableLike">
            {savedSequences.length ? savedSequences.map((item) => (
              <div className="row" key={item.id}>
                <div className="rowTop"><strong>{item.title}</strong><span className="badge">{item.story_count} stories</span></div>
                <span className="muted">Tipo: {labelOf(SEQUENCIAS, item.sequence_type)} · Objetivo: {labelOf(OBJETIVOS, item.objective)} · Objeção: {labelOf(OBJECOES, item.main_objection)}</span>
                <span className="muted">Registros: {item.performance_entries || 0} · DMs úteis: {item.total_useful_dms || 0} · Leads: {item.total_leads || 0}</span>
              </div>
            )) : <p className="muted">Nenhuma sequência salva ainda.</p>}
          </div>
        </article>

        <form className="formCard" onSubmit={registrarPerformance}>
          <div className="formHeader">
            <span className="badge">Pós-postagem</span>
            <h3>Registrar performance</h3>
            <p className="muted">Use depois de postar para o sistema aprender quais temas, objeções, CTAs e stickers geram DM útil.</p>
          </div>
          <label className="muted small">Sequência</label>
          <select className="input" name="sequence_id" defaultValue={savedId || ''}>
            <option value="">Selecione uma sequência salva</option>
            {savedSequences.map((item) => <option key={item.id} value={item.id}>{item.title}</option>)}
          </select>
          <input className="input" type="date" name="posted_at" />
          <div className="grid" style={{ gridTemplateColumns: '1fr 1fr', gap: 10 }}>
            <input className="input" type="number" min="0" name="views" placeholder="Views" />
            <input className="input" type="number" min="0" name="replies" placeholder="Replies" />
            <input className="input" type="number" min="0" name="useful_dms" placeholder="DMs úteis" />
            <input className="input" type="number" min="0" name="leads" placeholder="Leads" />
            <input className="input" type="number" min="0" name="prints" placeholder="Prints" />
            <input className="input" type="number" min="0" name="sticker_taps" placeholder="Stickers" />
            <input className="input" type="number" min="0" name="shares" placeholder="Envios" />
            <input className="input" type="number" min="0" name="saves" placeholder="Salvamentos" />
            <input className="input" type="number" min="0" max="100" name="retention_initial_pct" placeholder="Retenção inicial %" />
            <input className="input" type="number" min="0" name="avg_watch_time_sec" placeholder="Tempo médio (s)" />
            <input className="input" type="number" min="1" name="best_story" placeholder="Melhor story #" />
            <input className="input" type="number" min="1" name="worst_story" placeholder="Pior story #" />
          </div>
          <input className="input" name="intent_signal" placeholder="Sinal de intenção real observado" />
          <input className="input" name="send_save_reason" placeholder="Por que salvaram/enviaram?" />
          <select className="input" name="quality_metric" defaultValue="dm_util">
            <option value="dm_util">DM útil</option>
            <option value="lead_util">Lead útil</option>
            <option value="envio">Envio</option>
            <option value="retencao">Retenção</option>
            <option value="salvamento">Salvamento</option>
          </select>
          <input className="input" name="dominant_objection" placeholder="Objeção dominante percebida" />
          <select className="input" name="decision" defaultValue="adaptar">
            <option value="repetir">Repetir</option>
            <option value="adaptar">Adaptar</option>
            <option value="descartar">Descartar</option>
          </select>
          <textarea className="textarea" name="notes" rows={4} placeholder="Observações: qual CTA puxou conversa, qual objeção apareceu, prints de respostas, ajustes para próxima rodada..." />
          <button className="primaryButton" disabled={perfLoading}>{perfLoading ? 'Registrando...' : 'Registrar performance'}</button>
          {perfMsg ? <span className={perfMsg.includes('registrada') ? 'successText' : 'errorText'}>{perfMsg}</span> : null}
        </form>
      </section>

      <section className="section grid" style={{ gridTemplateColumns: 'minmax(0, 1fr) minmax(320px, 440px)', gap: 24, alignItems: 'start' }}>
        <article className="card">
          <div className="rowTop"><h3>Ranking de vencedoras</h3><span className="badge">DM útil + lead</span></div>
          <p className="muted">Score: lead ×10, DM útil ×4, reply ×1, print ×1.5 e sticker ×0.5. Views servem para taxa, não para vaidade.</p>
          <div className="tableLike">
            {winners.length ? winners.map((item, index) => (
              <div className="row" key={item.id}>
                <div className="rowTop"><strong>#{index + 1} · {item.title}</strong><span className="badge">score {item.winner_score}</span></div>
                <span className="muted">Leads: {item.total_leads || 0} · DMs úteis: {item.total_useful_dms || 0} · Envios: {item.total_shares || 0} · Salvamentos: {item.total_saves || 0} · Replies: {item.total_replies || 0}</span>
                <span className="muted">Taxa DM útil: {item.useful_dm_rate ?? 'N/D'}% · Taxa lead: {item.lead_rate ?? 'N/D'}% · Retenção inicial média: {item.avg_retention_initial_pct ?? 'N/D'}% · Sinal: {item.learned_intent_signal || 'N/D'}</span>
                <span className="muted">Objeção: {item.dominant_objection_learned || labelOf(OBJECOES, item.main_objection)}</span>
                <button type="button" className="secondaryLink" style={{ width: 'fit-content' }} onClick={() => gerarVariacoes(item.id)} disabled={variationLoading === item.id}>
                  {variationLoading === item.id ? 'Gerando...' : 'Gerar A/B'}
                </button>
              </div>
            )) : <p className="muted">Ainda não há vencedoras. Registre performance para ativar o ranking.</p>}
          </div>
        </article>

        <article className="card">
          <div className="rowTop"><h3>Variações A/B</h3><span className="badge">hook · CTA · sticker</span></div>
          {variation ? (
            <div className="tableLike">
              <p className="muted"><strong>Base:</strong> {variation.source_title}</p>
              {variation.variations.map((item) => (
                <div className="row" key={item.variant}>
                  <div className="rowTop"><strong>Variação {item.variant}</strong><span className="badge">{item.focus}</span></div>
                  <span>{item.hook}</span>
                  <span className="muted"><strong>CTA:</strong> {item.cta}</span>
                  <span className="muted"><strong>Sticker:</strong> {item.sticker}</span>
                  <span className="muted"><strong>Por quê:</strong> {item.why}</span>
                </div>
              ))}
              <p className="muted small">{variation.usage_note}</p>
            </div>
          ) : (
            <p className="muted">Clique em “Gerar A/B” em uma sequência vencedora para criar variações controladas de hook, CTA e sticker.</p>
          )}
        </article>
      </section>
    </div>
  )
}
