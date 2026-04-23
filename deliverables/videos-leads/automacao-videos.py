#!/usr/bin/env python3
"""
Automacao de envio de videos para leads - Instituto Vital Slim

Como usar:
    python3 automacao-videos.py --mensagem "texto da conversa" --nome "Maria"

Retorna qual video enviar + sugestao de mensagem.
"""

import argparse
import json
import re

# Videos disponiveis (originais, sem renomear)
VIDEOS = {
    "primeira_consulta": {
        "arquivo": "/root/.openclaw/media/inbound/file_506---d9124a51-4880-4143-b536-866a2fbda5ab.mp4",
        "nome": "Primeira Consulta",
        "descricao": "Apresentacao da abordagem holistica da Vital Slim"
    },
    "bioimpedancia": {
        "arquivo": "/root/.openclaw/media/inbound/file_505---64879356-cf76-4a10-95e2-7bcc31b80b6c.mp4",
        "nome": "Exame de Bioimpedancia",
        "descricao": "Demonstracao do exame de composicao corporal"
    }
}

# Palavras-chave para cada fluxo
PALAVRAS_CHAVE = {
    "primeira_consulta": [
        # Lead novo, duvidas gerais
        "como funciona", "o que voces fazem", "quem e a dra", "como e a consulta",
        "o que inclui", "como e o tratamento", "o que voces tratam", "especialidade",
        "endocrino", "emagrecimento", "perder peso", "metabolismo", "hormonios",
        "primeira vez", "nunca fui", "quero conhecer", "quero saber mais",
        # Objeccao de valor
        "e caro", "qual o valor", "quanto custa", "preco", "investimento",
        "plano", "convenio", "cobertura", "e diferenete", "por que voces",
        # Comparacao
        "diferenca", "melhor", "outras clinicas", "ja tentei", "nao funcionou"
    ],
    "bioimpedancia": [
        # Exames especificos
        "exame", "avaliacao", "bioimpedancia", "composicao corporal",
        "gordura", "massa magra", "massa muscular", "hidratacao",
        "peso", "balanca", "medir", "analise", "resultados",
        "percentual", "gordura visceral", "metabolismo basal",
        # Antes da consulta
        "preciso fazer exame", "quais exames", "tenho exames", "trazer exames",
        # Durante agendamento
        "oque levar", "como me preparar", "orientacoes"
    ]
}

# Mensagens templates
MENSAGENS = {
    "primeira_consulta": """Oi {nome}! A Dra. Daniely faz uma consulta diferente porque olha para voce como um todo — energia, sono, metabolismo, hormonios. Nada de protocolo pronto. Cada paciente tem um plano unico.

Da uma olhada em como funciona:
[VIDEO: primeira-consulta-vsl.mp4]

Me conta: qual seu maior objetivo hoje?""",

    "bioimpedancia": """Oi {nome}! Durante a consulta faremos um exame de bioimpedancia — uma tecnologia avancada que mede gordura visceral, massa muscular, hidratacao celular e muito mais. Voce recebe os resultados em tempo real no celular e acompanha sua evolucao.

Da uma olhada no exame:
[VIDEO: exame-bioimpedancia.mp4]

Tem alguma duvida sobre o exame?""",

    "bioimpedancia_pre_consulta": """Ola {nome}! Sua consulta esta agendada. Vai ser um prazer te receber.

Durante a consulta faremos um exame de bioimpedancia — uma tecnologia avancada que mede gordura visceral, massa muscular, hidratacao celular e muito mais. Voce recebe os resultados em tempo real no celular e acompanha sua evolucao.

Da uma olhada no exame:
[VIDEO: exame-bioimpedancia.mp4]

Traga exames recentes se tiver. Ate la!"""
}


def detectar_fluxo(mensagem):
    """Detecta qual fluxo usar baseado na mensagem do lead."""
    texto = mensagem.lower()
    
    pontuacao = {
        "primeira_consulta": 0,
        "bioimpedancia": 0
    }
    
    # Contar matches
    for fluxo, palavras in PALAVRAS_CHAVE.items():
        for palavra in palavras:
            if palavra in texto:
                pontuacao[fluxo] += 1
    
    # Regras especificas
    if re.search(r'\bagend.+\b', texto) or re.search(r'\bconfirm.+\b', texto):
        pontuacao["bioimpedancia"] += 2  # Se agendou, enviar bioimpedancia
    
    if re.search(r'\bcaro\b|\bcusta\b|\bvalor\b|\bpreco\b|\binvestimento\b', texto):
        pontuacao["primeira_consulta"] += 3  # Objeccao de valor = mostrar diferencial
    
    # Determinar vencedor
    if pontuacao["bioimpedancia"] > pontuacao["primeira_consulta"]:
        return "bioimpedancia"
    elif pontuacao["primeira_consulta"] > 0:
        return "primeira_consulta"
    else:
        return None  # Nao detectou


def gerar_resposta(fluxo, nome=""):
    """Gera mensagem de resposta para o fluxo detectado."""
    if fluxo not in MENSAGENS:
        return None
    
    mensagem = MENSAGENS[fluxo].format(nome=nome or "")
    
    return {
        "fluxo": fluxo,
        "video": VIDEOS[fluxo]["arquivo"],
        "nome_video": VIDEOS[fluxo]["nome"],
        "mensagem": mensagem,
        "acao": "enviar_video"
    }


def analisar_conversa(mensagem, nome="", historico=None):
    """
    Analisa a conversa completa e decide se envia video.
    
    Args:
        mensagem: Ultima mensagem do lead
        nome: Nome do lead
        historico: Lista de mensagens anteriores (opcional)
    
    Returns:
        dict com decisao ou None
    """
    fluxo = detectar_fluxo(mensagem)
    
    if not fluxo:
        return {
            "acao": "aguardar",
            "motivo": "Nenhuma palavra-chave detectada",
            "sugestao": "Responder normalmente sem video"
        }
    
    # Verificar se ja enviou este video antes (se historico fornecido)
    if historico:
        video_ja_enviado = False
        for msg in historico:
            if VIDEOS[fluxo]["arquivo"] in str(msg):
                video_ja_enviado = True
                break
        
        if video_ja_enviado:
            return {
                "acao": "nao_enviar",
                "motivo": f"Video de {fluxo} ja foi enviado anteriormente",
                "sugestao": "Continuar conversa normalmente, sem reenviar"
            }
    
    return gerar_resposta(fluxo, nome)


def main():
    parser = argparse.ArgumentParser(description="Automacao de videos para leads")
    parser.add_argument("--mensagem", required=True, help="Texto da mensagem do lead")
    parser.add_argument("--nome", default="", help="Nome do lead")
    parser.add_argument("--json", action="store_true", help="Saida em JSON")
    args = parser.parse_args()
    
    resultado = analisar_conversa(args.mensagem, args.nome)
    
    if args.json:
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
    else:
        print("=" * 60)
        print(f"FLUXO: {resultado.get('fluxo', 'N/A')}")
        print(f"ACAO: {resultado['acao']}")
        print("=" * 60)
        if resultado['acao'] == 'enviar_video':
            print(f"\nVIDEO: {resultado['nome_video']}")
            print(f"ARQUIVO: {resultado['video']}")
            print(f"\nMENSAGEM SUGERIDA:\n{resultado['mensagem']}")
        else:
            print(f"\nMOTIVO: {resultado.get('motivo', '')}")
            print(f"SUGESTAO: {resultado.get('sugestao', '')}")


if __name__ == "__main__":
    main()
