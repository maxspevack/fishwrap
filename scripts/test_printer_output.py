"""
Tests for the printer's edition date and 'today' pointer.

Run: python3 scripts/test_printer_output.py
Or:  make test
"""
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fishwrap.printer import edition_date, write_pointer  # noqa: E402


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

    def test_default_now_is_a_date(self):
        self.assertRegex(edition_date(_Masthead()), r"^\d{4}-\d{2}-\d{2}$")


class PointerTests(unittest.TestCase):

    def test_pointer_redirects_to_dated_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = write_pointer(Path(tmp), "2026-11-02")
            self.assertEqual(p.name, "index.html")
            html = p.read_text()
            self.assertIn('http-equiv="refresh"', html)
            self.assertIn("url=2026-11-02/", html)
            self.assertIn('href="2026-11-02/"', html)


if __name__ == "__main__":
    unittest.main()
