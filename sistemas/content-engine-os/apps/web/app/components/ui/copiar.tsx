'use client'

// Botões de copiar para a área de transferência (padrão /trafego, extraído por cópia).
// BotaoCopiar = botão grande dourado; CopiarMini = botãozinho discreto inline.

import { useState } from 'react'

export function BotaoCopiar({ texto, rotulo }: { texto: string; rotulo: string }) {
  const [ok, setOk] = useState(false)
  return (
    <button
      type="button"
      onClick={async () => {
        await navigator.clipboard.writeText(texto)
        setOk(true)
        setTimeout(() => setOk(false), 2500)
      }}
      style={{ background: ok ? 'var(--state-good)' : 'var(--state-warn)', color: ok ? '#fff' : '#141210',
        border: 'none', borderRadius: 10, padding: '10px 18px', fontWeight: 800, fontSize: '.9rem',
        cursor: 'pointer', whiteSpace: 'nowrap' }}>
      {ok ? '✓ Copiado!' : `📋 ${rotulo}`}
    </button>
  )
}

export function CopiarMini({ texto }: { texto: string }) {
  const [ok, setOk] = useState(false)
  return (
    <button
      type="button"
      title={`copiar ${texto}`}
      onClick={async (e) => {
        e.preventDefault()
        e.stopPropagation()
        await navigator.clipboard.writeText(texto)
        setOk(true)
        setTimeout(() => setOk(false), 1800)
      }}
      style={{ background: ok ? 'var(--state-good)' : 'rgba(255,255,255,.08)', color: ok ? '#fff' : 'inherit',
        border: `1px solid ${ok ? 'var(--state-good)' : 'rgba(255,255,255,.09)'}`, borderRadius: 8,
        padding: '3px 9px', fontSize: '.75rem', cursor: 'pointer', flexShrink: 0 }}>
      {ok ? '✓' : '📋'}
    </button>
  )
}
