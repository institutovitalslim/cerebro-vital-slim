#!/usr/bin/env python3
"""Fluxo seguro para localizar paciente no Quarkclinic e cadastrar/atualizar no Omie."""
import argparse
import json
import os
import re
import sys
import time
import unicodedata
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

QUARK_ENV_FILE = Path("/root/.openclaw/quarkclinic.env")
OMIE_ENV_FILE = Path("/root/.openclaw/secure/omie_api.env")
QUARK_BASE_URL = "https://api.quark.tec.br/clinic/ext"
OMIE_BASE_URL = "https://app.omie.com.br/api/"
OMIE_RATE_DELAY = 0.35
_last_omie_call = 0.0


def load_env_file(path: Path) -> dict:
    data = {}
    if not path.exists():
        return data
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def norm(value: str) -> str:
    return unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode("ascii").lower().strip()


def only_digits(value: str) -> str:
    return re.sub(r"\D", "", value or "")


def mask_cpf(value: str) -> str:
    digits = only_digits(value)
    if len(digits) != 11:
        return value or ""
    return f"***.{digits[3:6]}.{digits[6:9]}-**"


def mask_email(value: str) -> str:
    if not value or "@" not in value:
        return value or ""
    local, domain = value.split("@", 1)
    local_mask = (local[:3] + "***") if len(local) > 3 else (local[:1] + "***")
    return f"{local_mask}@{domain}"


def mask_phone(value: str) -> str:
    digits = only_digits(value)
    if len(digits) == 13 and digits.startswith("55"):
        digits = digits[2:]
    if len(digits) in (10, 11):
        ddd = digits[:2]
        final = digits[-4:]
        return f"({ddd}) *****-{final}"
    return value or ""


def epoch_ms_to_date(value):
    if value in (None, ""):
        return ""
    try:
        return datetime.fromtimestamp(int(value) / 1000, tz=timezone.utc).strftime("%d/%m/%Y")
    except Exception:
        return ""


def quark_request(method: str, path: str, query=None, body=None, timeout=60):
    creds = load_env_file(QUARK_ENV_FILE)
    token = creds.get("QUARKCLINIC_AUTH_TOKEN")
    if not token:
        raise SystemExit("Missing QUARKCLINIC_AUTH_TOKEN in /root/.openclaw/quarkclinic.env")
    base_url = creds.get("QUARKCLINIC_BASE_URL", QUARK_BASE_URL).rstrip("/")
    url = base_url + "/" + path.lstrip("/")
    if query:
        from urllib.parse import urlencode
        url += "?" + urlencode(query, doseq=True)
    headers = {"Accept": "application/json", "Auth-token": token}
    payload = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        headers["X-Chave-Key"] = creds.get("QUARKCLINIC_X_CHAVE_KEY", "")
        headers["X-Secret-Key"] = creds.get("QUARKCLINIC_X_SECRET_KEY", "")
        payload = json.dumps(body).encode("utf-8")
    req = Request(url, method=method, headers=headers, data=payload)
    try:
        with urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(raw)
        except Exception:
            parsed = {"error": raw}
        return exc.code, parsed
    except URLError as exc:
        return 599, {"error": str(exc.reason)}


def omie_throttle():
    global _last_omie_call
    elapsed = time.time() - _last_omie_call
    if elapsed < OMIE_RATE_DELAY:
        time.sleep(OMIE_RATE_DELAY - elapsed)
    _last_omie_call = time.time()


def omie_call(endpoint: str, method: str, params: dict):
    creds = load_env_file(OMIE_ENV_FILE)
    app_key = creds.get("OMIE_APP_KEY")
    app_secret = creds.get("OMIE_APP_SECRET")
    base_url = creds.get("OMIE_BASE_URL", OMIE_BASE_URL).rstrip("/")
    if not app_key or not app_secret:
        raise SystemExit("Missing Omie credentials in /root/.openclaw/secure/omie_api.env")
    omie_throttle()
    payload = {
        "call": method,
        "app_key": app_key,
        "app_secret": app_secret,
        "param": [params],
    }
    req = Request(
        f"{base_url}/v1/{endpoint}/",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        return {"error": True, "status": exc.code, "message": raw}
    except URLError as exc:
        return {"error": True, "message": str(exc.reason)}


def score_candidate(query: str, patient_name: str) -> float:
    q = norm(query)
    n = norm(patient_name)
    if not q or not n:
        return 0.0
    if q == n:
        return 1.0
    tokens = [t for t in re.split(r"\s+", n) if t]
    if q in tokens:
        return 0.98
    if n.startswith(q):
        return 0.92
    if q in n:
        return 0.88

    prefix = q[:3]
    best_token = max((SequenceMatcher(None, q, token).ratio() for token in tokens), default=0.0)
    best_full = SequenceMatcher(None, q, n).ratio()
    has_prefix_match = any(token.startswith(prefix) for token in tokens if prefix)
    if has_prefix_match and best_token >= 0.72:
        return max(best_token, 0.78)
    if best_token >= 0.9 or best_full >= 0.9:
        return max(best_token, best_full)
    return 0.0


def iter_quark_patients(max_pages=30):
    for page in range(1, max_pages + 1):
        status, payload = quark_request("GET", "/v1/pacientes", query=[("page", str(page))])
        if status >= 400:
            raise SystemExit(f"Quarkclinic GET /v1/pacientes failed on page {page}: {payload}")
        items = payload.get("response", []) if isinstance(payload, dict) else []
        if not items:
            break
        for item in items:
            yield item
        if len(items) < 100:
            break


def search_quarkclinic(name: str, limit=5):
    scored = []
    for patient in iter_quark_patients():
        score = score_candidate(name, patient.get("nome", ""))
        if score >= 0.72:
            scored.append((score, patient))
    scored.sort(key=lambda item: (-item[0], norm(item[1].get("nome", ""))))
    results = []
    for score, patient in scored[:limit]:
        pid = patient.get("id")
        phones = []
        if pid:
            phone_status, phone_payload = quark_request("GET", f"/v1/pacientes/{pid}/telefones")
            if phone_status < 400 and isinstance(phone_payload, dict):
                phones = phone_payload.get("response", []) or []
        results.append(
            {
                "score": round(score, 3),
                "id": pid,
                "nome": patient.get("nome", ""),
                "cpf": patient.get("cpf", ""),
                "cpf_masked": mask_cpf(patient.get("cpf", "")),
                "email": patient.get("email", ""),
                "email_masked": mask_email(patient.get("email", "")),
                "data_nascimento": epoch_ms_to_date(patient.get("dataNascimento")),
                "bairro": patient.get("bairro") or "",
                "cidade": patient.get("cidade") or "",
                "telefone": phones[0] if phones else "",
                "telefone_masked": mask_phone(phones[0]) if phones else "",
            }
        )
    return results


def get_quark_patient(patient_id: int) -> dict:
    status, payload = quark_request("GET", f"/v1/pacientes/{patient_id}")
    if status >= 400:
        raise SystemExit(f"Quarkclinic patient {patient_id} not found: {payload}")
    items = payload.get("response", []) if isinstance(payload, dict) else []
    if not items:
        raise SystemExit(f"Quarkclinic patient {patient_id} returned no data")
    patient = items[0]
    phone_status, phone_payload = quark_request("GET", f"/v1/pacientes/{patient_id}/telefones")
    phones = phone_payload.get("response", []) if phone_status < 400 and isinstance(phone_payload, dict) else []
    patient["telefone_principal"] = phones[0] if phones else ""
    return patient


def split_phone(raw_phone: str):
    digits = only_digits(raw_phone)
    if len(digits) == 13 and digits.startswith("55"):
        digits = digits[2:]
    if len(digits) < 10:
        return "", ""
    return digits[:2], digits[2:]


def iter_omie_clients():
    for page in range(1, 200):
        result = omie_call("geral/clientes", "ListarClientes", {"pagina": page, "registros_por_pagina": 50})
        if result.get("error"):
            raise SystemExit(f"Omie ListarClientes failed on page {page}: {result}")
        items = result.get("clientes_cadastro", [])
        if not items:
            break
        for item in items:
            yield item
        if page >= result.get("total_de_paginas", page):
            break


def find_omie_duplicates(cpf: str, full_name: str):
    target_cpf = only_digits(cpf)
    target_name = norm(full_name)
    matches = []
    for client in iter_omie_clients():
        client_cpf = only_digits(client.get("cnpj_cpf", ""))
        client_name = norm(client.get("razao_social", ""))
        client_alias = norm(client.get("nome_fantasia", ""))
        if (target_cpf and client_cpf == target_cpf) or (target_name and (client_name == target_name or client_alias == target_name)):
            matches.append(
                {
                    "codigo_cliente_omie": client.get("codigo_cliente_omie"),
                    "codigo_cliente_integracao": client.get("codigo_cliente_integracao", ""),
                    "razao_social": client.get("razao_social", ""),
                    "cnpj_cpf": client.get("cnpj_cpf", ""),
                    "email": client.get("email", ""),
                    "cidade": client.get("cidade", ""),
                    "estado": client.get("estado", ""),
                }
            )
    return matches


def build_omie_payload(patient: dict, overrides: dict | None = None):
    overrides = overrides or {}
    phone_ddd, phone_number = split_phone(patient.get("telefone_principal", ""))
    payload = {
        "codigo_cliente_integracao": f"QC-{patient['id']}",
        "razao_social": patient.get("nome", ""),
        "nome_fantasia": patient.get("nome", ""),
        "cnpj_cpf": patient.get("cpf", ""),
        "email": patient.get("email", ""),
        "telefone1_ddd": phone_ddd,
        "telefone1_numero": phone_number,
        "endereco": patient.get("logradouro") or "",
        "endereco_numero": patient.get("numero") or "",
        "bairro": patient.get("bairro") or "",
        "cidade": patient.get("cidade") or "",
        "estado": "",
        "cep": "",
        "complemento": patient.get("complemento") or "",
        "pessoa_fisica": "S",
        "codigo_pais": "1058",
        "exterior": "N",
        "bloquear_faturamento": "N",
        "inativo": "N",
        "optante_simples_nacional": "N",
        "enviar_anexos": "N",
        "tags": [{"tag": "Cliente"}],
    }
    for key, value in overrides.items():
        if value is not None:
            payload[key] = value
    return payload


def command_search(args):
    results = search_quarkclinic(args.nome, limit=args.limit)
    print(json.dumps({"query": args.nome, "results": results}, ensure_ascii=False, indent=2))
    return 0


def command_create(args):
    if not args.write_ok:
        raise SystemExit("Use --write-ok para criar cadastro no Omie.")
    patient = get_quark_patient(args.quark_id)
    duplicates = find_omie_duplicates(patient.get("cpf", ""), patient.get("nome", ""))
    if duplicates and not args.force_create:
        print(json.dumps({"status": "duplicate", "matches": duplicates}, ensure_ascii=False, indent=2))
        return 2
    overrides = {
        "cidade": args.cidade,
        "estado": args.estado,
        "cep": args.cep,
        "complemento": args.complemento,
        "bairro": args.bairro,
        "endereco": args.endereco,
        "endereco_numero": args.numero,
        "email": args.email,
    }
    payload = build_omie_payload(patient, overrides)
    result = omie_call("geral/clientes", "IncluirCliente", payload)
    print(json.dumps({"patient": patient.get("nome", ""), "payload": payload, "result": result}, ensure_ascii=False, indent=2))
    return 0 if str(result.get("codigo_status", "")) == "0" else 1


def command_update(args):
    if not args.write_ok:
        raise SystemExit("Use --write-ok para alterar cadastro no Omie.")
    current = omie_call("geral/clientes", "ConsultarCliente", {"codigo_cliente_omie": args.omie_id})
    if current.get("error"):
        raise SystemExit(f"Omie ConsultarCliente falhou: {current}")
    payload = {
        "codigo_cliente_omie": args.omie_id,
        "codigo_cliente_integracao": current.get("codigo_cliente_integracao", ""),
        "razao_social": current.get("razao_social", ""),
        "nome_fantasia": current.get("nome_fantasia", current.get("razao_social", "")),
        "cnpj_cpf": current.get("cnpj_cpf", ""),
        "email": args.email if args.email is not None else current.get("email", ""),
        "telefone1_ddd": current.get("telefone1_ddd", ""),
        "telefone1_numero": current.get("telefone1_numero", ""),
        "endereco": args.endereco if args.endereco is not None else current.get("endereco", ""),
        "endereco_numero": args.numero if args.numero is not None else current.get("endereco_numero", ""),
        "bairro": args.bairro if args.bairro is not None else current.get("bairro", ""),
        "cidade": args.cidade if args.cidade is not None else current.get("cidade", ""),
        "estado": args.estado if args.estado is not None else current.get("estado", ""),
        "cep": args.cep if args.cep is not None else current.get("cep", ""),
        "complemento": args.complemento if args.complemento is not None else current.get("complemento", ""),
        "pessoa_fisica": current.get("pessoa_fisica", "S"),
        "codigo_pais": current.get("codigo_pais", "1058"),
        "exterior": current.get("exterior", "N"),
        "bloquear_faturamento": current.get("bloquear_faturamento", "N"),
        "inativo": current.get("inativo", "N"),
        "optante_simples_nacional": current.get("optante_simples_nacional", "N"),
        "enviar_anexos": current.get("enviar_anexos", "N"),
        "tags": current.get("tags") or [{"tag": "Cliente"}],
    }
    result = omie_call("geral/clientes", "AlterarCliente", payload)
    print(json.dumps({"payload": payload, "result": result}, ensure_ascii=False, indent=2))
    return 0 if str(result.get("codigo_status", "")) == "0" else 1


def build_parser():
    parser = argparse.ArgumentParser(description="Fluxo seguro para cadastro de pacientes do Quarkclinic no Omie")
    sub = parser.add_subparsers(dest="command", required=True)

    search = sub.add_parser("search", help="Buscar paciente no Quarkclinic")
    search.add_argument("nome")
    search.add_argument("--limit", type=int, default=5)
    search.set_defaults(func=command_search)

    create = sub.add_parser("create", help="Criar paciente no Omie a partir do ID do Quarkclinic")
    create.add_argument("--quark-id", type=int, required=True)
    create.add_argument("--cidade")
    create.add_argument("--estado")
    create.add_argument("--cep")
    create.add_argument("--complemento")
    create.add_argument("--bairro")
    create.add_argument("--endereco")
    create.add_argument("--numero")
    create.add_argument("--email")
    create.add_argument("--write-ok", action="store_true")
    create.add_argument("--force-create", action="store_true")
    create.set_defaults(func=command_create)

    update = sub.add_parser("update", help="Atualizar cadastro existente no Omie")
    update.add_argument("--omie-id", type=int, required=True)
    update.add_argument("--cidade")
    update.add_argument("--estado")
    update.add_argument("--cep")
    update.add_argument("--complemento")
    update.add_argument("--bairro")
    update.add_argument("--endereco")
    update.add_argument("--numero")
    update.add_argument("--email")
    update.add_argument("--write-ok", action="store_true")
    update.set_defaults(func=command_update)
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    try:
        raise SystemExit(args.func(args))
    except KeyboardInterrupt:
        raise SystemExit(130)


if __name__ == "__main__":
    main()
