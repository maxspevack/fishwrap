"""
Shared fixture for the runsheet, replay, and printer tests: a small instance
with two sections, a ban, a whitelist, and candidates that exercise every
fate (published, policy, duplicate, diversity_cap, capacity).
"""
import json
import time
from pathlib import Path

MASTHEAD_TOML = """\
[identity]
name = "Fixture Paper"
timezone = "America/Los_Angeles"

[engine]
expiration_hours = 24
dedup_similarity_threshold = 0.70

[[section]]
id = "news"
title = "News"
description = "What happened"
edition_size = 3
lead_count = 1
feature_count = 1
max_per_source = 2
keywords = ["election"]

[[section]]
id = "sports"
title = "Sports"
description = "Games"
edition_size = 2
lead_count = 1
feature_count = 1
max_per_source = 2
keywords = ["playoffs"]

[source_sections]
"alpha.example" = "news"
"beta.example" = "news"
"gamma.example" = "sports"
"banned.example" = "news"

[feeds]
urls = [
  "https://alpha.example/feed",
  "https://beta.example/feed",
  "https://gamma.example/feed",
  "https://banned.example/feed",
  "https://silent.example/feed",
]
"""

POLICIES = [
    {"event": "create", "policy_id": "p-ban", "sentence": "Never print banned.example.",
     "policy": {"type": "source_ban", "match": "banned.example"}},
    {"event": "create", "policy_id": "p-all", "sentence": "Print everything gamma files.",
     "policy": {"type": "source_whitelist", "match": "gamma.example"}},
]


def write_instance(tmp: Path) -> Path:
    inst = Path(tmp) / "inst"
    inst.mkdir(parents=True, exist_ok=True)
    (inst / "masthead.toml").write_text(MASTHEAD_TOML)
    (inst / "dossier.md").write_text("# Dossier\nOne line.\n")
    (inst / "policies.jsonl").write_text("\n".join(json.dumps(p) for p in POLICIES) + "\n")
    return inst


BASE_TS = 1_793_000_000.0  # 2026-10-26 in UTC, a fixed anchor


def _c(slug, title, source, minutes_ago, content=""):
    return {"link": f"https://{source}/{slug}", "title": title,
            "source_url": f"https://{source}/feed", "timestamp": BASE_TS - minutes_ago * 60,
            "categories": [], "content": content}


def candidates():
    return [
        # news: alpha files 3 (cap 2 -> the third is cut by the cap), beta files 1
        _c("a1", "Senate passes the budget after a long night", "alpha.example", 5),
        _c("a2", "Supreme Court rules on the redistricting case", "alpha.example", 10),
        _c("a3", "President signs the executive order on tariffs", "alpha.example", 15),
        # b1 is the same story as a1 (newer), so a1 leads the cluster and b1 is folded
        _c("b1", "Senate passes budget after long night", "beta.example", 20),
        _c("a4", "Federal regulator opens a probe into the merger", "alpha.example", 18),
        # a fourth distinct news story that overflows capacity (3 slots)
        _c("b2", "City council votes on the transit plan tonight", "beta.example", 30),
        # banned source
        _c("x1", "A story from the banned source", "banned.example", 1),
        # sports: gamma whitelisted, files 3 for 2 slots -> one cut by capacity
        _c("g1", "Hurricanes win the Stanley Cup in overtime", "gamma.example", 2),
        _c("g2", "Knicks take Game 7 at the Garden", "gamma.example", 4),
        _c("g3", "World Cup draw announced in Zurich", "gamma.example", 6),
    ]


def feed_counts(masthead, cands):
    seen = {}
    for c in cands:
        seen[c["source_url"]] = seen.get(c["source_url"], 0) + 1
    return {u: seen.get(u, 0) for u in masthead.feeds}


def build_runsheet(masthead, cands=None):
    """Run the editor once and return (header, records, cands)."""
    from fishwrap import editor, runsheet
    cands = cands or candidates()
    edition, rejects, funnel = editor.select_edition(cands, masthead)
    header, records = runsheet.build(masthead, cands, edition, rejects, funnel,
                                     date="2026-10-26", anchor_ts=BASE_TS,
                                     feed_counts=feed_counts(masthead, cands), engine="fixture")
    return header, records, cands
