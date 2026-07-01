# RC-25 Candidate — Snapshot diário Hostinger VPS IVS

Data: 2026-06-13
Solicitante: Tiaro
Executor: Maria
Status: ativo em produção assistida

## Fato operacional
Tiaro autorizou criar rotina diária para snapshot manual de backup da VPS Hostinger do IVS.

## VPS alvo
- Hostname: `srv1429339.hstgr.cloud`
- VPS ID Hostinger: `1429339`
- IPv4 esperado: `187.77.58.193`

## Implementação
- Script canônico: `/root/cerebro-vital-slim/scripts/hostinger_snapshot_backup.py`
- Logs: `/root/cerebro-vital-slim/logs/hostinger-snapshots/`
- Último status: `/root/cerebro-vital-slim/logs/hostinger-snapshots/latest.json`
- Cron Hermes atual: `9c70429610e5` (`IVS Hostinger VPS snapshot diário`)
- Cron Gateway legado: `0e95960c-a39d-4274-9feb-2e83e737f564` (não estava mais ativo na lista Hermes em 2026-07-01)
- Agenda: diariamente às `23:30` em `America/Sao_Paulo` (`02:30 UTC`)
- Entrega: `origin` para Tiaro em linha única com status do snapshot

## Processo de validação
A rotina valida:
1. VPS alvo existe.
2. VPS está `running`.
3. IP esperado está associado à VPS.
4. Ação `ct_snapshot_create` termina em `success`.
5. Snapshot existe após a ação.
6. `created_at` do snapshot é posterior ao início da execução.
7. `expires_at` está no futuro.
8. `restore_time` está presente e maior que zero.

## Limite técnico
A API Hostinger não permite verificar a integridade interna do snapshot sem restore. Portanto, a validação de qualidade é operacional/API. Teste de restore deve ser uma rotina separada, não destrutiva ou em VPS clone, se Tiaro autorizar.

## Guardrails
- A criação de snapshot sobrescreve o snapshot anterior.
- Alterações destrutivas, restore ou manipulação de VPS exigem autorização explícita do Tiaro.
- Token não deve ser registrado no cérebro ou em relatórios.
