import hashlib
import json
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "ivs_design_qa.py"


def sample_html(extra: str = "") -> str:
    sections = "".join(f"<section><h2>Seção {i}</h2><p>Conteúdo sintético {i}</p></section>" for i in range(1, 7))
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Piloto</title><style>*{{box-sizing:border-box}}body{{margin:0}}section{{max-width:900px;margin:auto;padding:32px}}@media(max-width:600px){{section{{padding:20px}}}}</style></head><body>{extra}{sections}</body></html>"""


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class CLITests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.html = self.root / "piloto.html"
        self.fake_site = self.root / "ivs-site"
        self.fake_site.write_text("#!/usr/bin/env python3\nimport json\nprint(json.dumps({'ok': True, 'issues': []}))\n", encoding="utf-8")
        self.fake_site.chmod(0o755)

    def run_cli(self, html_text: str, artifact_type: str = "site"):
        self.html.write_text(html_text, encoding="utf-8")
        before = digest(self.html)
        out = self.root / "qa"
        proc = subprocess.run(
            [
                "python3", str(CLI), "--input", str(self.html), "--out-dir", str(out),
                "--artifact-type", artifact_type, "--data-mode", "anonymous",
                "--ivs-site-executable", str(self.fake_site),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=120,
        )
        return proc, out, before, digest(self.html)

    def test_healthy_site_passes_and_writes_redacted_reports(self):
        proc, out, before, after = self.run_cli(sample_html())
        self.assertEqual(proc.returncode, 0, proc.stderr)
        summary = json.loads(proc.stdout)
        self.assertEqual(summary["status"], "PASS")
        report_json = out / "ivs-design-qa.report.json"
        report_html = out / "ivs-design-qa.report.html"
        self.assertTrue(report_json.is_file())
        self.assertTrue(report_html.is_file())
        report = json.loads(report_json.read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["blockers"], [])
        self.assertEqual(before, after)
        self.assertTrue(report["governance"]["original_unchanged"])
        self.assertFalse(report["governance"]["patient_send_ready"])
        self.assertTrue((out / "browser" / "desktop.png").is_file())
        self.assertTrue((out / "browser" / "mobile.png").is_file())
        serialized = report_json.read_text(encoding="utf-8")
        self.assertNotIn("Conteúdo sintético", serialized)

    def test_filtered_ivs_site_false_positive_is_auditable_in_report(self):
        self.fake_site.write_text(
            "#!/usr/bin/env python3\nimport json,sys\nprint(json.dumps({'ok': False, 'issues': ['blocked_placeholder:\\\\bTODO\\\\b']}))\nsys.exit(1)\n",
            encoding="utf-8",
        )
        self.fake_site.chmod(0o755)
        proc, out, _, _ = self.run_cli(sample_html("<p>Revisar cada detalhe e todo o conteúdo.</p>"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        report = json.loads((out / "ivs-design-qa.report.json").read_text(encoding="utf-8"))
        component = report["components"]["ivs_site"]
        self.assertTrue(component["ok"])
        self.assertEqual(component["returncode"], 1)
        self.assertEqual(component["filtered_issues_count"], 1)

    def test_sensitive_local_report_redacts_source_and_content(self):
        self.html = self.root / "Paciente-Secreto-12345678900.html"
        html = sample_html("<h1>Paciente Secreto</h1><p>contato-interno@example.com CPF 123.456.789-00</p>")
        self.html.write_text(html, encoding="utf-8")
        out = self.root / "qa-sensitive"
        proc = subprocess.run(
            [
                "python3", str(CLI), "--input", str(self.html), "--out-dir", str(out),
                "--artifact-type", "patient-presentation", "--data-mode", "sensitive-local",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=120,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        report_text = (out / "ivs-design-qa.report.json").read_text(encoding="utf-8")
        report = json.loads(report_text)
        self.assertEqual(report["source"], "[sensitive-local-input]")
        self.assertTrue(report["governance"]["sensitive_outputs"])
        self.assertFalse(report["governance"]["patient_send_ready"])
        self.assertNotIn("contato-interno@example.com", report_text)
        self.assertNotIn("Paciente Secreto", report_text)
        self.assertNotIn("Paciente-Secreto", report_text)
        self.assertNotIn("123.456.789-00", report_text)
        self.assertNotIn(str(self.root), report_text)
        self.assertNotIn(str(self.root), proc.stdout)
        self.assertNotIn("Paciente-Secreto", proc.stdout)
        self.assertFalse(report["components"]["visual_layer"]["ran"])
        self.assertFalse((out / "visual-layer").exists())
        self.assertEqual(stat.S_IMODE(out.stat().st_mode), 0o700)
        for sensitive_file in (
            out / "ivs-design-qa.report.json",
            out / "ivs-design-qa.report.html",
            out / "browser" / "desktop.png",
            out / "browser" / "mobile.png",
        ):
            self.assertEqual(stat.S_IMODE(sensitive_file.stat().st_mode), 0o600)

    def test_output_directory_cannot_contain_or_overwrite_input(self):
        self.html = self.root / "ivs-design-qa.report.html"
        original = sample_html()
        self.html.write_text(original, encoding="utf-8")
        before = digest(self.html)
        proc = subprocess.run(
            [
                "python3", str(CLI), "--input", str(self.html), "--out-dir", str(self.root),
                "--artifact-type", "site", "--data-mode", "anonymous",
                "--ivs-site-executable", str(self.fake_site),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=120,
        )
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertEqual(before, digest(self.html))
        self.assertEqual(self.html.read_text(encoding="utf-8"), original)

    def test_placeholder_blocks_but_still_writes_evidence(self):
        proc, out, before, after = self.run_cli(sample_html("<p>TODO [preencher nome]</p>"))
        self.assertEqual(proc.returncode, 2, proc.stderr)
        summary = json.loads(proc.stdout)
        self.assertEqual(summary["status"], "BLOCKED")
        report = json.loads((out / "ivs-design-qa.report.json").read_text(encoding="utf-8"))
        self.assertIn("placeholder_detected", {item["code"] for item in report["blockers"]})
        self.assertEqual(before, after)
        self.assertTrue((out / "ivs-design-qa.report.html").is_file())


if __name__ == "__main__":
    unittest.main()
