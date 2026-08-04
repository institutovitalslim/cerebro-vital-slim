import { cookies } from 'next/headers'

type ReuseMap = {
  core_theme: string
  angles: { label: string; thesis: string }[]
  hooks: string[]
  audiences: string[]
  repurposing: { format: string; goal: string; instruction: string }[]
}

export default async function EstrategiaPage() {
  const data: ReuseMap = await fetch('http://api:8010/strategy/reuse-map', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', cookie: cookies().toString() },
    body: JSON.stringify({
      tenant_slug: 'demo',
      core_theme: 'Emagrecimento com contexto clínico',
      core_promise: 'mais clareza para a paciente entender por que não consegue evoluir',
      audience_base: 'mulheres 35+ que não se reconhecem mais no espelho',
    }),
    cache: 'no-store',
  }).then((r) => r.json())

  return (
    <div>
      <header className="pageHeader">
        <p className="eyebrow">Estratégia</p>
        <h2 className="pageTitle">Mapa de reaproveitamento do conteúdo</h2>
        <p className="muted">Aqui o sistema começa a provar que um núcleo forte pode render muitos criativos com públicos, hooks e objetivos diferentes.</p>
      </header>

      <section className="grid" style={{ gridTemplateColumns: '1fr 1fr' }}>
        <article className="card">
          <h3>Ângulos sugeridos</h3>
          <div className="tableLike">
            {data.angles.map((item) => (
              <div className="row" key={item.label}>
                <div className="rowTop"><strong>{item.label}</strong><span className="badge">Ângulo</span></div>
                <span className="muted">{item.thesis}</span>
              </div>
            ))}
          </div>
        </article>
        <article className="card">
          <h3>Públicos derivados</h3>
          <div className="tableLike">
            {data.audiences.map((item) => (
              <div className="row" key={item}>
                <span className="muted">{item}</span>
              </div>
            ))}
          </div>
        </article>
      </section>

      <section className="section grid" style={{ gridTemplateColumns: '1fr 1fr' }}>
        <article className="card">
          <h3>Hooks</h3>
          <div className="tableLike">
            {data.hooks.map((item) => (
              <div className="row" key={item}>
                <span className="muted">{item}</span>
              </div>
            ))}
          </div>
        </article>
        <article className="card">
          <h3>Repurposing por formato</h3>
          <div className="tableLike">
            {data.repurposing.map((item) => (
              <div className="row" key={item.format}>
                <div className="rowTop"><strong>{item.format}</strong><span className="badge">{item.goal}</span></div>
                <span className="muted">{item.instruction}</span>
              </div>
            ))}
          </div>
        </article>
      </section>
    </div>
  )
}
