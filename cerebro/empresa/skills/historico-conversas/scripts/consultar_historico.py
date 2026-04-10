#!/usr/bin/env python3
"""
consultar_historico.py — Consulta o historico de conversas de um lead/paciente
na planilha central do Instituto Vital Slim antes de atender.

Uso:
    python3 consultar_historico.py --telefone 5571986968887
    python3 consultar_historico.py --telefone 557192501702 --json
    python3 consultar_historico.py --telefone 557192501702 --apenas-status
"""

import argparse
import json
import os
import re
import subprocess
import sys

SPREADSHEET_ID = "1QXvRhElCx1t7mxMAwGkcvh5V7YyKLjP9zozSGH7LHnM"
ACCOUNT = "medicalemagrecimento@gmail.com"
RAW_SHEET = "Folha1"
PATIENTS_SHEET = "pacientes"
CONTEXT_SHEET = "contexto_paciente"


def setup_env():
    """Resolve GOG_KEYRING_PASSWORD from 1Password if not set."""
    if not os.environ.get("GOG_KEYRING_PASSWORD"):
        try:
            sa_env = "/root/.openclaw/.op.service-account.env"
            if os.path.isfile(sa_env):
                with open(sa_env) as f:
                    for line in f:
                        if line.startswith("OP_SERVICE_ACCOUNT_TOKEN="):
                            os.environ["OP_SERVICE_ACCOUNT_TOKEN"] = line.split("=", 1)[1].strip()
            result = subprocess.run(
                ["op", "item", "get", "gog-keyring-pass", "--vault", "openclaw",
                 "--fields", "password", "--reveal"],
                capture_output=True, text=True, timeout=15
            )
            if result.returncode == 0:
                os.environ["GOG_KEYRING_PASSWORD"] = result.stdout.strip()
        except Exception as e:
            print(f"[warn] could not get GOG_KEYRING_PASSWORD: {e}", file=sys.stderr)


def normalize_phone(phone: str) -> list:
    """Generate possible variants of a phone number for matching."""
    digits = re.sub(r"\D", "", phone)
    variants = {digits}
    # Remove leading 55 (Brazil country code)
    if digits.startswith("55") and len(digits) > 11:
        variants.add(digits[2:])
    # Add 55 if missing
    if not digits.startswith("55"):
        variants.add("55" + digits)
    # Remove area code 9 (old format)
    if len(digits) == 13 and digits[4] == "9":
        variants.add(digits[:4] + digits[5:])
    if len(digits) == 11 and digits[2] == "9":
        variants.add(digits[:2] + digits[3:])
    return list(variants)


def gog_get(sheet_range: str) -> list:
    """Get values from a sheet range via gog CLI."""
    cmd = ["gog", "sheets", "get", "-a", ACCOUNT, SPREADSHEET_ID, sheet_range, "-j"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            return {"error": r.stderr.strip()}
        data = json.loads(r.stdout) if r.stdout.strip() else {}
        return data.get("values", []) if isinstance(data, dict) else []
    except Exception as e:
        return {"error": str(e)}


def search_in_sheet(phone_variants: list, sheet_name: str) -> list:
    """Search for phone variants in a sheet. Returns matching rows."""
    data = gog_get(f"{sheet_name}!A:Z")
    if isinstance(data, dict) and "error" in data:
        return data
    if not data:
        return []

    header = data[0] if data else []
    matches = []
    for row in data[1:]:
        row_text = " ".join(str(cell) for cell in row)
        for v in phone_variants:
            if v and v in row_text:
                match = {}
                for i, cell in enumerate(row):
                    col = header[i] if i < len(header) else f"col{i}"
                    match[col] = cell
                matches.append(match)
                break
    return matches


def classify_lead(raw_matches: list, patient_matches: list) -> str:
    """Classify the lead based on matches found."""
    if patient_matches:
        return "paciente_ativo"
    if not raw_matches:
        return "lead_novo"
    if len(raw_matches) <= 2:
        return "lead_primeiro_contato"
    if len(raw_matches) <= 10:
        return "lead_em_qualificacao"
    return "lead_recorrente"


def main():
    parser = argparse.ArgumentParser(description="Consulta historico de conversas")
    parser.add_argument("--telefone", required=True, help="Numero de telefone do lead")
    parser.add_argument("--json", action="store_true", help="Saida em JSON")
    parser.add_argument("--apenas-status", action="store_true",
                        help="Apenas verificar se e paciente ativo")
    args = parser.parse_args()

    setup_env()

    phone_variants = normalize_phone(args.telefone)

    # Check if patient first
    patient_matches = search_in_sheet(phone_variants, PATIENTS_SHEET)
    if isinstance(patient_matches, dict) and "error" in patient_matches:
        print(f"ERRO ao acessar sheet pacientes: {patient_matches['error']}", file=sys.stderr)
        sys.exit(2)

    if args.apenas_status:
        is_patient = bool(patient_matches)
        if args.json:
            print(json.dumps({"telefone": args.telefone, "is_patient": is_patient}))
        else:
            print("PACIENTE_ATIVO" if is_patient else "LEAD")
        return

    # Get raw conversation history
    raw_matches = search_in_sheet(phone_variants, RAW_SHEET)
    if isinstance(raw_matches, dict) and "error" in raw_matches:
        raw_matches = []

    # Get structured context
    context_matches = search_in_sheet(phone_variants, CONTEXT_SHEET)
    if isinstance(context_matches, dict) and "error" in context_matches:
        context_matches = []

    classification = classify_lead(raw_matches, patient_matches)

    result = {
        "telefone": args.telefone,
        "phone_variants_buscadas": phone_variants,
        "classificacao": classification,
        "is_paciente_ativo": bool(patient_matches),
        "total_interacoes": len(raw_matches),
        "patient_data": patient_matches[0] if patient_matches else None,
        "contexto_estruturado": context_matches[0] if context_matches else None,
        "historico_raw": raw_matches[-20:] if raw_matches else [],
    }

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"=== Historico para {args.telefone} ===")
        print(f"Classificacao: {classification}")
        print(f"Paciente ativo: {bool(patient_matches)}")
        print(f"Total de interacoes: {len(raw_matches)}")
        if patient_matches:
            print(f"\nDados do paciente:")
            for k, v in patient_matches[0].items():
                print(f"  {k}: {v}")
        if context_matches:
            print(f"\nContexto estruturado:")
            for k, v in context_matches[0].items():
                print(f"  {k}: {v}")
        if raw_matches:
            print(f"\nUltimas {min(20, len(raw_matches))} interacoes:")
            for row in raw_matches[-20:]:
                print(f"  - {row}")
        else:
            print("\nSem historico registrado — LEAD NOVO")


if __name__ == "__main__":
    main()
