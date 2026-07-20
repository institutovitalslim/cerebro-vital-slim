import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path('/root/cerebro-vital-slim/skills/ivs-motion-layer')
SCRIPT = ROOT / 'scripts' / 'apply_motion.py'
DEMO = ROOT / 'examples' / 'demo-apresentacao-ivs-motion.html'


class IVSMotionLayerTest(unittest.TestCase):
    def test_assets_exist_and_have_core_integrations(self):
        js = (ROOT / 'assets' / 'ivs-motion.js').read_text(encoding='utf-8')
        css = (ROOT / 'assets' / 'ivs-motion.css').read_text(encoding='utf-8')
        self.assertIn('lenis@1.3.25', js)
        self.assertIn('gsap@3.15.0', js)
        self.assertIn('vanta@0.5.24', js)
        self.assertIn('prefers-reduced-motion', css)
        self.assertIn('data-ivs-motion="off"', css)

    def test_apply_motion_injects_assets_without_overwriting_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            src = tmp_path / 'input.html'
            out = tmp_path / 'output.html'
            src.write_text('<!doctype html><html><head><title>x</title></head><body><section><div class="card">A</div></section></body></html>', encoding='utf-8')
            result = subprocess.run(['python3', str(SCRIPT), str(src), '--out', str(out), '--profile', 'presentation', '--vanta'], text=True, capture_output=True, check=True)
            generated = out.read_text(encoding='utf-8')
            original = src.read_text(encoding='utf-8')
            self.assertIn(str(out.resolve()), result.stdout)
            self.assertIn('id="ivs-motion-css"', generated)
            self.assertIn('id="ivs-motion-js"', generated)
            self.assertIn('data-ivs-motion="fade-up"', generated)
            self.assertIn('ivs-motion-assets/ivs-motion.css', generated)
            self.assertNotIn('id="ivs-motion-css"', original)
            self.assertTrue((tmp_path / 'ivs-motion-assets' / 'ivs-motion.js').exists())

    def test_demo_has_required_presets_and_no_secrets(self):
        html = DEMO.read_text(encoding='utf-8')
        required = ['data-ivs-counter', 'data-ivs-progress', 'data-ivs-vanta', 'split-title', 'ivs-motion-assets/ivs-motion.js']
        for token in required:
            self.assertIn(token, html)
        forbidden = [r'RAPIDAPI_KEY', r'OPENAI_API_KEY', r'AIza[0-9A-Za-z_-]+', r'sk-[0-9A-Za-z_-]{20,}', r'Bearer\s+[0-9A-Za-z._-]+']
        for pattern in forbidden:
            self.assertIsNone(re.search(pattern, html))


if __name__ == '__main__':
    unittest.main()
