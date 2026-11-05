"""
Tests for fishwrap.runsheet: every candidate gets a record with the right
fate, the header's funnel adds up, the file round-trips, the editor is
deterministic over its own snapshots, and diff reports real changes only.

Run: python3 scripts/test_runsheet.py
Or:  make test
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)

import fixtures_runsheet as fx  # noqa: E402
from fishwrap import editor, runsheet  # noqa: E402
from fishwrap.masthead import Masthead  # noqa: E402


class RunsheetBuildTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.masthead = Masthead.load(fx.write_instance(Path(self.tmp.name)))
        self.header, self.records, self.cands = fx.build_runsheet(self.masthead)
        self.by_link = {r["link"]: r for r in self.records}

    def tearDown(self):
        self.tmp.cleanup()

    def test_every_candidate_has_a_record_and_no_unknown_fates(self):
        self.assertEqual(len(self.records), len(self.cands))
        self.assertEqual([r for r in self.records if r["fate"].get("step") == "unknown"], [])

    def test_fates(self):
        f = lambda slug, src="alpha.example": self.by_link[f"https://{src}/{slug}"]["fate"]  # noqa: E731
        self.assertEqual(f("x1", "banned.example")["step"], "policy")
        self.assertEqual(f("x1", "banned.example")["detail"], "Never print banned.example.")
        self.assertEqual(f("b1", "beta.example")["step"], "duplicate")
        self.assertEqual(f("b1", "beta.example")["detail"], "https://alpha.example/a1")  # the newer copy leads
        self.assertTrue(f("a1")["published"])
        self.assertEqual((f("a1")["seed"], f("a1")["tier"]), (1, "lead"))
        self.assertEqual(f("a3")["step"], "diversity_cap")       # alpha's third story
        self.assertEqual(f("a4")["step"], "diversity_cap")       # alpha's fourth
        self.assertTrue(f("b2", "beta.example")["published"])    # fills slot 3
        self.assertEqual(f("g3", "gamma.example")["step"], "capacity")  # whitelisted but the 2 slots are full

    def test_cluster_and_coverage(self):
        leader = self.by_link["https://alpha.example/a1"]
        self.assertEqual(leader["cluster"], {"leader": True, "size": 2, "sources": 2,
                                             "members": ["https://beta.example/b1"]})
        self.assertEqual(leader["signals"]["coverage"], 2)
        dup = self.by_link["https://beta.example/b1"]
        self.assertEqual(dup["cluster"], {"leader": False, "of": "https://alpha.example/a1"})
        self.assertIsNone(dup["signals"]["coverage"])

    def test_policies_recorded_on_the_record(self):
        self.assertEqual(self.by_link["https://banned.example/x1"]["policies"],
                         [{"id": "p-ban", "sentence": "Never print banned.example.", "effect": "excluded"}])
        g1 = self.by_link["https://gamma.example/g1"]
        self.assertEqual([p["effect"] for p in g1["policies"]], ["cap_bypass"])

    def test_header_funnel_adds_up(self):
        f = self.header["funnel"]
        self.assertEqual(f["intake"], 10)
        self.assertEqual(f["intake"], f["policy"] + f["duplicate"] + f["competed"])
        self.assertEqual(f["competed"], f["diversity_cap"] + f["capacity"] + f["published"])
        self.assertEqual(f["published"], 5)
        self.assertEqual(self.header["feeds"]["https://silent.example/feed"], 0)
        self.assertEqual(self.header["dedup"], {"threshold": 0.70, "window_hours": 48})
        self.assertEqual(self.header["edition"], "2026-10-26")
        for key in ("masthead_sha", "dossier_sha", "policies_sha"):
            self.assertRegex(self.header[key], r"^[0-9a-f]{12}$")

    def test_snapshot_truncates_content(self):
        art = {"link": "l", "title": "t", "source_url": "s", "timestamp": 1, "content": "x" * 5000}
        self.assertEqual(len(runsheet.snapshot(art)["content"]), runsheet.SNAPSHOT_CHARS)

    def test_round_trip_gz_and_plain(self):
        for name in ("rs.jsonl.gz", "rs.jsonl"):
            p = runsheet.write(Path(self.tmp.name) / name, self.header, self.records)
            h, rs = runsheet.read(p)
            self.assertEqual(h, self.header)
            self.assertEqual(rs, self.records)

    def test_unicode_line_breakers_round_trip(self):
        # 2026-11-03: a body carried U+2028; json.dumps leaves it raw and
        # str.splitlines() breaks on it, so the reader saw half a record.
        nasty = {"link": "https://x.example/1", "title": "before\u2028after", "source": "s", "domain": "d",
                 "ts": 1, "categories": [], "content_head": "nel\x85here \u2029 ps\nnewline\rcr",
                 "section": None, "section_reason": {}, "cluster": {"leader": True, "size": 1, "sources": 1, "members": []},
                 "policies": [], "signals": {}, "fate": {"published": False, "step": "policy", "detail": "x"}}
        p = runsheet.write(Path(self.tmp.name) / "nasty.jsonl.gz", self.header, [nasty])
        import gzip
        raw = gzip.open(p, "rt", encoding="utf-8", newline="").read()
        self.assertEqual(raw.count("\n"), 2)                      # header + one record, no stray breaks
        self.assertEqual(len(raw.splitlines()), 2)                 # even a splitlines() reader sees two lines
        h, rs = runsheet.read(p)
        self.assertEqual(rs, [nasty])

    def test_latest_finds_the_newest_dated_runsheet(self):
        root = Path(self.tmp.name) / "out"
        self.assertIsNone(runsheet.latest(root))
        (root / "2026-10-25").mkdir(parents=True)
        runsheet.write(root / "2026-10-25" / runsheet.FILENAME, self.header, self.records)
        (root / "2026-10-26").mkdir()  # newer, but no runsheet yet
        self.assertEqual(runsheet.latest(root), root / "2026-10-25" / runsheet.FILENAME)

    def test_history_reads_newest_first_and_skips_missing(self):
        root = Path(self.tmp.name) / "arch"
        for d in ("2026-10-24", "2026-10-25", "2026-10-26"):
            runsheet.write(root / d / runsheet.FILENAME, dict(self.header, edition=d), self.records)
        (root / "2026-10-27").mkdir()  # no runsheet
        hs = runsheet.history(root, 2)
        self.assertEqual([h["edition"] for h in hs], ["2026-10-26", "2026-10-25"])

    def test_editor_is_deterministic_over_its_own_snapshots(self):
        cands = runsheet.candidates_from(self.records)
        edition, rejects, funnel = editor.select_edition(cands, self.masthead)
        _h, again = runsheet.build(self.masthead, cands, edition, rejects, funnel, date="2026-10-26",
                                   anchor_ts=fx.BASE_TS, feed_counts=self.header["feeds"], engine="fixture")
        self.assertEqual(again, self.records)
        self.assertTrue(runsheet.diff_is_empty(runsheet.diff(self.records, again)))

    def test_diff_reports_a_ban(self):
        self.masthead.policies.append({"policy_id": "p2", "sentence": "Never print alpha.",
                                       "policy": {"type": "source_ban", "match": "alpha.example"}})
        _h, after, _c = fx.build_runsheet(self.masthead, runsheet.candidates_from(self.records))
        d = runsheet.diff(self.records, after)
        self.assertEqual(sorted(i["link"] for i in d["left"]),
                         ["https://alpha.example/a1", "https://alpha.example/a2"])
        self.assertEqual([i["link"] for i in d["entered"]], ["https://beta.example/b1"])  # no longer a duplicate
        moved = {i["link"]: i for i in d["moved"]}
        self.assertEqual(set(moved), {"https://beta.example/b2"})
        self.assertEqual((moved["https://beta.example/b2"]["before"]["seed"], moved["https://beta.example/b2"]["after"]["seed"]), (3, 2))
        self.assertEqual(d["resectioned"], [])


if __name__ == "__main__":
    unittest.main()
