"""
fishwrap.scoring — policy evaluation.

The new engine does not assign a numeric score to each article. Articles are
seeded within a section by recency, then re-ordered for the lead tier by
section_lead_preference policies. This module is the home for the policy
evaluation primitives — given a candidate article and a set of active
policies, what fires?

Five primitives, all signed policies from policies.jsonl:

  source_ban              drop all articles from a source domain
  title_pattern_ban       drop articles whose title matches the regex
  topic_ban               drop articles whose title or content contains any
                          listed phrase
  source_whitelist        include articles from a source bypassing diversity
                          caps (with optional except_pattern)
  section_lead_preference for a given section, prefer items whose title
                          matches keywords for the lead tier slots

The historical compute_score() function is intentionally gone. There is no
numeric score for an article in the new pipeline; recency is the default
ordering and editorial weight is expressed as policies, not boosts.
"""
from __future__ import annotations

import re
from collections import defaultdict


def apply_exclusion_policies(articles, policies):
    """Apply source_ban, title_pattern_ban, topic_ban at intake.

    Returns (kept, dropped) where dropped is a list of (article, policy) tuples
    so the audit can attribute each exclusion to the signed policy that fired.
    """
    by_type = defaultdict(list)
    for p in policies:
        by_type[p["policy"]["type"]].append(p)
    source_bans = by_type.get("source_ban", [])
    title_bans = [(p, re.compile(p["policy"]["pattern"])) for p in by_type.get("title_pattern_ban", [])]
    topic_bans = by_type.get("topic_ban", [])

    kept, dropped = [], []
    for art in articles:
        src = (art.get("source_url") or "").lower()
        hit = next((p for p in source_bans if p["policy"]["match"].lower() in src), None)
        if hit:
            dropped.append((art, hit))
            continue
        title = art.get("title") or ""
        hit = next((p for p, rx in title_bans if rx.search(title)), None)
        if hit:
            dropped.append((art, hit))
            continue
        blob = (title + " " + (art.get("content") or "")).lower()
        hit = next(
            (p for p in topic_bans
             if any(phrase.lower() in blob for phrase in p["policy"].get("phrases", []))),
            None,
        )
        if hit:
            dropped.append((art, hit))
            continue
        kept.append(art)
    return kept, dropped


def is_whitelisted(article, policies):
    """Return the matching source_whitelist policy, or None.

    A whitelist may carry an except_pattern; titles matching it do NOT get
    the bypass and the function returns None.
    """
    src = (article.get("source_url") or "").lower()
    title = article.get("title") or ""
    for p in policies:
        pp = p["policy"]
        if pp["type"] != "source_whitelist":
            continue
        if pp.get("match", "").lower() not in src:
            continue
        ex = pp.get("except_pattern")
        if ex and re.search(ex, title):
            return None
        return p
    return None


def lead_preference_for(section_id, policies):
    """Return the section_lead_preference policy for this section, or None."""
    for p in policies:
        pp = p["policy"]
        if pp["type"] == "section_lead_preference" and pp.get("section") == section_id:
            return p
    return None
