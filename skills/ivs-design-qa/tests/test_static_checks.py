import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "static_checks.py"


def load_module():
    spec = importlib.util.spec_from_file_location("ivs_design_qa_static_checks", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("não foi possível carregar static_checks")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


HEALTHY = """<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Piloto IVS</title><style>@media(max-width:700px){main{padding:1rem}}</style></head>
<body><main><section><h1>Conteúdo sintético</h1></section></main></body></html>"""


class StaticChecksTests(unittest.TestCase):
    def setUp(self):
        self.mod = load_module()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "fixture.html"

    def test_healthy_html_has_no_blockers_and_redacted_metrics(self):
        self.path.write_text(HEALTHY, encoding="utf-8")
        result = self.mod.scan_html(self.path, "site", "anonymous")
        self.assertEqual(result["blockers"], [])
        self.assertGreater(result["metrics"]["bytes"], 0)
        self.assertEqual(result["metrics"]["sections"], 1)
        self.assertNotIn("content", result)
        self.assertEqual(len(result["source_sha256"]), 64)

    def test_placeholder_and_missing_viewport_are_blockers(self):
        html = "<!doctype html><html><head><title>X</title></head><body><section>TODO [preencher nome]</section></body></html>"
        self.path.write_text(html, encoding="utf-8")
        result = self.mod.scan_html(self.path, "internal-report", "anonymous")
        codes = {item["code"] for item in result["blockers"]}
        self.assertIn("placeholder_detected", codes)
        self.assertIn("viewport_missing", codes)

    def test_anonymous_patient_presentation_blocks_direct_identifiers(self):
        html = HEALTHY.replace("Conteúdo sintético", "Contato teste@example.com CPF 123.456.789-00 telefone (71) 99999-9999")
        self.path.write_text(html, encoding="utf-8")
        result = self.mod.scan_html(self.path, "patient-presentation", "anonymous")
        codes = {item["code"] for item in result["blockers"]}
        self.assertIn("direct_identifier_detected", codes)
        pii = result["metrics"]["direct_identifier_counts"]
        self.assertEqual(pii["email"], 1)
        self.assertEqual(pii["cpf"], 1)
        self.assertGreaterEqual(pii["phone"], 1)
        serialized = str(result)
        self.assertNotIn("teste@example.com", serialized)
        self.assertNotIn("123.456.789-00", serialized)

    def test_sensitive_local_omits_title_and_marks_sensitive_outputs(self):
        self.path.write_text(HEALTHY.replace("Piloto IVS", "Nome confidencial"), encoding="utf-8")
        result = self.mod.scan_html(self.path, "patient-presentation", "sensitive-local")
        self.assertNotIn("title", result)
        self.assertTrue(result["governance"]["sensitive_outputs"])
        self.assertFalse(result["governance"]["external_publish"])
        self.assertFalse(result["governance"]["patient_send_ready"])


if __name__ == "__main__":
    unittest.main()
