"""
fishwrap.show — an edition as text, for a terminal or a chat.

    python -m fishwrap.show [runsheet] [--cuts N] [--section ID]

Default runsheet: the newest under demo/output. Prints each section's
printed stories in seed order and, with --cuts N, the N freshest cut stories
per section with the reason, then the feeds that delivered nothing. This is
the Publisher's reading copy. Feedback becomes a policy (fishwrap.policy) or
a masthead edit, and replay shows the consequence before the next build.
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from fishwrap import runsheet
from fishwrap.printer import fresh_age

WIDTH = 84


def _t(title: str, width: int = WIDTH) -> str:
    t = " ".join((title or "(untitled)").split())
    return t if len(t) <= width else t[:width - 1] + "…"


def render(header: dict, records: list[dict], cuts: int = 0, section: str | None = None) -> str:
    f = header["funnel"]
    anchor = header["anchor_ts"]
    closed = datetime.fromtimestamp(anchor, ZoneInfo(header["timezone"])).strftime("%a %b %d %H:%M %Z")
    delivered = sum(1 for n in header["feeds"].values() if n)
    out = [
        f"{header['name']} · edition {header['edition']} · {f['published']} of {f['intake']:,} candidates · engine {header['engine']}",
        f"window closed {closed} · {delivered} of {len(header['feeds'])} feeds delivered · "
        f"{f['policy']} excluded by policy · {f['duplicate']} duplicates folded",
    ]
    pub = defaultdict(list)
    cut = defaultdict(list)
    for r in records:
        if r["fate"]["published"]:
            pub[r["fate"]["section"]].append(r)
        elif r["fate"].get("step") in ("diversity_cap", "capacity"):
            cut[r["section"]].append(r)
    for s in header["sections"]:
        sid = s["id"]
        if section and sid != section:
            continue
        printed = sorted(pub[sid], key=lambda r: r["fate"]["seed"])
        pool = next((r["signals"].get("pool") for r in printed + cut[sid] if r["signals"].get("pool")), 0)
        out.append("")
        out.append(f"{s['title'].upper()} · {len(printed)} of {s['edition_size']} · {pool} competed · cap {s['max_per_source']}/source")
        for r in printed:
            cov = r["cluster"].get("sources", 1)
            out.append(f"  {r['fate']['seed']:>2} {r['fate']['tier'][:4].upper():4} [{cov} src] "
                       f"{_t(r['title'])}  — {r['domain']} · {fresh_age(r['ts'], anchor)}")
        by_cap = Counter(r["domain"] for r in cut[sid] if r["fate"]["step"] == "diversity_cap")
        n_full = sum(1 for r in cut[sid] if r["fate"]["step"] == "capacity")
        if by_cap:
            top = ", ".join(f"{d} {n}" for d, n in by_cap.most_common(5))
            out.append(f"  cut by cap ({sum(by_cap.values())}): {top}")
        if n_full:
            out.append(f"  cut by capacity ({n_full})")
        if cuts:
            for r in sorted(cut[sid], key=lambda r: r["signals"].get("recency_rank") or 0)[:cuts]:
                why = "cap" if r["fate"]["step"] == "diversity_cap" else "full"
                out.append(f"     r{r['signals'].get('recency_rank') or '?':<4} {why:4} {_t(r['title'], 70)}  — {r['domain']}")
    silent = sorted(u for u, n in header["feeds"].items() if not n)
    if not section:
        out.append("")
        out.append(f"feeds that delivered nothing ({len(silent)} of {len(header['feeds'])}):")
        for u in silent:
            out.append(f"  {u}")
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("runsheet", nargs="?", type=Path, help="a runsheet.jsonl(.gz); default: newest under demo/output")
    ap.add_argument("--cuts", type=int, default=0, help="also list the N freshest cut stories per section")
    ap.add_argument("--section", help="only this section id")
    a = ap.parse_args(argv)
    path = a.runsheet
    if path is None:
        from fishwrap import _config
        path = runsheet.latest(Path(_config.OUTPUT_DIR))
        if path is None:
            raise SystemExit(f"show: no runsheet under {_config.OUTPUT_DIR}; run the editor first")
    header, records = runsheet.read(path)
    print(render(header, records, cuts=a.cuts, section=a.section))
    return 0


if __name__ == "__main__":
    sys.exit(main())
