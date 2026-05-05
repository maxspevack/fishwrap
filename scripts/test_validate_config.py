"""
Unit tests for fishwrap.validate_config.

Run:  python3 scripts/test_validate_config.py
Or:   make test
"""

import os
import sys
import unittest

# Make the engine importable when run from the repo root.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fishwrap.validate_config import (  # noqa: E402
    validate_config_namespace,
    load_config_namespace,
)


def _valid_namespace() -> dict:
    """A minimal valid config namespace, used as the base for variant tests."""
    return {
        "FEEDS": ["https://example.com/feed.xml"],
        "SECTIONS": [{"id": "news", "title": "News"}],
        "KEYWORDS": {"news": ["breaking"]},
        "EDITORIAL_POLICIES": [],
        "SCORING_PROFILES": {
            "dynamic": {"score_weight": 1.0},
            "static": {"base_boosts": 10},
        },
        "EDITION_SIZE": {"news": 10},
        "MIN_SECTION_SCORES": {"news": 0},
        "DATABASE_URL": "sqlite:///newsroom.db",
        "LATEST_HTML_FILE": "output/index.html",
        "TIMEZONE": "UTC",
        "THEME": "demo/themes/basic",
    }


class RequiredKeysTests(unittest.TestCase):

    def test_minimal_valid_namespace_passes(self):
        self.assertEqual(validate_config_namespace(_valid_namespace()), [])

    def test_missing_FEEDS(self):
        ns = _valid_namespace()
        del ns["FEEDS"]
        errs = validate_config_namespace(ns)
        self.assertTrue(any("FEEDS" in e and "missing" in e for e in errs))

    def test_FEEDS_wrong_type(self):
        ns = _valid_namespace()
        ns["FEEDS"] = "http://example.com/feed.xml"
        errs = validate_config_namespace(ns)
        self.assertTrue(any("FEEDS" in e and "list" in e for e in errs))

    def test_FEEDS_empty(self):
        ns = _valid_namespace()
        ns["FEEDS"] = []
        errs = validate_config_namespace(ns)
        self.assertTrue(any("FEEDS" in e and "non-empty" in e for e in errs))

    def test_FEEDS_contains_non_string(self):
        ns = _valid_namespace()
        ns["FEEDS"] = ["https://ok.example/feed", 42]
        errs = validate_config_namespace(ns)
        self.assertTrue(any("FEEDS" in e and "[1]" in e for e in errs))

    def test_DATABASE_URL_wrong_type(self):
        ns = _valid_namespace()
        ns["DATABASE_URL"] = 12345
        errs = validate_config_namespace(ns)
        self.assertTrue(any("DATABASE_URL" in e and "string" in e for e in errs))


class NestedShapeTests(unittest.TestCase):

    def test_SECTIONS_missing_id(self):
        ns = _valid_namespace()
        ns["SECTIONS"] = [{"title": "Has no id"}]
        errs = validate_config_namespace(ns)
        self.assertTrue(any("SECTIONS[0]" in e and "id" in e for e in errs))

    def test_SECTIONS_missing_title(self):
        ns = _valid_namespace()
        ns["SECTIONS"] = [{"id": "news"}]
        errs = validate_config_namespace(ns)
        self.assertTrue(any("SECTIONS[0]" in e and "title" in e for e in errs))

    def test_SECTIONS_id_wrong_type(self):
        ns = _valid_namespace()
        ns["SECTIONS"] = [{"id": 99, "title": "Numeric ID"}]
        errs = validate_config_namespace(ns)
        self.assertTrue(any("SECTIONS[0].id" in e for e in errs))

    def test_SECTIONS_entry_not_a_dict(self):
        ns = _valid_namespace()
        ns["SECTIONS"] = ["not a dict"]
        errs = validate_config_namespace(ns)
        self.assertTrue(any("SECTIONS[0]" in e and "dict" in e for e in errs))

    def test_SCORING_PROFILES_missing_dynamic(self):
        ns = _valid_namespace()
        ns["SCORING_PROFILES"] = {"static": {"base_boosts": 10}}
        errs = validate_config_namespace(ns)
        self.assertTrue(any("SCORING_PROFILES" in e and "dynamic" in e for e in errs))

    def test_SCORING_PROFILES_dynamic_not_a_dict(self):
        ns = _valid_namespace()
        ns["SCORING_PROFILES"] = {"dynamic": "not a dict", "static": {}}
        errs = validate_config_namespace(ns)
        self.assertTrue(any("SCORING_PROFILES.dynamic" in e for e in errs))

    def test_EDITORIAL_POLICIES_missing_type(self):
        ns = _valid_namespace()
        ns["EDITORIAL_POLICIES"] = [{"boosts": 1}]
        errs = validate_config_namespace(ns)
        self.assertTrue(any("EDITORIAL_POLICIES[0]" in e and "type" in e for e in errs))

    def test_EDITORIAL_POLICIES_boosts_wrong_type(self):
        ns = _valid_namespace()
        ns["EDITORIAL_POLICIES"] = [{"type": "keyword_boost", "boosts": "fifteen"}]
        errs = validate_config_namespace(ns)
        self.assertTrue(any("EDITORIAL_POLICIES[0].boosts" in e for e in errs))


class OptionalKeysTests(unittest.TestCase):

    def test_BOOST_UNIT_VALUE_optional_when_absent(self):
        ns = _valid_namespace()
        self.assertNotIn("BOOST_UNIT_VALUE", ns)
        self.assertEqual(validate_config_namespace(ns), [])

    def test_BOOST_UNIT_VALUE_validated_when_present(self):
        ns = _valid_namespace()
        ns["BOOST_UNIT_VALUE"] = "one hundred"
        errs = validate_config_namespace(ns)
        self.assertTrue(any("BOOST_UNIT_VALUE" in e for e in errs))

    def test_BOOST_UNIT_VALUE_bool_rejected(self):
        # bool is a subclass of int but should be rejected for number-typed keys.
        ns = _valid_namespace()
        ns["BOOST_UNIT_VALUE"] = True
        errs = validate_config_namespace(ns)
        self.assertTrue(any("BOOST_UNIT_VALUE" in e and "bool" in e for e in errs))


class CollectAllAndPermissivenessTests(unittest.TestCase):

    def test_collect_all_errors_at_once(self):
        ns = _valid_namespace()
        del ns["FEEDS"]
        del ns["SECTIONS"]
        ns["DATABASE_URL"] = 0
        errs = validate_config_namespace(ns)
        self.assertTrue(any("FEEDS" in e for e in errs))
        self.assertTrue(any("SECTIONS" in e for e in errs))
        self.assertTrue(any("DATABASE_URL" in e for e in errs))

    def test_unknown_keys_ignored(self):
        ns = _valid_namespace()
        ns["MY_CUSTOM_THING"] = "consumers may add their own keys"
        self.assertEqual(validate_config_namespace(ns), [])


class DemoConfigsIntegration(unittest.TestCase):
    """The shipped demo configs must validate. Catches regressions in the schema."""

    def test_all_demo_configs_validate(self):
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        demo_dir = os.path.join(repo_root, "demo")
        for cfg in ("config.py", "cyber_config.py", "ai_config.py", "showrunner_config.py"):
            cfg_path = os.path.join(demo_dir, cfg)
            if not os.path.exists(cfg_path):
                self.skipTest(f"{cfg_path} not found")
            with self.subTest(config=cfg):
                ns = load_config_namespace(cfg_path)
                errs = validate_config_namespace(ns)
                self.assertEqual(errs, [], f"{cfg} should validate but had: {errs}")


if __name__ == "__main__":
    unittest.main()
