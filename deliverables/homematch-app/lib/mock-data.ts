export interface Property {
  id: string;
  title: string;
  location: string;
  neighborhood: string;
  price: string;
  score: number;
  type: string;
  beds: number;
  baths: number;
  area: number;
  image: string;
  gallery: string[];
  summary: string;
  highlight: string;
  tags: string[];
  matchReasons: string[];
  amenities: string[];
  detailSections: { title: string; content: string }[];
  marketSignals: { label: string; value: string }[];
  visitWindows: { day: string; time: string }[];
  nextActions: { label: string; href: string }[];
}

export const properties: Property[] = [
  {
    id: "aurora-park-101",
    title: "Aurora Park Residence",
    location: "São Paulo, SP",
    neighborhood: "Jardins",
    price: "R$ 2.450.000",
    score: 96,
    type: "Apartamento",
    beds: 3,
    baths: 2,
    area: 142,
    image: "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800&q=80",
    gallery: [
      "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800&q=80",
      "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800&q=80",
      "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=800&q=80",
    ],
    summary:
      "Apartamento de alto padrão no coração dos Jardins, com vista panorâmica e acabamentos premium.",
    highlight: "Varanda gourmet com vista para o Parque Trianon",
    tags: ["Alto padrão", "Vista livre", "Pet friendly"],
    matchReasons: [
      "Perfil compatível com sua busca por imóveis de luxo",
      "Localização próxima ao seu escritório",
      "Condomínio com estrutura completa para famílias",
    ],
    amenities: [
      "Piscina aquecida",
      "Academia",
      "Salão de festas",
      "Brinquedoteca",
      "Sauna",
      "Espaço gourmet",
    ],
    detailSections: [
      {
        title: "Descrição",
        content:
          "Apartamento com 142m² de área útil, 3 suítes, living integrado com varanda gourmet, cozinha com ilha e área de serviço completa. Acabamentos em mármore travertino e marcenaria sob medida.",
      },
      {
        title: "Condomínio",
        content:
          "Condomínio com lazer completo: piscina aquecida, academia equipada, salão de festas, brinquedoteca, sauna e espaço gourmet com churrasqueira.",
      },
    ],
    marketSignals: [
      { label: "Valor/m²", value: "R$ 17.253" },
      { label: "Appreciation", value: "+8,2% / ano" },
      { label: "Tempo médio", value: "45 dias" },
    ],
    visitWindows: [
      { day: "Segunda", time: "14:00 - 18:00" },
      { day: "Quarta", time: "09:00 - 12:00" },
      { day: "Sábado", time: "10:00 - 16:00" },
    ],
    nextActions: [
      { label: "Agendar visita", href: "/match/" },
      { label: "Fazer proposta", href: "/offer/" },
      { label: "Conversar com corretor", href: "/chat/" },
    ],
  },
  {
    id: "costa-mar-22",
    title: "Costa do Mar",
    location: "Rio de Janeiro, RJ",
    neighborhood: "Leblon",
    price: "R$ 3.890.000",
    score: 92,
    type: "Cobertura",
    beds: 4,
    baths: 3,
    area: 210,
    image: "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800&q=80",
    gallery: [
      "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800&q=80",
      "https://images.unsplash.com/photo-1600585154526-990dced4db0d?w=800&q=80",
      "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?w=800&q=80",
    ],
    summary:
      "Cobertura duplex no Leblon com piscina privativa e vista deslumbrante para o mar.",
    highlight: "Piscina privativa com vista 360° para o mar",
    tags: ["Cobertura", "Vista mar", "Duplex"],
    matchReasons: [
      "Vista para o mar conforme solicitado",
      "Espaço amplo para receber amigos e família",
      "Localização nobre do Leblon",
    ],
    amenities: [
      "Piscina privativa",
      "Terraço",
      "Elevador privativo",
      "Home office",
      "Depósito",
      "2 vagas",
    ],
    detailSections: [
      {
        title: "Descrição",
        content:
          "Cobertura duplex de 210m² com 4 quartos, sendo 3 suítes. Piso superior com piscina privativa e terraço de 80m². Elevador privativo e 2 vagas de garagem.",
      },
      {
        title: "Condomínio",
        content:
          "Condomínio com segurança 24h, portaria blindada, jardins paisagísticos e serviços de concierge.",
      },
    ],
    marketSignals: [
      { label: "Valor/m²", value: "R$ 18.524" },
      { label: "Appreciation", value: "+6,5% / ano" },
      { label: "Tempo médio", value: "62 dias" },
    ],
    visitWindows: [
      { day: "Terça", time: "10:00 - 16:00" },
      { day: "Quinta", time: "14:00 - 18:00" },
      { day: "Sábado", time: "09:00 - 17:00" },
    ],
    nextActions: [
      { label: "Agendar visita", href: "/match/" },
      { label: "Fazer proposta", href: "/offer/" },
      { label: "Conversar com corretor", href: "/chat/" },
    ],
  },
  {
    id: "verde-habitat-8",
    title: "Verde Habitat",
    location: "Curitiba, PR",
    neighborhood: "Batel",
    price: "R$ 1.890.000",
    score: 89,
    type: "Apartamento",
    beds: 3,
    baths: 2,
    area: 118,
    image: "https://images.unsplash.com/photo-1600585154363-67eb9e2e2099?w=800&q=80",
    gallery: [
      "https://images.unsplash.com/photo-1600585154363-67eb9e2e2099?w=800&q=80",
      "https://images.unsplash.com/photo-1600573472550-8090b5e0745e?w=800&q=80",
      "https://images.unsplash.com/photo-1600566752355-35792bedcfea?w=800&q=80",
    ],
    summary:
      "Apartamento sustentável no Batel com jardim vertical, energia solar e materiais eco-friendly.",
    highlight: "Jardim vertical privativo e energia solar",
    tags: ["Sustentável", "Jardim vertical", "Batel"],
    matchReasons: [
      "Projeto sustentável alinhado aos seus valores",
      "Bairro tranquilo e arborizado",
      "Ótimo custo-benefício para a região",
    ],
    amenities: [
      "Jardim vertical",
      "Energia solar",
      "Bike sharing",
      "Composteira",
      "Espaço coworking",
      "Jardim comunitário",
    ],
    detailSections: [
      {
        title: "Descrição",
        content:
          "Apartamento de 118m² com conceito sustentável, 3 quartos, jardim vertical privativo e sistema de energia solar. Materiais eco-friendly e reaproveitamento de água da chuva.",
      },
      {
        title: "Condomínio",
        content:
          "Condomínio sustentável com jardim comunitário, composteira coletiva, bike sharing, espaço coworking e gestão inteligente de resíduos.",
      },
    ],
    marketSignals: [
      { label: "Valor/m²", value: "R$ 16.017" },
      { label: "Appreciation", value: "+9,1% / ano" },
      { label: "Tempo médio", value: "38 dias" },
    ],
    visitWindows: [
      { day: "Segunda", time: "09:00 - 12:00" },
      { day: "Quarta", time: "14:00 - 18:00" },
      { day: "Sábado", time: "10:00 - 15:00" },
    ],
    nextActions: [
      { label: "Agendar visita", href: "/match/" },
      { label: "Fazer proposta", href: "/offer/" },
      { label: "Conversar com corretor", href: "/chat/" },
    ],
  },
];

export const getPropertyById = (id: string): Property | undefined =>
  properties.find((p) => p.id === id);
