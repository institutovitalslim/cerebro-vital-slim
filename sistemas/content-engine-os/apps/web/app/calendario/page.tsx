import { fetchJson } from '../api'
import { CalendarBoard, CalendarEntry, STATUS_COPY } from '../components/calendar-board'
import { CalendarEntryForm } from '../components/forms'

export default async function CalendarioPage() {
  const data = await fetchJson<{ items: CalendarEntry[] }>('/calendar/entries?tenant_slug=demo')
  const items = data.items || []

  return (
    <div className="dashboardRoot">
      <header className="pageHeader heroHeader">
        <div>
          <p className="eyebrow">Motor A · etapa 8</p>
          <h2 className="pageTitle">Calendário & status</h2>
          <p className="muted">O calendário fecha o ciclo da máquina: peça aprovada vira compromisso editorial, publicação e aprendizado de performance.</p>
        </div>
      </header>

      <section className="splitSection">
        <CalendarEntryForm />
        <article className="featurePanel featurePanelDark">
          <span className="badge">Estados do fluxo</span>
          <div className="checkGrid">
            {Object.entries(STATUS_COPY).map(([key, label]) => (
              <div key={key} className="row">
                <div className="rowTop">
                  <strong>{key}</strong>
                  <span className="badge badgeDark">status</span>
                </div>
                <span className="muted small">{label}</span>
              </div>
            ))}
          </div>
        </article>
      </section>

      <CalendarBoard initialItems={items} />
    </div>
  )
}
