import { DraPhotos } from '../../components/dra-photos'

export default function DraFotosPage() {
  return (
    <div>
      <header className="pageHeader">
        <p className="eyebrow">Biblioteca · Marca</p>
        <h2 className="pageTitle">Banco de fotos da Dra</h2>
        <p className="muted">
          Inclua e gerencie as fotos reais da Dra Daniely usadas nos criativos. Toda nova foto passa pelo gate de
          compliance (sem medicação, seringa, caneta de aplicação, jaleco ou ambiente clínico). Prefira sempre fotos
          reais, padrão de fundo preto.
        </p>
      </header>
      <DraPhotos />
    </div>
  )
}
