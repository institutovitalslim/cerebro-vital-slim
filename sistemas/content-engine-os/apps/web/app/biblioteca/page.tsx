import { fetchJson } from '../api'
import { BibliotecaTabs, type Asset, type TabId } from '../components/biblioteca-tabs'

// Biblioteca unificada: assets genéricos, fotos da Dra e b-roll em 3 abas client-side.
// As rotas antigas (/biblioteca/dra e /stories-engine/broll) continuam funcionando.
export default async function BibliotecaPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>
}) {
  const sp = await searchParams
  const rawTab = Array.isArray(sp.tab) ? sp.tab[0] : sp.tab
  const initialTab: TabId = rawTab === 'dra' || rawTab === 'broll' ? rawTab : 'assets'

  let assets: Asset[] = []
  let assetsErro = false
  try {
    const data = await fetchJson<{ items: Asset[] }>('/assets?tenant_slug=demo')
    assets = data.items || []
  } catch {
    assetsErro = true // a aba mostra aviso visível — nunca zero silencioso
  }

  return (
    <div>
      <header className="pageHeader">
        <p className="eyebrow">Biblioteca</p>
        <h2 className="pageTitle">Todo o material bruto num lugar só</h2>
        <p className="muted">
          Assets e referências, fotos reais da Dra e b-roll de Stories/Reels — o que o sistema usa para
          gerar criativo sem inventar imagem. Quanto melhor o acervo aqui, melhor a peça que sai lá.
        </p>
      </header>
      <BibliotecaTabs initialAssets={assets} assetsErro={assetsErro} initialTab={initialTab} />
    </div>
  )
}
