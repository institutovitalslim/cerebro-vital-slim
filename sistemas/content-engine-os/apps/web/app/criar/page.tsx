import Link from 'next/link'
import { FormGerar } from '../components/galeria'

export default function Page() {
  return (
    <div className="dashboardRoot">
      <header className="pageHeader heroHeader">
        <div>
          <p className="eyebrow">Produção · família de conteúdo</p>
          <h2 className="pageTitle">Criar conteúdo com direção, não peça solta</h2>
          <p className="heroText">
            Escolha uma tese, defina hipótese criativa e gere uma peça ou matriz. O fluxo correto é: criar → revisar → aprovar → planejar → medir.
          </p>
        </div>
        <div className="heroActions">
          <Link className="secondaryLink" href="/business-intelligence">Ver BI antes de criar</Link>
          <Link className="secondaryLink" href="/banco-criativos">Abrir fila de aprovação</Link>
        </div>
      </header>
      <FormGerar />
    </div>
  )
}
