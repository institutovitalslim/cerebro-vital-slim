#!/usr/bin/env python3
import json, subprocess, unittest, pathlib
BASE=pathlib.Path('/root/.openclaw/workspace/skills/ivs-agent-operating-layer')
HANDOFF=pathlib.Path('/root/.openclaw/workspace/skills/ivs-agent-handoff-guard/scripts/handoff_dispatcher.py')

def j(cmd):
    return json.loads(subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT, timeout=60))

class AgentOSRegression(unittest.TestCase):
    def test_workflow_registry_clean(self):
        d=j(['python3',str(BASE/'scripts/workflow_registry.py'),'--json'])
        self.assertTrue(d['ok']); self.assertEqual(d['totals']['findings'],0)
    def test_capability_registry_clean(self):
        d=j(['python3','/root/.openclaw/workspace/skills/ivs-agent-capability-registry/scripts/capability_registry.py','--json'])
        self.assertTrue(d['ok']); self.assertEqual(d['totals']['findings'],0)
    def test_permission_blocks_clinical_clara(self):
        d=j(['python3',str(BASE/'scripts/permission_gate.py'),'--agent','clara-whatsapp','--action','clinical_diagnosis','--sensitivity','clinical'])
        self.assertFalse(d['ok']); self.assertEqual(d['decision'],'forbidden')
    def test_action_gate_requires_approval(self):
        d=j(['python3',str(BASE/'scripts/action_gate.py'),'--agent','pedro-controller-ivs','--action','omie_write','--sensitivity','financial'])
        self.assertFalse(d['ok']); self.assertEqual(d['final'],'BLOCK_APPROVAL_REQUIRED')
    def test_sensitive_guard_enforces(self):
        p=subprocess.run(['python3',str(BASE/'scripts/sensitive_action_guard.py'),'--agent','pedro-controller-ivs','--action','omie_write','--sensitivity','financial'], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.assertNotEqual(p.returncode,0)
    def test_handoff_dispatcher_internal_dryrun(self):
        d=j(['python3',str(HANDOFF),'--from','maria-gerente','--to','agente-reels-intel','--subject','Teste','--context','Contexto','--next-action','Próxima ação','--sensitivity','marketing'])
        self.assertTrue(d['ok']); self.assertEqual(d['dispatch'],'dry_run_no_delivery')
    def test_pedro_omie_guard_blocks_without_approval(self):
        p=subprocess.run(['python3','/root/.openclaw/workspace/skills/pedro-controller-ivs/scripts/pedro_omie_action_guard.py','--evidence','teste sem aprovação'], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.assertNotEqual(p.returncode,0)
        d=json.loads(p.stdout)
        self.assertFalse(d['ok'])

    def test_clara_admin_send_dryrun_safe(self):
        out=subprocess.check_output(['curl','-sS','-X','POST','http://127.0.0.1:8787/admin/send','-H','Content-Type: application/json','-d','{"phone":"5511999990000","message":"teste dry run","dry_run":true}'], text=True, timeout=20)
        d=json.loads(out)
        self.assertTrue(d['ok'])
        self.assertTrue(d['dry_run'])

    def test_unified_cockpit_generates(self):
        d=j(['python3',str(BASE/'scripts/generate_agent_os_cockpit.py'),'--out','/tmp/cockpit-test.html','--json-out','/tmp/cockpit-test.json'])
        self.assertTrue(d['ok']); self.assertEqual(d['status'],'OK')

if __name__=='__main__': unittest.main()
