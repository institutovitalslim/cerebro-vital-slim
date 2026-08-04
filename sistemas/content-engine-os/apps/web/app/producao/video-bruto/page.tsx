import { VideoBruto } from '../../components/video-bruto'

export default function VideoBrutoPage() {
  return (
    <div>
      <header className="pageHeader">
        <p className="eyebrow">Produção · Vídeo</p>
        <h2 className="pageTitle">Vídeo bruto → Reel pronto</h2>
        <p className="muted">
          Envie a gravação crua da Dra e o sistema monta o reel inteiro: cortes e sincronização, legenda cinética,
          b-roll compliant (com gate de compliance), intro de gancho, transições e efeitos sonoros — em 9:16.
        </p>
      </header>
      <VideoBruto />
    </div>
  )
}
