"""
fishwrap.editor — the selection pipeline.

Six deterministic steps over a candidate list in total order (newest first,
ties by link):

  1. INTAKE    — load the window from the database; the editor sees each
                 candidate as its title and the first SNAPSHOT_CHARS of body
  2. EXCLUDE   — drop articles caught by source_ban, title_pattern_ban,
                 topic_ban (signed policies)
  3. CLASSIFY  — assign each article to a section: source_default first,
                 keyword_fallback second, last-section fallback last
  4. DEDUP     — global fuzzy dedup (time-windowed, Jaccard-prefiltered,
                 SequenceMatcher ratio); the leader keeps its cluster
  5. DIVERSIFY — per section, walk in order and skip any article whose
                 source has already contributed max_per_source items
                 (whitelisted sources bypass)
  6. TRUNCATE+TIER — take edition_size per section; assign tiers (lead /
                    feature / standard) using lead_count + feature_count,
                    with section_lead_preference re-ordering lead slots

No numeric scoring; ordering is recency. Editorial weight is expressed
through the policies. Every decision is recorded on the candidate dict
(underscore fields) and written to the runsheet, which is the only thing
anything downstream reads.
"""
from __future__ import annotations

import difflib
import json
import re
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from fishwrap import _config
from fishwrap import runsheet
from fishwrap import scoring
from fishwrap.db import repository
from fishwrap.log import get_logger
from fishwrap.masthead import Masthead

log = get_logger(__name__)

DEDUP_SIMILARITY_THRESHOLD = 0.70
DEDUP_WINDOW_HOURS = 48
DEDUP_WINDOW_SECONDS = DEDUP_WINDOW_HOURS * 3600


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

    Returns (leaders, drop_map) where drop_map[duplicate_link] = leader_link.
    Articles must arrive in total order (newest first); the leader of a
    cluster is the newest member.
    """
    leaders = []
    drop_map: dict[str, str] = {}
    token_cache = {
        a["link"]: set(w for w in (a.get("title") or "").lower().split() if len(w) > 3)
        for a in articles
    }
    for c in articles:
        c_t = (c.get("title") or "").lower()
        c_ts = c.get("timestamp", 0) or 0
        c_w = token_cache[c["link"]]
        matched = None
        for L in leaders:
            if abs(c_ts - (L.get("timestamp", 0) or 0)) > DEDUP_WINDOW_SECONDS:
                continue
            if c_w.isdisjoint(token_cache[L["link"]]):
                continue
            if difflib.SequenceMatcher(None, c_t, (L.get("title") or "").lower()).ratio() > threshold:
                matched = L
                break
        if matched:
            drop_map[c["link"]] = matched["link"]
        else:
            leaders.append(c)
    return leaders, drop_map


def _attach_clusters(articles, leaders, drop_map):
    """Record each cluster on its leader and point each duplicate at it."""
    by_link = {a["link"]: a for a in articles}
    members = defaultdict(list)
    for dup_link, leader_link in drop_map.items():
        members[leader_link].append(dup_link)
        by_link[dup_link]["_dup_of"] = leader_link
    for L in leaders:
        links = members.get(L["link"], [])
        domains = {runsheet.domain_of(L.get("source_url"))}
        domains.update(runsheet.domain_of(by_link[m].get("source_url")) for m in links)
        L["_cluster"] = {"leader": True, "size": 1 + len(links), "sources": len(domains), "members": links}


# ============ selection pipeline ============

def select_edition(articles, masthead: Masthead):
    """Run the full pipeline against a candidate list.

    Returns (edition, rejects, funnel):
      edition[section_id]   = list of selected articles in seed order
      rejects[section_id]   = list of {article, reason, detail}
      funnel                = dict of step counts + settings
    Every candidate dict is annotated in place with the decision trail.
    """
    sections = {s["id"]: s for s in masthead.sections}
    section_order = [s["id"] for s in masthead.sections]
    policies = masthead.policies
    threshold = getattr(masthead, "dedup_threshold", DEDUP_SIMILARITY_THRESHOLD)

    articles = sorted(articles, key=runsheet.total_key)
    funnel = {"intake": len(articles), "dedup_threshold": threshold, "dedup_window_hours": DEDUP_WINDOW_HOURS}

    # Step 2: exclusion policies at intake
    kept, policy_drops = scoring.apply_exclusion_policies(articles, policies)
    for art, policy in policy_drops:
        art["_policy_drop"] = policy
    funnel["after_exclusion_policies"] = len(kept)
    funnel["dropped_by_policy"] = len(policy_drops)
    funnel["policy_drops_by_type"] = Counter(p["policy"]["type"] for _, p in policy_drops)

    # Step 3: classify
    for a in kept:
        a["_section"], a["_class_reason"] = classify(a, masthead)

    # Step 4: dedup (input already in total order)
    leaders, drop_map = dedup(kept, threshold)
    _attach_clusters(kept, leaders, drop_map)
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
        for rank, art in enumerate(items, 1):
            domain = runsheet.domain_of(art.get("source_url"))
            art["_domain"] = domain
            art["_pool_rank"] = rank
            art["_pool_size"] = len(items)
            wl = scoring.is_whitelisted(art, policies)
            art["_whitelist_policy"] = wl
            if not wl and src_counts[domain] >= cap:
                art["_reject"] = {"reason": "diversity_cap", "detail": f"{domain} at {cap}"}
                rejects[sid].append({"article": art, **art["_reject"]})
                continue
            if len(selected) >= size:
                art["_reject"] = {"reason": "capacity", "detail": f"size {size}"}
                rejects[sid].append({"article": art, **art["_reject"]})
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
            lead_links = {a["link"] for a in leads}
            for a in selected:
                if a["link"] in lead_links:
                    a["_lead_promoted_by"] = lead_pref
            selected = leads + [a for a in selected if a["link"] not in lead_links]

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

def load_pipeline_inputs(masthead: Masthead, verbose: bool = True):
    """Load the candidate window from the DB as editor snapshots, in total order.

    The window is anchored to wall-clock, or to the DB's freshest article
    when the DB is staler than the window (dev against a snapshot), so a
    stale DB yields its most recent N hours instead of nothing.

    Returns (candidates, anchor_ts).
    """
    db_max_ts = repository.get_max_timestamp()
    now = time.time()
    if db_max_ts is None or now - db_max_ts < masthead.expiration_hours * 3600:
        anchor_ts = now
    else:
        if verbose:
            print(f"[FISHWRAP] WARNING: DB freshest article is {(now - db_max_ts) / 3600:.1f}h old. "
                  f"Anchoring the window to the DB's max timestamp instead of wall clock.")
        anchor_ts = db_max_ts

    raw = repository.get_recent_articles(hours=masthead.expiration_hours, anchor_ts=anchor_ts)
    active = set(masthead.feeds)
    candidates = [runsheet.snapshot(c) for c in raw if (c.get("source_url") or "") in active]
    if verbose and len(candidates) != len(raw):
        print(f"[FISHWRAP] Active-feed filter: {len(raw)} -> {len(candidates)}")
    candidates.sort(key=runsheet.total_key)
    return candidates, anchor_ts


def run_editor():
    """Build an edition: load the window, run the pipeline, write the runsheet."""
    print("\n[EDITOR] Starting...")
    masthead = _config.MASTHEAD
    candidates, anchor_ts = load_pipeline_inputs(masthead)
    print(f"[EDITOR] Loaded {len(candidates)} candidates.")

    edition, rejects, funnel = select_edition(candidates, masthead)
    for sec in masthead.sections:
        n = len(edition.get(sec["id"], []))
        print(f"  {sec['title']:12s} ({sec['id']}): {n}/{sec['edition_size']}")

    date = runsheet.edition_date(masthead, datetime.fromtimestamp(anchor_ts, tz=timezone.utc))
    seen = Counter(c["source_url"] for c in candidates)
    feed_counts = {u: seen.get(u, 0) for u in masthead.feeds}
    header, records = runsheet.build(masthead, candidates, edition, rejects, funnel,
                                     date=date, anchor_ts=anchor_ts, feed_counts=feed_counts)
    path = runsheet.write(Path(_config.OUTPUT_DIR) / date / runsheet.FILENAME, header, records)
    print(f"[EDITOR] Published {header['funnel']['published']} of {len(records)} candidates. "
          f"Runsheet: {path}")


if __name__ == "__main__":
    run_editor()
