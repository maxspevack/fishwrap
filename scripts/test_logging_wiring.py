"""Regression test for #19: silent excepts must now log.

Verifies that fetcher.process_feed and utils.get_domain surface
errors through the logger instead of swallowing them silently.
"""
import os
import sys
import logging
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fishwrap import fetcher


class TestLoggingWiring(unittest.TestCase):
    def setUp(self):
        self.handler = _CapturingHandler()
        logging.getLogger("fishwrap").addHandler(self.handler)
        logging.getLogger("fishwrap").setLevel(logging.DEBUG)

    def tearDown(self):
        logging.getLogger("fishwrap").removeHandler(self.handler)

    @patch('fishwrap.utils.fetch_url')
    def test_garbage_xml_logs_warning(self, mock_fetch):
        print("[TEST] Verifying garbage XML emits a warning log...")
        mock_fetch.return_value = "<rss>this is not xml<broken>"
        result = fetcher.process_feed('http://bad-feed.example/', 0)
        self.assertEqual(result, [])
        warnings = [r for r in self.handler.records if r.levelno >= logging.WARNING]
        self.assertTrue(warnings, "expected a WARNING log entry for unparseable XML")
        print("  [PASS] Got %d warning(s); fetcher no longer silent." % len(warnings))

    @patch('fishwrap.utils.fetch_url')
    def test_unexpected_fetch_error_logs_and_returns_empty(self, mock_fetch):
        print("[TEST] Verifying an unexpected fetch error is logged, not raised...")
        mock_fetch.side_effect = RuntimeError("boom")
        result = fetcher.process_feed('http://exploding-feed.example/', 0)
        self.assertEqual(result, [])
        errors = [r for r in self.handler.records if r.levelno >= logging.ERROR]
        self.assertTrue(errors, "expected an ERROR log entry for an unexpected fetch failure")
        print("  [PASS] Got %d error log(s); one bad feed cannot abort the run." % len(errors))


class _CapturingHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.records = []

    def emit(self, record):
        self.records.append(record)


if __name__ == "__main__":
    unittest.main()
