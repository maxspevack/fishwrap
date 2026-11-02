"""
Unit tests for The Morgue — git-backed versioning UX rendering.

Verifies:
  * _git_log_entries reads commits from an instance git repo
  * _render_diff_html produces +/− HTML with the expected classes
  * render_morgue_restore renders the "what happens / what does NOT happen"
    block with line-count substitutions

Run: python3 scripts/test_morgue.py
Or:  make test
"""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fishwrap.masthead import Masthead  # noqa: E402


MINIMAL_TOML_V1 = """\
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

MINIMAL_TOML_V2 = MINIMAL_TOML_V1.replace('edition_size = 5', 'edition_size = 7')


def _git(cwd, *args):
    subprocess.run(["git", "-c", "commit.gpgsign=false", *args],
                   cwd=str(cwd), check=True, capture_output=True)


def _init_instance_repo(tmp: Path) -> Path:
    """Create a tmp instance dir with a 2-commit history on masthead.toml."""
    inst = tmp / "inst"
    inst.mkdir()
    (inst / "masthead.toml").write_text(MINIMAL_TOML_V1)
    (inst / "dossier.md").write_text("# initial dossier\nLine A\n")
    _git(inst, "init", "-q")
    _git(inst, "config", "user.email", "test@example.com")
    _git(inst, "config", "user.name", "Test")
    _git(inst, "add", "-A")
    _git(inst, "commit", "-q", "-m", "founding masthead")
    (inst / "masthead.toml").write_text(MINIMAL_TOML_V2)
    (inst / "dossier.md").write_text("# initial dossier\nLine A\nLine B\n")
    _git(inst, "add", "-A")
    _git(inst, "commit", "-q", "-m", "bump edition_size to 7")
    return inst


class MorgueRenderingTests(unittest.TestCase):

    def setUp(self):
        from fishwrap import printer
        self.printer = printer

    def test_git_log_returns_two_entries(self):
        with tempfile.TemporaryDirectory() as tmp:
            inst = _init_instance_repo(Path(tmp))
            entries = self.printer._git_log_entries(inst)
            self.assertEqual(len(entries), 2)
            # newest first
            self.assertIn("bump", entries[0]["subject"])
            self.assertIn("founding", entries[1]["subject"])

    def test_render_diff_html_classes(self):
        diff = (
            "@@ -1,3 +1,4 @@\n"
            " context\n"
            "-old line\n"
            "+new line\n"
        )
        out = self.printer._render_diff_html(diff)
        self.assertIn('class="del"', out)
        self.assertIn('class="add"', out)
        self.assertIn("old line", out)
        self.assertIn("new line", out)

    def test_render_diff_html_empty(self):
        out = self.printer._render_diff_html("")
        self.assertIn("No changes", out)

    def test_morgue_list_offers_view_but_never_restore(self):
        from fishwrap import printer
        with tempfile.TemporaryDirectory() as tmp:
            inst = _init_instance_repo(Path(tmp))
            m = Masthead.load(inst)
            entries = printer._git_log_entries(inst)
            html = printer.render_morgue(m, entries)
            self.assertIn(f'href="morgue-view-{entries[1]["short"]}.html"', html)
            self.assertIn("CURRENT", html)
            for gone in ("republish", "Republish", "restore", "git"):
                self.assertNotIn(gone, html)
            view = printer.render_morgue_view(m, entries, 1)
            self.assertIn('class="add"', view)   # the edition_size change shows as a diff
            self.assertNotIn("Republish", view)


if __name__ == "__main__":
    unittest.main()
