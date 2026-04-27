#!/usr/bin/env python3
"""
Busca respostas de questionários para um paciente específico.

Fontes (em ordem de prioridade):
  1. Portal IVS (/root/ivs-preconsulta-data/*.json) — pré-consulta online
  2. Google Forms (pre-consulta + analise-hormonal)
  3. PDF de questionário na pasta do paciente no Google Drive

Uso:
    python3 buscar_questionarios.py "Nome do Paciente" [--sexo FEMININO|MASCULINO]

Saída: JSON com as respostas encontradas para cada formulário + status de PDF no Drive
"""

import sys
import json
import subprocess
import re
import os
import glob
import unicodedata

GOG_ACCOUNT = "institutovitalslim@gmail.com"
DRIVE_ACCOUNT = "medicalcontabilidade@gmail.com"
DRIVE_FOLDER_ID = "1dCDANfnUcTX-iRFCCNtipQ5a3NWzHzSL"
PORTAL_IVS_DIR = "/root/ivs-preconsulta-data"
FORMS = {
    "pre-consulta": "1j8h3FUn4riAqSPJoWsRv1Ura_PPcFx4SDG7kafVcX1g",
    "analise-hormonal": "1XGIH3MiwVkHWI5FaH9hjsmByMTAS-Td_H2_rm7T7T0s",
}

# Mapeamento de campos técnicos -> rótulos legíveis para o portal IVS
PORTAL_LABELS = {
    "nome": "Nome",
    "email": "E-mail",
    "telefone": "Telefone",
    "dataNascimento": "Data de Nascimento",
    "sexo": "Sexo",
    "comoConheceu": "Como nos conheceu",
    "medicamentosAtuais": "Medicamentos Atuais",
    "cirurgias": "Cirurgias",
    "doencasCronicas": "Doenças Crônicas",
    "reposicaoHormonal": "Reposição Hormonal",
    "historicoFamiliarCancer": "Histórico Familiar de Câncer",
    "alergiasIntolerâncias": "Alergias / Intolerâncias",
    "habitoFumar": "Hábito de Fumar",
    "consumoAlcool": "Consumo de Álcool",
    "altura": "Altura (cm)",
    "pesoAtual": "Peso Atual (kg)",
    "pesoMaximoAnterior": "Peso Máximo Anterior (kg)",
    "pesoIdeal": "Peso Ideal (kg)",
    "frequenciaAtividade": "Frequência de Atividade Física",
    "atividadeFisica": "Tipo de Atividade Física",
    "frequenciaIntestinal": "Frequência Intestinal",
    "consumoAgua": "Consumo de Água",
    "profissao": "Profissão",
    "vinculoEmpregaticio": "Vínculo Empregatício",
    "investeSaude": "Investe em Saúde",
    "barreiraSaude": "Barreira para Cuidar da Saúde",
    "planoSaude": "Plano de Saúde",
    "tipoTrabalho": "Tipo de Trabalho",
    "horariosTrabalho": "Horários de Trabalho",
    "nivelEnergia": "Nível de Energia (1-10)",
    "qualidadeSono": "Qualidade do Sono (1-10)",
    "horasSono": "Horas de Sono",
    "cansacoDurante": "Cansaço Durante o Dia",
    "consumoDoces": "Consumo de Doces",
    "refeicoesDia": "Refeições por Dia",
    "localRefeicoes": "Local das Refeições",
    "formaAdocar": "Forma de Adoçar",
    "alimentosNaoGosta": "Alimentos que Não Gosta",
    "alimentosGosta": "Alimentos que Gosta",
    "alimentacaoFimSemana": "Alimentação no Fim de Semana",
    "cafeDaManha": "Café da Manhã",
    "lancheManha": "Lanche da Manhã",
    "almoco": "Almoço",
    "lancheTarde": "Lanche da Tarde",
    "jantar": "Jantar",
    "prefernciaPlano": "Preferência de Plano Alimentar",
    "spin_s_tempoLuta": "SPIN — Há quanto tempo luta com o peso?",
    "spin_s_tentativas": "SPIN — O que já tentou?",
    "spin_p_principalIncomodo": "SPIN — Principal incômodo hoje",
    "spin_p_desafios": "SPIN — Principais desafios",
    "spin_i_impactoVida": "SPIN — Impacto na vida",
    "spin_i_cenario1ano": "SPIN — Cenário sem tratamento em 1 ano",
    "spin_i_investimentoPerdido": "SPIN — Investimento já perdido",
    "spin_i_oportunidadesPerdidas": "SPIN — Oportunidades perdidas",
    "spin_n_vidaResolvida": "SPIN — Vida resolvida seria...",
    "spin_n_interessePrograma": "SPIN — Interesse no programa",
    "ciclomenstrual": "Ciclo Menstrual",
    "sintomasCiclo": "Sintomas do Ciclo",
    "metodoContraceptivo": "Método Contraceptivo",
    "menopausa": "Menopausa",
    "libido": "Libido",
    "ressecamentoVaginal": "Ressecamento Vaginal",
    "dispareunia": "Dispareunia",
    "quedaCabelo": "Queda de Cabelo",
    "condicaoPele": "Condição da Pele",
    "alteracoesUnhas": "Alterações nas Unhas",
    "acordarDisposicao": "Acorda Disposto(a)?",
    "sensacaoFimDia": "Sensação no Fim do Dia",
    "disc": "Perfil DISC (detalhado)",
    "discPerfil": "Perfil DISC",
    "tresObjetivos": "3 Objetivos Principais",
    "tresMudancas": "3 Mudanças que Deseja",
    "interesseAcompanhamento": "Interesse em Acompanhamento",
    "observacoes": "Observações Livres",
    "perfilFinanceiro": "Perfil Financeiro",
    "submittedAt": "Data de Envio",
}


# ---------------------------------------------------------------------------
# Portal IVS
# ---------------------------------------------------------------------------

def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn')


def normalizar_palavras(texto):
    """Retorna conjunto de palavras normalizadas (upper sem acentos, min 3 chars)."""
    texto_norm = strip_accents(texto.upper())
    return {p for p in re.split(r'[^A-Z0-9]+', texto_norm) if len(p) >= 3}


def buscar_portal_ivs(nome_paciente):
    """
    Escaneia PORTAL_IVS_DIR/*.json e retorna (data_dict, arquivo_path) do match
    mais recente com score >= 2 palavras em comum.
    Retorna (None, None) se não encontrar.
    """
    padrao = os.path.join(PORTAL_IVS_DIR, "*.json")
    arquivos = sorted(glob.glob(padrao), reverse=True)  # mais recente primeiro

    palavras_busca = normalizar_palavras(nome_paciente)
    nome_norm = strip_accents(nome_paciente.upper())

    melhor_data = None
    melhor_arquivo = None
    melhor_score = 0

    for arq in arquivos:
        try:
            with open(arq, encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue

        nome_portal = data.get("nome", "")
        if not nome_portal:
            continue

        # Match exato (sem acentos, case insensitive)
        if strip_accents(nome_portal.upper()) == nome_norm:
            return data, arq

        # Match por intersecao de palavras
        palavras_portal = normalizar_palavras(nome_portal)
        score = len(palavras_busca & palavras_portal)

        if score >= 2 and score > melhor_score:
            melhor_score = score
            melhor_data = data
            melhor_arquivo = arq

    return melhor_data, melhor_arquivo


def formatar_portal_como_questionario(data):
    """Converte o dict do portal IVS em dict legível com rótulos em português."""
    resultado = {}
    for chave, valor in data.items():
        if valor is None or valor == "":
            continue
        rotulo = PORTAL_LABELS.get(chave, chave)
        resultado[rotulo] = valor
    return resultado


# ---------------------------------------------------------------------------
# Google Forms
# ---------------------------------------------------------------------------

def gog_forms_get(form_id):
    """Obtém a estrutura do formulário."""
    cmd = ["/usr/local/bin/gog", "forms", "get", form_id, "--json", "--results-only"]
    env = {"GOG_ACCOUNT": GOG_ACCOUNT, "HOME": "/root", "GOG_KEYRING_PASSWORD": "Tf100314@!"}
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        print(f"ERRO gog forms get: {result.stderr}", file=sys.stderr)
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def gog_forms_responses(form_id, page_token=None, max_per_page=200):
    """Lista respostas do formulário."""
    cmd = ["/usr/local/bin/gog", "forms", "responses", "list", form_id,
           "--json", "--results-only", f"--max={max_per_page}"]
    if page_token:
        cmd.append(f"--page={page_token}")

    env = {"GOG_ACCOUNT": GOG_ACCOUNT, "HOME": "/root", "GOG_KEYRING_PASSWORD": "Tf100314@!"}
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        print(f"ERRO gog forms responses: {result.stderr}", file=sys.stderr)
        return []
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return []


def gog_forms_responses_all(form_id, max_per_page=200):
    """Busca TODAS as respostas do formulário (paginando automaticamente)."""
    all_responses = []
    page_token = None
    page_count = 0
    max_pages = 50

    while page_count < max_pages:
        data = gog_forms_responses(form_id, page_token, max_per_page)

        if isinstance(data, dict):
            responses = data.get("responses", [])
            page_token = data.get("nextPageToken")
        elif isinstance(data, list):
            responses = data
            page_token = None
        else:
            break

        all_responses.extend(responses)
        page_count += 1

        if not page_token:
            break

    if page_count >= max_pages:
        print(f"AVISO: limite de {max_pages} páginas atingido.", file=sys.stderr)

    print(f"Total de respostas: {len(all_responses)} ({page_count} página(s))", file=sys.stderr)
    return all_responses


def encontrar_resposta_paciente(responses, nome_paciente):
    """Encontra a resposta que corresponde ao paciente no Google Forms."""
    nome_norm = re.sub(r'[^a-zA-Z0-9]', '', nome_paciente).upper()
    palavras_nome = {p for p in re.split(r'[^A-Z0-9]+', nome_paciente.upper()) if len(p) > 2}

    melhor_match = None
    melhor_score = 0

    for resp in responses:
        answers = resp.get("answers", {})

        for qid, ans in answers.items():
            val = ans.get("textAnswers", {}).get("answers", [{}])[0].get("value", "")
            val_norm = re.sub(r'[^a-zA-Z0-9]', '', val).upper()

            if nome_norm == val_norm:
                return resp

            palavras_val = {p for p in re.split(r'[^A-Z0-9]+', val.upper()) if len(p) > 2}
            comuns = palavras_nome & palavras_val
            score = len(comuns)

            if score > melhor_score:
                melhor_score = score
                melhor_match = resp

    if melhor_match and melhor_score >= 2:
        return melhor_match

    return None


def formatar_resposta_forms(resposta, form_structure):
    """Formata a resposta do Google Forms em dict legível."""
    if not resposta:
        return None

    items = form_structure.get("items", [])
    question_map = {}
    for item in items:
        qid = item.get("questionItem", {}).get("question", {}).get("questionId", "")
        title = item.get("title", "")
        if qid:
            question_map[qid] = title

    answers = resposta.get("answers", {})
    result = {}

    for qid, answer_data in answers.items():
        pergunta = question_map.get(qid, qid)
        valores = answer_data.get("textAnswers", {}).get("answers", [])
        valor = ", ".join([v.get("value", "") for v in valores])
        result[pergunta] = valor

    return result


# ---------------------------------------------------------------------------
# Google Drive (PDF fallback)
# ---------------------------------------------------------------------------

def gog_drive_search(query, max_results=50):
    """Executa busca no Google Drive."""
    cmd = [
        "/usr/local/bin/gog", "drive", "search", query,
        "--max", str(max_results),
        "--json"
    ]
    env = {"GOG_ACCOUNT": DRIVE_ACCOUNT, "HOME": "/root", "GOG_KEYRING_PASSWORD": "Tf100314@!"}
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        print(f"ERRO gog drive: {result.stderr}", file=sys.stderr)
        return []
    try:
        data = json.loads(result.stdout)
        return data.get("files", [])
    except json.JSONDecodeError:
        return []


def encontrar_pasta_paciente_drive(nome_paciente):
    """Encontra a pasta do paciente no Drive."""
    query = f"'{DRIVE_FOLDER_ID}' in parents and mimeType = 'application/vnd.google-apps.folder'"
    pastas = gog_drive_search(query, max_results=100)

    nome_norm = re.sub(r'[^a-zA-Z0-9]', '', nome_paciente).upper()

    for pasta in pastas:
        pasta_nome = pasta.get("name", "").upper()
        pasta_nome_norm = re.sub(r'[^a-zA-Z0-9]', '', pasta_nome)

        if nome_norm == pasta_nome_norm:
            return pasta

        # Match por palavras (threshold >= 2 para suportar nomes curtos)
        palavras_nome = {p for p in re.split(r'[^A-Z0-9]+', nome_paciente.upper()) if len(p) > 2}
        palavras_pasta = {p for p in re.split(r'[^A-Z0-9]+', pasta_nome) if len(p) > 2}
        palavras_comuns = palavras_nome & palavras_pasta

        if len(palavras_comuns) >= 2:
            return pasta

    return None


def verificar_questionario_pdf_na_pasta(pasta_id):
    """Verifica se há PDF com 'questionário' na pasta do paciente."""
    query = f"'{pasta_id}' in parents and mimeType = 'application/pdf'"
    arquivos = gog_drive_search(query, max_results=50)

    for arq in arquivos:
        nome = arq.get("name", "").lower()
        if ("questionario" in nome or "questionário" in nome
                or "pre-consulta" in nome or "pre consulta" in nome):
            return {
                "encontrado": True,
                "arquivo": arq.get("name", ""),
                "id": arq.get("id", ""),
                "link": f"https://drive.google.com/file/d/{arq.get('id', '')}/view"
            }

    return {"encontrado": False}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 buscar_questionarios.py 'Nome do Paciente' [--sexo FEMININO|MASCULINO]")
        sys.exit(1)

    nome_paciente = sys.argv[1]
    sexo = None
    if "--sexo" in sys.argv:
        idx = sys.argv.index("--sexo")
        if idx + 1 < len(sys.argv):
            sexo = sys.argv[idx + 1].upper()

    resultados = {}

    # ── Source 1: Portal IVS ──────────────────────────────────────────────────
    print(f"[Portal IVS] Buscando '{nome_paciente}'...", file=sys.stderr)
    portal_data, portal_arquivo = buscar_portal_ivs(nome_paciente)

    if portal_data:
        print(f"[Portal IVS] Encontrado: {portal_arquivo}", file=sys.stderr)
        # Inferir sexo do portal se não passado como argumento
        if not sexo:
            sexo_portal = portal_data.get("sexo", "").upper()
            if sexo_portal in ("FEMININO", "MASCULINO"):
                sexo = sexo_portal
                print(f"[Portal IVS] Sexo inferido: {sexo}", file=sys.stderr)

        resultados["portal-ivs"] = {
            "encontrado": True,
            "arquivo": portal_arquivo,
            "respostas": formatar_portal_como_questionario(portal_data),
        }
    else:
        print("[Portal IVS] Não encontrado.", file=sys.stderr)
        resultados["portal-ivs"] = {"encontrado": False}

    # ── Source 2: Google Forms (pré-consulta) ─────────────────────────────────
    print("[Google Forms] Buscando pré-consulta...", file=sys.stderr)
    form_id = FORMS["pre-consulta"]
    form_structure = gog_forms_get(form_id)
    responses = gog_forms_responses_all(form_id)

    resposta_forms = None
    if responses:
        resposta_forms = encontrar_resposta_paciente(responses, nome_paciente)

    # Source 3: PDF no Drive
    pasta_paciente = encontrar_pasta_paciente_drive(nome_paciente)
    pdf_questionario = {"encontrado": False}
    if pasta_paciente:
        pdf_questionario = verificar_questionario_pdf_na_pasta(pasta_paciente["id"])

    # Consolida pre-consulta com a melhor fonte disponível.
    # "dados" = dict raw camelCase que gerar_apresentacao.py consome diretamente.
    # Prioridade: portal_ivs > forms > pdf_drive
    if portal_data:
        # Portal IVS contém os mesmos dados da pré-consulta — usa como fonte primária.
        fonte_pre = "portal_ivs"
        dados_pre = portal_data          # raw camelCase (altura, pesoAtual, spin_* etc.)
        encontrado_pre = True
    elif resposta_forms is not None:
        fonte_pre = "forms"
        dados_pre = {}                   # Forms usa texto de pergunta como chave; sem mapeamento reverso
        encontrado_pre = True
    elif pdf_questionario["encontrado"]:
        fonte_pre = "pdf_drive"
        dados_pre = {}
        encontrado_pre = True
    else:
        fonte_pre = None
        dados_pre = {}
        encontrado_pre = False

    resultados["pre-consulta"] = {
        "encontrado": encontrado_pre,
        "fonte": fonte_pre,
        "dados": dados_pre,
        "respostas": formatar_resposta_forms(resposta_forms, form_structure) if resposta_forms else None,
        "pdf_drive": pdf_questionario if pdf_questionario["encontrado"] else None,
    }

    # ── Source 2b: Google Forms (análise hormonal — apenas mulheres) ──────────
    if sexo == "FEMININO":
        print("[Google Forms] Buscando análise hormonal...", file=sys.stderr)
        form_id = FORMS["analise-hormonal"]
        form_structure = gog_forms_get(form_id)
        responses = gog_forms_responses_all(form_id)

        resposta_forms = None
        if responses:
            resposta_forms = encontrar_resposta_paciente(responses, nome_paciente)

        encontrado = resposta_forms is not None

        resultados["analise-hormonal"] = {
            "encontrado": encontrado,
            "fonte": "forms" if resposta_forms else None,
            "respostas": formatar_resposta_forms(resposta_forms, form_structure) if resposta_forms else None,
        }

    print(json.dumps(resultados, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
