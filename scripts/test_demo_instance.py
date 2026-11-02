"""
Integrity of the demo instance in demo/.

demo/ is the engine's integration environment: the demo workflow builds it
from main every day and publishes it to fishwrap.org/demo/vanilla/. A config
defect there is a red build, so it is checked here, with the suite.

Run: python3 scripts/test_demo_instance.py
Or:  make test
"""
import os
import sys
import unittest
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, str(ROOT))

from fishwrap.masthead import Masthead  # noqa: E402

DEMO = ROOT / "demo"


class DemoInstanceTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.m = Masthead.load(DEMO)

    def test_identity(self):
        self.assertEqual(self.m.name, "The Vanilla")
        self.assertTrue(self.m.timezone)

    def test_no_vote_ranked_sources(self):
        # Dropped 2026-11-01 (Max): Reddit answers feed fetches with a login
        # page (302 /login/?reason=lor2 or 403), and with Reddit gone Hacker
        # News was the last vote-ranked source. Votes are not an ordering
        # input; coverage across sources is. The engine no longer carries
        # vote plumbing, so these come back as a card field, if ever.
        for marker in ("reddit.com", "hnrss.org", "news.ycombinator.com"):
            self.assertEqual([u for u in self.m.feeds if marker in u], [], marker)
            self.assertEqual([k for k in self.m.source_sections if marker in k], [], marker)

    def test_feeds_are_unique_well_formed_urls(self):
        self.assertEqual(len(self.m.feeds), len(set(self.m.feeds)))
        for u in self.m.feeds:
            parsed = urlparse(u)
            self.assertIn(parsed.scheme, ("http", "https"), u)
            self.assertTrue(parsed.netloc, u)

    def test_routing_targets_are_declared_sections(self):
        declared = {s["id"] for s in self.m.sections}
        for dom, sid in self.m.source_sections.items():
            self.assertIn(sid, declared, f"{dom} routes to {sid}")

    def test_section_tier_counts_fit_edition_size(self):
        for s in self.m.sections:
            self.assertLessEqual(
                s["lead_count"] + s["feature_count"], s["edition_size"],
                f"section {s['id']}: lead_count + feature_count exceeds edition_size",
            )


if __name__ == "__main__":
    unittest.main()
