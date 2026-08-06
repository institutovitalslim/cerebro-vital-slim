import base64
import json
import os
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

    def test_external_browser_request_is_blocked_and_reported(self):
        body = "<section><h1>Piloto</h1><script src='https://example.invalid/remote.js'></script></section>"
        proc, _ = self.run_probe(body=body)
        self.assertIn(proc.returncode, (0, 2), proc.stderr)
        data = json.loads(proc.stdout)
        self.assertIn("external_request_blocked", {item["code"] for item in data["concerns"]})
        self.assertTrue(any(item["blocked_external_requests"] for item in data["viewports"]))

    def test_browser_launch_failure_closes_server_and_exits(self):
        html = self.tmp_path / "fixture.html"
        html.write_text("<!doctype html><html><head><title>x</title></head><body><section>x</section></body></html>", encoding="utf-8")
        env = {**os.environ, "CHROMIUM_PATH": "/nonexistent/chromium"}
        try:
            proc = subprocess.run(
                ["node", str(PROBE), "--input", str(html), "--out-dir", str(self.tmp_path / "out-launch")],
                cwd=ROOT,
                text=True,
                capture_output=True,
                timeout=10,
                env=env,
            )
        except subprocess.TimeoutExpired as error:
            self.fail(f"probe não encerrou após falha de launch: {error}")
        self.assertEqual(proc.returncode, 1)

    def test_unreferenced_sibling_file_is_not_served(self):
        (self.tmp_path / "secret.txt").write_text("segredo-local", encoding="utf-8")
        body = """<section><h1>Piloto</h1><!-- <img src='secret.txt'> --><script>const decoy = '<img src="secret.txt">'; fetch('secret.txt').then(r=>{if(r.ok){throw new Error('unreferenced sibling readable')}})</script></section>"""
        proc, _ = self.run_probe(body=body)
        self.assertEqual(proc.returncode, 2, proc.stderr)
        data = json.loads(proc.stdout)
        codes = {item["code"] for item in data["blockers"]}
        self.assertIn("console_error", codes)
        self.assertNotIn("page_error", codes)

    def test_declared_relative_assets_are_served(self):
        pixel = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Y9Z3V0AAAAASUVORK5CYII=")
        (self.tmp_path / "pixel.png").write_bytes(pixel)
        (self.tmp_path / "style.css").write_text("body{background-image:url('pixel.png')}", encoding="utf-8")
        proc, _ = self.run_probe(body="<link rel='stylesheet' href='style.css'><section><h1>Piloto</h1></section>")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = json.loads(proc.stdout)
        self.assertEqual(data["blockers"], [])

    def test_static_server_rejects_symlink_escape(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            site = root / "site"
            site.mkdir()
            outside = root / "outside.png"
            outside.write_bytes(base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Y9Z3V0AAAAASUVORK5CYII="))
            (site / "escape.png").symlink_to(outside)
            html = site / "index.html"
            html.write_text(
                "<!doctype html><html><head><meta name='viewport' content='width=device-width'><title>x</title></head><body><section><img src='escape.png' alt='teste'></section></body></html>",
                encoding="utf-8",
            )
            out = root / "out"
            proc = subprocess.run(
                ["node", str(PROBE), "--input", str(html), "--out-dir", str(out)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                timeout=90,
            )
            self.assertEqual(proc.returncode, 2, proc.stderr)
            data = json.loads(proc.stdout)
            self.assertIn("broken_images", {item["code"] for item in data["blockers"]})

    def test_rendered_page_without_section_is_blocking(self):
        proc, _ = self.run_probe(body="<main><h1>Sem seção</h1></main>")
        self.assertEqual(proc.returncode, 2, proc.stderr)
        data = json.loads(proc.stdout)
        self.assertIn("semantic_section_missing_browser", {item["code"] for item in data["blockers"]})

    def test_nested_horizontal_scroll_is_a_concern(self):
        body = """<section><div style="width:100%;max-width:100%;overflow-x:auto"><table style="width:2000px"><tr><td>x</td></tr></table></div></section>"""
        proc, _ = self.run_probe(body=body)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = json.loads(proc.stdout)
        self.assertIn("nested_horizontal_scroll", {item["code"] for item in data["concerns"]})

    def test_horizontal_overflow_is_blocking(self):
        proc, _ = self.run_probe(body="<section><div style='width:2000px'>Faixa</div></section>")
        self.assertEqual(proc.returncode, 2, proc.stderr)
        result = json.loads(proc.stdout)
        codes = {item["code"] for item in result["blockers"]}
        self.assertIn("horizontal_overflow", codes)
        self.assertTrue(any(item["horizontal_overflow"] for item in result["viewports"]))


if __name__ == "__main__":
    unittest.main()
