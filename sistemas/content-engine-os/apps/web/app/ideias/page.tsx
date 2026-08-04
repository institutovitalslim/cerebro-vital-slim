'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'

import { CardAcao } from '../components/ui/card-acao'
import { Chip } from '../components/ui/chip'

// ————— /ideias — a fila do dia —————
// O sistema olha tudo o que pode virar conteúdo (roteiros do banco, posts que
// bombaram, garimpo externo, temas anotados, oportunidades) e traz aqui só as
// melhores de hoje, já em ordem. Produzir leva pro /criar com tudo preenchido.

const api = process.env.NEXT_PUBLIC_API_BASE_URL || '/api'

type Ideia = {
  id: string
  tipo: string
  titulo: string
  resumo: string | null
  hook: string | null
  formato_sugerido: string | null
  origem: string | null
  engajamento: number | null
  criado_em: string | null
  score: number
  url: string | null
}

const TIPOS: Record<string, { emoji: string; rotulo: string; cor: string }> = {
  roteiro: { emoji: '📜', rotulo: 'Roteiro', cor: '#2f9e63' },
  sinal: { emoji: '📡', rotulo: 'Post que bombou', cor: '#c9a227' },
  externo: { emoji: '🔭', rotulo: 'Garimpo externo', cor: '#4d7fb0' },
  tema: { emoji: '🗂', rotulo: 'Tema anotado', cor: '#6f6a61' },
  oportunidade: { emoji: '💡', rotulo: 'Oportunidade', cor: '#b0684d' },
}

const FORMATO_NOME: Record<string, string> = {
  reel: 'Reel', carrossel: 'Carrossel', estatico: 'Estático', stories: 'Stories',
}

const num = (v: number) => v.toLocaleString('pt-BR')

function linkProduzir(i: Ideia): string {
  const qs = new URLSearchParams({ source: 'ideias', formato: i.formato_sugerido || 'reel' })
  if (i.tipo) qs.set('tipo', i.tipo)
  if (i.titulo) qs.set('titulo', i.titulo)
  if (i.hook) qs.set('hook', i.hook)
  return `/criar?${qs.toString()}`
}

function BarraScore({ score }: { score: number }) {
  const pct = Math.min(100, Math.max(3, Math.round(score * 100)))
  return (
    <div title={`força da ideia: ${pct} de 100`}
      style={{ background: 'rgba(255,255,255,.08)', borderRadius: 99, height: 8, width: '100%' }}>
      <div style={{ width: `${pct}%`, height: 8, borderRadius: 99, background: 'var(--state-warn)' }} />
    </div>
  )
}

export default function Page() {
  const [itens, setItens] = useState<Ideia[] | null>(null)
  const [total, setTotal] = useState(0)
  const [erro, setErro] = useState(false)
  const [aviso, setAviso] = useState<string | null>(null)
  const [busca, setBusca] = useState('')
  const [tipo, setTipo] = useState('')
  const [guardadas, setGuardadas] = useState<Set<string>>(new Set())
  const [salvando, setSalvando] = useState<string | null>(null)

  function carregar(q: string, t: string) {
    setErro(false)
    const qs = new URLSearchParams({ tenant_slug: 'demo', limit: '15' })
    if (q.trim()) qs.set('q', q.trim())
    if (t) qs.set('tipo', t)
    fetch(`${api}/ideias/fila?${qs.toString()}`, { credentials: 'include', cache: 'no-store' })
      .then((r) => {
        if (r.status === 401) { window.location.href = '/login'; throw new Error('401') }
        if (!r.ok) throw new Error(String(r.status))
        return r.json()
      })
      .then((d) => { setItens(d.itens || []); setTotal(d.total || 0) })
      .catch(() => { setItens((cur) => cur ?? []); setErro(true) })
  }

  // busca e filtro com respiro de 350ms para não metralhar a API a cada tecla
  useEffect(() => {
    const timer = setTimeout(() => carregar(busca, tipo), itens === null ? 0 : 350)
    return () => clearTimeout(timer)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [busca, tipo])

  async function marcar(id: string, estado: 'guardada' | 'descartada') {
    setAviso(null)
    setSalvando(id)
    try {
      const qs = new URLSearchParams({ tenant_slug: 'demo', ideia_id: id, estado })
      const r = await fetch(`${api}/ideias/estado?${qs.toString()}`, { method: 'POST', credentials: 'include' })
      if (r.status === 401) { window.location.href = '/login'; return }
      if (!r.ok) throw new Error(String(r.status))
      if (estado === 'descartada') {
        setItens((cur) => (cur || []).filter((i) => i.id !== id))
        setTotal((t) => Math.max(0, t - 1))
      } else {
        setGuardadas((cur) => new Set(cur).add(id))
      }
    } catch {
      setAviso('Não consegui salvar agora. Espere um instante e tente de novo.')
    } finally {
      setSalvando(null)
    }
  }

  return (
    <div className="dashboardRoot">
      <header className="pageHeader heroHeader">
        <div>
          <p className="eyebrow">Ideias</p>
          <h2 className="pageTitle">As melhores de hoje</h2>
          <p className="heroText">
            O sistema olha tudo o que pode virar conteúdo — roteiros prontos, posts
            que bombaram, achados de outros perfis, temas anotados — e traz aqui só
            o que vale seu tempo hoje, já em ordem de força.
          </p>
        </div>
        <div className="heroActions">
          <Link className="secondaryLink" href="/hoje">← Voltar pro seu dia</Link>
        </div>
      </header>

      <section className="featurePanel">
        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', alignItems: 'center' }}>
          <input
            className="input"
            style={{ flex: 1, minWidth: 200 }}
            placeholder="🔍 buscar por assunto… (ex: menopausa, jejum, culpa)"
            value={busca}
            onChange={(e) => setBusca(e.target.value)}
          />
          <select className="input" style={{ flex: '0 1 auto' }} value={tipo} onChange={(e) => setTipo(e.target.value)}>
            <option value="">Todas as origens</option>
            <option value="roteiro">📜 Roteiros</option>
            <option value="sinal">📡 Posts que bombaram</option>
            <option value="externo">🔭 Garimpo externo</option>
            <option value="tema">🗂 Temas anotados</option>
            <option value="oportunidade">💡 Oportunidades</option>
          </select>
          {itens !== null && !erro ? (
            <span className="muted small">mostrando as {itens.length} melhores de {num(total)} ideias vivas</span>
          ) : null}
        </div>

        {aviso ? <div className="empty">⚠️ {aviso}</div> : null}

        {erro ? (
          <div className="empty">
            ⚠️ Não consegui carregar a fila de ideias agora.{' '}
            <button className="secondaryLink" type="button" onClick={() => carregar(busca, tipo)}>Tentar de novo</button>
          </div>
        ) : itens === null ? (
          <div className="empty">Separando as melhores ideias de hoje…</div>
        ) : itens.length === 0 ? (
          <div className="empty">
            Nenhuma ideia encontrada {busca || tipo ? 'com esse filtro — limpe a busca e tente de novo' : 'ainda — cadastre temas ou fontes para alimentar a fila'}.
          </div>
        ) : (
          <div style={{ display: 'grid', gap: 12 }}>
            {itens.map((i) => {
              const t = TIPOS[i.tipo] || { emoji: '✨', rotulo: i.tipo, cor: 'var(--state-neutral)' }
              const guardada = guardadas.has(i.id)
              const origem = [
                i.origem ? `vinda de: ${i.origem}` : null,
                i.engajamento != null && i.engajamento > 0 ? `${num(i.engajamento)} interações` : null,
              ].filter(Boolean).join(' · ')
              return (
                <CardAcao
                  key={i.id}
                  emoji={t.emoji}
                  cor={t.cor}
                  titulo={i.titulo}
                  sub={i.hook ? `Gancho: ${i.hook}` : i.resumo || undefined}
                  direita={<Chip cor={t.cor}>{t.emoji} {t.rotulo}</Chip>}
                >
                  <div style={{ display: 'grid', gap: 10, marginTop: 10 }}>
                    <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', alignItems: 'center' }}>
                      {i.formato_sugerido ? (
                        <span className="badge">{FORMATO_NOME[i.formato_sugerido] || i.formato_sugerido}</span>
                      ) : null}
                      {origem ? <span className="muted small">{origem}</span> : null}
                    </div>
                    <div style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
                      <div style={{ flex: 1, minWidth: 140 }}><BarraScore score={i.score} /></div>
                      <span className="muted small" style={{ whiteSpace: 'nowrap' }}>força {Math.round(i.score * 100)}/100</span>
                    </div>
                    <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
                      <Link className="primaryButton" style={{ padding: '8px 16px' }} href={linkProduzir(i)}>▶ Produzir</Link>
                      <button
                        className="secondaryLink"
                        type="button"
                        disabled={guardada || salvando === i.id}
                        onClick={() => marcar(i.id, 'guardada')}
                      >
                        {guardada ? '✓ Guardada' : '💾 Guardar'}
                      </button>
                      <button
                        className="secondaryLink"
                        type="button"
                        disabled={salvando === i.id}
                        onClick={() => marcar(i.id, 'descartada')}
                      >
                        ✕ Descartar
                      </button>
                    </div>
                  </div>
                </CardAcao>
              )
            })}
          </div>
        )}

        <p className="muted small" style={{ margin: 0 }}>
          Isto é a fila do dia — o acervo completo vive no{' '}
          <Link href="/banco-roteiros">Banco de roteiros</Link>.
        </p>
      </section>
    </div>
  )
}
