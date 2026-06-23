import Link from 'next/link'
import { FormGerar } from '../../components/galeria'

export default function Page() {
  return (
    <div className="dashboardRoot">
      <header className="pageHeader heroHeader">
        <div>
          <p className="eyebrow">Produção · Estáticos</p>
          <h2 className="pageTitle">Estáticos para tese forte, anúncio e presença premium</h2>
          <p className="heroText">Use estático quando a mensagem precisa ser instantânea: uma dor, uma promessa segura, uma objeção ou uma prova visual.</p>
        </div>
        <div className="heroActions">
          <Link className="secondaryLink" href="/business-intelligence">Ver BI antes</Link>
          <Link className="secondaryLink" href="/banco-criativos">Revisar estáticos</Link>
        </div>
      </header>
      <FormGerar defaultFormato="estatico" lockFormato />
    </div>
  )
}
