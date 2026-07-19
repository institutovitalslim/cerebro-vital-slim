import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.services.motion_video_theme_collector import (
    build_theme_ingest_payload,
    parse_hashtag_posts,
    theme_tags,
)


class MotionThemeCollectorTests(unittest.TestCase):
    def test_theme_tags_has_menopause_seed_set(self):
        tags = theme_tags("menopausa", "")
        self.assertIn("menopausa", tags)
        self.assertIn("climaterio", tags)
        self.assertLessEqual(len(tags), 12)

    def test_parse_hashtag_posts_filters_and_scores_menopause(self):
        data = {
            "posts": {
                "edges": [
                    {"node": {"shortcode": "ABC", "is_video": True, "edge_liked_by": {"count": 10}, "edge_media_to_comment": {"count": 2}, "edge_media_to_caption": {"edges": [{"node": {"text": "Menopausa, sono e fogachos precisam de avaliação."}}]}}},
                    {"node": {"shortcode": "NOISE", "edge_liked_by": {"count": 999}, "edge_media_to_caption": {"edges": [{"node": {"text": "Receita aleatória sem relação."}}]}}},
                ]
            }
        }
        items = parse_hashtag_posts("menopausa", "fogachos", data, limit=10)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["shortcode"], "ABC")
        self.assertEqual(items[0]["score"], 20)
        self.assertEqual(items[0]["format"], "reel")

    def test_build_theme_ingest_payload_is_safe_reference(self):
        payload = build_theme_ingest_payload({
            "shortcode": "ABC",
            "url": "https://www.instagram.com/reel/ABC/",
            "caption": "Menopausa não é frescura: sono, humor e metabolismo mudam.",
            "likes": 40,
            "comments": 3,
            "score": 55,
            "hashtag": "menopausa",
            "format": "reel",
        }, topic="menopausa")
        self.assertEqual(payload["external_id"], "instagram:ABC")
        self.assertEqual(payload["source_type"], "rapidapi_instagram_theme_search")
        self.assertEqual(payload["content_format"], "sinal_escondido")
        self.assertEqual(payload["compliance_risk"], "review_required")
        self.assertIn("não copiar", payload["why_this_example_works"].lower())


if __name__ == "__main__":
    unittest.main()
