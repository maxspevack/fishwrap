"""
fishwrap.policy — the Publisher's pen: append a signed policy to policies.jsonl.

    python -m fishwrap.policy ban-source <domain>                 --because "<sentence>"
    python -m fishwrap.policy ban-title  <regex>                  --because "<sentence>"
    python -m fishwrap.policy ban-topic  <phrase> [<phrase>...]   --because "<sentence>"
    python -m fishwrap.policy print-all  <domain> [--except <re>] --because "<sentence>"
    python -m fishwrap.policy prefer-lead <section> <kw> [<kw>...] --because "<sentence>"
    python -m fishwrap.policy strike <policy_id>                  --because "<sentence>"
    python -m fishwrap.policy list

Every policy is a sentence the Publisher wrote plus the primitive that
enforces it. The file is append-only: a strike is an event, not a deletion.
The Morgue files every change; replay shows what any policy would do to an
edition that already happened. The instance is FISHWRAP_CONFIG or --instance.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import date
from pathlib import Path

from fishwrap.masthead import Masthead

VERBS = {
    "ban-source": "source_ban",
    "ban-title": "title_pattern_ban",
    "ban-topic": "topic_ban",
    "print-all": "source_whitelist",
    "prefer-lead": "section_lead_preference",
}


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:40] or "x"


def _ids(instance: Path) -> set[str]:
    p = instance / "policies.jsonl"
    if not p.exists():
        return set()
    return {json.loads(ln)["policy_id"] for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip()}


def _new_id(instance: Path, kind: str, target: str, today: str) -> str:
    base = f"{kind}-{_slug(target)}-{today.replace('-', '')}"
    taken = _ids(instance)
    pid, n = base, 2
    while pid in taken:
        pid, n = f"{base}-{n}", n + 1
    return pid


def build_event(verb: str, args: list[str], because: str, *, instance: Path, except_pattern: str | None = None,
                today: str | None = None) -> dict:
    """Validate and build one event line (not yet written)."""
    today = today or date.today().isoformat()
    if not because or not because.strip():
        raise ValueError("--because is required: every policy is a sentence you wrote")
    if verb == "strike":
        (pid,) = args
        if pid not in _ids(instance):
            raise ValueError(f"no policy with id {pid!r} in {instance / 'policies.jsonl'}")
        return {"event": "strike", "policy_id": pid, "sentence": because.strip(), "created": today}

    kind = VERBS[verb]
    if verb == "ban-source":
        (domain,) = args
        policy = {"type": kind, "match": domain.lower()}
        target = domain
    elif verb == "ban-title":
        (pattern,) = args
        re.compile(pattern)
        policy = {"type": kind, "pattern": pattern}
        target = pattern
    elif verb == "ban-topic":
        if not args:
            raise ValueError("ban-topic needs at least one phrase")
        policy = {"type": kind, "phrases": list(args)}
        target = args[0]
    elif verb == "print-all":
        (domain,) = args
        policy = {"type": kind, "match": domain.lower()}
        if except_pattern:
            re.compile(except_pattern)
            policy["except_pattern"] = except_pattern
        target = domain
    elif verb == "prefer-lead":
        section, *keywords = args
        if not keywords:
            raise ValueError("prefer-lead needs a section and at least one keyword")
        m = Masthead.load(instance)
        if m.section_by_id(section) is None:
            raise ValueError(f"no section {section!r}; sections are {[s['id'] for s in m.sections]}")
        policy = {"type": kind, "section": section, "lead_keywords": list(keywords)}
        target = f"{section}-{keywords[0]}"
    else:
        raise ValueError(f"unknown verb {verb!r}")
    return {"event": "create", "policy_id": _new_id(instance, kind, target, today),
            "sentence": because.strip(), "created": today, "policy": policy}


def append(instance: Path, event: dict) -> Path:
    p = instance / "policies.jsonl"
    text = p.read_text(encoding="utf-8") if p.exists() else ""
    if text and not text.endswith("\n"):
        text += "\n"
    p.write_text(text + json.dumps(event, ensure_ascii=False) + "\n", encoding="utf-8")
    return p


def format_list(instance: Path) -> str:
    m = Masthead.load(instance)
    if not m.policies:
        return "no active policies"
    lines = []
    for p in m.policies:
        pp = p["policy"]
        what = {k: v for k, v in pp.items() if k != "type"}
        lines.append(f"{p['policy_id']:40s} {pp['type']:24s} {json.dumps(what, ensure_ascii=False)}")
        lines.append(f"{'':40s} \"{p.get('sentence', '')}\"")
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("verb", choices=[*VERBS, "strike", "list"])
    ap.add_argument("args", nargs="*")
    ap.add_argument("--because", default="", help="the sentence this policy is (required except for list)")
    ap.add_argument("--except", dest="except_pattern", help="print-all: titles matching this regex do not bypass the cap")
    ap.add_argument("--instance", type=Path, default=None, help="instance directory (default: $FISHWRAP_CONFIG or demo)")
    a = ap.parse_args(argv)
    instance = a.instance or Path(os.environ.get("FISHWRAP_CONFIG") or "demo")

    if a.verb == "list":
        print(format_list(instance))
        return 0
    try:
        event = build_event(a.verb, a.args, a.because, instance=instance, except_pattern=a.except_pattern)
    except (ValueError, re.error) as e:
        print(f"policy: {e}", file=sys.stderr)
        return 2
    p = append(instance, event)
    print(f"filed {event['policy_id']} in {p}")
    print(f"  {json.dumps(event.get('policy', {'strike': event['policy_id']}), ensure_ascii=False)}")
    print(f'  "{event["sentence"]}"')
    print("next: make replay DATE=<edition> to see what it changes; the next build applies it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
