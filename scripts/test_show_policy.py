"""
Tests for fishwrap.show (the text edition) and fishwrap.policy (the
Publisher's pen): every verb files the right event, the loader applies it,
a strike retires it, and the text view carries what the Publisher needs.

Run: python3 scripts/test_show_policy.py
Or:  make test
"""
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)

import fixtures_runsheet as fx  # noqa: E402
from fishwrap import policy, show  # noqa: E402
from fishwrap.masthead import Masthead  # noqa: E402


class ShowTests(unittest.TestCase):

    def test_text_edition(self):
        with tempfile.TemporaryDirectory() as tmp:
            m = Masthead.load(fx.write_instance(Path(tmp)))
            header, records, _ = fx.build_runsheet(m)
            text = show.render(header, records, cuts=5)
            self.assertIn("Fixture Paper · edition 2026-10-26 · 5 of 10 candidates", text)
            self.assertIn("NEWS · 3 of 3 ·", text)
            self.assertIn("1 LEAD [2 src] Senate passes the budget after a long night  — alpha.example", text)
            self.assertIn("cut by cap (2): alpha.example 2", text)
            self.assertIn("SPORTS · 2 of 2", text)
            self.assertIn("cut by capacity (1)", text)
            self.assertIn("full World Cup draw announced in Zurich", text)
            self.assertIn("feeds that delivered nothing (1 of 5):\n  https://silent.example/feed", text)
            only = show.render(header, records, section="sports")
            self.assertNotIn("NEWS", only)
            self.assertNotIn("feeds that delivered nothing", only)


class PolicyTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.inst = fx.write_instance(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = policy.main([*argv, "--instance", str(self.inst)])
        return rc, out.getvalue(), err.getvalue()

    def _events(self):
        return [json.loads(ln) for ln in (self.inst / "policies.jsonl").read_text().splitlines() if ln.strip()]

    def test_every_verb_files_and_applies(self):
        self.assertEqual(self._run("ban-source", "alpha.example", "--because", "Alpha is a rewrite shop.")[0], 0)
        self.assertEqual(self._run("ban-title", r"(?i)\bopen thread\b", "--because", "No open threads.")[0], 0)
        self.assertEqual(self._run("ban-topic", "horoscope", "astrology", "--because", "No stars.")[0], 0)
        self.assertEqual(self._run("print-all", "beta.example", "--except", "^Ad:", "--because", "Beta prints all.")[0], 0)
        self.assertEqual(self._run("prefer-lead", "sports", "playoffs", "final", "--because", "Playoffs lead.")[0], 0)
        ev = self._events()[2:]  # after the fixture's two
        self.assertEqual([e["policy"]["type"] for e in ev],
                         ["source_ban", "title_pattern_ban", "topic_ban", "source_whitelist", "section_lead_preference"])
        self.assertEqual(ev[2]["policy"]["phrases"], ["horoscope", "astrology"])
        self.assertEqual(ev[3]["policy"]["except_pattern"], "^Ad:")
        self.assertEqual(ev[4]["policy"], {"type": "section_lead_preference", "section": "sports",
                                           "lead_keywords": ["playoffs", "final"]})
        self.assertTrue(all(e["sentence"] for e in ev))
        self.assertTrue(all(e["created"] for e in ev))
        m = Masthead.load(self.inst)
        self.assertEqual(len(m.policies), 7)
        # the ban is live: alpha's stories leave the paper
        header, records, _ = fx.build_runsheet(m)
        self.assertEqual([r["fate"]["step"] for r in records if r["domain"] == "alpha.example"], ["policy"] * 4)

    def test_strike_retires_a_policy(self):
        rc, out, _ = self._run("ban-source", "alpha.example", "--because", "x")
        pid = self._events()[-1]["policy_id"]
        self.assertIn(f"filed {pid}", out)
        self.assertEqual(self._run("strike", pid, "--because", "Changed my mind.")[0], 0)
        self.assertNotIn(pid, [p["policy_id"] for p in Masthead.load(self.inst).policies])
        self.assertEqual(self._run("strike", "nope", "--because", "x")[0], 2)

    def test_ids_are_unique_per_day_and_sentence_is_required(self):
        self._run("ban-source", "alpha.example", "--because", "one")
        self._run("ban-source", "alpha.example", "--because", "two")
        ids = [e["policy_id"] for e in self._events()[2:]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(ids[1].endswith("-2"))
        rc, _, err = self._run("ban-source", "gamma.example")
        self.assertEqual(rc, 2)
        self.assertIn("--because is required", err)

    def test_validation(self):
        self.assertEqual(self._run("ban-title", "(unclosed", "--because", "x")[0], 2)
        rc, _, err = self._run("prefer-lead", "nosuch", "kw", "--because", "x")
        self.assertEqual(rc, 2)
        self.assertIn("no section", err)

    def test_list(self):
        rc, out, _ = self._run("list")
        self.assertEqual(rc, 0)
        self.assertIn("p-ban", out)
        self.assertIn("Never print banned.example.", out)


if __name__ == "__main__":
    unittest.main()
