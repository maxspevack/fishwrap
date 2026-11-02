"""
Tests for scripts/demo_archive.py: the state tree keeps every edition, the
publish tree keeps the newest --keep, the index lists newest first, and the
'today' pointer follows the newest edition.

Run: python3 scripts/test_demo_archive.py
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

import demo_archive as da  # noqa: E402


def _edition(root: Path, date: str, marker: str) -> Path:
    d = root / date
    d.mkdir(parents=True, exist_ok=True)
    (d / "index.html").write_text(marker)
    (d / "morgue.html").write_text("morgue " + marker)
    return d


class DemoArchiveTests(unittest.TestCase):

    def _run(self, out, state, pub, keep):
        return da.main(["--output", str(out), "--state", str(state), "--publish", str(pub),
                        "--keep", str(keep), "--title", "T"])

    def test_two_days(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            out, state, pub = tmp / "output", tmp / "state", tmp / "publish"

            _edition(out, "2026-11-01", "one")
            self.assertEqual(self._run(out, state, pub, keep=1), 0)
            self.assertEqual(da.dated_dirs(state), ["2026-11-01"])
            self.assertIn("url=2026-11-01/", (pub / "index.html").read_text())

            # Day two: a newer edition; the old one is still in output locally.
            _edition(out, "2026-11-02", "two")
            self.assertEqual(self._run(out, state, pub, keep=1), 0)
            self.assertEqual(da.dated_dirs(state), ["2026-11-02", "2026-11-01"])  # state keeps all
            self.assertEqual(da.dated_dirs(pub), ["2026-11-02"])                  # publish keeps --keep
            self.assertIn("url=2026-11-02/", (state / "index.html").read_text())
            self.assertIn("url=2026-11-02/", (pub / "index.html").read_text())
            self.assertEqual((pub / "2026-11-02" / "index.html").read_text(), "two")
            index = (state / "editions.html").read_text()
            self.assertLess(index.index("2026-11-02"), index.index("2026-11-01"))  # newest first
            self.assertIn("2 editions", index)

    def test_same_date_rebuild_replaces_without_leftovers(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            out, state, pub = tmp / "output", tmp / "state", tmp / "publish"
            d = _edition(out, "2026-11-01", "first build")
            (d / "morgue-view-abc.html").write_text("stale")
            self._run(out, state, pub, keep=90)
            (d / "morgue-view-abc.html").unlink()
            (d / "index.html").write_text("second build")
            self._run(out, state, pub, keep=90)
            self.assertEqual((state / "2026-11-01" / "index.html").read_text(), "second build")
            self.assertFalse((state / "2026-11-01" / "morgue-view-abc.html").exists())
            self.assertEqual(da.dated_dirs(state), ["2026-11-01"])

    def test_edition_without_index_is_a_hard_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            d = tmp / "output" / "2026-11-01"
            d.mkdir(parents=True)
            (d / "morgue.html").write_text("pages but no index")
            with self.assertRaises(SystemExit):
                self._run(tmp / "output", tmp / "state", tmp / "publish", keep=90)
            self.assertFalse((tmp / "state").exists())

    def test_no_edition_is_a_hard_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            (tmp / "output").mkdir()
            (tmp / "output" / "index.html").write_text("pointer only, no edition")
            with self.assertRaises(SystemExit):
                self._run(tmp / "output", tmp / "state", tmp / "publish", keep=90)
            self.assertFalse((tmp / "publish").exists())


if __name__ == "__main__":
    unittest.main()
