const SCREENS: Record<string, { nome: string; rota: string; desc: string }[]> = {
  'Início': [
    { nome: '🏠 Hoje', rota: '/hoje', desc: 'Sua página inicial. Mostra o que precisa da sua atenção agora: peças esperando revisão, métricas para registrar e o próximo passo do dia.' },
  ],
  'Acompanhar': [
    { nome: '🎯 Central de Tráfego', rota: '/trafego', desc: 'Anúncios do Meta e do Google em um só lugar: o que está rodando, o que precisa de ação e quanto custa cada conversa no WhatsApp.' },
    { nome: '📊 Instagram & funil', rota: '/business-intelligence', desc: 'O que o conteúdo está gerando: seguidores (ganho e perda por dia), performance por formato, leads e agendamentos. O Instagram da Dra é coletado todo dia, inclusive métricas privadas via conexão oficial com a Meta.' },
    { nome: '🤝 Pessoas & social selling', rota: '/social-selling', desc: 'Fila de pessoas que interagiram de verdade (comentários e marcações entram todo dia), com sugestão de abertura para abordagem manual. Nada dispara sozinho.' },
  ],
  'Criar': [
    { nome: '💡 Ideias do dia', rota: '/ideias', desc: 'Sugestões prontas de tema, montadas a partir dos seus números e das suas referências. Escolha uma e leve para o Estúdio.' },
    { nome: '🎬 Estúdio', rota: '/criar', desc: 'Onde o conteúdo nasce: carrossel, estático, reel e stories. Cada formato tem o próprio sprint semanal — escolha o pilar e gere 7 peças, uma por dia — ou gere uma peça avulsa.' },
    { nome: '🎥 Vídeo bruto → Reel', rota: '/producao/video-bruto', desc: 'Grave a Dra falando e suba o vídeo (9 por 16). O sistema monta o reel pronto: cortes, legenda, b-roll e intro. Leva de 20 a 40 minutos.' },
    { nome: '📱 Stories', rota: '/stories-engine', desc: 'Sequência de 10 a 12 stories conectados (texto, visual, sticker e DM esperada). Usa os b-rolls reais da biblioteca quando o tema tem clipes gravados.' },
  ],
  'Publicar': [
    { nome: '✅ Revisão & aprovação', rota: '/banco-criativos', desc: 'Tudo que foi gerado chega aqui. Revise, peça correção (por slide ou geral), aprove, baixe ou apague. Peça aprovada ganha o botão "Publicar no Instagram", com preview da legenda e confirmação.' },
    { nome: '📅 Calendário', rota: '/calendario', desc: 'Organize a semana, marque cada peça como publicada e registre as métricas. Registrar métrica é o que faz o sistema aprender.' },
    { nome: '📦 Campanhas Meta', rota: '/planejamento', desc: 'As peças aprovadas separadas entre anúncio e feed, prontas para montar campanha.' },
  ],
  'Aprender': [
    { nome: '📈 Aprendizado', rota: '/aprendizado', desc: 'Rankings do que venceu: formato, gancho, objeção, visual e CTA — com a próxima tese sugerida para a semana seguinte.' },
    { nome: '🏆 Campeões', rota: '/criativos-campeoes', desc: 'As peças com melhor resultado. Preencha os indicadores e receba um score com os pontos a melhorar.' },
  ],
  'Acervo': [
    { nome: '🗂 Biblioteca', rota: '/biblioteca', desc: 'Material bruto com tags: vídeos, imagens, PDFs e prints. Inclui as fotos reais da Dra (/biblioteca/dra) — com gate que bloqueia jaleco, seringa e ambiente clínico — e os b-rolls usados em reels e stories.' },
    { nome: '📜 Banco de roteiros', rota: '/banco-roteiros', desc: 'Repositório de roteiros virais com busca e filtro. Cole uma referência e receba três roteiros na voz da Dra.' },
    { nome: '🛰 Fontes & sinais', rota: '/fontes', desc: 'Perfis, canais e bases científicas que abastecem o sistema com ganchos, provas e respostas às objeções. Sem fontes, o conteúdo sai fraco.' },
    { nome: '🔭 Radar externo', rota: '/radar-externo', desc: 'O que está funcionando lá fora. O sistema entende o padrão por trás do conteúdo alheio e sugere adaptação original — nunca cópia.' },
  ],
  'Rodapé do menu': [
    { nome: '🛡 Compliance', rota: '/compliance', desc: 'Revisão de segurança antes de publicar. Afirmação de saúde precisa de fonte; promessa de resultado, diagnóstico ou prescrição são barrados.' },
    { nome: '❔ Ajuda', rota: '/ajuda', desc: 'Este guia.' },
  ],
}

export default function AjudaPage() {
  const grupos = Object.entries(SCREENS)
  const dicasNum = 4 + grupos.length

  return (
    <div className="section">
      <header className="pageHeader">
        <p className="eyebrow">Ajuda</p>
        <h2 className="pageTitle">Manual do Content Engine OS</h2>
        <p className="muted">Como usar o sistema, do login ao aprendizado — na ordem do menu.</p>
      </header>

      <div className="briefingBox">
        <p style={{ margin: 0 }}><strong>Regras de ouro:</strong> nada publica nem manda mensagem sozinho — toda peça passa pela sua aprovação; conteúdo de saúde passa pelo Compliance; as fotos da Dra são reais, com fundo escuro, sem jaleco e sem ambiente clínico.</p>
      </div>

      <h3 className="sectionTitle">1. Acesso</h3>
      <ol className="muted" style={{ lineHeight: 1.7 }}>
        <li>Abra o site e faça login com e-mail e senha.</li>
        <li>Trocar senha e sair: rodapé do menu. No celular, abra o menu primeiro.</li>
        <li>Se algo parecer desatualizado, recarregue com ctrl + shift + r.</li>
      </ol>

      <h3 className="sectionTitle">2. O fluxo do dia</h3>
      <p className="muted">O menu segue a ordem do trabalho, de cima para baixo:</p>
      <ol className="muted" style={{ lineHeight: 1.7 }}>
        <li><strong>Hoje:</strong> abra e veja o que pede sua atenção — revisões pendentes, métricas para registrar, próximo passo.</li>
        <li><strong>Ideias do dia:</strong> escolha um tema sugerido (ou traga o seu, pela experiência clínica).</li>
        <li><strong>Estúdio:</strong> gere a semana inteira do formato (7 peças, 1 por dia) ou uma peça avulsa. Vídeo gravado pela Dra entra por Vídeo bruto → Reel; stories têm motor próprio.</li>
        <li><strong>Revisão & aprovação:</strong> revise, corrija se preciso e aprove. Peça de saúde passa pelo Compliance. Aprovada, dá para publicar direto no Instagram.</li>
        <li><strong>Calendário:</strong> marque como publicada e depois registre as métricas de cada peça.</li>
        <li><strong>Aprendizado:</strong> veja o que venceu e comece a próxima rodada já sabendo o que funciona.</li>
      </ol>

      <div className="briefingBox" style={{ borderColor: 'rgba(212,168,60,.35)' }}>
        <p style={{ margin: 0 }}><strong>Dois modelos de carrossel:</strong> o <strong>viral</strong> (10 slides, fio contínuo com re-gancho no meio, virada, "faça hoje" e palavra-comentário no final) serve para alcance e identificação; o <strong>científico</strong> (capa com a Dra + slides em formato "tweet premium" + print real do estudo no PubMed com referência) serve para autoridade e prova. O Estúdio escolhe pelo objetivo, e você pode trocar o modelo no formulário.</p>
        <p style={{ margin: 0 }}><strong>Sprint semanal por formato:</strong> carrossel, estático e reel têm, cada um, o próprio sprint dentro do Estúdio. Você escolhe o pilar e o sistema gera <strong>7 peças, uma por dia (domingo a sábado)</strong>, cada uma com o próprio gancho. Leva alguns minutos e tudo cai na Revisão — nada publica sozinho.</p>
      </div>

      <h3 className="sectionTitle">3. Primeira vez (semana 0)</h3>
      <p className="muted">No começo, os números estão vazios — ainda não há peças medidas. Então não comece pelos rankings:</p>
      <ol className="muted" style={{ lineHeight: 1.7 }}>
        <li><strong>Monte a base (uma vez só):</strong> cadastre de três a cinco referências em Fontes & sinais, suba as fotos reais da Dra na Biblioteca e grave alguns b-rolls.</li>
        <li><strong>Escolha o primeiro tema pela experiência:</strong> a dor mais comum das pacientes 40+ — "faço tudo e não emagreço", sono e cortisol, tireoide.</li>
        <li><strong>Produza, aprove e publique</strong> a primeira semana pelo Estúdio e pela Revisão.</li>
        <li><strong>Registre as métricas no Calendário.</strong> É esse registro que liga o Aprendizado e as Ideias do dia.</li>
        <li><strong>Repita por uma a duas semanas</strong> — daí em diante o sistema passa a sugerir com base em dados reais.</li>
      </ol>

      {grupos.map(([grupo, itens], gi) => (
        <section key={grupo} style={{ marginTop: 8 }}>
          <h3 className="sectionTitle">{4 + gi}. Telas — {grupo.toLowerCase()}</h3>
          <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: 12 }}>
            {itens.map((s) => (
              <article key={s.rota} className="card" style={{ padding: '0.7rem 0.95rem', margin: 0 }}>
                <h4 style={{ margin: '0 0 4px' }}>{s.nome} <span className="badge" style={{ fontSize: '.62rem' }}>{s.rota}</span></h4>
                <p className="muted small" style={{ margin: 0, lineHeight: 1.45 }}>{s.desc}</p>
              </article>
            ))}
          </div>
        </section>
      ))}

      <h3 className="sectionTitle" style={{ marginTop: 16 }}>{dicasNum}. Dicas</h3>
      <ul className="muted" style={{ lineHeight: 1.7 }}>
        <li>Base boa, conteúdo bom: quanto melhores as fontes e os b-rolls, melhor o que o sistema gera.</li>
        <li>Depois da semana 0: olhe os números antes de criar, aprove antes de publicar, registre métrica depois de publicar.</li>
        <li>Carrossel aprofunda e gera autoridade; reel é alcance e retenção; stories é conexão e conversa no direct.</li>
        <li>O Instagram da Dra já é coletado todo dia — seguidores, curtidas e comentários entram sozinhos no painel.</li>
      </ul>

      <div className="briefingBox" style={{ borderColor: 'rgba(212,168,60,.35)' }}>
        <p style={{ margin: 0 }}><strong>Meta conectada (API oficial):</strong> as métricas privadas do Instagram entram todo dia — alcance, visitas ao perfil, salvamentos e compartilhamentos por publicação, retenção de reels e demografia das seguidoras. A mesma conexão alimenta a fila de Pessoas & social selling (quem comentou e em qual post), a Central de Tráfego (investimento e conversas de WhatsApp por campanha) e o botão "Publicar no Instagram" da Revisão. DMs na fila dependem de aprovação avançada da Meta — pendência registrada.</p>
      </div>
    </div>
  )
}
