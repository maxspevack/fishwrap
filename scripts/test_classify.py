"""
Unit tests for fishwrap.editor.classify — section routing.

Run: python3 scripts/test_classify.py
Or:  make test
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class _FakeMasthead:
    """Minimal masthead-like object with just what classify() reads."""

    def __init__(self, sections, source_sections):
        self.sections = sections
        self.source_sections = source_sections


SECTIONS = [
    {"id": "news",   "title": "News",   "keywords": ["politics", "election"]},
    {"id": "sports", "title": "Sports", "keywords": ["nba", "stanley cup"]},
    {"id": "tech",   "title": "Tech",   "keywords": ["python", "linux"]},
    {"id": "gala",   "title": "Gala",   "keywords": []},
]

SOURCE_SECTIONS = {
    "defector.com": "sports",
    "nytimes.com": "news",
}


class ClassifyTests(unittest.TestCase):

    def setUp(self):
        from fishwrap import editor
        self.editor = editor
        self.masthead = _FakeMasthead(SECTIONS, SOURCE_SECTIONS)

    def test_source_default_wins(self):
        # nytimes.com → news even if the title talks about NBA
        art = {"title": "NBA Finals tonight", "content": "", "source_url": "https://nytimes.com/foo",
               "categories": None}
        sid, reason = self.editor.classify(art, self.masthead)
        self.assertEqual(sid, "news")
        self.assertEqual(reason["path"], "source_default")
        self.assertEqual(reason["match"], "nytimes.com")

    def test_keyword_fallback_finds_best_section(self):
        # source has no default; title matches sports keywords
        art = {"title": "NBA finals, stanley cup, basketball",
               "content": "", "source_url": "https://random.example/foo",
               "categories": None}
        sid, reason = self.editor.classify(art, self.masthead)
        self.assertEqual(sid, "sports")
        self.assertEqual(reason["path"], "keyword_fallback")
        self.assertGreater(len(reason["matched_terms"]), 0)

    def test_keyword_fallback_ties_pick_first_declared(self):
        # one news keyword AND one tech keyword; news is declared first
        art = {"title": "election day python release", "content": "",
               "source_url": "https://other.example/foo", "categories": None}
        sid, _ = self.editor.classify(art, self.masthead)
        self.assertEqual(sid, "news")  # declared first wins on tie

    def test_fallback_routes_to_last_section(self):
        # no source default, no keyword matches → last declared section (gala)
        art = {"title": "Generic story about clouds", "content": "",
               "source_url": "https://other.example/foo", "categories": None}
        sid, reason = self.editor.classify(art, self.masthead)
        self.assertEqual(sid, "gala")
        self.assertEqual(reason["path"], "fallback")

    def test_content_searched_when_title_empty(self):
        art = {"title": "", "content": "Talking about NBA and stanley cup",
               "source_url": "https://other.example/foo", "categories": None}
        sid, _ = self.editor.classify(art, self.masthead)
        self.assertEqual(sid, "sports")

    def test_word_boundary_matching(self):
        # "election" must match, but "selection" must not
        art = {"title": "Voter selection process",  # 'selection' contains 'election'
               "content": "", "source_url": "https://other.example/foo",
               "categories": None}
        sid, reason = self.editor.classify(art, self.masthead)
        # selection is not election; with no other matches, fallback to gala
        self.assertEqual(sid, "gala")

    def test_keyword_phrase_with_space(self):
        # "stanley cup" is one keyword (two words). Verify it matches.
        art = {"title": "Stanley Cup Final", "content": "",
               "source_url": "https://other.example/foo", "categories": None}
        sid, reason = self.editor.classify(art, self.masthead)
        self.assertEqual(sid, "sports")
        self.assertIn("stanley cup", reason["matched_terms"])


if __name__ == "__main__":
    unittest.main()
