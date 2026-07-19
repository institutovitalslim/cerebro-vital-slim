import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(PROJECT / "scripts"))

from motion_video_phase4_collect import build_ingest_payload, choose_content_format  # noqa: E402


class MotionPhase4CollectorTests(unittest.TestCase):
    def test_choose_content_format_for_menopause_caption(self):
        caption = "Menopausa não é só parar de menstruar: cérebro, sono, músculo e metabolismo mudam."
        self.assertEqual(choose_content_format(caption), "sinal_escondido")

    def test_build_ingest_payload_is_governed(self):
        item = {
            "shortcode": "MENOPAUSA123",
            "url": "https://www.instagram.com/p/MENOPAUSA123/",
            "caption": "Menopausa não é frescura. Fogachos, sono e metabolismo merecem avaliação.",
            "score": 220,
            "likes": 120,
            "comments": 20,
            "hashtag": "menopausa",
            "format": "post",
        }
        payload = build_ingest_payload(item, topic="menopausa")
        self.assertEqual(payload["content_format"], "sinal_escondido")
        self.assertEqual(payload["external_id"], "instagram:MENOPAUSA123")
        self.assertEqual(payload["source_type"], "rapidapi_instagram_theme_search")
        self.assertEqual(payload["compliance_risk"], "review_required")
        self.assertIn("não copiar", payload["why_this_example_works"].lower())
        self.assertLessEqual(len(payload["transcript_summary"]), 520)


if __name__ == "__main__":
    unittest.main()
