import importlib.util
import os
import signal
import tempfile
import time
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "integrations.py"
VISUAL_SCRIPT = Path(__file__).resolve().parents[2] / "ivs-visual-layer" / "scripts" / "ivs_visual_layer.py"


def load_module():
    spec = importlib.util.spec_from_file_location("ivs_design_qa_integrations", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("não foi possível carregar integrations")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


HTML = """<!doctype html><html><head><meta name="viewport" content="width=device-width"><title>Piloto</title><style>@media(max-width:600px){body{margin:0}}</style></head><body><section><h1>Piloto</h1></section></body></html>"""


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.mod = load_module()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.html = self.root / "input.html"
        self.html.write_text(HTML, encoding="utf-8")

    def test_browser_probe_false_without_blockers_fails_closed(self):
        fake = self.root / "browser-false.mjs"
        fake.write_text(
            "process.stdout.write(JSON.stringify({ok:false,blockers:[],concerns:[],viewports:[{name:'desktop'},{name:'mobile'}]})+'\\n');process.exit(2);",
            encoding="utf-8",
        )
        result = self.mod.run_browser_probe(self.html, self.root / "browser-out", script_path=fake)
        self.assertFalse(result["ok"])
        self.assertIn("browser_probe_contract_invalid", {item["code"] for item in result["blockers"]})

    def test_browser_probe_missing_viewports_fails_closed(self):
        fake = self.root / "browser-missing-viewports.mjs"
        fake.write_text(
            "process.stdout.write(JSON.stringify({ok:true,blockers:[],concerns:[],viewports:[]})+'\\n');",
            encoding="utf-8",
        )
        result = self.mod.run_browser_probe(self.html, self.root / "browser-out", script_path=fake)
        self.assertFalse(result["ok"])
        self.assertIn("browser_probe_contract_invalid", {item["code"] for item in result["blockers"]})

    def test_browser_timeout_kills_entire_process_group(self):
        pid_file = self.root / "child.pid"
        fake = self.root / "browser-hangs.mjs"
        fake.write_text(
            "import{spawn}from'node:child_process';import{writeFileSync}from'node:fs';"
            f"const c=spawn('sleep',['60'],{{stdio:'ignore'}});writeFileSync({str(pid_file)!r},String(c.pid));setInterval(()=>{{}},1000);",
            encoding="utf-8",
        )
        child_pid = None
        try:
            result = self.mod.run_browser_probe(self.html, self.root / "browser-timeout", script_path=fake, timeout=1)
            self.assertFalse(result["ok"])
            for _ in range(20):
                if pid_file.exists():
                    child_pid = int(pid_file.read_text(encoding="utf-8"))
                    break
                time.sleep(0.05)
            self.assertIsNotNone(child_pid)
            assert child_pid is not None
            time.sleep(0.2)
            process_stat = Path(f"/proc/{child_pid}/stat")
            running = process_stat.exists() and process_stat.read_text(encoding="utf-8").split()[2] != "Z"
            self.assertFalse(running, f"processo filho ainda ativo: {child_pid}")
        finally:
            if child_pid:
                try:
                    os.kill(child_pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass

    def test_ivs_site_success_is_parsed_without_raw_page_content(self):
        fake = self.root / "ivs-site"
        fake.write_text("#!/usr/bin/env python3\nimport json\nprint(json.dumps({'ok': True, 'issues': []}))\n", encoding="utf-8")
        fake.chmod(0o755)
        result = self.mod.run_ivs_site(self.html, executable=str(fake))
        self.assertTrue(result["available"])
        self.assertTrue(result["ok"])
        self.assertEqual(result["blockers"], [])
        self.assertNotIn("stdout", result)

    def test_ivs_site_failure_becomes_blocker(self):
        fake = self.root / "ivs-site"
        fake.write_text("#!/usr/bin/env python3\nimport json,sys\nprint(json.dumps({'ok': False, 'issues': ['falha']}));sys.exit(2)\n", encoding="utf-8")
        fake.chmod(0o755)
        result = self.mod.run_ivs_site(self.html, executable=str(fake))
        self.assertFalse(result["ok"])
        self.assertIn("ivs_site_validation_failed", {item["code"] for item in result["blockers"]})

    def test_ivs_site_known_portuguese_todo_false_positive_is_filtered(self):
        self.html.write_text(HTML.replace("Piloto", "Cuidado que entende o todo"), encoding="utf-8")
        fake = self.root / "ivs-site"
        known_issue = r"blocked_placeholder:\bTODO\b"
        fake.write_text(
            "#!/usr/bin/env python3\nimport json,sys\n"
            f"print(json.dumps({{'ok': False, 'issues': [{known_issue!r}]}}));sys.exit(1)\n",
            encoding="utf-8",
        )
        fake.chmod(0o755)
        result = self.mod.run_ivs_site(self.html, executable=str(fake))
        self.assertTrue(result["ok"])
        self.assertEqual(result["filtered_issues_count"], 1)
        self.assertEqual(result["blockers"], [])

    def test_ivs_site_todo_workaround_rejects_variants_and_custom_issues(self):
        fake = self.root / "ivs-site"
        known_issue = r"blocked_placeholder:\bTODO\b"
        cases = [
            ("Sem marcador", known_issue),
            ("Marcador Todo", known_issue),
            ("Marcador ToDo", known_issue),
            ("Marcador TODO", known_issue),
            ("todo e também TODO", known_issue),
            ("Cuidado que entende o todo", "blocked_placeholder:custom TODO"),
        ]
        for text, issue in cases:
            with self.subTest(text=text, issue=issue):
                self.html.write_text(HTML.replace("Piloto", text), encoding="utf-8")
                fake.write_text(
                    "#!/usr/bin/env python3\nimport json,sys\n"
                    f"print(json.dumps({{'ok': False, 'issues': [{issue!r}]}}));sys.exit(1)\n",
                    encoding="utf-8",
                )
                fake.chmod(0o755)
                result = self.mod.run_ivs_site(self.html, executable=str(fake))
                self.assertFalse(result["ok"])
                self.assertEqual(result["filtered_issues_count"], 0)

    def test_visual_layer_missing_declared_outputs_fails_closed(self):
        fake_visual = self.root / "fake_visual_missing.py"
        fake_visual.write_text(
            "import json\nprint(json.dumps({'ok': True, 'output_html': '/tmp/not-created.html', 'audit_json': '/tmp/not-created.json', 'sections_count': 1, 'risks': []}))\n",
            encoding="utf-8",
        )
        out_dir = self.root / "visual-missing"
        result = self.mod.run_visual_layer(self.html, out_dir, "site", script_path=fake_visual)
        self.assertFalse(result["ok"])
        self.assertIn("visual_layer_contract_invalid", {item["code"] for item in result["blockers"]})

    def test_visual_layer_generates_copy_and_preserves_original(self):
        before = self.mod.sha256_file(self.html)
        result = self.mod.run_visual_layer(
            self.html,
            self.root / "visual",
            "site",
            script_path=VISUAL_SCRIPT,
        )
        after = self.mod.sha256_file(self.html)
        self.assertTrue(result["available"])
        self.assertTrue(result["ok"])
        self.assertEqual(before, after)
        self.assertTrue(Path(result["output_html"]).is_file())
        self.assertTrue(Path(result["audit_json"]).is_file())
        self.assertTrue(result["original_unchanged"])
        self.assertNotEqual(Path(result["output_html"]), self.html)


if __name__ == "__main__":
    unittest.main()
