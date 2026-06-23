import Link from 'next/link'
import { FormGerar } from '../../components/galeria'

export default function Page() {
  return (
    <div className="dashboardRoot">
      <header className="pageHeader heroHeader">
        <div>
          <p className="eyebrow">Produção · Reels</p>
          <h2 className="pageTitle">Reels para retenção, alcance e autoridade em vídeo</h2>
          <p className="heroText">Use reels quando a tese precisa de fala, ritmo, prova viva ou bastidor da Dra. Daniely para gerar consciência e conversa.</p>
        </div>
        <div className="heroActions">
          <Link className="secondaryLink" href="/business-intelligence">Ver BI antes</Link>
          <Link className="secondaryLink" href="/banco-criativos">Revisar reels</Link>
        </div>
      </header>
      <FormGerar defaultFormato="reels" lockFormato />
    </div>
  )
}
