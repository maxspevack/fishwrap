"""
fishwrap.runsheet — the per-edition artifact.

One file per edition, runsheet.jsonl.gz, in the edition's dated output
directory. Line 1 is the header: what the edition was built from. Every line
after it is one candidate: where it came from, how it competed, where it
landed. The editor writes it; the enhancer, the printer, and replay read it.
Nothing downstream of the editor recomputes a decision.

The editor sees a candidate as its title and the first SNAPSHOT_CHARS of its
body, and nothing deeper. That truncated view is what the runsheet stores, so
replaying a runsheet feeds the editor exactly what it saw the first time.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

SCHEMA = 1
SNAPSHOT_CHARS = 2000
FILENAME = "runsheet.jsonl.gz"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


# ============ small helpers ============

def edition_date(masthead, now: datetime | None = None) -> str:
    """The edition's date, YYYY-MM-DD, in the masthead's timezone.

    A 13:00 UTC build is the same calendar day in America/Los_Angeles; a
    05:00 UTC build is the day before. The date names the output directory,
    so it is decided once, here, never from the runner's clock.
    """
    tz = ZoneInfo(masthead.timezone)
    if now is None:
        now = datetime.now(tz)
    elif now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    return now.astimezone(tz).date().isoformat()


def domain_of(url: str | None) -> str:
    try:
        return urlparse(url or "").netloc or "unknown"
    except ValueError:
        return "unknown"


def engine_commit() -> str:
    """Short commit of the engine that built the edition, or 'unknown'."""
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(Path(__file__).resolve().parent), capture_output=True, text=True, check=True,
        ).stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def file_sha(path: Path) -> str | None:
    """First 12 hex characters of the file's SHA-256, or None if absent."""
    p = Path(path)
    if not p.is_file():
        return None
    return hashlib.sha256(p.read_bytes()).hexdigest()[:12]


def total_key(article: dict):
    """The total order every editor pass uses: newest first, ties by link."""
    return (-(article.get("timestamp") or 0), article.get("link") or "")


def snapshot(article: dict) -> dict:
    """The editor's view of a candidate: the only fields a decision may use."""
    return {
        "link": article.get("link") or "",
        "title": article.get("title") or "",
        "source_url": article.get("source_url") or "",
        "timestamp": float(article.get("timestamp") or 0),
        "categories": article.get("categories") or [],
        "content": (article.get("content") or "")[:SNAPSHOT_CHARS],
    }


# ============ build ============

def _policy_ref(policy: dict | None, effect: str) -> dict | None:
    if not policy:
        return None
    return {"id": policy.get("policy_id"), "sentence": policy.get("sentence"), "effect": effect}


def build(masthead, candidates, edition, rejects, funnel, *, date: str, anchor_ts: float,
          feed_counts: dict, engine: str | None = None):
    """Turn one editor pass into (header, records).

    `candidates` is the editor's input in total order, mutated by
    select_edition with the underscore fields it records as it goes.
    """
    published: dict[str, tuple[str, int, str]] = {}
    for sid, arts in edition.items():
        for art in arts:
            published[art["link"]] = (sid, art.get("_seed", 0), art.get("_tier", "standard"))

    records = []
    for art in sorted(candidates, key=total_key):
        link = art["link"]
        cluster = art.get("_cluster")
        if cluster is None and art.get("_dup_of"):
            cluster = {"leader": False, "of": art["_dup_of"]}
        if cluster is None:
            cluster = {"leader": True, "size": 1, "sources": 1, "members": []}

        policies = [p for p in (
            _policy_ref(art.get("_policy_drop"), "excluded"),
            _policy_ref(art.get("_whitelist_policy"), "cap_bypass"),
            _policy_ref(art.get("_lead_promoted_by"), "lead_promoted"),
        ) if p]

        if link in published:
            sid, seed, tier = published[link]
            fate = {"published": True, "section": sid, "seed": seed, "tier": tier}
        elif art.get("_policy_drop"):
            p = art["_policy_drop"]
            fate = {"published": False, "step": "policy",
                    "detail": p.get("sentence") or p.get("policy_id") or "policy"}
        elif art.get("_dup_of"):
            fate = {"published": False, "step": "duplicate", "detail": art["_dup_of"]}
        elif art.get("_reject"):
            fate = {"published": False, "step": art["_reject"]["reason"], "detail": art["_reject"]["detail"]}
        else:
            fate = {"published": False, "step": "unknown", "detail": ""}

        records.append({
            "link": link,
            "title": art.get("title") or "",
            "source": art.get("source_url") or "",
            "domain": domain_of(art.get("source_url")),
            "ts": art.get("timestamp") or 0,
            "categories": art.get("categories") or [],
            "content_head": (art.get("content") or "")[:SNAPSHOT_CHARS],
            "section": art.get("_section"),
            "section_reason": art.get("_class_reason") or {},
            "cluster": cluster,
            "policies": policies,
            "signals": {
                "recency_rank": art.get("_pool_rank"),
                "pool": art.get("_pool_size"),
                "coverage": cluster.get("sources") if cluster.get("leader") else None,
            },
            "fate": fate,
        })

    steps = Counter(r["fate"]["step"] for r in records if not r["fate"]["published"])
    n_pub = sum(1 for r in records if r["fate"]["published"])
    inst = Path(masthead.instance_dir)
    header = {
        "schema": SCHEMA,
        "edition": date,
        "name": masthead.name,
        "engine": engine or engine_commit(),
        "built_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "anchor_ts": anchor_ts,
        "window_hours": masthead.expiration_hours,
        "timezone": masthead.timezone,
        "masthead_sha": file_sha(inst / "masthead.toml"),
        "dossier_sha": file_sha(inst / "dossier.md"),
        "policies_sha": file_sha(inst / "policies.jsonl"),
        "dedup": {"threshold": funnel.get("dedup_threshold"), "window_hours": funnel.get("dedup_window_hours")},
        "sections": [{k: s.get(k) for k in ("id", "title", "edition_size", "lead_count", "feature_count", "max_per_source")}
                     for s in masthead.sections],
        "feeds": dict(feed_counts),
        "funnel": {
            "intake": len(records),
            "policy": steps.get("policy", 0),
            "duplicate": steps.get("duplicate", 0),
            "competed": len(records) - steps.get("policy", 0) - steps.get("duplicate", 0),
            "diversity_cap": steps.get("diversity_cap", 0),
            "capacity": steps.get("capacity", 0),
            "published": n_pub,
        },
    }
    return header, records


# ============ read / write / locate ============

# JSON leaves these unescaped, and str.splitlines() treats them as line
# breaks. A feed shipped one inside a body on 2026-11-03 and the reader cut
# the record in half. Escape them on write; read by "\n" alone.
_LINE_BREAKERS = {"\u2028": "\\u2028", "\u2029": "\\u2029", "\x85": "\\u0085"}


def _line(obj) -> str:
    s = json.dumps(obj, ensure_ascii=False)
    for ch, esc in _LINE_BREAKERS.items():
        s = s.replace(ch, esc)
    return s + "\n"


def write(path: Path, header: dict, records: list[dict]) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "wt", encoding="utf-8", newline="\n") as f:
        f.write(_line(header))
        for r in records:
            f.write(_line(r))
    return path


def read(path: Path) -> tuple[dict, list[dict]]:
    path = Path(path)
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8", newline="\n") as f:
        lines = [ln.rstrip("\n") for ln in f if ln.strip()]
    if not lines:
        raise ValueError(f"empty runsheet: {path}")
    header = json.loads(lines[0])
    if header.get("schema") != SCHEMA:
        raise ValueError(f"runsheet schema {header.get('schema')!r} at {path}; this engine reads {SCHEMA}")
    return header, [json.loads(ln) for ln in lines[1:]]


def dated_dirs(root: Path) -> list[str]:
    root = Path(root)
    if not root.exists():
        return []
    return sorted((p.name for p in root.iterdir() if p.is_dir() and DATE_RE.match(p.name)), reverse=True)


def latest(output_root: Path) -> Path | None:
    """The newest dated directory under output_root that holds a runsheet."""
    for d in dated_dirs(output_root):
        p = Path(output_root) / d / FILENAME
        if p.is_file():
            return p
    return None


# ============ replay support ============

def candidates_from(records: list[dict]) -> list[dict]:
    """Rebuild the editor's input from a runsheet, in total order."""
    cands = [{
        "link": r["link"],
        "title": r["title"],
        "source_url": r["source"],
        "timestamp": r["ts"],
        "categories": r.get("categories") or [],
        "content": r.get("content_head") or "",
    } for r in records]
    cands.sort(key=total_key)
    return cands


def diff(before: list[dict], after: list[dict]) -> dict:
    """What changed between two runsheets over the same candidates.

    entered: not printed before, printed now. left: the reverse.
    resectioned: printed in both, different section.
    moved: printed in both, same section, different seed or tier.
    """
    b = {r["link"]: r for r in before}
    a = {r["link"]: r for r in after}
    out = {"entered": [], "left": [], "resectioned": [], "moved": []}
    for link in sorted(set(b) | set(a)):
        rb, ra = b.get(link), a.get(link)
        fb = rb["fate"] if rb else {"published": False, "step": "absent", "detail": ""}
        fa = ra["fate"] if ra else {"published": False, "step": "absent", "detail": ""}
        item = {"link": link, "title": (ra or rb)["title"], "before": fb, "after": fa}
        if not fb["published"] and fa["published"]:
            out["entered"].append(item)
        elif fb["published"] and not fa["published"]:
            out["left"].append(item)
        elif fb["published"] and fa["published"]:
            if fb["section"] != fa["section"]:
                out["resectioned"].append(item)
            elif fb["seed"] != fa["seed"] or fb["tier"] != fa["tier"]:
                out["moved"].append(item)
    return out


def diff_is_empty(d: dict) -> bool:
    return not any(d.values())
