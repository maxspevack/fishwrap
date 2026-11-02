"""
fishwrap.replay — re-run the editor on an archived runsheet under the masthead as it is now.

    python -m fishwrap.replay demo/output/2026-11-01/runsheet.jsonl.gz
    python -m fishwrap.replay PATH --expect-zero   # exit 1 on any change: the CI determinism gate
    python -m fishwrap.replay PATH --json          # machine-readable

Nothing is fetched and nothing is written. Replay feeds the editor the same
candidates it saw the first time (the runsheet's snapshots) under the current
masthead.toml, dossier.md and policies.jsonl, and prints what moved. Change a
dial, replay yesterday, read the consequence.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from fishwrap import editor
from fishwrap import runsheet


def replay(path: Path, masthead):
    """Returns (old_header, new_header, changes)."""
    header, records = runsheet.read(path)
    cands = runsheet.candidates_from(records)
    edition, rejects, funnel = editor.select_edition(cands, masthead)
    new_header, new_records = runsheet.build(
        masthead, cands, edition, rejects, funnel,
        date=header["edition"], anchor_ts=header["anchor_ts"], feed_counts=header.get("feeds", {}),
        engine=header.get("engine"),
    )
    return header, new_header, runsheet.diff(records, new_records)


_STEP_WORDS = {
    "policy": "excluded by policy: {detail}",
    "duplicate": "folded as a duplicate of {detail}",
    "diversity_cap": "cut by the per-source cap ({detail})",
    "capacity": "cut by section capacity",
    "absent": "not a candidate",
}


def _fate_txt(fate, titles):
    if fate.get("published"):
        return f"{titles.get(fate['section'], fate['section'])} #{fate['seed']} {fate['tier']}"
    step = fate.get("step") or "unknown"
    return _STEP_WORDS.get(step, "cut: " + step).format(detail=fate.get("detail") or "")


def format_report(old_header: dict, new_header: dict, changes: dict) -> str:
    titles = {s["id"]: s["title"] for s in new_header["sections"]}
    lines = [f"replay of edition {old_header['edition']} ({old_header['funnel']['intake']} candidates) "
             f"under the masthead as it is now"]
    for name, key in (("masthead.toml", "masthead_sha"), ("dossier.md", "dossier_sha"), ("policies.jsonl", "policies_sha")):
        a, b = old_header.get(key), new_header.get(key)
        lines.append(f"  {name:15s} {'unchanged' if a == b else f'changed ({a} -> {b})'}")
    if runsheet.diff_is_empty(changes):
        lines.append("no changes: the edition would print exactly as it did.")
        return "\n".join(lines)
    for group, mark, label in (("entered", "+", "entered the paper"), ("left", "-", "left the paper"),
                               ("resectioned", "~", "changed section"), ("moved", "~", "moved within a section")):
        items = changes[group]
        if not items:
            continue
        lines.append(f"\n{label} ({len(items)}):")
        for it in items:
            lines.append(f"  {mark} {' '.join(it['title'].split())[:90]}")
            lines.append(f"      was: {_fate_txt(it['before'], titles)}")
            lines.append(f"      now: {_fate_txt(it['after'], titles)}")
    total = sum(len(v) for v in changes.values())
    lines.append(f"\n{total} change{'s' if total != 1 else ''}.")
    return "\n".join(lines)


def main(argv=None, masthead=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("runsheet", type=Path, help="an archived runsheet.jsonl(.gz)")
    ap.add_argument("--expect-zero", action="store_true", help="exit 1 if anything would change")
    ap.add_argument("--json", action="store_true", help="print the diff as JSON")
    a = ap.parse_args(argv)

    if masthead is None:
        from fishwrap import _config
        masthead = _config.MASTHEAD
        if masthead is None:
            raise SystemExit("replay: set FISHWRAP_CONFIG to the instance directory (e.g. demo/)")

    old_header, new_header, changes = replay(a.runsheet, masthead)
    if a.json:
        print(json.dumps({"edition": old_header["edition"], "changes": changes}, indent=2))
    else:
        print(format_report(old_header, new_header, changes))
    if a.expect_zero and not runsheet.diff_is_empty(changes):
        print("\nreplay: --expect-zero failed; the editor is not deterministic or the masthead changed", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
