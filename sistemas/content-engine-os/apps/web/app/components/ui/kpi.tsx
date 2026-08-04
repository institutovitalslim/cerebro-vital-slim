'use client'

// Kpi — card de número grande, centrado, com borda colorida + glow interno.
// Extraído POR CÓPIA do padrão da /trafego (não importa nada de lá).
// Cor aceita hex ('#2f9e63') ou token CSS ('var(--state-good)').

import type { CSSProperties } from 'react'

export function Kpi({ rotulo, valor, sub, cor }: { rotulo: string; valor: string; sub?: string; cor?: string }) {
  const style = cor ? ({ '--cor': cor } as CSSProperties) : undefined
  return (
    <article className="kpiTile" style={style}>
      <p className="kpiRotulo">{rotulo}</p>
      <p className="kpiValor">{valor}</p>
      {sub ? <p className="muted small" style={{ margin: 0 }}>{sub}</p> : null}
    </article>
  )
}
