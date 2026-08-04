// Máquina canônica de estados de uma peça de conteúdo.
// Fio do produto: ideia → peça → revisão → publicação → medição → aprendizado.
// Rótulos em pt-BR humano; cores pelos tokens --state-* do styles.css.
// Chaves canônicas + apelidos comuns vindos da API (inglês) apontam para o MESMO objeto.

type EstadoVisual = { rotulo: string; emoji: string; cor: string }

const RASCUNHO: EstadoVisual = { rotulo: 'Rascunho', emoji: '📝', cor: 'var(--state-neutral)' }
const RENDERIZADA: EstadoVisual = { rotulo: 'Arte pronta', emoji: '🖼️', cor: 'var(--state-warn)' }
const EM_REVISAO: EstadoVisual = { rotulo: 'Em revisão', emoji: '👀', cor: 'var(--state-warn)' }
const APROVADA: EstadoVisual = { rotulo: 'Aprovada', emoji: '✅', cor: 'var(--state-good)' }
const AGENDADA: EstadoVisual = { rotulo: 'Agendada', emoji: '📅', cor: 'var(--state-warn)' }
const PUBLICADA: EstadoVisual = { rotulo: 'Publicada', emoji: '🚀', cor: 'var(--state-good)' }
const MEDIDA: EstadoVisual = { rotulo: 'Resultado medido', emoji: '📊', cor: 'var(--state-good)' }
const GERADA: EstadoVisual = { rotulo: 'Texto pronto', emoji: '✍️', cor: 'var(--state-warn)' }
const ERRO: EstadoVisual = { rotulo: 'Erro no render', emoji: '⚠️', cor: 'var(--state-bad)' }
const AJUSTES: EstadoVisual = { rotulo: 'Ajustes pedidos', emoji: '✏️', cor: 'var(--state-warn)' }
const PAUSADA: EstadoVisual = { rotulo: 'Pausada', emoji: '⏸️', cor: 'var(--state-neutral)' }

export const ESTADO_PECA: Record<string, { rotulo: string; emoji: string; cor: string }> = {
  // estados canônicos
  rascunho: RASCUNHO,
  renderizada: RENDERIZADA,
  em_revisao: EM_REVISAO,
  aprovada: APROVADA,
  agendada: AGENDADA,
  publicada: PUBLICADA,
  medida: MEDIDA,
  // apelidos comuns (inglês → canônico)
  draft: RASCUNHO,
  rendered: RENDERIZADA,
  in_review: EM_REVISAO,
  approved: APROVADA,
  scheduled: AGENDADA,
  published: PUBLICADA,
  measured: MEDIDA,
  // estados específicos da galeria de criativos
  gerado: GERADA,
  render_erro: ERRO,
  ajustes_solicitados: AJUSTES,
  pausado_formato: PAUSADA,
}
