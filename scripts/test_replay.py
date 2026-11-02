"""
Tests for fishwrap.replay: zero diff under an unchanged masthead, a real diff
after a policy change, the report text, and the --expect-zero exit code.

Run: python3 scripts/test_replay.py
Or:  make test
"""
import io
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
from fishwrap import replay, runsheet  # noqa: E402
from fishwrap.masthead import Masthead  # noqa: E402


class ReplayTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.inst = fx.write_instance(Path(self.tmp.name))
        self.masthead = Masthead.load(self.inst)
        header, records, _ = fx.build_runsheet(self.masthead)
        self.path = runsheet.write(Path(self.tmp.name) / "2026-10-26" / runsheet.FILENAME, header, records)

    def tearDown(self):
        self.tmp.cleanup()

    def test_unchanged_masthead_is_zero(self):
        old, new, changes = replay.replay(self.path, self.masthead)
        self.assertTrue(runsheet.diff_is_empty(changes))
        self.assertEqual(old["masthead_sha"], new["masthead_sha"])
        self.assertIn("no changes", replay.format_report(old, new, changes))

    def test_policy_change_is_reported(self):
        (self.inst / "policies.jsonl").write_text(
            (self.inst / "policies.jsonl").read_text()
            + '{"event": "create", "policy_id": "p2", "sentence": "Never print alpha.", '
              '"policy": {"type": "source_ban", "match": "alpha.example"}}\n')
        masthead = Masthead.load(self.inst)
        old, new, changes = replay.replay(self.path, masthead)
        self.assertEqual(len(changes["left"]), 2)  # a1, a2; a4 was already cut by the cap
        report = replay.format_report(old, new, changes)
        self.assertRegex(report, r"policies\.jsonl\s+changed \(")
        self.assertRegex(report, r"masthead\.toml\s+unchanged")
        self.assertIn("left the paper (2)", report)
        self.assertIn("entered the paper (1)", report)
        self.assertIn("Senate passes the budget", report)
        self.assertIn("now: excluded by policy: Never print alpha.", report)
        self.assertIn("was: folded as a duplicate of https://alpha.example/a1", report)

    def test_expect_zero_exit_codes(self):
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(replay.main([str(self.path), "--expect-zero"], masthead=self.masthead), 0)
        self.masthead.policies.append({"policy_id": "p3", "sentence": "Never print gamma.",
                                       "policy": {"type": "source_ban", "match": "gamma.example"}})
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(replay.main([str(self.path), "--expect-zero"], masthead=self.masthead), 1)

    def test_json_output(self):
        import json
        out = io.StringIO()
        with redirect_stdout(out):
            replay.main([str(self.path), "--json"], masthead=self.masthead)
        payload = json.loads(out.getvalue())
        self.assertEqual(payload["edition"], "2026-10-26")
        self.assertEqual(payload["changes"], {"entered": [], "left": [], "resectioned": [], "moved": []})


if __name__ == "__main__":
    unittest.main()
