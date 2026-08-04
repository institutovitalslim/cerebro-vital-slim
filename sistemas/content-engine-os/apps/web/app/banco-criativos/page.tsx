import { Galeria } from '../components/galeria'

export default function Page() {
  return (
    <div>
      <header className="pageHeader">
        <div>
          <p className="eyebrow">Revisão &amp; aprovação</p>
          <h2 className="pageTitle">Banco de criativos</h2>
          <p className="muted">Biblioteca das peças geradas. Clique para revisar todos os slides, aprovar e baixar. Filtre por formato ou só aprovadas.</p>
        </div>
      </header>
      <Galeria />
    </div>
  )
}
