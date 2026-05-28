"""
Unit tests for the full editor pipeline — exclusion → classify → dedup →
diversify → truncate → tier.

Run: python3 scripts/test_pipeline.py
Or:  make test
"""
import os
import sys
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class _FakeMasthead:
    def __init__(self, sections, source_sections, policies=None):
        self.sections = sections
        self.source_sections = source_sections
        self.policies = policies or []


SECTIONS = [
    {"id": "news",   "title": "News",   "edition_size": 3,
     "lead_count": 1, "feature_count": 1, "max_per_source": 2, "keywords": []},
    {"id": "sports", "title": "Sports", "edition_size": 3,
     "lead_count": 1, "feature_count": 1, "max_per_source": 2, "keywords": []},
]

SOURCE_SECTIONS = {
    "alpha.example": "news",
    "beta.example": "news",
    "gamma.example": "sports",
}


def _art(aid, title, source, ts_offset=0):
    """Helper: build a candidate article dict."""
    return {
        "id": aid,
        "title": title,
        "content": "",
        "source_url": f"https://{source}/article/{aid}",
        "timestamp": time.time() - ts_offset,
        "categories": None,
        "stats_score": 0,
        "stats_comments": 0,
    }


class PipelineTests(unittest.TestCase):

    def setUp(self):
        from fishwrap import editor
        self.editor = editor

    def test_basic_classify_and_select(self):
        # Distinct titles so fuzzy dedup doesn't collapse them.
        articles = [
            _art("a1", "Congress passes infrastructure overhaul", "alpha.example", ts_offset=10),
            _art("a2", "Federal Reserve cuts interest rates again", "beta.example",  ts_offset=20),
            _art("a3", "Hurricanes win Stanley Cup in overtime",   "gamma.example", ts_offset=30),
        ]
        masthead = _FakeMasthead(SECTIONS, SOURCE_SECTIONS)
        edition, rejects, funnel = self.editor.select_edition(articles, masthead)
        self.assertEqual(len(edition["news"]), 2)
        self.assertEqual(len(edition["sports"]), 1)
        self.assertEqual(funnel["intake"], 3)
        self.assertEqual(funnel["after_dedup"], 3)

    def test_diversity_cap_drops_extras_from_same_source(self):
        # max_per_source for news is 2; supply 4 from same source.
        # Distinct titles so fuzzy dedup doesn't collapse them.
        articles = [
            _art("a1", "Senate passes budget bill",          "alpha.example", ts_offset=10),
            _art("a2", "Supreme Court rules on case",        "alpha.example", ts_offset=20),
            _art("a3", "President signs executive order",    "alpha.example", ts_offset=30),
            _art("a4", "Federal regulator announces probe",  "alpha.example", ts_offset=40),
        ]
        masthead = _FakeMasthead(SECTIONS, SOURCE_SECTIONS)
        edition, rejects, _ = self.editor.select_edition(articles, masthead)
        self.assertEqual(len(edition["news"]), 2)  # cap kicked in
        self.assertEqual(
            sum(1 for r in rejects.get("news", []) if r["reason"] == "diversity_cap"),
            2,
        )

    def test_truncate_to_edition_size(self):
        # max_per_source=2 limits gamma to 2 in sports; we expect 2 selected.
        # Distinct titles so fuzzy dedup doesn't collapse them.
        SPORTS_TITLES = [
            "Knicks win Game 7",
            "Stanley Cup Finals begin tonight",
            "World Cup draw announced today",
            "Hurricanes acquire star defenseman",
            "NFL training camp opens Tuesday",
        ]
        articles = [
            _art(f"g{i}", SPORTS_TITLES[i], "gamma.example", ts_offset=i * 10)
            for i in range(5)
        ]
        masthead = _FakeMasthead(SECTIONS, SOURCE_SECTIONS)
        edition, _rejects, _ = self.editor.select_edition(articles, masthead)
        self.assertEqual(len(edition["sports"]), 2)

    def test_lead_and_feature_tiers(self):
        # Distinct titles so fuzzy dedup doesn't collapse them.
        ALPHA_TITLES = [
            "Senate passes budget bill",
            "Supreme Court rules on case",
            "President signs executive order",
            "Federal regulator announces probe",
            "Congressional hearing draws crowd",
        ]
        articles = [
            _art(f"a{i}", ALPHA_TITLES[i], "alpha.example", ts_offset=i * 10)
            for i in range(5)
        ]
        articles += [_art("b1", "Climate report released this morning",
                          "beta.example", ts_offset=15)]
        masthead = _FakeMasthead(SECTIONS, SOURCE_SECTIONS)
        edition, _, _ = self.editor.select_edition(articles, masthead)
        if edition["news"]:
            self.assertEqual(edition["news"][0]["_tier"], "lead")
            if len(edition["news"]) > 1:
                self.assertEqual(edition["news"][1]["_tier"], "feature")

    def test_dedup_collapses_similar_titles(self):
        # Three near-identical titles; dedup should keep only the first
        articles = [
            _art("a1", "Pope Leo XIV apologizes for slavery role", "alpha.example", ts_offset=10),
            _art("a2", "Pope Leo XIV apologizes for slavery role today", "beta.example", ts_offset=20),
            _art("a3", "Pope Leo XIV apologizes for the Holy See's slavery role", "gamma.example", ts_offset=30),
        ]
        masthead = _FakeMasthead(SECTIONS, SOURCE_SECTIONS)
        _edition, _, funnel = self.editor.select_edition(articles, masthead)
        self.assertGreaterEqual(funnel["deduped_out"], 1)

    def test_source_ban_drops_article(self):
        policies = [{
            "policy_id": "p1",
            "sentence": "ban alpha",
            "policy": {"type": "source_ban", "match": "alpha.example"},
        }]
        articles = [
            _art("a1", "Story from banned alpha source",  "alpha.example", ts_offset=10),
            _art("a2", "Story from allowed beta source",  "beta.example",  ts_offset=20),
        ]
        masthead = _FakeMasthead(SECTIONS, SOURCE_SECTIONS, policies=policies)
        edition, _, funnel = self.editor.select_edition(articles, masthead)
        self.assertEqual(funnel["dropped_by_policy"], 1)
        all_ids = [a["id"] for arts in edition.values() for a in arts]
        self.assertNotIn("a1", all_ids)
        self.assertIn("a2", all_ids)

    def test_title_pattern_ban_drops_article(self):
        policies = [{
            "policy_id": "p1",
            "sentence": "ban open thread",
            "policy": {"type": "title_pattern_ban", "pattern": r"(?i)\bopen thread\b"},
        }]
        articles = [
            _art("a1", "Open Thread for May 27", "alpha.example"),
            _art("a2", "Real news today",        "beta.example"),
        ]
        masthead = _FakeMasthead(SECTIONS, SOURCE_SECTIONS, policies=policies)
        _edition, _, funnel = self.editor.select_edition(articles, masthead)
        self.assertEqual(funnel["dropped_by_policy"], 1)

    def test_source_whitelist_bypasses_diversity_cap(self):
        policies = [{
            "policy_id": "p1",
            "sentence": "whitelist gamma",
            "policy": {"type": "source_whitelist", "match": "gamma.example"},
        }]
        # Supply 4 articles from gamma; cap is 2 but whitelist bypasses
        articles = [
            _art(f"g{i}", f"G{i}", "gamma.example", ts_offset=i * 10)
            for i in range(4)
        ]
        masthead = _FakeMasthead(SECTIONS, SOURCE_SECTIONS, policies=policies)
        edition, _, _ = self.editor.select_edition(articles, masthead)
        self.assertEqual(len(edition["sports"]), 3)  # edition_size, not cap

    def test_section_lead_preference_promotes_to_lead(self):
        policies = [{
            "policy_id": "p1",
            "sentence": "prefer NBA",
            "policy": {
                "type": "section_lead_preference",
                "section": "sports",
                "lead_keywords": ["nba"],
            },
        }]
        articles = [
            _art("a1", "Soccer story", "gamma.example", ts_offset=10),
            _art("a2", "NBA Finals tonight", "gamma.example", ts_offset=20),
        ]
        masthead = _FakeMasthead(SECTIONS, SOURCE_SECTIONS, policies=policies)
        edition, _, _ = self.editor.select_edition(articles, masthead)
        # NBA should be lead even though Soccer is fresher
        leads = [a for a in edition["sports"] if a["_tier"] == "lead"]
        self.assertTrue(any("NBA" in a["title"] for a in leads))


if __name__ == "__main__":
    unittest.main()
