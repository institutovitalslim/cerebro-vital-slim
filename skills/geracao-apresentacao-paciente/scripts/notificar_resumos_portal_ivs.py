#!/usr/bin/env python3
"""
Notifica resumos de pré-consulta do Portal IVS para o Telegram.

Varre /root/ivs-preconsulta-data/, monta resumo e envia ao grupo AI Vital Slim.
Controle de idempotência em state/notified_portal_submissions.json

Uso:
    python3 notificar_resumos_portal_ivs.py                    # modo normal (cron)
    python3 notificar_resumos_portal_ivs.py --force-file FILE  # reenviar arquivo específico
"""

import os
import sys
import json
import glob
import requests
from datetime import datetime

# Config
DATA_DIR = "/root/ivs-preconsulta-data"
STATE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "state")
STATE_FILE = os.path.join(STATE_DIR, "notified_portal_submissions.json")
LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs", "portal-ivs-notify.log")

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
# Grupo AI Vital Slim, tópico 271 (pré-consulta)
CHAT_ID = "-1003803476669"
TOPIC_ID = 271

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_state(state):
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def send_telegram_message(text):
    if not TELEGRAM_BOT_TOKEN:
        log("ERRO: TELEGRAM_BOT_TOKEN não configurado")
        return False
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "message_thread_id": TOPIC_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        r = requests.post(url, json=payload, timeout=30)
        data = r.json()
        if data.get("ok"):
            log("OK: mensagem enviada ao Telegram")
            return True
        else:
            log(f"ERRO Telegram: {data}")
            return False
    except Exception as e:
        log(f"ERRO ao enviar: {e}")
        return False

def montar_resumo(data):
    nome = data.get("nome", "N/A")
    email = data.get("email", "N/A")
    tel = data.get("telefone", "N/A")
    nasc = data.get("dataNascimento", "N/A")
    peso = data.get("pesoAtual", "N/A")
    altura = data.get("altura", "N/A")
    peso_max = data.get("pesoMaximoAnterior", "N/A")
    peso_ideal = data.get("pesoIdeal", "N/A")
    atividade = data.get("atividadeFisica", "N/A")
    freq_ativ = data.get("frequenciaAtividade", "N/A")
    energia = data.get("nivelEnergia", "N/A")
    sono = data.get("qualidadeSono", "N/A")
    sono_h = data.get("horasSono", "N/A")
    obj = data.get("tresObjetivos", "N/A")
    perfil_fin = data.get("perfilFinanceiro", "N/A")
    investe = data.get("investeSaude", "N/A")
    reposicao = data.get("reposicaoHormonal", "Nenhuma")
    historicoc = data.get("historicoFamiliarCancer", "Nenhum")
    doencas = data.get("doencasCronicas", "Nenhuma")
    medicamentos = data.get("medicamentosAtuais", "Nenhum")
    cirurgias = data.get("cirurgias", "Nenhuma")
    barreira = data.get("barreiraSaude", "N/A")
    como = data.get("comoConheceu", "N/A")
    interesse = data.get("interesseAcompanhamento", "N/A")
    disc = data.get("discPerfil", "N/A")
    submitted = data.get("submittedAt", "N/A")
    plano = data.get("planoSaude", "N/A")

    texto = f"""<b>🩺 NOVO PRÉ-CONSULTA — Portal IVS</b>

<b>Paciente:</b> {nome}
<b>Nascimento:</b> {nasc}
<b>Contato:</b> {tel} | {email}
<b>Submetido em:</b> {submitted}

<b>📊 Perfil</b>
• Peso atual: {peso}kg | Altura: {altura}cm
• Peso máximo anterior: {peso_max}kg | Peso ideal: {peso_ideal}kg
• Perfil financeiro: {perfil_fin}
• Investe em saúde: {investe}
• Plano de saúde: {plano}

<b>🏥 Clínico</b>
• Doenças crônicas: {doencas}
• Medicamentos: {medicamentos}
• Cirurgias: {cirurgias}
• Reposição hormonal: {reposicao}
• Histórico familiar de câncer: {historicoc}

<b>💪 Estilo de Vida</b>
• Atividade física: {atividade} ({freq_ativ})
• Energia (1-10): {energia}
• Sono (1-10): {sono} ({sono_h}h)

<b>🎯 Objetivos</b>
• {obj}

<b>🧠 DISC:</b> {disc}
<b>🔍 Barreira:</b> {barreira}
<b>📢 Como conheceu:</b> {como}
<b>✅ Interesse no programa:</b> {interesse}
"""
    return texto

def processar_arquivo(filepath, state, force=False):
    filename = os.path.basename(filepath)
    file_id = filename

    if not force and file_id in state:
        return False, "já_notificado"

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        log(f"ERRO ao ler {filename}: {e}")
        return False, "erro_leitura"

    resumo = montar_resumo(data)
    ok = send_telegram_message(resumo)

    if ok:
        state[file_id] = {
            "notified_at": datetime.now().isoformat(),
            "paciente": data.get("nome", "N/A")
        }
        save_state(state)
        log(f"OK: resumo enviado para {data.get('nome', 'N/A')} ({filename})")
        return True, "enviado"
    else:
        log(f"FALHA: não consegui enviar resumo de {filename}")
        return False, "falha_envio"

def main():
    force_file = None
    if len(sys.argv) >= 3 and sys.argv[1] == "--force-file":
        force_file = sys.argv[2]

    state = load_state()
    enviados = 0

    if force_file:
        if os.path.exists(force_file):
            ok, status = processar_arquivo(force_file, state, force=True)
            if ok:
                enviados += 1
            log(f"Force-file: {force_file} -> {status}")
        else:
            log(f"ERRO: arquivo não encontrado: {force_file}")
            sys.exit(1)
    else:
        if not os.path.isdir(DATA_DIR):
            log(f"ERRO: diretório {DATA_DIR} não existe")
            sys.exit(1)

        arquivos = sorted(glob.glob(os.path.join(DATA_DIR, "*.json")))
        if not arquivos:
            log("Nenhum arquivo pendente encontrado.")
            sys.exit(0)

        for filepath in arquivos:
            ok, status = processar_arquivo(filepath, state)
            if ok:
                enviados += 1

    log(f"Resumo: {enviados} resumo(s) enviado(s).")
    print(f"OK: {enviados} resumo(s) enviado(s).")

if __name__ == "__main__":
    main()
