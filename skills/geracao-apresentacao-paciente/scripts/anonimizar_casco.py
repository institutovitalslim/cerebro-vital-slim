#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Anonimiza o casco V12 (HTML aprovado) para virar asset de REFERENCIA VISUAL.

Politica: default-deny.
  - Todo conteudo dentro de container clinico vira placeholder, sem excecao.
  - Fora de container clinico, so sobrevive texto que EXISTE identico no render
    ficticio do V11 (ou seja: copy estatico vindo do codigo, nao do paciente).
  - Toda imagem base64 e removida.
  - Nome do paciente e substituido por placeholder em todo o documento.

Saida: assets/casco-v12.html
"""
import glob
import re
import sys
from bs4 import BeautifulSoup, NavigableString, Comment

CASCO = "/root/.hermes/profiles/ana/cache/documents/doc_2bbb3295b00f_apresentacao-greice-filippetto.html"
DEST = "/root/cerebro-vital-slim/skills/geracao-apresentacao-paciente/assets/casco-v12.html"

# Containers cujo conteudo e SEMPRE derivado do paciente -> redacao incondicional.
CLINICAL_IDS = {
    "hero", "executive-diagnosis", "patient-mirror", "bioimpedancia",
    "leitura-integrada", "decision-checklist", "final-cta",
    "technical-appendix", "questionnaire-appendix",
    "interpretacao-clinica", "cruzamento-q-e", "send-modal",
}
CLINICAL_CLASSES = {
    "hero-meta-bar", "hero-clinical-h1", "diag-card", "diag-grid", "diag-grid-2col",
    "mirror-grid", "mirror-card", "bio-card", "bio-grid", "bio-kpi", "bio-highlight",
    "bio-image-wrap", "exam-row", "exam-group", "exam-groups-v12", "exam-kpi",
    "exam-kpi-grid", "exam-count", "leitura-block", "tese-clinica", "context-list",
    "context-item", "compact-decision", "checklist-card", "checklist-item",
    "ex-card-v2", "ex-grid-v2", "hip-card", "hip-grid-list", "plano-bloco",
    "extra-bloco", "cta-card", "cta-frame", "cta-decision", "lever-card",
}


def static_vocab():
    """Vocabulario de copy estatico: text nodes do render V11 com fixture FICTICIA."""
    cands = sorted(glob.glob("/tmp/v12work/out/*-v11-*.html"))
    if not cands:
        sys.exit("ERRO: nenhum render ficticio V11 em /tmp/v12work/out — rode render_v11_fake.py antes")
    soup = BeautifulSoup(open(cands[-1], encoding="utf-8").read(), "html.parser")
    vocab = set()
    for s in soup.find_all(string=True):
        if s.parent.name in ("script", "style"):
            continue
        t = re.sub(r"\s+", " ", str(s)).strip()
        if t:
            vocab.add(t)
    return vocab


def in_clinical(node):
    p = node.parent
    while p is not None and getattr(p, "name", None):
        pid = p.get("id") if hasattr(p, "get") else None
        if pid and pid in CLINICAL_IDS:
            return True
        pcls = p.get("class") if hasattr(p, "get") else None
        if pcls and CLINICAL_CLASSES.intersection(pcls):
            return True
        p = p.parent
    return False


def main():
    raw = open(CASCO, encoding="utf-8").read()
    soup = BeautifulSoup(raw, "html.parser")
    vocab = static_vocab()

    # --- 1) nome do paciente: extrai do hero-meta-bar e monta lista de tokens ---
    nome_tokens = []
    for item in soup.select(".hero-meta-item"):
        strong = item.find("strong")
        if strong and item.get_text(strip=True).lower().startswith(("nome", "paciente")):
            nome_full = strong.get_text(strip=True)
            nome_tokens = [t for t in re.split(r"\s+", nome_full) if len(t) > 2]
            break

    # --- 2) imagens base64 fora ---
    n_img = 0
    for img in soup.find_all("img"):
        if img.get("src", "").startswith("data:"):
            img["src"] = "{{IMAGEM_REMOVIDA_NA_ANONIMIZACAO}}"
            n_img += 1
    for tag in soup.find_all(style=True):
        if "base64" in tag["style"]:
            tag["style"] = re.sub(r"url\([^)]*base64[^)]*\)", "url({{IMAGEM_REMOVIDA}})", tag["style"])

    # --- 3) atributos que carregam dado do paciente ---
    for inp in soup.find_all(["input", "textarea"]):
        if inp.get("value"):
            inp["value"] = "{{PACIENTE_TELEFONE}}"
        if inp.name == "textarea":
            inp.string = "{{MENSAGEM_WHATSAPP}}"
    if soup.title:
        soup.title.string = "{{PACIENTE_NOME}} · Apresentacao V12 · Instituto Vital Slim (REFERENCIA ANONIMIZADA)"
    for meta in soup.find_all("meta", attrs={"name": "description"}):
        meta["content"] = "Referencia visual anonimizada — sem dados de paciente."

    # --- 4) text nodes ---
    stats = {"mantido": 0, "redigido_clinico": 0, "redigido_naovocab": 0, "redigido_digito": 0}
    redigidos_amostra = []
    for s in list(soup.find_all(string=True)):
        if isinstance(s, Comment):
            s.extract()
            continue
        if s.parent.name in ("script", "style"):
            continue
        txt = str(s)
        norm = re.sub(r"\s+", " ", txt).strip()
        if not norm:
            continue
        if in_clinical(s):
            s.replace_with("{{CONTEUDO_CLINICO}}")
            stats["redigido_clinico"] += 1
            continue
        if re.search(r"\d", norm) and norm not in vocab:
            s.replace_with("{{VALOR}}")
            stats["redigido_digito"] += 1
            redigidos_amostra.append(norm[:60])
            continue
        if norm in vocab:
            stats["mantido"] += 1
            continue
        s.replace_with("{{TEXTO_NAO_ESTATICO}}")
        stats["redigido_naovocab"] += 1
        redigidos_amostra.append(norm[:60])

    out = str(soup)

    # --- 5) varredura final por tokens do nome (defesa em profundidade) ---
    for tok in nome_tokens:
        out = re.sub(r"(?i)\b" + re.escape(tok) + r"\b", "{{PACIENTE_NOME}}", out)

    header = (
        "<!--\n"
        "  casco-v12.html — REFERENCIA VISUAL ANONIMIZADA (CSS + estrutura DOM).\n"
        "\n"
        "  ORIGEM: HTML V12 aprovado clinicamente, exportado do cache efemero do profile\n"
        "  da agente Ana. Este arquivo versiona o PADRAO VISUAL, nao o conteudo.\n"
        "\n"
        "  NAO E FONTE DE CONTEUDO. Todo texto clinico, todo valor de exame, todo dado\n"
        "  identificavel e toda imagem (foto da Dra. e laudo de bioimpedancia) foram\n"
        "  removidos e trocados por placeholders:\n"
        "    {{PACIENTE_NOME}}                  nome do paciente\n"
        "    {{PACIENTE_TELEFONE}}              telefone no modal de envio\n"
        "    {{CONTEUDO_CLINICO}}               qualquer texto dentro de container clinico\n"
        "    {{VALOR}}                          qualquer texto numerico nao-estatico\n"
        "    {{TEXTO_NAO_ESTATICO}}             texto que nao veio do codigo do renderer\n"
        "    {{MENSAGEM_WHATSAPP}}              corpo da mensagem de envio\n"
        "    {{IMAGEM_REMOVIDA_NA_ANONIMIZACAO}} src de <img> (base64 apagado)\n"
        "\n"
        "  O QUE PERMANECE INTACTO E UTIL: o bloco <style> completo (design system,\n"
        "  tokens, grid, tipografia, media queries, patch V12 de isolamento de modos),\n"
        "  o bloco <script> e o esqueleto DOM com ids/classes na ordem canonica V12.\n"
        "\n"
        "  FONTE DE VERDADE EXECUTAVEL: scripts/gerar_apresentacao_v12.py\n"
        "  (render_apresentacao_v12). Este HTML serve para conferencia visual do delta,\n"
        "  nunca para copiar/colar conteudo de paciente.\n"
        "\n"
        "  Gerado por scripts/anonimizar_casco.py — politica default-deny.\n"
        "-->\n"
    )
    out = header + out

    open(DEST, "w", encoding="utf-8").write(out)

    print("ASSET GRAVADO:", DEST)
    print("tamanho:", len(out), "chars (casco original:", len(raw), ")")
    print("imagens base64 removidas:", n_img)
    print("tokens de nome neutralizados:", len(nome_tokens))
    print("text nodes:", stats)
    print("\n--- amostra do que foi redigido fora de container clinico (30) ---")
    for x in redigidos_amostra[:30]:
        print("   *", x)


if __name__ == "__main__":
    main()
