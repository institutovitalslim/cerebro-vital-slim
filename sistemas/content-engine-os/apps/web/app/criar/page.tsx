'use client'

import Link from 'next/link'
import { useEffect, useState } from 'react'

type Prefill = { titulo: string; hook: string; formato: string; tipo: string }

const FORMATO_ROTA: Record<string, string> = {
  reels: '/producao/reels',
  carrossel: '/producao/carrosseis',
  estatico: '/producao/estaticos',
  stories: '/stories-engine',
}
const FORMATO_NOME: Record<string, string> = {
  reels: 'Reel roteirizado',
  carrossel: 'Carrossel',
  estatico: 'Estático',
  stories: 'Stories',
}

function normalizaFormato(f: string) {
  const x = (f || '').toLowerCase()
  if (x === 'reel') return 'reels'
  if (x === 'story') return 'stories'
  if (x === 'carrosseis' || x === 'carrossél') return 'carrossel'
  if (x === 'estaticos' || x === 'estático') return 'estatico'
  return FORMATO_ROTA[x] ? x : 'reels'
}

const cards = [
  {
    formato: 'reels',
    emoji: '🎬',
    label: 'Reel roteirizado',
    title: 'Vídeo curto para alcançar gente nova',
    quando: 'Use quando o objetivo é alcance e engajamento: aparecer para quem ainda não conhece a Dra e fazer o público interagir, salvar e compartilhar.',
  },
  {
    formato: 'carrossel',
    emoji: '🧠',
    label: 'Carrossel',
    title: 'Explicação em sequência que constrói confiança',
    quando: 'Use quando o assunto pede profundidade: educar, provar e mostrar autoridade. É o formato que as pacientes salvam para reler depois.',
  },
  {
    formato: 'estatico',
    emoji: '🖼️',
    label: 'Estático',
    title: 'Uma imagem, uma mensagem forte',
    quando: 'Use quando uma única frase resolve: um recado direto, um posicionamento ou um anúncio sem distração.',
  },
  {
    formato: 'stories',
    emoji: '💬',
    label: 'Stories',
    title: 'Conversa diária com quem já te segue',
    quando: 'Use para manter a conexão de todo dia: bastidor, enquete, resposta de dúvida — o que aquece a relação e puxa conversa no direct.',
  },
]

export default function Page() {
  const [prefill, setPrefill] = useState<Prefill | null>(null)

  useEffect(() => {
    if (typeof window === 'undefined') return
    const qs = new URLSearchParams(window.location.search)
    const source = qs.get('source')
    if (source !== 'ideias' && source !== 'weekly-sprint' && source !== 'radar') return
    const titulo = qs.get('titulo') || qs.get('thesis') || ''
    const hook = qs.get('hook') || qs.get('objective') || ''
    if (!titulo && !hook) return
    setPrefill({ titulo, hook, formato: normalizaFormato(qs.get('formato') || ''), tipo: qs.get('tipo') || source })
  }, [])

  function comIdeia(formato: string) {
    const rota = FORMATO_ROTA[formato] || '/producao/reels'
    if (!prefill) return rota
    const qs = new URLSearchParams(typeof window !== 'undefined' ? window.location.search : '')
    qs.set('formato', formato)
    if (!qs.get('source')) qs.set('source', 'ideias')
    if (prefill.titulo && !qs.get('titulo')) qs.set('titulo', prefill.titulo)
    if (prefill.hook && !qs.get('hook')) qs.set('hook', prefill.hook)
    return `${rota}?${qs.toString()}`
  }

  return (
    <div className="dashboardRoot">
      <header className="pageHeader heroHeader">
        <div>
          <p className="eyebrow">Estúdio</p>
          <h2 className="pageTitle">O que vamos criar hoje?</h2>
          <p className="heroText">Escolha o formato pelo que você quer que aconteça: alcançar gente nova, aprofundar a confiança, dar um recado direto ou conversar com quem já acompanha.</p>
        </div>
        <div className="heroActions">
          <Link className="secondaryLink" href="/banco-roteiros">Pegar uma ideia pronta</Link>
          <Link className="secondaryLink" href="/banco-criativos">Revisar o que já foi gerado</Link>
        </div>
      </header>

      {prefill ? (
        <section className="section">
          <article className="featurePanel featurePanelDark">
            <div className="sectionHeaderInline">
              <div>
                <p className="eyebrow">Ideia escolhida</p>
                <h3 className="sectionTitle">🎯 Produzindo a ideia: {prefill.titulo || prefill.hook}</h3>
              </div>
              <span className="badge">{FORMATO_NOME[prefill.formato] || 'Reel roteirizado'}</span>
            </div>
            {prefill.hook && prefill.titulo ? <p className="muted small" style={{ margin: 0 }}>Hook: {prefill.hook}</p> : null}
            <p className="muted small" style={{ margin: 0 }}>Ela já vai entrar preenchida na tela de produção — é só revisar e gerar.</p>
            <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
              <a className="primaryButton" href={comIdeia(prefill.formato)}>Produzir agora como {FORMATO_NOME[prefill.formato] || 'Reel'} →</a>
              <span className="muted small" style={{ alignSelf: 'center' }}>ou escolha outro formato abaixo — a ideia vai junto.</span>
            </div>
          </article>
        </section>
      ) : null}

      <section className="flowRail">
        {cards.map((card) => (
          <a className="flowCard" href={comIdeia(card.formato)} key={card.formato}>
            <span className="badge badgeDark">{card.emoji} {card.label}</span>
            <h3>{card.title}</h3>
            <p className="muted small">{card.quando}</p>
            <span className="secondaryLink">Criar {card.label.toLowerCase()} →</span>
          </a>
        ))}
      </section>

      <section className="section">
        <article className="featurePanel featurePanelDark">
          <div className="sectionHeaderInline">
            <div>
              <p className="eyebrow">Atalho</p>
              <h3 className="sectionTitle">🎥 Tenho vídeo bruto da Dra</h3>
            </div>
          </div>
          <p className="muted small" style={{ margin: 0 }}>A Dra já gravou? Mande o vídeo do jeito que saiu do celular: ele volta como reel pronto, com cortes, legenda e capa — sem regravar nada.</p>
          <div>
            <Link className="primaryButton" href="/producao/video-bruto">Transformar vídeo bruto em reel →</Link>
          </div>
        </article>
      </section>
    </div>
  )
}
