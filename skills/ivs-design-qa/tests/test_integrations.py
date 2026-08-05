import importlib.util
import tempfile
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
