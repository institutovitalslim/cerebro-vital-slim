'use client'

// CardAcao — card no estilo da fila de ações da /trafego (extraído por cópia):
// featurePanel com borda esquerda 4px na cor do estado, emoji grande à esquerda,
// título + subtexto no meio e um bloco livre à direita. Vira link se receber href.
// Cor aceita hex ('#2f9e63') ou token CSS ('var(--state-good)').

import Link from 'next/link'
import type { CSSProperties, ReactNode } from 'react'

export function CardAcao({ emoji, cor, titulo, sub, direita, href, children }: {
  emoji: string; cor: string; titulo: string; sub?: string
  direita?: ReactNode; href?: string; children?: ReactNode
}) {
  const style = { '--cor': cor } as CSSProperties
  const conteudo = (
    <>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
        <span style={{ fontSize: '1.5rem' }} aria-hidden>{emoji}</span>
        <div style={{ flex: 1, minWidth: 220 }}>
          <strong style={{ fontSize: '1.02rem' }}>{titulo}</strong>
          {sub ? <p className="muted small" style={{ margin: '2px 0 0' }}>{sub}</p> : null}
        </div>
        {direita ? <div style={{ textAlign: 'right' }}>{direita}</div> : null}
      </div>
      {children}
    </>
  )
  if (href) {
    return (
      <Link href={href} className="featurePanel cardAcao" style={style}>
        {conteudo}
      </Link>
    )
  }
  return (
    <article className="featurePanel cardAcao" style={style}>
      {conteudo}
    </article>
  )
}
