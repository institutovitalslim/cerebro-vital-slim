import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROBE = ROOT / "scripts" / "browser_probe.mjs"


class BrowserProbeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.tmp_path = Path(self.tmp.name)

    def run_probe(self, body_css: str = "", body: str = "<section><h1>Piloto</h1></section>"):
        html = self.tmp_path / "fixture.html"
        html.write_text(
            f"""<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Piloto</title><style>html,body{{margin:0}}{body_css}</style></head><body>{body}</body></html>""",
            encoding="utf-8",
        )
        out = self.tmp_path / "out"
        proc = subprocess.run(
            ["node", str(PROBE), "--input", str(html), "--out-dir", str(out)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=90,
        )
        return proc, out

    def test_healthy_html_generates_two_screenshots_without_browser_blockers(self):
        proc, out = self.run_probe(body_css="section{max-width:900px;margin:auto;padding:24px}")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        result = json.loads(proc.stdout)
        self.assertEqual(result["blockers"], [])
        self.assertEqual({item["name"] for item in result["viewports"]}, {"desktop", "mobile"})
        self.assertTrue((out / "desktop.png").is_file())
        self.assertTrue((out / "mobile.png").is_file())
        for viewport in result["viewports"]:
            self.assertFalse(viewport["horizontal_overflow"])
            self.assertEqual(viewport["page_errors"], 0)
            self.assertEqual(viewport["broken_images"], 0)

    def test_horizontal_overflow_is_blocking(self):
        proc, _ = self.run_probe(body="<section><div style='width:2000px'>Faixa</div></section>")
        self.assertEqual(proc.returncode, 2, proc.stderr)
        result = json.loads(proc.stdout)
        codes = {item["code"] for item in result["blockers"]}
        self.assertIn("horizontal_overflow", codes)
        self.assertTrue(any(item["horizontal_overflow"] for item in result["viewports"]))


if __name__ == "__main__":
    unittest.main()
