import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "ivs_visual_layer.py"
spec = importlib.util.spec_from_file_location("ivs_visual_layer", MODULE_PATH)
assert spec is not None and spec.loader is not None
mod = importlib.util.module_from_spec(spec)
sys.modules["ivs_visual_layer"] = mod
spec.loader.exec_module(mod)


class IVSVisualLayerEditTests(unittest.TestCase):
    def test_edit_spec_text_replace_generates_edited_copy_and_diff_without_touching_original(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_path = Path(td)
            src = tmp_path / "sample.html"
            original = """<!doctype html><html><head><style>@media screen{body{}}</style><title>Teste</title></head><body><section id=\"hero\" class=\"section hero\"><h1>Título antigo</h1></section></body></html>"""
            src.write_text(original, encoding="utf-8")
            spec_path = tmp_path / "edit.json"
            spec_path.write_text(json.dumps({
                "operations": [
                    {"type": "text_replace", "old": "Título antigo", "new": "Título novo", "count": 1}
                ]
            }), encoding="utf-8")

            audit = mod.run(src, tmp_path / "out", "presentation-v12", edit_spec_path=spec_path)

            edited = Path(audit["edit"]["edited_html"])
            diff = Path(audit["edit"]["diff_file"])
            self.assertEqual(src.read_text(encoding="utf-8"), original)
            self.assertTrue(edited.exists())
            self.assertTrue(diff.exists())
            self.assertIn("Título novo", edited.read_text(encoding="utf-8"))
            diff_text = diff.read_text(encoding="utf-8")
            self.assertIn("-", diff_text)
            self.assertIn("+", diff_text)
            self.assertEqual(audit["edit"]["operations_applied"], 1)

    def test_edit_spec_add_class_targets_section_by_id(self):
        with tempfile.TemporaryDirectory() as td:
            tmp_path = Path(td)
            src = tmp_path / "sample.html"
            src.write_text("""<!doctype html><html><head><style>@media screen{body{}}</style><title>Teste</title></head><body><section id=\"final-cta\" class=\"section final\"><h2>Decisão</h2></section></body></html>""", encoding="utf-8")
            spec_path = tmp_path / "edit.json"
            spec_path.write_text(json.dumps({
                "operations": [
                    {"type": "add_class", "id": "final-cta", "class": "ivs-review-focus"}
                ]
            }), encoding="utf-8")

            audit = mod.run(src, tmp_path / "out", "presentation-v12", edit_spec_path=spec_path)

            edited_text = Path(audit["edit"]["edited_html"]).read_text(encoding="utf-8")
            self.assertIn('id="final-cta"', edited_text)
            self.assertIn("ivs-review-focus", edited_text)
            self.assertEqual(audit["edit"]["operations_applied"], 1)


if __name__ == "__main__":
    unittest.main()
