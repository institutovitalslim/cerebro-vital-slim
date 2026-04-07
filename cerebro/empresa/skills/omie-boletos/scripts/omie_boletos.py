#!/usr/bin/env python3
"""Omie Boletos — baixa boletos de faturamentos e organiza por paciente."""
import argparse
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, "/root/.openclaw/workspace/skills/omie-api/scripts")
from omie_api import resolve_credentials, api_call

ACCOUNT = "medicalemagrecimento@gmail.com"
DRIVE_ROOT = "1_on_1ABIODqcbpby-EwKHgciT0m4_P9f"
LOCAL_ROOT = r"C:\Users\tiaro\Documents\## Medical Contabilidade\#Instituto Vital Slim\Boletos de Programa de Acompanhamento"


def gog(args):
    cmd = ["gog"] + args + ["-a", ACCOUNT]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    return r.stdout.strip(), r.stderr.strip(), r.returncode


def find_or_create_drive_folder(parent_id, name):
    """Find existing folder by name or create new one. Never duplicate."""
    stdout, stderr, rc = gog(["drive", "ls", "--parent", parent_id, "-j"])
    if rc == 0 and stdout:
        parsed = json.loads(stdout)
        files = parsed.get("files", []) if isinstance(parsed, dict) else parsed
        for f in files:
            if isinstance(f, dict) and f.get("name") == name and "folder" in f.get("mimeType", ""):
                return f["id"]

    # Create new folder
    stdout, stderr, rc = gog(["drive", "mkdir", "--parent", parent_id, name, "-j"])
    if rc == 0:
        result = json.loads(stdout)
        return result.get("folder", {}).get("id", "")
    return ""


def get_faturamentos(data_de, data_ate):
    """Get all receivables emitted in the date range."""
    all_titles = []
    for page in range(1, 50):
        result = api_call("financas/contareceber", "ListarContasReceber", {
            "pagina": page,
            "registros_por_pagina": 50,
            "filtrar_por_emissao_de": data_de,
            "filtrar_por_emissao_ate": data_ate
        })
        titles = result.get("conta_receber_cadastro", [])
        all_titles.extend(titles)
        if page >= result.get("total_de_paginas", 1):
            break
    return all_titles


def group_by_client(titles):
    """Group titles by client, excluding cancelled."""
    clients = {}
    for t in titles:
        if t.get("status_titulo") == "CANCELADO":
            continue
        cid = str(t["codigo_cliente_fornecedor"])
        if cid not in clients:
            clients[cid] = {"titles": [], "name": ""}
        clients[cid]["titles"].append({
            "codigo_lancamento": t["codigo_lancamento_omie"],
            "numero_parcela": t.get("numero_parcela", ""),
            "valor": t.get("valor_documento", 0),
            "vencimento": t.get("data_vencimento", ""),
            "status": t.get("status_titulo", ""),
            "boleto_gerado": t.get("boleto", {}).get("cGerado", "N"),
        })
    return clients


def resolve_client_names(clients):
    """Fetch client names from Omie."""
    for cid in list(clients.keys()):
        time.sleep(0.4)
        r = api_call("geral/clientes", "ConsultarCliente", {"codigo_cliente_omie": int(cid)})
        clients[cid]["name"] = r.get("razao_social", r.get("nome_fantasia", "Cliente_" + cid))
    return clients


def download_boleto(codigo_lancamento):
    """Get boleto PDF link and download to temp file."""
    time.sleep(0.4)
    result = api_call("financas/contareceberboleto", "ObterBoleto", {"nCodTitulo": codigo_lancamento})
    link = result.get("cLinkBoleto", "")
    if not link:
        return None

    tmp_file = f"/tmp/boleto_{codigo_lancamento}.pdf"
    subprocess.run(["curl", "-s", "-L", "-o", tmp_file, link], timeout=30)

    if os.path.exists(tmp_file) and os.path.getsize(tmp_file) > 100:
        return tmp_file
    return None


def boleto_filename(t):
    parcela = t["numero_parcela"].replace("/", "-")
    valor = t["valor"]
    venc = t["vencimento"].replace("/", "-")
    return f"Boleto_P{parcela}_R${valor}_Venc{venc}.pdf"


def main():
    parser = argparse.ArgumentParser(description="Omie Boletos — baixa e organiza boletos por paciente")
    parser.add_argument("--data", help="Data de emissão (DD/MM/AAAA)")
    parser.add_argument("--de", help="Data inicial do período (DD/MM/AAAA)")
    parser.add_argument("--ate", help="Data final do período (DD/MM/AAAA)")
    parser.add_argument("--listar", action="store_true", help="Apenas listar, sem baixar")
    parser.add_argument("--drive", action="store_true", help="Salvar no Google Drive")
    parser.add_argument("--local", action="store_true", help="Salvar no disco local")
    args = parser.parse_args()

    if args.data:
        data_de = data_ate = args.data
    elif args.de and args.ate:
        data_de, data_ate = args.de, args.ate
    else:
        print("Erro: informe --data ou --de/--ate", file=sys.stderr)
        sys.exit(1)

    if not args.listar and not args.drive and not args.local:
        args.drive = True  # default: salvar no Drive

    resolve_credentials()

    print(f"Consultando faturamentos de {data_de} a {data_ate}...")
    titles = get_faturamentos(data_de, data_ate)
    clients = group_by_client(titles)
    clients = resolve_client_names(clients)

    total_parcelas = sum(len(c["titles"]) for c in clients.values())
    total_com_boleto = sum(1 for c in clients.values() for t in c["titles"] if t["boleto_gerado"] == "S")
    print(f"Encontrados: {len(clients)} pacientes, {total_parcelas} parcelas, {total_com_boleto} com boleto")

    if args.listar:
        for cid, data in clients.items():
            print(f"\n{data['name']}:")
            for t in data["titles"]:
                bol = "✓" if t["boleto_gerado"] == "S" else "✗"
                print(f"  P{t['numero_parcela']} | R$ {t['valor']} | Venc {t['vencimento']} | Bol {bol}")
        return

    # Find or create Pacientes folder on Drive
    drive_pacientes_id = ""
    if args.drive:
        print("\nPreparando Google Drive...")
        drive_pacientes_id = find_or_create_drive_folder(DRIVE_ROOT, "Pacientes")
        if not drive_pacientes_id:
            print("ERRO: não conseguiu criar/encontrar pasta Pacientes no Drive")
            args.drive = False

    # Process each client
    for cid, data in clients.items():
        name = data["name"]
        titles_list = data["titles"]
        boletos = [t for t in titles_list if t["boleto_gerado"] == "S"]

        if not boletos:
            print(f"\n{name}: sem boletos, pulando")
            continue

        print(f"\n=== {name} ({len(boletos)} boletos) ===")

        # Create client folder on Drive
        drive_folder_id = ""
        if args.drive and drive_pacientes_id:
            drive_folder_id = find_or_create_drive_folder(drive_pacientes_id, name)
            if drive_folder_id:
                print(f"  Drive: pasta OK")
            else:
                print(f"  Drive: ERRO ao criar pasta")

        # Create local folder
        local_folder = ""
        if args.local:
            local_folder = os.path.join(LOCAL_ROOT, name)
            os.makedirs(local_folder, exist_ok=True)
            print(f"  Local: {local_folder}")

        # Download and save boletos
        for t in boletos:
            filename = boleto_filename(t)
            parcela = t["numero_parcela"].replace("/", "-")

            tmp_file = download_boleto(t["codigo_lancamento"])
            if not tmp_file:
                print(f"  P{parcela}: sem link de boleto")
                continue

            # Upload to Drive
            if args.drive and drive_folder_id:
                stdout, stderr, rc = gog(["drive", "upload", "--parent", drive_folder_id, "--name", filename, tmp_file])
                if rc == 0:
                    print(f"  P{parcela}: {filename} → Drive ✓")
                else:
                    print(f"  P{parcela}: Drive ERRO - {stderr[:80]}")

            # Copy to local
            if args.local and local_folder:
                import shutil
                dest = os.path.join(local_folder, filename)
                shutil.copy2(tmp_file, dest)
                print(f"  P{parcela}: {filename} → Local ✓")

            os.remove(tmp_file)

    print("\n=== CONCLUÍDO ===")


if __name__ == "__main__":
    main()
