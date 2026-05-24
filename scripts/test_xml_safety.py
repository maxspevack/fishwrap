"""Regression test for #21: XML parsing must reject entity-expansion attacks.

Constructs a billion-laughs payload and feeds it to fetcher.process_feed via
the mocked utils.fetch_url. defusedxml.ElementTree.fromstring raises
EntitiesForbidden, which fetcher catches and logs.

Verifies:
  1. The parser does NOT expand the entities (no exponential blowup, no
     EntitiesForbidden propagating to the caller).
  2. The function returns [] (skipping the malicious feed).
  3. A WARNING-or-higher log entry fires (per #19 wiring).
"""
import os
import sys
import logging
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fishwrap import fetcher


BILLION_LAUGHS = """<?xml version="1.0"?>
<!DOCTYPE lolz [
  <!ENTITY lol "lol">
  <!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
  <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
  <!ENTITY lol4 "&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;">
]>
<rss><channel><item><title>&lol4;</title></item></channel></rss>
"""


class TestXmlSafety(unittest.TestCase):
    def setUp(self):
        self.handler = _CapturingHandler()
        logging.getLogger("fishwrap").addHandler(self.handler)
        logging.getLogger("fishwrap").setLevel(logging.DEBUG)

    def tearDown(self):
        logging.getLogger("fishwrap").removeHandler(self.handler)

    @patch('fishwrap.utils.fetch_url')
    def test_billion_laughs_rejected(self, mock_fetch):
        print("[TEST] Verifying billion-laughs payload is rejected by defusedxml...")
        mock_fetch.return_value = BILLION_LAUGHS

        result = fetcher.process_feed('http://malicious-feed.example/', 0)

        self.assertEqual(result, [], "expected empty list, got expanded entities")
        warnings = [r for r in self.handler.records if r.levelno >= logging.WARNING]
        self.assertTrue(warnings, "expected a WARNING log entry for the rejected payload")
        print("  [PASS] defusedxml refused the payload; fetcher returned []; warning logged.")


class _CapturingHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.records = []

    def emit(self, record):
        self.records.append(record)


if __name__ == "__main__":
    unittest.main()
