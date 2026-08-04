// A home É a página do dia: a raiz renderiza exatamente o conteúdo de /hoje.
// O cockpit antigo foi absorvido por /hoje — não existe mais versão separada.
// /hoje continua acessível na própria rota.
export { default } from './hoje/page'

// Segment config não atravessa re-export com segurança no Next,
// então declaramos aqui também (mesmo valor de app/hoje/page.tsx).
export const dynamic = 'force-dynamic'
