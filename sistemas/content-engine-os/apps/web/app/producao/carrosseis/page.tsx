import Link from 'next/link'
import { FormGerar } from '../../components/galeria'

export default function Page() {
  return (
    <div className="dashboardRoot">
      <header className="pageHeader heroHeader">
        <div>
          <p className="eyebrow">Produção · Carrosséis</p>
          <h2 className="pageTitle">Carrosséis para autoridade, salvamento e compartilhamento</h2>
          <p className="heroText">Use carrossel quando a tese precisa de progressão lógica: hook, rehook, mecanismo, prova, objeção e CTA.</p>
        </div>
        <div className="heroActions">
          <Link className="secondaryLink" href="/business-intelligence">Ver BI antes</Link>
          <Link className="secondaryLink" href="/banco-criativos">Revisar carrosséis</Link>
        </div>
      </header>
      <FormGerar defaultFormato="carrossel" lockFormato />
    </div>
  )
}
