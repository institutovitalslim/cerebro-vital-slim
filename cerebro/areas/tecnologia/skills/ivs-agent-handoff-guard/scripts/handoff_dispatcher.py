#!/usr/bin/env python3
"""Safe handoff dispatcher.
Creates a handoff packet and optionally performs an internal sessions_send only for allowed internal agents.
Default is dry-run/no-delivery.
"""
import argparse, json, subprocess, time
from pathlib import Path
PACKET=Path('/root/.openclaw/workspace/skills/ivs-agent-handoff-guard/scripts/handoff_packet.py')
INTERNAL={'maria-gerente','agente-reels-intel','pedro-controller-ivs','conselho-growth-vital-slim','llm-council'}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--from',dest='from_agent',required=True); ap.add_argument('--to',dest='to_agent',required=True); ap.add_argument('--subject',required=True); ap.add_argument('--context',required=True); ap.add_argument('--next-action',required=True); ap.add_argument('--sensitivity',default='internal'); ap.add_argument('--dry-run',action='store_true',default=True); ap.add_argument('--real-internal-send',action='store_true')
    args=ap.parse_args()
    cmd=['python3',str(PACKET),'--from',args.from_agent,'--to',args.to_agent,'--subject',args.subject,'--context',args.context,'--next-action',args.next_action,'--sensitivity',args.sensitivity]
    packet=json.loads(subprocess.check_output(cmd,text=True,stderr=subprocess.STDOUT,timeout=20))
    decision={'ok':packet.get('ok') and (args.to_agent in INTERNAL), 'packet':packet, 'dispatch':'dry_run_no_delivery', 'generated_at':int(time.time())}
    if args.to_agent not in INTERNAL:
        decision['ok']=False; decision['dispatch']='blocked_non_internal_destination'
    if args.real_internal_send:
        # This script intentionally does not call sessions_send because tool calls must remain under Maria/OpenClaw control.
        decision['dispatch']='ready_for_maria_sessions_send'; decision['note']='Use sessions_send manually with this packet if appropriate.'
    print(json.dumps(decision,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
