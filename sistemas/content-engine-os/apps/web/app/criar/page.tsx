import Link from 'next/link'

const cards = [
  {
    href: '/producao/carrosseis',
    label: 'Carrosséis',
    title: 'Autoridade que a pessoa salva e compartilha',
    desc: 'Sequência lógica para educar, quebrar objeção, explicar mecanismo e levar para uma próxima ação.',
    bullets: ['educação', 'prova', 'objeção', 'salvamento'],
  },
  {
    href: '/producao/estaticos',
    label: 'Estáticos',
    title: 'Mensagem forte em uma peça premium',
    desc: 'Peça única para campanha, feed, anúncio ou posicionamento rápido com clareza visual.',
    bullets: ['impacto', 'anúncio', 'tese', 'presença'],
  },
  {
    href: '/producao/reels',
    label: 'Reels',
    title: 'Retenção, alcance e relacionamento em vídeo',
    desc: 'Roteiro e storyboard para vídeo curto com hook, ritmo, desenvolvimento e CTA seguro.',
    bullets: ['retenção', 'alcance', 'fala da Dra.', 'conversa'],
  },
  {
    href: '/stories-engine',
    label: 'Stories',
    title: 'Sequência diária conectada à Clara',
    desc: 'Stories já ficam em motor próprio: CTA, tracking, handoff Clara e aprendizado por sequência.',
    bullets: ['aquecimento', 'DM', 'WhatsApp', 'handoff'],
  },
]

export default function Page() {
  return (
    <div className="dashboardRoot">
      <header className="pageHeader heroHeader">
        <div>
          <p className="eyebrow">Produção</p>
          <h2 className="pageTitle">Escolha o tipo de conteúdo antes de criar</h2>
          <p className="heroText">A produção agora é separada por formato. O usuário entra já no modo certo: carrossel, estático, reel ou stories.</p>
        </div>
        <div className="heroActions">
          <Link className="secondaryLink" href="/business-intelligence">Ver BI antes de criar</Link>
          <Link className="secondaryLink" href="/banco-criativos">Aprovar fila</Link>
        </div>
      </header>

      <section className="flowRail">
        {cards.map((card) => (
          <Link className="flowCard" href={card.href} key={card.href}>
            <span className="badge badgeDark">{card.label}</span>
            <h3>{card.title}</h3>
            <p className="muted small">{card.desc}</p>
            <div className="checkGrid">
              {card.bullets.map((bullet) => <div className="checkRow" key={bullet}><span className="checkDot" />{bullet}</div>)}
            </div>
            <span className="secondaryLink">Abrir módulo →</span>
          </Link>
        ))}
      </section>
    </div>
  )
}
