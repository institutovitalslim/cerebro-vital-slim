import { StrategyIntakeForm } from '../components/forms'

const steps = [
  {
    title: '1. Entenda a clínica em 3 minutos',
    text: 'Especialidade, cidade, principal oferta, perfil de paciente e nível de autoridade atual.',
  },
  {
    title: '2. Defina a dor central',
    text: 'O sistema começa pelo que o paciente sente, não pelo que a clínica quer falar.',
  },
  {
    title: '3. Escolha o objetivo do conteúdo',
    text: 'Atrair, educar, quebrar objeção, converter ou reaproveitar material antigo.',
  },
  {
    title: '4. Gere com reaproveitamento nativo',
    text: 'O mesmo núcleo pode render vários hooks, públicos e formatos.',
  },
]

export default function OnboardingPage() {
  return (
    <div>
      <header className="pageHeader">
        <p className="eyebrow">Onboarding</p>
        <h2 className="pageTitle">Entrada simples para médicos que não conseguem produzir conteúdo com consistência</h2>
        <p className="muted">
          A lógica do produto é guiar o médico com linguagem humana, poucas decisões por tela e muita direção prática.
        </p>
      </header>

      <section className="grid cards">
        {steps.map((step) => (
          <article key={step.title} className="card">
            <h3>{step.title}</h3>
            <p className="muted">{step.text}</p>
          </article>
        ))}
      </section>

      <section className="section grid" style={{ gridTemplateColumns: '1.1fr 0.9fr' }}>
        <StrategyIntakeForm />
        <article className="card">
          <h3>Resultado que o cliente precisa sentir</h3>
          <div className="tableLike">
            <div className="row"><span className="muted">“Agora eu sei o que postar sem depender de agência.”</span></div>
            <div className="row"><span className="muted">“Consigo reaproveitar minha consulta, meu vídeo e meu story em vários criativos.”</span></div>
            <div className="row"><span className="muted">“O sistema entende a dor do meu paciente e me ajuda a falar com clareza.”</span></div>
          </div>
        </article>
        <article className="card">
          <h3>Próximas telas premium</h3>
          <ul className="muted" style={{ paddingLeft: 18, marginBottom: 0 }}>
            <li>onboarding por especialidade</li>
            <li>upload e reaproveitamento de conteúdo bruto</li>
            <li>playbooks por persona</li>
            <li>fila de aprovação com prioridade</li>
          </ul>
        </article>
      </section>
    </div>
  )
}
