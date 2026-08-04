"""stories_broll.py — Biblioteca de b-roll (fotos e vídeos curtos) da Dra p/ Stories.

A Dra grava/carrega fotos e vídeos "coringa" (evergreen) e específicos por tema; ficam
na biblioteca e são usados na geração dos stories. O endpoint /suggest usa o tema do
dia/semana p/ propor uma LISTA DE GRAVAÇÃO (o que gravar), marcando o que já existe.

Regras de marca (herdadas): sem jaleco, sem ambiente hospitalar/clínico, lifestyle
elegante, rosto fiel. Vídeos curtos 9:16.
"""
from __future__ import annotations

import io
import json
import re
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse

from app.services.codex_client import CodexClient
from app.services.upload_security import (
    MAX_BROLL_VIDEO_BYTES,
    MAX_IMAGE_BYTES,
    save_upload_limited,
)

router = APIRouter(prefix="/stories/broll", tags=["stories-broll"])

ROOT = Path("/root/cerebro-vital-slim/sistemas/content-engine-os/storage/assets/stories_broll")
META = ROOT / "library.json"
THUMBS = ROOT / ".thumbs"
IMG_EXT = {".png", ".jpg", ".jpeg", ".webp"}
VID_EXT = {".mp4", ".mov", ".webm", ".m4v"}

# Método B-roll 101 adaptado ao IVS: objeto → ação → plano → sequência.
# Conteúdo externo entra como hipótese operacional; não copiamos roteiro externo e mantemos compliance IVS.
BROLL_METHOD = {
    "etapas": [
        "Definir a função do b-roll: gancho, prova visual, mecanismo, emoção, transição ou CTA.",
        "Escolher uma ação-âncora que traduza o tema em movimento real — não uma cena bonita solta.",
        "Listar objetos físicos/visuais presentes no universo do tema.",
        "Para cada objeto, listar micro-ações de 5-15s com começo, pico e fim claros.",
        "Desenhar o plano antes de gravar: enquadramento, luz, direção do movimento, som ambiente e duração.",
        "Escolher movimento de câmera com intenção: aproximação, afastamento, lateral, tilt, orbit/parallax, reveal, follow ou estático de impacto.",
        "Aplicar o grid profissional de B-roll: separar b-roll sequencial e ilustrativo; usar eixo horizontal para progressão e eixo vertical para alinhar imagem à emoção/fala.",
        "Definir tratamento de edição: velocidade real, aceleração curta, corte no movimento, pausa rítmica ou sound design — sem depender de slow motion.",
        "Criar alças de transição: como o shot entra e como ele sai para conectar com o próximo corte.",
        "Montar sequências com cobertura mínima: establishing, detalhe da ação, textura/som, reação/autoridade e saída para CTA.",
        "Evitar imagem genérica: todo shot precisa ter função narrativa, emocional ou de prova do método.",
    ],
    "gramatica_visual": {
        "cobertura_minima": [
            "establishing do ambiente/luz",
            "mãos ou objeto iniciando a ação",
            "macro/textura do objeto em uso",
            "reação/rosto/autoridade calma",
            "plano de saída com movimento compatível com o próximo corte",
        ],
        "alcas_de_transicao": [
            "objeto entra ou sai cobrindo a lente",
            "movimento lateral que permite whip pan",
            "mão apoia/fecha/abre criando ponto de corte",
            "som ambiente vira ponte: água, página, caneta, passos, respiração",
            "match cut por forma, cor, direção ou gesto",
        ],
        "tratamentos_edicao": [
            "velocidade real com corte no pico da ação",
            "aceleração curta antes/depois do gesto principal",
            "pausa rítmica de 2-4 frames no momento de impacto/decisão",
            "sound hit ou som ambiente marcando o corte",
            "repetição rápida do gesto quando a ação for didática ou satisfatória",
            "evitar slow motion automático quando o shot pode ganhar força por ritmo, som e corte",
        ],
        "movimentos_camera": [
            "push-in para aproximar atenção e reforçar importância",
            "pull-out para revelar contexto ou fechar sequência",
            "slide lateral para criar parallax e transição por direção",
            "tilt up/down para revelar objeto, rosto ou texto",
            "orbit/arco curto para dar profundidade em objeto estático",
            "follow/acompanhar mãos quando a ação é o assunto",
            "reveal saindo de trás de objeto para abrir cena",
            "estático de impacto quando o som/gesto já carrega o corte",
        ],
        "pares_movimento_transicao": [
            "push-in → match cut ou corte no impacto",
            "pull-out → reveal de contexto ou hard cut para plano aberto",
            "slide lateral → whip pan ou corte por direção contínua",
            "tilt → corte por eixo vertical ou reveal de texto/rosto",
            "orbit/parallax → corte no ápice da profundidade",
            "objeto cobrindo lente → wipe natural",
            "mãos entram/saem do quadro → ponto de corte limpo",
        ],
        "broll_grid_profissional": {
            "tipos": [
                "sequencial: cadeia de shots que mostra processo, jornada ou progressão de ação",
                "ilustrativo: shot individual que traduz emoção, informação, local, objeto ou subtexto",
            ],
            "eixos": [
                "horizontal: progressão shot a shot no tempo, criando micro-história visual",
                "vertical: alinhamento do b-roll com palavra, emoção, pico tonal ou subtexto da fala",
            ],
            "criterios": [
                "não usar b-roll como papel de parede para esconder corte",
                "identificar picos emocionais, palavras-chave e mudanças de tom antes de escolher imagem",
                "cada imagem deve reforçar, contrastar ou revelar o que a fala quer fazer sentir",
                "um shot mostrado no momento certo ganha poder narrativo; escolher imagem é escolher importância",
            ],
        },
        "pergunta_de_grid": "Este b-roll está apenas decorando a timeline ou está estruturando progressão, emoção e subtexto?",
        "pergunta_de_qualidade": "Se eu desligar o áudio, este shot ainda ajuda a entender a ideia ou sentir a dor?",
        "pergunta_de_edicao": "Este shot precisa mesmo de slow motion ou fica mais forte com corte no movimento + som + ritmo?",
        "pergunta_de_movimento": "O movimento da câmera reforça a ação ou está competindo com ela?",
    },
    "guardrails": [
        "Sem jaleco, maca, hospital, ambiente clínico ou promessa de resultado.",
        "Priorizar lifestyle premium, rotina real, cuidado, método, acolhimento e autoridade calma.",
        "Usar objetos como prova visual do método, não como claim médico.",
        "Não mostrar dados de paciente em caderno, tablet, tela ou papéis.",
    ],
}

# Lista CORINGA (evergreen) — serve de baseline p/ o /suggest e de checklist de gravação.
CORINGA = {
    "fotos": [
        "Retrato acolhedor: sorriso, blazer, fundo neutro elegante (autoridade + conexão)",
        "Braços cruzados, olhar confiante (autoridade)",
        "Escrevendo/analisando em caderno ou tablet (método/estudo)",
        "Mãos segurando xícara de chá/café, sem rosto (rotina/aconchego)",
        "Caminhando ao ar livre, look esportivo elegante (vida ativa)",
        "Copo/jarra de água com limão, still life (hidratação)",
        "Prato colorido saudável montado, still life (alimentação real)",
        "Olhando pela janela, serena/pensativa (transição/emocional)",
        "Close do rosto, expressão empática (falas ao paciente)",
        "Sentada em poltrona conversando com a câmera (formato conversa)",
    ],
    "videos": [
        "'Oi' acolhedor + aceno (abertura de stories)",
        "Assentindo/ouvindo com empatia (reação/transição)",
        "Falando à câmera em tom de conversa (base p/ narração)",
        "B-roll: preparando copo de água/chá (transição de rotina)",
        "B-roll: caminhada ao ar livre (movimento)",
        "B-roll: escrevendo/analisando papel ou tablet (método)",
        "Riso natural (humaniza)",
        "Transição: virar/ajustar postura (corte dinâmico)",
        "Apontando pro lado (CTA 'arrasta')",
        "Respiração/calma em close (temas sono/estresse)",
    ],
}

CORINGA_OBJETOS = [
    {"objeto": "caderno ou tablet", "categoria": "método", "proposito_visual": "mostrar avaliação organizada sem expor dados sensíveis", "acoes": [
        {"acao": "abrir", "shot": "close da mão abrindo o caderno/tablet", "transicao": "match cut para fala da Dra"},
        {"acao": "marcar", "shot": "caneta sublinhando palavra neutra como rotina/sono", "transicao": "whip pan curto"},
        {"acao": "virar página", "shot": "plano detalhe da folha virando", "transicao": "page wipe natural"},
    ]},
    {"objeto": "xícara de chá/café ou copo d'água", "categoria": "rotina", "proposito_visual": "humanizar e criar pausa emocional", "acoes": [
        {"acao": "servir", "shot": "líquido entrando no copo em velocidade real com som marcando o corte", "transicao": "corte no som do líquido"},
        {"acao": "segurar", "shot": "mãos envolvendo a xícara, sem rosto", "transicao": "push-in suave"},
        {"acao": "apoiar na mesa", "shot": "xícara entrando no quadro e parando", "transicao": "impact cut no apoio"},
    ]},
    {"objeto": "janela/espelho/ambiente de casa", "categoria": "identificação", "proposito_visual": "representar a mulher que não se reconhece mais no espelho sem explorar sofrimento", "acoes": [
        {"acao": "olhar", "shot": "Dra de perfil olhando pela janela", "transicao": "fade curto para texto"},
        {"acao": "aproximar", "shot": "movimento lento até o reflexo, sem corpo exposto", "transicao": "rack focus"},
        {"acao": "respirar", "shot": "close calmo, expressão empática", "transicao": "corte por piscar"},
    ]},
]

SUGGEST_SYSTEM = (
    'Você é diretor de conteúdo do Instituto Vital Slim (Dra. Daniely Freitas, emagrecimento e saúde hormonal da mulher 40+). Dado um TEMA, proponha b-roll p/ Stories e Reels (9:16, 5-15s). Use lógica de filmagem + grid profissional de edição: 1) defina a função narrativa do b-roll; 2) escolha uma ação-âncora; 3) separe b-roll sequencial (processo/progressão) de b-roll ilustrativo (emoção/subtexto/local/objeto); 4) marque eixo horizontal quando a sequência mostrar progressão no tempo e eixo vertical quando a imagem alinhar com emoção, palavra-chave ou subtexto da fala; 5) liste objetos graváveis; 6) descreva micro-ações com começo/pico/fim; 7) desenhe enquadramento, luz, movimento, som e duração; 8) escolha movimento de câmera intencional e compatível com a transição; 9) defina tratamento de edição sem depender de slow motion; 10) crie alças de transição de entrada/saída; 11) monte sequências com establishing, detalhe, textura, reação e CTA. Regras de marca: SEM jaleco, SEM ambiente hospitalar/clínico, lifestyle elegante, rosto fiel, nada de promessa médica, nada de dados de paciente em telas/papéis. Cada shot deve ser concreto, gravável e ter função narrativa. Responda SOMENTE JSON no formato: {"fotos":[str], "videos":[str], "plano_broll":{"estrategia_edicao":{"tipo_broll":str,"eixo_horizontal":str,"eixo_vertical":str,"pico_emocional":str,"subtexto":str,"decisao_de_poder":str},"objetos":[{"objeto":str,"categoria":str,"proposito_visual":str,"acoes":[{"acao":str,"shot":str,"transicao":str,"som_ambiente":str}]}],"sequencias":[{"nome":str,"objetivo":str,"tipo_broll":str,"eixo_horizontal":str,"eixo_vertical":str,"shots":[{"ordem":int,"funcao_narrativa":str,"objeto":str,"acao":str,"enquadramento":str,"movimento_camera":str,"movimento_categoria":str,"duracao_s":str,"entrada_movimento":str,"saida_movimento":str,"continuidade_direcao":str,"transicao_camera":str,"transicao_para_proximo":str,"som_ambiente":str,"setup_luz":str,"tratamento_edicao":str,"ponto_de_corte":str,"alinhamento_emocional":str,"observacao":str}]}],"checklist":[str]}}. Gere 5 a 8 fotos, 5 a 8 vídeos, 4 a 6 objetos e 2 a 3 sequências.'
)


def _fallback_broll_plan(tema: str = "") -> dict:
    label = (tema or "tema do dia").strip()
    return {
        "metodo": BROLL_METHOD,
        "gramatica_visual": BROLL_METHOD.get("gramatica_visual", {}),
        "estrategia_edicao": {
            "tipo_broll": "misto: sequencial para progressão + ilustrativo para emoção/subtexto",
            "eixo_horizontal": "cadeia de ações visuais que mostra método/rotina evoluindo no tempo",
            "eixo_vertical": "shots posicionados para reforçar dor, alívio, autoridade ou clareza da fala",
            "pico_emocional": "momento em que a paciente percebe que não é falta de força de vontade",
            "subtexto": "há método e leitura individual por trás da transformação de rotina",
            "decisao_de_poder": "dar peso visual ao método e à emoção, não apenas cobrir cortes",
        },
        "objetos": CORINGA_OBJETOS,
        "sequencias": [
            {"nome": f"Sequência método visual — {label}", "objetivo": "cobrir explicação de mecanismo sem ficar só em talking head", "tipo_broll": "sequencial", "eixo_horizontal": "abrir método → marcar análise → autoridade calma", "eixo_vertical": "reforça a fala sobre método individual e quebra culpa", "shots": [
                {"ordem": 1, "objeto": "caderno ou tablet", "acao": "abrir", "enquadramento": "close 9:16 das mãos", "movimento_camera": "push-in curto", "movimento_categoria": "push-in", "continuidade_direcao": "aproximação frontal", "transicao_camera": "match cut por aproximação", "duracao_s": "3-4", "transicao_para_proximo": "match cut", "entrada_movimento": "mão entra abrindo", "saida_movimento": "página/caderno ocupa o quadro", "funcao_narrativa": "establishing de método", "alinhamento_emocional": "clareza e início de método", "som_ambiente": "página abrindo", "setup_luz": "luz lateral suave", "tratamento_edicao": "velocidade real com micro-aceleração na abertura", "ponto_de_corte": "quando a página/caderno ocupa o quadro", "observacao": "não mostrar dados de paciente"},
                {"ordem": 2, "objeto": "caderno ou tablet", "acao": "marcar", "enquadramento": "plano detalhe da caneta", "movimento_camera": "câmera fixa com ação entrando no quadro", "movimento_categoria": "estático de impacto", "continuidade_direcao": "mão/caneta entra e sai pelo mesmo eixo", "transicao_camera": "corte no gesto", "duracao_s": "3-5", "transicao_para_proximo": "corte no gesto", "entrada_movimento": "caneta entra pelo canto inferior", "saida_movimento": "caneta sai na direção do próximo corte", "funcao_narrativa": "prova visual de análise", "alinhamento_emocional": "prova de que existe leitura individual, não culpa", "som_ambiente": "risco da caneta", "setup_luz": "top light suave sem reflexo na tela", "tratamento_edicao": "corte seco no risco da caneta, sem slow motion", "ponto_de_corte": "no fim do sublinhado", "observacao": "palavras neutras: rotina, sono, fome, energia"},
                {"ordem": 3, "objeto": "rosto da Dra", "acao": "olhar para câmera", "enquadramento": "plano médio elegante", "movimento_camera": "estável", "movimento_categoria": "estático de autoridade", "continuidade_direcao": "olhar sobe e estabiliza", "transicao_camera": "hard cut ou pausa rítmica", "duracao_s": "5-8", "transicao_para_proximo": "hard cut para CTA", "entrada_movimento": "olhar sobe para a câmera", "saida_movimento": "leve inclinação para CTA", "funcao_narrativa": "autoridade calma", "alinhamento_emocional": "segurança e acolhimento no CTA", "som_ambiente": "sem som obrigatório", "setup_luz": "janela ou softbox frontal suave", "tratamento_edicao": "pausa rítmica curta antes do CTA", "ponto_de_corte": "quando o olhar estabiliza na câmera", "observacao": "fechar com acolhimento, sem promessa"},
            ]},
            {"nome": f"Sequência rotina premium — {label}", "objetivo": "dar textura de rotina real e reduzir sensação de anúncio genérico", "tipo_broll": "misto", "eixo_horizontal": "servir → contemplar → fechar", "eixo_vertical": "traduz acolhimento, rotina e fechamento emocional", "shots": [
                {"ordem": 1, "objeto": "xícara/copo", "acao": "servir", "enquadramento": "close lateral", "movimento_camera": "push-in leve", "movimento_categoria": "push-in", "continuidade_direcao": "aproximação para o objeto", "transicao_camera": "corte no impacto do apoio", "duracao_s": "3-4", "transicao_para_proximo": "corte pelo som", "entrada_movimento": "jarra/copo entra no quadro", "saida_movimento": "copo apoia e cria ponto de corte", "funcao_narrativa": "rotina tangível", "alinhamento_emocional": "cotidiano possível e não castigo", "som_ambiente": "água/objeto apoiando", "setup_luz": "luz natural lateral", "tratamento_edicao": "som do líquido/apoio como ponto de impacto, não slow motion obrigatório", "ponto_de_corte": "quando o copo encosta na mesa", "observacao": "usar luz natural"},
                {"ordem": 2, "objeto": "janela", "acao": "olhar", "enquadramento": "perfil da Dra", "movimento_camera": "pan muito suave", "movimento_categoria": "slide/pan lateral", "continuidade_direcao": "movimento lateral contínuo", "transicao_camera": "rack focus ou whip pan leve", "duracao_s": "4-6", "transicao_para_proximo": "rack focus", "entrada_movimento": "pan começa no ambiente e encontra a Dra", "saida_movimento": "rack focus para fundo neutro", "funcao_narrativa": "identificação emocional", "alinhamento_emocional": "sensação de não se reconhecer mais no espelho sem explorar sofrimento", "som_ambiente": "ambiente baixo", "setup_luz": "contraluz suave da janela", "tratamento_edicao": "pan em velocidade real + corte no final do rack focus", "ponto_de_corte": "quando o foco troca para a Dra ou fundo", "observacao": "tom sereno, sem dramatizar"},
                {"ordem": 3, "objeto": "caderno/tablet", "acao": "fechar", "enquadramento": "plano detalhe", "movimento_camera": "tilt curto", "movimento_categoria": "tilt", "continuidade_direcao": "eixo vertical curto", "transicao_camera": "wipe pelo fechamento do objeto", "duracao_s": "3-4", "transicao_para_proximo": "final", "entrada_movimento": "mão retorna ao caderno/tablet", "saida_movimento": "fechamento cobre parte do quadro", "funcao_narrativa": "fechamento de sequência", "alinhamento_emocional": "sensação de processo organizado e próximo passo", "som_ambiente": "caderno fechando/toque na mesa", "setup_luz": "mesma luz para continuidade", "tratamento_edicao": "caderno fechando como wipe/corte de saída", "ponto_de_corte": "no impacto do fechamento", "observacao": "encerra com sensação de método"},
            ]},
        ],
        "checklist": [
            "Gravar todos os clipes em 9:16, 5-15s, com luz natural ou softbox suave.",
            "Capturar som ambiente útil quando houver ação: água servindo, página virando, caneta marcando.",
            "Fazer 2 takes por ação: um close e um plano médio.",
            "Evitar jaleco, clínica, equipamento médico e qualquer dado sensível de paciente.",
        ],
    }


def _normalize_broll_plan(plan: dict | None, tema: str = "") -> dict:
    base = _fallback_broll_plan(tema)
    if not isinstance(plan, dict):
        return base
    return {
        "metodo": BROLL_METHOD,
        "gramatica_visual": BROLL_METHOD.get("gramatica_visual", {}),
        "estrategia_edicao": (plan.get("estrategia_edicao") if isinstance(plan.get("estrategia_edicao"), dict) else base.get("estrategia_edicao", {})),
        "objetos": (plan.get("objetos") if isinstance(plan.get("objetos"), list) else base["objetos"])[:8],
        "sequencias": (plan.get("sequencias") if isinstance(plan.get("sequencias"), list) else base["sequencias"])[:4],
        "checklist": [str(x) for x in (plan.get("checklist") if isinstance(plan.get("checklist"), list) else base["checklist"])[:8]],
    }


def _mark_object_plan(plan: dict, have_txt: str) -> dict:
    def exists_for(text: str) -> bool:
        kws = [w for w in re.findall(r"\w{4,}", (text or "").lower())][:4]
        return bool(kws) and any(k in have_txt for k in kws)
    out = dict(plan)
    objetos = []
    for obj in out.get("objetos") or []:
        if not isinstance(obj, dict):
            continue
        obj2 = dict(obj)
        action_text = " ".join(str(a.get("acao", "")) + " " + str(a.get("shot", "")) for a in obj2.get("acoes", []) if isinstance(a, dict))
        obj2["na_biblioteca"] = exists_for(f"{obj2.get('objeto', '')} {action_text}")
        objetos.append(obj2)
    out["objetos"] = objetos
    return out


def gerar_roteiro_filmagem_broll(tema: str = "", plan: dict | None = None) -> dict:
    """Gera objetos, ações e sequências de filmagem de b-roll para o Content OS."""
    plano = _normalize_broll_plan(plan, tema)
    objetos_acoes = []
    for obj in plano.get("objetos") or []:
        if isinstance(obj, dict):
            for ac in obj.get("acoes", []):
                if isinstance(ac, dict) and (ac.get("shot") or ac.get("acao")):
                    objetos_acoes.append(f"{obj.get('objeto', 'objeto')}: {ac.get('shot') or ac.get('acao')}")
    sequencias = []
    for seq in plano.get("sequencias") or []:
        if isinstance(seq, dict):
            for sh in seq.get("shots", [])[:4]:
                if isinstance(sh, dict):
                    sequencias.append(f"{seq.get('nome', 'Sequência')} [{seq.get('tipo_broll', 'b-roll')}; H: {seq.get('eixo_horizontal', '')}; V: {seq.get('eixo_vertical', '')}] — {sh.get('ordem', '')}. {sh.get('funcao_narrativa', 'shot')}: {sh.get('objeto', '')} / {sh.get('acao', '')} ({sh.get('enquadramento', '')}; emoção: {sh.get('alinhamento_emocional', '')}; movimento: {sh.get('movimento_categoria', sh.get('movimento_camera', ''))}; entra: {sh.get('entrada_movimento', '')}; sai: {sh.get('saida_movimento', '')}; edição: {sh.get('tratamento_edicao', '')}; corte: {sh.get('ponto_de_corte', '')})")
    return {"objetos_acoes": objetos_acoes[:10], "sequencias": sequencias[:10], "checklist": plano.get("checklist") or []}


create_broll_shooting_sequences = gerar_roteiro_filmagem_broll
BROLL_SHOOTING_METHOD = BROLL_METHOD
BROLL_OBJECT_BANK = CORINGA_OBJETOS

def _load() -> list[dict]:
    if not META.exists():
        return []
    try:
        return json.load(open(META, encoding="utf-8"))
    except Exception:
        return []


def _save(items: list[dict]) -> None:
    ROOT.mkdir(parents=True, exist_ok=True)
    json.dump(items, open(META, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def _safe(name: str) -> str:
    n = Path(name or "").name
    if not n or n.startswith("."):
        raise HTTPException(400, "nome inválido")
    return n


def _kind(ext: str) -> str | None:
    if ext in IMG_EXT:
        return "foto"
    if ext in VID_EXT:
        return "video"
    return None


@router.get("")
def list_broll(kind: str | None = None, q: str | None = None) -> dict:
    out = []
    for it in _load():
        f = it.get("file", "")
        if not (ROOT / f).exists():
            continue
        if kind and it.get("kind") != kind:
            continue
        if q and q.lower() not in (" ".join([it.get("tags", ""), it.get("theme", ""), f])).lower():
            continue
        out.append({**it, "url": f"/stories/broll/media/{f}",
                    "thumb": f"/stories/broll/thumb/{f}" if it.get("kind") == "foto" else None})
    return {"items": out, "total": len(out)}


@router.get("/media/{filename}")
def media(filename: str) -> FileResponse:
    p = ROOT / _safe(filename)
    if not p.exists():
        raise HTTPException(404, "não encontrado")
    return FileResponse(str(p))


@router.get("/thumb/{filename}")
def thumb(filename: str) -> FileResponse:
    name = _safe(filename)
    src = ROOT / name
    if not src.exists():
        raise HTTPException(404, "não encontrado")
    if Path(name).suffix.lower() not in IMG_EXT:
        raise HTTPException(415, "thumb só p/ foto")
    THUMBS.mkdir(parents=True, exist_ok=True)
    th = THUMBS / (name + ".jpg")
    if not th.exists() or th.stat().st_mtime < src.stat().st_mtime:
        try:
            from PIL import Image
            with Image.open(src) as im:
                im = im.convert("RGB")
                im.thumbnail((480, 720), Image.LANCZOS)
                im.save(th, format="JPEG", quality=82)
        except Exception:
            return FileResponse(str(src))
    return FileResponse(str(th), media_type="image/jpeg")


@router.post("/upload")
async def upload(file: UploadFile = File(...), tags: str = Form(""),
                 theme: str = Form(""), note: str = Form("")) -> JSONResponse:
    ext = Path(file.filename or "").suffix.lower()
    kind = _kind(ext)
    if not kind:
        raise HTTPException(400, f"formato {ext or '?'} não suportado (fotos png/jpg/webp; vídeos mp4/mov/webm)")
    ROOT.mkdir(parents=True, exist_ok=True)
    idx = len(_load()) + 1
    fname = f"broll-{idx:03d}-{uuid.uuid4().hex[:8]}{ext}"
    max_bytes = MAX_BROLL_VIDEO_BYTES if kind == "video" else MAX_IMAGE_BYTES
    await save_upload_limited(file, ROOT / fname, max_bytes=max_bytes)
    items = _load()
    items.append({
        "file": fname, "kind": kind,
        "tags": tags.strip(), "theme": theme.strip(), "note": note.strip(),
        "bytes": (ROOT / fname).stat().st_size,
        "source": "upload", "added_at": datetime.now(timezone.utc).isoformat(),
    })
    _save(items)
    return JSONResponse(status_code=200, content={"ok": True, "file": fname, "kind": kind})


@router.delete("/{filename}")
def delete(filename: str) -> dict:
    name = _safe(filename)
    (ROOT / name).unlink(missing_ok=True)
    (THUMBS / (name + ".jpg")).unlink(missing_ok=True)
    _save([it for it in _load() if it.get("file") != name])
    return {"ok": True, "file": name}


def match_broll(text: str, kind: str | None = None, limit: int = 6) -> list[dict]:
    """Rankeia assets da biblioteca por sobreposição de palavras (tags+theme+note) com o texto/tema.
    Usado na geração de Stories (handoff) e Reels (broll_pipeline) p/ usar footage REAL da Dra."""
    kws = set(re.findall(r"\w{4,}", (text or "").lower()))
    scored = []
    for it in _load():
        f = it.get("file", "")
        if not (ROOT / f).exists():
            continue
        if kind and it.get("kind") != kind:
            continue
        hay = (it.get("tags", "") + " " + it.get("theme", "") + " " + it.get("note", "")).lower()
        score = sum(1 for k in kws if k in hay)
        scored.append((score, it))
    scored.sort(key=lambda x: -x[0])
    return [{"file": it["file"], "kind": it["kind"], "theme": it.get("theme", ""),
             "tags": it.get("tags", ""), "score": s, "url": f"/stories/broll/media/{it['file']}"}
            for s, it in scored[:limit]]


@router.get("/match")
def match(text: str = "", kind: str | None = None, limit: int = 6) -> dict:
    """Clipes/fotos da biblioteca que melhor casam com um texto/tema (usar na geração)."""
    return {"items": match_broll(text, kind, limit), "text": text}


@router.get("/suggest")
async def suggest(tema: str = "") -> dict:
    """Lista de gravação p/ o tema (Codex) + baseline coringa; marca o que já existe na biblioteca."""
    have = _load()
    have_txt = " ".join((it.get("tags", "") + " " + it.get("theme", "") + " " + it.get("note", "")) for it in have).lower()
    tema_specific = {"fotos": [], "videos": []}
    plano_broll = _fallback_broll_plan(tema)
    if tema.strip():
        try:
            res = await CodexClient().generate_json(
                prompt=f"TEMA: {tema.strip()}", system=SUGGEST_SYSTEM, timeout=120)
            j = res.get("json") or {}
            if isinstance(j.get("fotos"), list):
                tema_specific["fotos"] = [str(x) for x in j["fotos"]][:8]
            if isinstance(j.get("videos"), list):
                tema_specific["videos"] = [str(x) for x in j["videos"]][:8]
            plano_broll = _normalize_broll_plan(j.get("plano_broll"), tema)
        except Exception:
            # fallback determinístico: mantém objetos → ações → sequências mesmo sem LLM.
            plano_broll = _fallback_broll_plan(tema)

    def _mark(lst: list[str]) -> list[dict]:
        out = []
        for s in lst:
            kws = [w for w in re.findall(r"\w{4,}", s.lower())][:3]
            exists = bool(kws) and any(k in have_txt for k in kws)
            out.append({"shot": s, "na_biblioteca": exists})
        return out

    return {
        "tema": tema,
        "coringa": {"fotos": _mark(CORINGA["fotos"]), "videos": _mark(CORINGA["videos"])},
        "do_tema": {"fotos": _mark(tema_specific["fotos"]), "videos": _mark(tema_specific["videos"])},
        "plano_broll": _mark_object_plan(plano_broll, have_txt),
        "roteiro_filmagem": gerar_roteiro_filmagem_broll(tema, plano_broll),
        "biblioteca_total": len(have),
    }
