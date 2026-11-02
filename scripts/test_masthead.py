"""
Unit tests for fishwrap.masthead.

Run: python3 scripts/test_masthead.py
Or:  make test
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fishwrap.masthead import Masthead, validate


MINIMAL_VALID_TOML = """\
[identity]
name = "Test"
timezone = "UTC"

[engine]
expiration_hours = 24

[[section]]
id = "news"
title = "News"
description = "News"
edition_size = 5
lead_count = 1
feature_count = 2
max_per_source = 3
keywords = ["politics"]

[feeds]
urls = ["https://example.com/feed.xml"]
"""


def _write_instance(tmp: Path, masthead_toml: str = MINIMAL_VALID_TOML,
                    dossier_md: str | None = None,
                    policies_jsonl: str | None = None) -> Path:
    inst = tmp / "inst"
    inst.mkdir(parents=True, exist_ok=True)
    (inst / "masthead.toml").write_text(masthead_toml)
    if dossier_md is not None:
        (inst / "dossier.md").write_text(dossier_md)
    if policies_jsonl is not None:
        (inst / "policies.jsonl").write_text(policies_jsonl)
    return inst


class ValidationTests(unittest.TestCase):

    def test_minimal_valid(self):
        import tomllib
        raw = tomllib.loads(MINIMAL_VALID_TOML)
        self.assertEqual(validate(raw), [])

    def test_missing_top_keys(self):
        raw = {"identity": {}, "engine": {}}
        errs = validate(raw)
        self.assertTrue(any("missing top-level table" in e for e in errs))

    def test_missing_section_keys(self):
        import tomllib
        raw = tomllib.loads(MINIMAL_VALID_TOML)
        raw["section"][0].pop("lead_count")
        errs = validate(raw)
        self.assertTrue(any("lead_count" in e for e in errs))

    def test_empty_feeds(self):
        import tomllib
        raw = tomllib.loads(MINIMAL_VALID_TOML)
        raw["feeds"]["urls"] = []
        errs = validate(raw)
        self.assertTrue(any("non-empty" in e for e in errs))

    def test_duplicate_section_ids(self):
        import tomllib
        raw = tomllib.loads(MINIMAL_VALID_TOML)
        raw["section"].append(dict(raw["section"][0]))
        errs = validate(raw)
        self.assertTrue(any("duplicate id" in e for e in errs))

    def test_source_sections_undeclared_target(self):
        import tomllib
        raw = tomllib.loads(MINIMAL_VALID_TOML)
        raw["source_sections"] = {"example.com": "news", "typo.example": "nws"}
        errs = validate(raw)
        self.assertEqual(len(errs), 1)
        self.assertIn("typo.example", errs[0])
        self.assertIn("nws", errs[0])

    def test_source_sections_declared_target_ok(self):
        import tomllib
        raw = tomllib.loads(MINIMAL_VALID_TOML)
        raw["source_sections"] = {"example.com": "news"}
        self.assertEqual(validate(raw), [])


class LoaderTests(unittest.TestCase):

    def test_load_minimal(self):
        with tempfile.TemporaryDirectory() as tmp:
            inst = _write_instance(Path(tmp))
            m = Masthead.load(inst)
            self.assertEqual(m.name, "Test")
            self.assertEqual(m.timezone, "UTC")
            self.assertEqual(m.expiration_hours, 24)
            self.assertEqual(len(m.sections), 1)
            self.assertEqual(m.sections[0]["id"], "news")
            self.assertEqual(m.feeds, ["https://example.com/feed.xml"])

    def test_dossier_loads(self):
        with tempfile.TemporaryDirectory() as tmp:
            inst = _write_instance(Path(tmp), dossier_md="hello\nworld\n")
            m = Masthead.load(inst)
            self.assertIn("hello", m.dossier_text)
            self.assertEqual(m.dossier_lines, ["hello", "world"])

    def test_dossier_optional(self):
        with tempfile.TemporaryDirectory() as tmp:
            inst = _write_instance(Path(tmp))  # no dossier
            m = Masthead.load(inst)
            self.assertEqual(m.dossier_text, "")
            self.assertEqual(m.dossier_lines, [])

    def test_policies_apply_strike(self):
        import json as _json
        policies = "\n".join([
            _json.dumps({"event": "create", "policy_id": "p1",
                         "sentence": "x", "policy": {"type": "source_ban", "match": "a"}}),
            _json.dumps({"event": "create", "policy_id": "p2",
                         "sentence": "y", "policy": {"type": "source_ban", "match": "b"}}),
            _json.dumps({"event": "strike", "policy_id": "p1"}),
        ])
        with tempfile.TemporaryDirectory() as tmp:
            inst = _write_instance(Path(tmp), policies_jsonl=policies)
            m = Masthead.load(inst)
            self.assertEqual(len(m.policies), 1)
            self.assertEqual(m.policies[0]["policy_id"], "p2")

    def test_missing_masthead_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                Masthead.load(tmp)

    def test_invalid_raises_with_message(self):
        with tempfile.TemporaryDirectory() as tmp:
            inst = Path(tmp) / "inst"
            inst.mkdir()
            (inst / "masthead.toml").write_text(
                MINIMAL_VALID_TOML.replace('lead_count = 1', '')
            )
            with self.assertRaises(ValueError) as cm:
                Masthead.load(inst)
            self.assertIn("lead_count", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
