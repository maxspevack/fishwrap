#!/usr/bin/env python3
"""
Archive a built demo edition into the state tree and assemble the publish tree.

The state tree is the repo's `state` branch, checked out by the demo workflow
at state/. Nothing but output lives there.

  <state>/<YYYY-MM-DD>/     one archived edition per date (same date: replaced)
  <state>/editions.html     index of every archived date, newest first
  <state>/index.html        the 'today' pointer: a redirect to the newest date,
                            written last

The publish tree is what fishwrap.org serves at /demo/vanilla/: the newest
--keep dates plus the two index pages. Older editions stay in the branch and
are reproducible from engine commit + runsheet.

Usage (the workflow):
  venv/bin/python3 scripts/demo_archive.py --output demo/output \\
      --state state/demo/vanilla --publish docs/demo/vanilla \\
      --keep 90 --title "The Vanilla"
"""
import argparse
import os
import re
import shutil
import sys
from html import escape
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fishwrap.printer import write_pointer  # noqa: E402

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

INDEX_CSS = (
    "body{font-family:'Libre Baskerville',Georgia,serif;background:#f6efe3;color:#16110b;"
    "max-width:40rem;margin:3rem auto;padding:0 1rem;line-height:1.6}"
    "h1{border-bottom:3px double #16110b;padding-bottom:.5rem}"
    "ol{list-style:none;padding:0}li{padding:.3rem 0;border-bottom:1px dotted #d4caba}"
    "a{color:#16110b}li:first-child a{font-weight:bold}"
    ".note{font-family:'iA Writer Mono',ui-monospace,monospace;font-size:.8rem;color:#4d4438}"
)


def dated_dirs(root: Path) -> list[str]:
    """Edition dates under root, newest first."""
    if not root.exists():
        return []
    return sorted((p.name for p in root.iterdir() if p.is_dir() and DATE_RE.match(p.name)),
                  reverse=True)


def newest_edition(output: Path) -> Path:
    dates = dated_dirs(output)
    if not dates:
        raise SystemExit(f"demo_archive: no dated edition under {output}")
    return output / dates[0]


def archive(state: Path, edition: Path) -> Path:
    """Copy one edition into the state tree, replacing a same-date edition."""
    state.mkdir(parents=True, exist_ok=True)
    dest = state / edition.name
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(edition, dest)
    return dest


def write_index(state: Path, title: str) -> Path:
    dates = dated_dirs(state)
    items = "".join(f'<li><a href="{d}/">{d}</a></li>' for d in dates)
    html = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<title>{escape(title)} · editions</title><style>{INDEX_CSS}</style></head>'
            f'<body><h1>{escape(title)}</h1>'
            f'<p class="note">{len(dates)} editions, newest first. Each stays at its date.</p>'
            f'<ol>{items}</ol></body></html>\n')
    p = state / "editions.html"
    p.write_text(html, encoding="utf-8")
    return p


def publish(state: Path, dest: Path, keep: int) -> list[str]:
    """Assemble dest from the newest `keep` editions plus the two index pages."""
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    kept = dated_dirs(state)[:keep]
    for d in kept:
        shutil.copytree(state / d, dest / d)
    for name in ("editions.html", "index.html"):
        shutil.copy2(state / name, dest / name)
    return kept


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--output", required=True, type=Path, help="printer output root (demo/output)")
    ap.add_argument("--state", required=True, type=Path, help="state tree (state/demo/vanilla)")
    ap.add_argument("--publish", required=True, type=Path, help="publish tree (docs/demo/vanilla)")
    ap.add_argument("--keep", type=int, default=90, help="editions to publish (default 90)")
    ap.add_argument("--title", default="Editions")
    a = ap.parse_args(argv)

    edition = newest_edition(a.output)
    archive(a.state, edition)
    write_index(a.state, a.title)
    write_pointer(a.state, edition.name)  # last: the pointer moves only once the edition is in place
    kept = publish(a.state, a.publish, a.keep)
    print(f"[ARCHIVE] {edition.name}: {len(dated_dirs(a.state))} editions in {a.state}; "
          f"published {len(kept)} to {a.publish}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
