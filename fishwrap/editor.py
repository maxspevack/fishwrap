"""
fishwrap.editor — the selection pipeline.

Six deterministic steps:

  1. INTAKE    — load articles from the database within the freshness window
  2. EXCLUDE   — drop articles caught by source_ban, title_pattern_ban,
                 topic_ban (from policies.jsonl)
  3. CLASSIFY  — assign each article to a section: source_default first,
                 keyword_fallback second, last-section fallback last
  4. DEDUP     — global fuzzy dedup (time-windowed, Jaccard-prefiltered,
                 SequenceMatcher ratio)
  5. DIVERSIFY — per section, walk in recency order and skip any article
                 whose source has already contributed max_per_source items
                 (whitelisted sources bypass)
  6. TRUNCATE+TIER — take edition_size per section; assign tiers (lead
                    / feature / standard) using lead_count + feature_count,
                    with section_lead_preference re-ordering lead slots
                    by title keyword match

No numeric scoring; ordering is recency. Editorial weight is expressed
through the policies, not through magic numbers.
"""
from __future__ import annotations

import difflib
import json
import os
import re
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone

from fishwrap import _config
from fishwrap import scoring
from fishwrap.db import repository
from fishwrap.log import get_logger
from fishwrap.masthead import Masthead

log = get_logger(__name__)

DEDUP_SIMILARITY_THRESHOLD = 0.70
DEDUP_WINDOW_SECONDS = 48 * 3600


# ============ classification ============

def classify(article, masthead: Masthead):
    """Assign a section + reason.

    Returns (section_id, reason_dict) where reason_dict carries enough info
    to reconstruct the decision in the audit. Three paths:
      source_default     — the article's source URL matches a key in
                           masthead.source_sections
      keyword_fallback   — the section's classification keywords matched
                           the article's title + content + categories
      fallback           — no source default, no keyword hit; routes to
                           the last section defined
    """
    src = (article.get("source_url") or "").lower()
    for key, sid in masthead.source_sections.items():
        if key.lower() in src:
            return sid, {"path": "source_default", "match": key}

    title = (article.get("title") or "").lower()
    content = (article.get("content") or "").lower()[:500]
    cats = ""
    try:
        c = article.get("categories")
        if isinstance(c, list):
            cats = " ".join(c)
        elif isinstance(c, str):
            cats = " ".join(json.loads(c) or [])
    except Exception:
        cats = ""
    text_blob = f"{title} {cats.lower()} {content}"

    scores, matched = {}, {}
    for sec in masthead.sections:
        sid = sec["id"]
        hits = [
            k for k in (sec.get("keywords") or [])
            if re.search(rf"\b{re.escape(k.lower())}\b", text_blob)
        ]
        scores[sid] = len(hits)
        matched[sid] = hits

    best = max(scores.values()) if scores else 0
    if best > 0:
        # First section (by declaration order) with the best score wins ties.
        for sec in masthead.sections:
            if scores[sec["id"]] == best:
                return sec["id"], {
                    "path": "keyword_fallback",
                    "matched_terms": matched[sec["id"]],
                }

    fallback = masthead.sections[-1]["id"] if masthead.sections else "news"
    return fallback, {"path": "fallback"}


# ============ dedup ============

def dedup(articles, threshold: float = DEDUP_SIMILARITY_THRESHOLD):
    """Global fuzzy dedup with time-windowed blocking + Jaccard pre-filter.

    Returns (leaders, drop_map) where drop_map[duplicate_id] = leader_id.
    Articles are assumed to be sorted recency-DESC at input.
    """
    leaders = []
    drop_map: dict[str, str] = {}
    token_cache = {
        a["id"]: set(w for w in (a.get("title") or "").lower().split() if len(w) > 3)
        for a in articles
    }
    for c in articles:
        c_t = (c.get("title") or "").lower()
        c_ts = c.get("timestamp", 0) or 0
        c_w = token_cache[c["id"]]
        matched = None
        for L in leaders:
            if abs(c_ts - (L.get("timestamp", 0) or 0)) > DEDUP_WINDOW_SECONDS:
                continue
            if c_w.isdisjoint(token_cache[L["id"]]):
                continue
            if difflib.SequenceMatcher(None, c_t, (L.get("title") or "").lower()).ratio() > threshold:
                matched = L
                break
        if matched:
            drop_map[c["id"]] = matched["id"]
        else:
            leaders.append(c)
    return leaders, drop_map


# ============ selection pipeline ============

def select_edition(articles, masthead: Masthead):
    """Run the full pipeline against a candidate list.

    Returns (edition, rejects, funnel):
      edition[section_id]   = list of selected articles in seed order
      rejects[section_id]   = list of {article, reason, detail}
      funnel                = dict of step counts + ancillary data
    """
    sections = {s["id"]: s for s in masthead.sections}
    section_order = [s["id"] for s in masthead.sections]
    policies = masthead.policies

    funnel = {"intake": len(articles)}

    # Step 2: exclusion policies at intake
    kept, policy_drops = scoring.apply_exclusion_policies(articles, policies)
    funnel["after_exclusion_policies"] = len(kept)
    funnel["dropped_by_policy"] = len(policy_drops)
    funnel["policy_drops_by_type"] = Counter(p["policy"]["type"] for _, p in policy_drops)
    funnel["dropped_by_policy_detail"] = policy_drops

    # Step 3: classify
    for a in kept:
        a["_section"], a["_class_reason"] = classify(a, masthead)

    # Step 4: dedup
    kept_sorted = sorted(kept, key=lambda x: x.get("timestamp", 0) or 0, reverse=True)
    leaders, drop_map = dedup(kept_sorted)
    funnel["after_dedup"] = len(leaders)
    funnel["deduped_out"] = len(drop_map)

    # Step 5: bucket by section
    buckets = defaultdict(list)
    for a in leaders:
        buckets[a["_section"]].append(a)

    edition: dict[str, list] = {}
    rejects: dict[str, list] = defaultdict(list)

    for sid in section_order:
        sec = sections[sid]
        items = buckets[sid]
        cap = sec.get("max_per_source", 5)
        size = sec.get("edition_size", 10)

        selected, src_counts = [], Counter()
        for art in items:
            try:
                domain = (art.get("source_url") or "").split("/")[2]
            except IndexError:
                domain = "unknown"
            art["_domain"] = domain
            wl = scoring.is_whitelisted(art, policies)
            art["_whitelist_policy"] = wl
            if not wl and src_counts[domain] >= cap:
                rejects[sid].append({"article": art, "reason": "diversity_cap",
                                     "detail": f"{domain} at {cap}"})
                continue
            if len(selected) >= size:
                rejects[sid].append({"article": art, "reason": "capacity",
                                     "detail": f"size {size}"})
                continue
            src_counts[domain] += 1
            selected.append(art)

        # Step 6: tier with section_lead_preference applied to lead slots
        lead_count = sec.get("lead_count", 2)
        feature_count = sec.get("feature_count", 5)
        lead_pref = scoring.lead_preference_for(sid, policies)
        if lead_pref:
            kws = [k.lower() for k in lead_pref["policy"].get("lead_keywords", [])]

            def matches(a, _kws=kws):
                txt = (a.get("title") or "").lower()
                return any(re.search(rf"\b{re.escape(k)}\b", txt) for k in _kws)

            matching = [a for a in selected if matches(a)]
            non_matching = [a for a in selected if not matches(a)]
            leads = matching[:lead_count]
            if len(leads) < lead_count:
                leads += non_matching[: lead_count - len(leads)]
            lead_ids = {a["id"] for a in leads}
            for a in selected:
                if a["id"] in lead_ids:
                    a["_lead_promoted_by"] = lead_pref
            selected = leads + [a for a in selected if a["id"] not in lead_ids]

        for i, a in enumerate(selected):
            if i < lead_count:
                a["_tier"] = "lead"
            elif i < lead_count + feature_count:
                a["_tier"] = "feature"
            else:
                a["_tier"] = "standard"
            a["_seed"] = i + 1
        edition[sid] = selected

    funnel["after_diversify_and_truncate"] = sum(len(v) for v in edition.values())
    funnel["rejected"] = sum(len(v) for v in rejects.values())
    return edition, dict(rejects), funnel


# ============ orchestrator (CLI entry point) ============

def run_editor():
    """Build an edition. Reads candidates from the database, runs the pipeline,
    writes the run sheet, then hands off to the auditor.
    """
    from fishwrap import auditor  # local import to avoid cycle at import time
    print("\n[EDITOR] Starting...")

    masthead = _config.MASTHEAD

    raw_candidates = repository.get_recent_articles(hours=masthead.expiration_hours)
    print(f"[EDITOR] Loaded {len(raw_candidates)} candidates.")

    active_feeds = set(masthead.feeds)
    candidates = [c for c in raw_candidates if (c.get("source_url") or "") in active_feeds]
    if len(candidates) != len(raw_candidates):
        print(f"[EDITOR] Active-feed filter: {len(raw_candidates)} -> {len(candidates)}")

    edition, rejects, funnel = select_edition(candidates, masthead)
    total = sum(len(arts) for arts in edition.values())
    for sec in masthead.sections:
        n = len(edition.get(sec["id"], []))
        print(f"  {sec['title']:12s} ({sec['id']}): {n}/{sec['edition_size']}")
    print(f"[EDITOR] Published {total} articles.")

    # Run sheet: keep as a simple per-section list for printer/auditor handoff.
    run_sheet = {sid: arts for sid, arts in edition.items()}
    with open(_config.RUN_SHEET_FILE, "w", encoding="utf-8") as f:
        json.dump(run_sheet, f, indent=2, default=str)

    # Auditor — persists run + per-article audit logs to the DB.
    auditor.audit_run(edition, rejects, funnel, candidates, masthead)


if __name__ == "__main__":
    run_editor()
