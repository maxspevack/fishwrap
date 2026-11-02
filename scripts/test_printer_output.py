"""
Tests for the printer: edition date, the 'today' pointer, and the pages
rendered from a fixture runsheet (paper, runsheet page, feeds, Morgue).

Run: python3 scripts/test_printer_output.py
Or:  make test
"""
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)

import fixtures_runsheet as fx  # noqa: E402
from fishwrap import printer  # noqa: E402
from fishwrap.masthead import Masthead  # noqa: E402
from fishwrap.runsheet import edition_date  # noqa: E402


class _Masthead:
    timezone = "America/Los_Angeles"


class EditionDateTests(unittest.TestCase):

    def test_utc_build_before_midnight_pacific_is_previous_day(self):
        now = datetime(2026, 11, 2, 5, 0, tzinfo=timezone.utc)   # 21:00 PST on the 1st
        self.assertEqual(edition_date(_Masthead(), now), "2026-11-01")

    def test_workflow_cron_time_is_same_day(self):
        now = datetime(2026, 11, 2, 13, 0, tzinfo=timezone.utc)  # 05:00 PST on the 2nd
        self.assertEqual(edition_date(_Masthead(), now), "2026-11-02")

    def test_naive_datetime_is_treated_as_utc(self):
        self.assertEqual(edition_date(_Masthead(), datetime(2026, 11, 2, 5, 0)), "2026-11-01")


class PointerTests(unittest.TestCase):

    def test_pointer_redirects_to_dated_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = printer.write_pointer(Path(tmp), "2026-11-02")
            html = p.read_text()
            self.assertEqual(p.name, "index.html")
            self.assertIn('http-equiv="refresh"', html)
            self.assertIn("url=2026-11-02/", html)


class RenderTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.masthead = Masthead.load(fx.write_instance(Path(self.tmp.name)))
        self.header, self.records, _ = fx.build_runsheet(self.masthead)

    def tearDown(self):
        self.tmp.cleanup()

    def test_paper(self):
        html = printer.render_paper(self.masthead, self.header, self.records)
        self.assertIn("<h1>Fixture Paper</h1>", html)
        self.assertIn("Senate passes the budget after a long night", html)
        self.assertNotIn("A story from the banned source", html)
        self.assertIn("Carried by <strong>2</strong> sources", html)        # the a4/b1 cluster
        self.assertIn("beta.example; those copies were folded", html)
        self.assertIn("<strong>print all</strong>", html)                   # gamma's whitelist in the drawer
        self.assertIn('href="runsheet.jsonl.gz"', html)
        self.assertIn("silent.example", html)                               # zero-yield feed flagged
        for gone in ("Glenn", "edition-reader", 'href="#"', "Sign in", "Upvotes"):
            self.assertNotIn(gone, html)

    def test_runsheet_page(self):
        html = printer.render_runsheet_page(self.masthead, self.header, self.records)
        self.assertIn("<strong>10</strong> stories arrived", html)
        self.assertIn("Never print banned.example.", html)                 # policy group
        self.assertIn("A story from the banned source", html)              # the excluded story is listed
        self.assertIn("Cut by the per-source cap: 2 stories", html)        # news: alpha's third and fourth
        self.assertIn("Cut by capacity: 1 story", html)                    # sports: gamma's third
        self.assertIn("Never print banned.example. · 1 story", html)
        self.assertIn("2 copies from 2 sources", html)                     # the duplicate cluster
        self.assertIn('class="flag"', html)                                # silent feed row
        self.assertIn("masthead " + self.header["masthead_sha"], html)

    def test_feeds_page(self):
        html = printer.render_feeds(self.masthead, self.header, self.records)
        for url in self.masthead.feeds:
            self.assertIn(url, html)
        self.assertIn("print all: Print everything gamma files.", html)
        self.assertIn("never: Never print banned.example.", html)
        self.assertIn("read-only", html)

    def test_morgue_without_history_and_without_restore(self):
        html = printer.render_morgue(self.masthead, entries=[])
        self.assertIn("The Morgue", html)
        for gone in ("republish", "Republish", "restore"):
            self.assertNotIn(gone, html)

    def test_write_edition_writes_every_page(self):
        out = Path(self.tmp.name) / "out" / "2026-10-26"
        written = {p.name for p in printer.write_edition(self.masthead, self.header, self.records, out)}
        self.assertEqual(written, {"index.html", "runsheet.html", "feeds.html", "morgue.html"})


if __name__ == "__main__":
    unittest.main()
