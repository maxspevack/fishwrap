"""
fishwrap.auditor — the audit data layer.

Persists run-level + per-article audit records to the DB. Produces the
per-story step-narrative (the prose-not-table audit) and the LLM editor's
rationale block (Editor mode only).

In Reader mode, the audit drawer shows the mechanical step-by-step:
  1. Where it came from (source + how it routed to a section)
  2. When it arrived (relative freshness)
  3. How it competed (pool size, freshness rank, diversity check)
  4. Where it landed (seed + tier + explanation of tier thresholds)
  i. Bonus info (upvotes/comments — informational only, never used for ranking)

In Editor mode, an additional 'editor's rationale' block sits above the
audit drawer with a one-sentence justification grounded in specific dossier
passages (cited by line number). In production, this is produced by a
Sonnet batched call per section with the dossier in context. The
substring-grounding contract verifies citations against dossier.md before
they render. In this demo, the rationales are pre-authored.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone

from fishwrap.db import repository
from fishwrap.log import get_logger
from fishwrap.masthead import Masthead

log = get_logger(__name__)


# ============ Editor mode rationales (hand-authored for the demo) ============
#
# Production: Sonnet batched call per section with dossier + candidates.
# Demo: pre-authored rationales mapped by partial title match. Each cited
# line is a real line in dossier.md.

def editor_rationales(dossier_lines):
    """Return a dict of {title_key: {rationale, citations}} for the demo.

    Each citation is (line_number, snippet) pointing to dossier.md.
    """
    def snip(n: int) -> str:
        n = max(1, min(n, len(dossier_lines)))
        return dossier_lines[n - 1].strip()[:120]

    return {
        "pope leo": {
            "rationale": "Pope Leo XIV's apology for the Holy See's role in slavery is the day's biggest moral-authority story from a major institution — squarely inside Beat's identity ([cite:1]). The r/worldnews provenance gives us conversation, not just wire copy ([cite:2]). I'm leading with it.",
            "citations": [(22, snip(22)), (52, snip(52))],
        },
        "anti-abortion": {
            "rationale": "Politico filed original reporting on a fault line inside the conservative coalition; this is the kind of named-source policy reporting Beat is for ([cite:1]). The Trump-administration angle and the Supreme Court frame both fire ([cite:2]). Feature, not lead — too narrow for the lead slot today.",
            "citations": [(23, snip(23)), (95, snip(95))],
        },
        "stanley cup": {
            "rationale": "Conference Finals are live; this is exactly the Turf seasonal-lead window I defined ([cite:1]). Stanley Cup + bracket = the most evergreen NHL-playoff frame available today.",
            "citations": [(37, snip(37))],
        },
        "knicks": {
            "rationale": "Knicks-Pacers Conference Finals; the dossier's calendar names this matchup family as the NBA lead slot through mid-June ([cite:1]). Pairs naturally with the Stanley Cup story for the two Turf leads.",
            "citations": [(37, snip(37))],
        },
        "wembanyama": {
            "rationale": "Defector + Wembanyama. The single highest-conviction byline+subject combination in the masthead — Drew Magary-adjacent voice on a current NBA story. Whitelisted; cap-bypass.",
            "citations": [(31, snip(31)), (66, snip(66))],
        },
        "openai": {
            "rationale": "OpenAI industry-drama story with named principals. Atom's AI-industry-drama lane ([cite:1]); the named-principal frame is what distinguishes this from a corporate-blog rewrite ([cite:2]).",
            "citations": [(41, snip(41)), (45, snip(45))],
        },
        "lwn": {
            "rationale": "LWN was hand-boosted in the founding masthead and remains a Tier-A source for the open-source substrate lane ([cite:1]). This kernel/distro piece is exactly what Atom's identity asks for.",
            "citations": [(67, snip(67))],
        },
        "krebs": {
            "rationale": "Original investigation under Krebs's byline — the named-researcher cybersec criterion fires ([cite:1]). This is what Atom wants; the wire-rewrites and corporate threat-intel get filtered out.",
            "citations": [(43, snip(43))],
        },
        "stephenson": {
            "rationale": "Neal Stephenson's substack. The author whose Diamond Age + Anathem epigraphs founded fishwrap itself — culture-of-ideas, not entertainment industry. Gala's prestige-thinking lane.",
            "citations": [(51, snip(51))],
        },
        "greenwald": {
            "rationale": "Greenwald's substack — the named-byline investigative-journalism criterion fires ([cite:1]). Beat lead candidate when his piece is the day's substantive story; otherwise feature.",
            "citations": [(23, snip(23))],
        },
        "magary": {
            "rationale": "Drew Magary at Defector. +1 content_boost in the founding masthead AND +3 source boost on the domain. The single highest-conviction byline in the configuration ([cite:1]).",
            "citations": [(31, snip(31))],
        },
        "dog accidentally": {
            "rationale": "Weird-news that earns the headline — belongs in Gala, not Beat ([cite:1]). The masthead's source_default routed this to news; the editorial judgment overrides on classification because the story shape fits Gala's identity.",
            "citations": [(51, snip(51))],
        },
    }


def attach_rationales(edition, rationales):
    """Mutate edition: attach _editor_rationale to each article that matches a key."""
    for arts in edition.values():
        for art in arts:
            t = (art.get("title") or "").lower()
            for key, payload in rationales.items():
                if key in t:
                    art["_editor_rationale"] = payload
                    break


# ============ run-level audit persistence ============

def audit_run(edition, rejects, funnel, candidates, masthead: Masthead):
    """Persist the run + audit logs to the DB.

    The DB schema is unchanged from v2 (runs, run_articles, audit_logs tables).
    What changed is the SHAPE of the audit data: no boosts/scores, just the
    per-step classification + dedup + diversify decisions.
    """
    selected_ids: set[str] = set()
    flat_selected: list[dict] = []
    for sid, arts in edition.items():
        for i, art in enumerate(arts):
            flat_selected.append({
                "article_id": art.get("id"),
                "rank": i + 1,
                "score": None,  # no numeric score in the new engine
                "section": sid,
            })
            selected_ids.add(art.get("id"))

    audit_logs: list[dict] = []
    for art in candidates:
        decision = "SELECTED" if art.get("id") in selected_ids else "REJECTED"
        trace = {
            "section": art.get("_section"),
            "class_reason": art.get("_class_reason"),
            "tier": art.get("_tier"),
            "seed": art.get("_seed"),
            "whitelist_policy_id": (art.get("_whitelist_policy") or {}).get("policy_id"),
            "lead_promoted_by_policy_id": (art.get("_lead_promoted_by") or {}).get("policy_id"),
        }
        audit_logs.append({
            "article_id": art.get("id"),
            "original_section": art.get("_section"),
            "final_section": art.get("_section"),
            "base_score": 0,
            "modifier_score": 0,
            "final_score": 0,
            "decision": decision,
            "trace": trace,
        })

    run_data = {
        "run_type": "daily",
        "stats_input": len(candidates),
        "stats_pool": funnel.get("after_dedup", 0),
        "stats_selected": len(selected_ids),
        "source_dominance": [],  # computed by printer.render_stats now
        "perf_metrics": {},
    }
    run_id = repository.save_run(run_data, flat_selected)
    repository.save_audit_logs(run_id, audit_logs)
    print(f"[AUDITOR] Run recorded: {run_id}. Audit logs saved: {len(audit_logs)}.")
    return run_id


# ============ funnel summary helpers (used by printer) ============

def funnel_summary(funnel: dict) -> dict:
    """Coerce the funnel dict into a stable shape for the printer."""
    return {
        "intake": funnel.get("intake", 0),
        "after_exclusion_policies": funnel.get("after_exclusion_policies", funnel.get("intake", 0)),
        "after_dedup": funnel.get("after_dedup", 0),
        "deduped_out": funnel.get("deduped_out", 0),
        "dropped_by_policy": funnel.get("dropped_by_policy", 0),
        "policy_drops_by_type": dict(funnel.get("policy_drops_by_type", {})),
        "dropped_by_policy_detail": funnel.get("dropped_by_policy_detail", []),
        "rejected": funnel.get("rejected", 0),
    }


def fresh_age(ts, max_ts) -> str:
    """Human-friendly age relative to the freshest article in the pool."""
    if not ts:
        return "?"
    age = max_ts - ts
    if age < 0:
        return "0m"
    if age < 3600:
        return f"{int(age/60)}m"
    if age < 86400:
        return f"{age/3600:.1f}h"
    return f"{age/86400:.1f}d"
