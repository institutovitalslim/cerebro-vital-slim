#!/usr/bin/env python3
"""
Busca pacientes novos (zero atendimentos realizados) no Quarkclinic para uma data e turno específicos.

Um paciente é considerado "novo" se não tiver NENHUM agendamento com status ATENDIMENTO_COMPLETO
na clínica. Ou seja, o agendamento atual é o primeiro dele.

A API Quarkclinic limita a janela de datas a 30 dias, então buscamos o histórico
em múltiplas chamadas de 30 dias cada.

Uso:
    python3 buscar_pacientes_novos.py <data_dd-MM-yyyy> <turno>
    
    turno: 'manha' (horario < 12:00) ou 'tarde' (horario >= 12:00)
    
Exemplo:
    python3 buscar_pacientes_novos.py 23-04-2026 tarde
"""

import sys
import json
import subprocess
from datetime import datetime, timedelta

SCRIPT_API = "/root/.openclaw/workspace/snapshot/openclaw-home/workspace/skills/quarkclinic-api/scripts/quarkclinic_api.py"
JANELA_DIAS = 30  # Limite da API Quarkclinic
DIAS_HISTORICO = 365  # Buscar 1 ano de histórico


def run_quarkclinic_api(path, queries=None):
    """Executa o cliente Quarkclinic API."""
    cmd = ["python3", SCRIPT_API, "GET", path]
    if queries:
        for q in queries:
            cmd.extend(["--query", q])
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERRO API Quarkclinic: {result.stderr}", file=sys.stderr)
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"ERRO: resposta inválida da API: {result.stdout[:200]}", file=sys.stderr)
        return None


def buscar_agendamentos(data_inicio, data_fim):
    """Busca todos os agendamentos em um intervalo de datas."""
    resp = run_quarkclinic_api("/v1/agendamentos", [
        f"data_agendamento_inicio={data_inicio}",
        f"data_agendamento_fim={data_fim}"
    ])
    if not resp:
        return []
    return resp.get("response", {}).get("response", [])


def buscar_historico_completo(data_str):
    """
    Busca histórico de agendamentos em janelas de 30 dias (limite da API).
    Retorna lista acumulada de todos os agendamentos do período.
    """
    data_ref = datetime.strptime(data_str, "%d-%m-%Y")
    data_inicio_global = data_ref - timedelta(days=DIAS_HISTORICO)
    
    todos = []
    cursor = data_inicio_global
    
    while cursor <= data_ref:
        fim_janela = min(cursor + timedelta(days=JANELA_DIAS - 1), data_ref)
        
        ini_str = cursor.strftime("%d-%m-%Y")
        fim_str = fim_janela.strftime("%d-%m-%Y")
        
        ags = buscar_agendamentos(ini_str, fim_str)
        todos.extend(ags)
        
        cursor = fim_janela + timedelta(days=1)
    
    return todos


def filtrar_turno(agendamentos, turno):
    """Filtra agendamentos por turno baseado no horário."""
    filtrados = []
    for ag in agendamentos:
        hora = ag.get("horaAgendamento", "00:00")
        try:
            hh = int(hora.split(":")[0])
            if turno == "manha" and hh < 12:
                filtrados.append(ag)
            elif turno == "tarde" and hh >= 12:
                filtrados.append(ag)
        except (ValueError, IndexError):
            continue
    return filtrados


def contar_atendimentos_por_paciente(todos_agendamentos):
    """
    Conta quantos ATENDIMENTO_COMPLETO cada paciente tem.
    Retorna dict: {pacienteId: count}
    """
    contagem = {}
    for ag in todos_agendamentos:
        pid = ag.get("pacienteId")
        if not pid:
            continue
        if ag.get("statusMarcacao") == "ATENDIMENTO_COMPLETO":
            contagem[pid] = contagem.get(pid, 0) + 1
    return contagem


def main():
    if len(sys.argv) < 3:
        print("Uso: python3 buscar_pacientes_novos.py <data_dd-MM-yyyy> <turno>")
        print("  turno: manha | tarde")
        sys.exit(1)
    
    data_str = sys.argv[1]
    turno = sys.argv[2].lower()
    
    if turno not in ("manha", "tarde"):
        print("ERRO: turno deve ser 'manha' ou 'tarde'")
        sys.exit(1)
    
    # 1. Busca agendamentos do dia especificado
    agendamentos_dia = buscar_agendamentos(data_str, data_str)
    agendamentos_turno = filtrar_turno(agendamentos_dia, turno)
    
    if not agendamentos_turno:
        print(json.dumps([], indent=2, ensure_ascii=False))
        return
    
    # 2. Busca histórico completo (1 ano) em janelas de 30 dias
    print(f"Buscando histórico de {DIAS_HISTORICO} dias...", file=sys.stderr)
    historico = buscar_historico_completo(data_str)
    
    # 3. Conta atendimentos realizados por paciente
    atendimentos_por_paciente = contar_atendimentos_por_paciente(historico)
    
    # 4. Filtra apenas pacientes com 0 atendimentos
    pacientes_novos = []
    
    for ag in agendamentos_turno:
        paciente_id = ag.get("pacienteId")
        if not paciente_id:
            continue
        
        atendimentos = atendimentos_por_paciente.get(paciente_id, 0)
        
        if atendimentos == 0:
            resp = run_quarkclinic_api(f"/v2/pacientes/{paciente_id}")
            if resp:
                paciente = resp.get("response", {}).get("response", [{}])[0]
                pacientes_novos.append({
                    "id": paciente_id,
                    "nome": ag.get("nomePaciente", ""),
                    "dataAgendamento": ag.get("dataAgendamento", ""),
                    "horaAgendamento": ag.get("horaAgendamento", ""),
                    "sexo": paciente.get("sexo", ""),
                    "telefone": paciente.get("telefones", [None])[0] or ag.get("telefone", ""),
                    "email": paciente.get("email", ""),
                    "dataNascimento": paciente.get("dataNascimento", None),
                    "cpf": paciente.get("cpf", ""),
                })
    
    print(json.dumps(pacientes_novos, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
