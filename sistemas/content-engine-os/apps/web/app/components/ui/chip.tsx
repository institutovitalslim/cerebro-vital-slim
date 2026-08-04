'use client'

// Chip — pill chapada colorida (padrão /trafego, extraído por cópia).
// Cor aceita hex ('#2f9e63') ou token CSS ('var(--state-good)').

import type { ReactNode } from 'react'

export function Chip({ cor, children }: { cor: string; children: ReactNode }) {
  return (
    <span className="stateChip" style={{ background: cor }}>{children}</span>
  )
}
