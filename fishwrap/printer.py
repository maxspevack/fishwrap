"""
fishwrap.printer — HTML rendering.

Produces four artifacts per run, all written to demo/output/ (or the
configured output directory):

  edition-reader.html  — the paper, signed out (no editor on duty).
  edition-editor.html  — the paper, editor on duty (LLM rationales visible).
  feeds-admin.html     — the per-feed admin surface (volume dial + section
                         routing dropdown + drop button). Demo-inert.
  morgue.html          — every prior version of masthead + dossier. The word
                         'git' never appears in user-facing copy.

Plus, for each non-current entry in the morgue:
  morgue-view-<SHA>.html       — side-by-side diff vs current
  morgue-restore-<SHA>.html    — republish confirmation, explicit what-happens

CSS is inlined. No external assets. Pages are self-contained.
"""
from __future__ import annotations

import json
import re
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from html import escape
from pathlib import Path

from fishwrap import _config
from fishwrap import auditor as fw_auditor
from fishwrap.log import get_logger
from fishwrap.masthead import Masthead

log = get_logger(__name__)


# ============ palette + CSS ============

CSS = """
:root {
  --cream: #f6efe3;
  --refusal: #16110b;
  --cardinal: #b3261e;
  --lead: #4d4438;
  --bone: #d4caba;
  --folio: #a8852c;
  --margin: #2a2520;
  --editor-on: #0B8759;
  --editor-off: #8a8478;
}
* { box-sizing: border-box; }
body { font-family: 'Libre Baskerville', Georgia, serif; background: var(--cream); color: var(--refusal); margin: 0; padding: 0; line-height: 1.5; }
.shell { max-width: 1080px; margin: 0 auto; padding: 2rem; }
nav.top { background: var(--refusal); color: var(--cream); padding: 0.5rem 2rem; font-family: 'iA Writer Mono', ui-monospace, monospace; font-size: 0.78rem; }
nav.top a { color: var(--cream); text-decoration: none; margin-right: 1.5rem; }
nav.top a.active { color: var(--editor-on); font-weight: bold; }
nav.top .right { float: right; }
header.masthead { border-bottom: 3px double var(--refusal); padding: 1.5rem 0 1rem; display: grid; grid-template-columns: 1fr auto; align-items: end; gap: 1rem; }
header.masthead h1 { font-size: 3rem; margin: 0; letter-spacing: -0.02em; }
header.masthead .dateline { font-style: italic; color: var(--lead); font-size: 0.95rem; }
header.masthead .editor-slot { font-family: 'iA Writer Mono', ui-monospace, monospace; font-size: 0.8rem; text-align: right; }
header.masthead .editor-slot .label { color: var(--margin); }
header.masthead .editor-slot .editor-on { color: var(--editor-on); font-weight: bold; }
header.masthead .editor-slot .editor-off { color: var(--editor-off); font-style: italic; }
.signin-strip { display: inline-block; padding: 0.3rem 0.7rem; text-decoration: none; font-family: 'iA Writer Mono', monospace; font-size: 0.78rem; }
.signin-strip.signed-out { border: 1px solid var(--lead); color: var(--lead); background: var(--cream); }
.signin-strip.signed-in { background: var(--editor-on); color: var(--cream); border: 1px solid var(--editor-on); }
.signin-strip.signed-out:hover { background: var(--editor-on); color: var(--cream); border-color: var(--editor-on); }
section.deck { margin: 2rem 0 3rem; }
section.deck > h2 { font-size: 1.6rem; border-bottom: 1px solid var(--refusal); padding-bottom: 0.25rem; display: flex; align-items: baseline; gap: 0.75rem; }
section.deck > h2 .pill { font-family: 'iA Writer Mono', ui-monospace, monospace; font-size: 0.7rem; background: var(--refusal); color: var(--cream); padding: 0.15rem 0.5rem; }
section.deck > h2 .pill.tier { background: var(--folio); }
article { margin: 1.5rem 0; padding: 1rem 0; border-bottom: 1px solid var(--bone); display: grid; grid-template-columns: 3rem 1fr; gap: 1rem; }
article .seed { font-family: 'iA Writer Mono', ui-monospace, monospace; font-size: 1.5rem; color: var(--margin); text-align: right; padding-top: 0.2rem; }
article.lead .seed { color: var(--cardinal); font-weight: bold; }
article.lead h3 { font-size: 1.5rem; }
article.feature h3 { font-size: 1.2rem; }
article.standard h3 { font-size: 1.0rem; }
article h3 { margin: 0 0 0.3rem 0; }
article h3 a { color: var(--refusal); text-decoration: none; }
article h3 a:hover { color: var(--cardinal); }
article .meta { font-family: 'iA Writer Mono', ui-monospace, monospace; font-size: 0.72rem; color: var(--margin); }
article .tier-label { display: inline-block; padding: 0.05rem 0.4rem; font-size: 0.66rem; font-family: 'iA Writer Mono', ui-monospace, monospace; background: var(--folio); color: var(--cream); vertical-align: middle; margin-left: 0.3rem; }
article .tier-label.lead { background: var(--cardinal); }
article .tier-label.standard { background: var(--lead); }
details.audit { margin-top: 0.6rem; background: rgba(0,0,0,0.02); padding: 0.6rem 0.85rem; border-left: 2px solid var(--folio); }
details.audit[open] { background: rgba(168, 133, 44, 0.08); }
details.audit summary { cursor: pointer; color: var(--lead); font-family: 'iA Writer Mono', ui-monospace, monospace; font-size: 0.78rem; }
details.audit summary:hover { color: var(--cardinal); }
.audit-body { margin-top: 0.75rem; font-size: 0.88rem; line-height: 1.55; }
.audit-step { margin: 0.5rem 0; padding-left: 2.2rem; position: relative; }
.audit-step .num { position: absolute; left: 0; top: 0; width: 1.6rem; height: 1.6rem; text-align: center; line-height: 1.6rem; border-radius: 50%; background: var(--folio); color: var(--cream); font-family: 'iA Writer Mono', monospace; font-size: 0.75rem; font-weight: bold; }
.audit-step .label { font-family: 'iA Writer Mono', monospace; font-size: 0.7rem; color: var(--margin); letter-spacing: 0.04em; text-transform: uppercase; }
.audit-step .body { color: var(--refusal); }
.audit-step.bonus .num { background: var(--bone); color: var(--margin); }
.audit-step.bonus .body { color: var(--margin); font-style: italic; }
.audit-step .check { color: var(--editor-on); font-weight: bold; }
.editor-rationale { background: rgba(11, 135, 89, 0.06); border-left: 2px solid var(--editor-on); padding: 0.6rem 0.85rem; margin-top: 0.6rem; font-family: 'Libre Baskerville', Georgia, serif; font-style: italic; font-size: 0.92rem; line-height: 1.45; }
.editor-rationale .sig { display: block; margin-top: 0.4rem; font-style: normal; font-family: 'iA Writer Mono', ui-monospace, monospace; font-size: 0.7rem; color: var(--editor-on); }
.editor-rationale sup { color: var(--cardinal); font-family: 'iA Writer Mono', ui-monospace, monospace; font-size: 0.62rem; vertical-align: super; }
.editor-rationale .citations { display: block; margin-top: 0.5rem; font-style: normal; font-family: 'iA Writer Mono', ui-monospace, monospace; font-size: 0.7rem; color: var(--margin); }
.editor-rationale .citations .cite-num { color: var(--cardinal); font-weight: bold; }
.actions { margin-top: 0.6rem; font-family: 'iA Writer Mono', ui-monospace, monospace; font-size: 0.72rem; }
.actions a.btn, .actions button { font-family: inherit; font-size: inherit; border: 1px solid var(--lead); background: var(--cream); color: var(--refusal); padding: 0.2rem 0.5rem; margin-right: 0.4rem; cursor: pointer; text-decoration: none; }
.actions .btn.spike { border-color: var(--cardinal); color: var(--cardinal); }
.actions .btn.spike:hover { background: var(--cardinal); color: var(--cream); }
.actions .btn.lead-pin { border-color: var(--folio); color: var(--folio); }
.actions .btn.lead-pin:hover { background: var(--folio); color: var(--cream); }
.actions .ask { border-color: var(--editor-on); color: var(--editor-on); }
.actions .ask:hover { background: var(--editor-on); color: var(--cream); }
.actions .ask[disabled] { border-color: var(--editor-off); color: var(--editor-off); cursor: not-allowed; background: var(--cream); }
section.nerds, section.admin { margin-top: 3rem; padding-top: 1.5rem; border-top: 3px double var(--refusal); }
section.nerds h2, section.admin h2 { font-size: 1.4rem; }
section.nerds h3, section.admin h3 { font-size: 1rem; margin-top: 1.5rem; border-bottom: 1px dotted var(--bone); }
section.nerds table, section.admin table { width: 100%; font-family: 'iA Writer Mono', ui-monospace, monospace; font-size: 0.76rem; border-collapse: collapse; }
section.nerds th, section.nerds td, section.admin th, section.admin td { text-align: left; padding: 0.25rem 0.5rem; border-bottom: 1px dotted var(--bone); }
.scroll-wrap { max-height: 480px; overflow-y: auto; border: 1px solid var(--bone); }
.muted { color: var(--margin); }
footer { margin: 3rem 0 0; padding-top: 1rem; border-top: 1px solid var(--bone); font-family: 'iA Writer Mono', monospace; font-size: 0.7rem; color: var(--margin); }
.feed-row { display: grid; grid-template-columns: 3fr 1.4fr 2.2fr 0.5fr; gap: 0.8rem; padding: 0.55rem 0; border-bottom: 1px dotted var(--bone); align-items: center; }
.feed-row.header { font-family: 'iA Writer Mono', monospace; font-size: 0.7rem; color: var(--margin); text-transform: uppercase; letter-spacing: 0.04em; border-bottom: 1px solid var(--refusal); padding-bottom: 0.5rem; }
.feed-row .friendly { font-weight: bold; font-size: 0.95rem; }
.feed-row .url { font-family: 'iA Writer Mono', monospace; font-size: 0.68rem; color: var(--margin); margin-top: 0.15rem; word-break: break-all; }
.feed-row select { font-family: inherit; font-size: 0.85rem; padding: 0.2rem 0.4rem; border: 1px solid var(--bone); background: var(--cream); color: var(--refusal); }
.feed-row .volume-control { display: flex; align-items: center; gap: 0.5rem; font-family: 'iA Writer Mono', monospace; font-size: 0.72rem; color: var(--margin); }
.feed-row .remove { text-align: center; font-size: 1.1rem; color: var(--cardinal); text-decoration: none; cursor: pointer; }
.feed-row .remove:hover { font-weight: bold; }
.dial { display: inline-flex; gap: 0; font-family: 'iA Writer Mono', monospace; font-size: 0.82rem; user-select: none; border: 1px solid var(--bone); }
.dial span { display: inline-block; min-width: 1.5rem; text-align: center; padding: 0.2rem 0.3rem; border-right: 1px solid var(--bone); background: var(--cream); color: var(--margin); cursor: pointer; }
.dial span:last-child { border-right: none; }
.dial span.active { font-weight: bold; }
.dial span.active.never { background: var(--cardinal); color: var(--cream); }
.dial span.active.less { background: var(--cardinal); color: var(--cream); opacity: 0.7; }
.dial span.active.normal { background: var(--bone); color: var(--refusal); }
.dial span.active.more { background: var(--editor-on); color: var(--cream); opacity: 0.85; }
.dial span.active.all { background: var(--editor-on); color: var(--cream); }
.dial-label { font-family: 'iA Writer Mono', monospace; font-size: 0.66rem; color: var(--margin); text-transform: uppercase; letter-spacing: 0.04em; }
.morgue-diff { font-family: 'iA Writer Mono', monospace; font-size: 0.78rem; background: rgba(0,0,0,0.03); padding: 0.8rem 1rem; margin: 0.5rem 0; border-left: 2px solid var(--folio); white-space: pre-wrap; }
.morgue-diff .add { background: rgba(11, 135, 89, 0.18); color: var(--refusal); display: block; }
.morgue-diff .del { background: rgba(179, 38, 30, 0.18); color: var(--refusal); display: block; text-decoration: line-through; text-decoration-color: var(--cardinal); }
.morgue-restore-confirm { border: 2px solid var(--folio); background: rgba(168, 133, 44, 0.05); padding: 1.5rem; margin: 1.5rem 0; }
.morgue-restore-confirm h3 { margin-top: 0; }
.morgue-restore-confirm ol, .morgue-restore-confirm ul { margin: 0.5rem 0; padding-left: 1.5rem; }
.morgue-restore-confirm li { margin: 0.4rem 0; }
.morgue-restore-confirm .cta { display: inline-block; margin-top: 1rem; padding: 0.5rem 1rem; background: var(--editor-on); color: var(--cream); text-decoration: none; border: 1px solid var(--editor-on); font-family: 'iA Writer Mono', monospace; font-size: 0.85rem; }
.morgue-restore-confirm .cancel { display: inline-block; margin-top: 1rem; margin-left: 0.5rem; padding: 0.5rem 1rem; background: var(--cream); color: var(--lead); text-decoration: none; border: 1px solid var(--lead); font-family: 'iA Writer Mono', monospace; font-size: 0.85rem; }
"""


# ============ shared chrome ============

def _render_topnav(active):
    items = [
        ("Reader",     "edition-reader.html", "reader"),
        ("Editor",     "edition-editor.html", "editor"),
        ("Feeds",      "feeds-admin.html",    "feeds"),
        ("The Morgue", "morgue.html",         "morgue"),
    ]
    links = "".join(
        f'<a class="{ "active" if a == active else "" }" href="{href}">{label}</a>'
        for label, href, a in items
    )
    return (f'<nav class="top">{links}'
            f'<span class="right">fishwrap · {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}</span></nav>')


def _render_masthead_header(masthead: Masthead, mode: str, page_label: str):
    today = datetime.now().strftime("%A, %B %d, %Y")
    if mode == "editor":
        editor_html = '<span class="editor-on">Editor on duty: Glenn Greenwald</span>'
        signin_html = '<a class="signin-strip signed-in" href="edition-reader.html">Signed in · sign out</a>'
    else:
        editor_html = '<span class="editor-off">No editor on duty</span>'
        signin_html = '<a class="signin-strip signed-out" href="edition-editor.html">Sign in as editor</a>'
    return f"""
<header class="masthead">
  <div>
    <h1>{escape(masthead.name)}</h1>
    <div class="dateline">{today} · {escape(page_label)}</div>
  </div>
  <div class="editor-slot">
    <span class="label">— editor's chair —</span><br>
    {editor_html}<br>
    {signin_html}
  </div>
</header>"""


# ============ per-story rendering ============

def _render_actions(mode):
    disabled = "" if mode == "editor" else ' disabled title="Editor mode required"'
    return f"""
<div class="actions">
  <a class="btn" href="#" title="Demote this story within the section">↓ reseed</a>
  <a class="btn" href="#" title="Move this story to a different section">→ reroute</a>
  <a class="btn lead-pin" href="#" title="Pin as the section's lead for today">📌 pin lead</a>
  <a class="btn spike" href="#" title="Never include this story again — proposes a policy">⚠ spike</a>
  <button class="ask"{disabled}>Ask the editor</button>
</div>"""


def _render_audit_narrative(art, section, max_ts, pool_size):
    reason = art.get("_class_reason", {})
    seed = art.get("_seed", 0)
    capacity = section.get("edition_size", 10)
    tier = art.get("_tier", "standard")
    lead_count = section.get("lead_count", 2)
    feature_count = section.get("feature_count", 5)
    max_per_source = section.get("max_per_source", 5)
    age = fw_auditor.fresh_age(art.get("timestamp"), max_ts)
    domain = art.get("_domain", "unknown")

    if reason.get("path") == "source_default":
        why_section = f"This source is set to route to <strong>{escape(section['title'])}</strong> by default."
    elif reason.get("path") == "keyword_fallback":
        terms = reason.get("matched_terms", [])
        if terms:
            terms_str = ", ".join(f'<em>"{escape(t)}"</em>' for t in terms[:5])
            more = f", and {len(terms)-5} more." if len(terms) > 5 else "."
            why_section = (f"Source had no default section. The story's text matched {len(terms)} keywords "
                           f"that route to <strong>{escape(section['title'])}</strong>: {terms_str}{more}")
        else:
            why_section = f"Source had no default. Routed to <strong>{escape(section['title'])}</strong> as the catch-all."
    else:
        why_section = f"No source default, no keyword match. Routed to <strong>{escape(section['title'])}</strong> (catch-all)."

    if art.get("_whitelist_policy"):
        wl_text = (f"<span class='check'>✓</span> Diversity check skipped — "
                   f"this source ({escape(domain)}) is set to <strong>print all</strong> "
                   f"(whitelisted), so it bypasses the per-source cap.")
    else:
        wl_text = (f"<span class='check'>✓</span> Diversity check passed "
                   f"(no more than <strong>{max_per_source}</strong> stories per source per section).")

    lp_text = ""
    if art.get("_lead_promoted_by") and tier == "lead":
        lp_text = ("<br><span class='check'>✓</span> Promoted into the lead slot because the story's "
                   "title matched a section lead-preference keyword (set in the masthead).")

    tier_explain = {
        "lead": f"The top <strong>{lead_count}</strong> stories in each section become the leads.",
        "feature": f"Stories ranked {lead_count+1} through {lead_count+feature_count} become features.",
        "standard": f"Stories ranked {lead_count+feature_count+1} through {capacity} are standard.",
    }.get(tier, "")

    return f"""
<div class="audit-body">
  <div class="audit-step">
    <div class="num">1</div>
    <div class="label">Where it came from</div>
    <div class="body">Pulled from <strong>{escape(domain)}</strong>. {why_section}</div>
  </div>
  <div class="audit-step">
    <div class="num">2</div>
    <div class="label">When it arrived</div>
    <div class="body">{age} ago, relative to the freshest story in today's pool.</div>
  </div>
  <div class="audit-step">
    <div class="num">3</div>
    <div class="label">How it competed</div>
    <div class="body"><strong>{pool_size}</strong> stories competed for the <strong>{capacity}</strong> {escape(section['title'])} slots in today's edition.<br>By freshness, this story ranked <strong>{seed} of {pool_size}</strong>.<br>{wl_text}{lp_text}</div>
  </div>
  <div class="audit-step">
    <div class="num">4</div>
    <div class="label">Where it landed</div>
    <div class="body">Printed at rank <strong>{seed} of {capacity}</strong> in {escape(section['title'])}. Tier: <strong>{tier}</strong>. {tier_explain}</div>
  </div>
  <div class="audit-step bonus">
    <div class="num">i</div>
    <div class="label">Bonus info (not used for ranking)</div>
    <div class="body"><a href="{escape(art.get('source_url') or '')}">source feed</a></div>
  </div>
</div>"""


def _render_article(art, section, max_ts, mode, pool_size):
    title = art.get("title") or "(untitled)"
    link = art.get("link") or "#"
    tier = art.get("_tier", "standard")
    seed = art.get("_seed", 0)
    domain = art.get("_domain", "unknown")
    age = fw_auditor.fresh_age(art.get("timestamp"), max_ts)

    rationale_html = ""
    if mode == "editor" and art.get("_editor_rationale"):
        r = art["_editor_rationale"]
        rationale_text = r["rationale"]
        for i, _ in enumerate(r["citations"], 1):
            rationale_text = rationale_text.replace(f"[cite:{i}]", f"<sup>{i}</sup>")
        citations_html = "".join(
            f'<div><span class="cite-num">{i}.</span> from your dossier (line {ln}): <em>{escape(snip)}</em></div>'
            for i, (ln, snip) in enumerate(r["citations"], 1)
        )
        rationale_html = (f'<div class="editor-rationale">{rationale_text}'
                          f'<span class="sig">— Glenn Greenwald, editor</span>'
                          f'<span class="citations">{citations_html}</span></div>')

    audit = _render_audit_narrative(art, section, max_ts, pool_size)
    actions = _render_actions(mode)

    return f"""
<article class="{tier}" id="art-{escape(art['id'])}">
  <div class="seed">{seed}</div>
  <div>
    <h3><a href="{escape(link)}" target="_blank" rel="noopener">{escape(title)}</a> <span class="tier-label {tier}">{tier}</span></h3>
    <div class="meta">{escape(domain)} · {age} old · section rank {seed} of {section['edition_size']}</div>
    {rationale_html}
    <details class="audit">
      <summary>How did this story end up here? (step-by-step)</summary>
      {audit}
    </details>
    {actions}
  </div>
</article>"""


# ============ stats for nerds ============

def _render_stats_for_nerds(candidates, edition, rejects, funnel, masthead: Masthead):
    sections = {s["id"]: s for s in masthead.sections}
    selected = sum(len(arts) for arts in edition.values())

    def dom(a):
        try:
            return (a.get("source_url") or "").split("/")[2]
        except IndexError:
            return "unknown"

    in_counts = Counter(dom(a) for a in candidates)
    out_counts = Counter(dom(a) for arts in edition.values() for a in arts)
    all_doms = sorted(set(in_counts) | set(out_counts), key=lambda d: -in_counts.get(d, 0))
    rows_html = "".join(
        f'<tr><td>{escape(d)}</td><td>{in_counts[d]}</td><td>{out_counts[d]}</td>'
        f'<td>{(out_counts[d]/in_counts[d]*100) if in_counts[d] else 0:.0f}%</td></tr>'
        for d in all_doms
    )
    yield_rows = "".join(
        f'<tr><td>{escape(sec["title"])} ({sid})</td>'
        f'<td>{len(edition.get(sid, []))} of {sec["edition_size"]}</td>'
        f'<td>{len(rejects.get(sid, []))}</td></tr>'
        for sid, sec in sections.items()
    )
    return f"""
<section class="nerds">
  <h2>Stats for nerds — the honest funnel</h2>
  <h3>Funnel</h3>
  <table>
    <tr><th>candidates intake (last {masthead.expiration_hours}h)</th><td>{funnel.get('intake',0):,}</td></tr>
    <tr><th>after signed-policy exclusion</th><td>{funnel.get('after_exclusion_policies', funnel.get('intake',0)):,}</td></tr>
    <tr><th>after dedup</th><td>{funnel.get('after_dedup',0):,} ({funnel.get('deduped_out',0):,} duplicates collapsed)</td></tr>
    <tr><th>selected to edition</th><td>{selected:,}</td></tr>
    <tr><th>rejected at diversify/capacity</th><td>{funnel.get('rejected',0):,}</td></tr>
  </table>
  <h3>Per-section yield</h3>
  <table><tr><th>section</th><th>filled</th><th>rejected</th></tr>{yield_rows}</table>
  <h3>Every contributing source</h3>
  <div class="scroll-wrap"><table><tr><th>domain</th><th>in</th><th>out</th><th>conversion</th></tr>{rows_html}</table></div>
</section>"""


# ============ edition page ============

def render_edition_page(masthead, edition, rejects, funnel, candidates, max_ts, mode):
    sections = {s["id"]: s for s in masthead.sections}
    page_label = "Signed in as editor" if mode == "editor" else "Reading without the editor"

    section_html = ""
    for sid, sec in sections.items():
        arts = edition.get(sid, [])
        rej_count = len(rejects.get(sid, []))
        pool_size = len(arts) + rej_count
        article_html = "".join(_render_article(a, sec, max_ts, mode, pool_size) for a in arts)
        standard_count = max(0, len(arts) - sec["lead_count"] - sec["feature_count"])
        section_html += f"""
<section class="deck" id="sec-{sid}">
  <h2>{escape(sec["title"])}
    <span class="pill">{escape(sec.get("description",""))}</span>
    <span class="pill tier">{sec["lead_count"]} leads · {sec["feature_count"]} features · {standard_count} standard</span>
  </h2>
  {article_html}
</section>"""

    nerds = _render_stats_for_nerds(candidates, edition, rejects, funnel, masthead)
    total = sum(len(a) for a in edition.values())

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{escape(masthead.name)} — {mode} mode</title>
  <style>{CSS}</style>
</head>
<body>
  {_render_topnav(mode)}
  <div class="shell">
    {_render_masthead_header(masthead, mode, page_label)}
    {section_html}
    {nerds}
    <footer>fishwrap · {mode} mode · {total} stories · data anchored to {datetime.fromtimestamp(max_ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}</footer>
  </div>
</body>
</html>"""


# ============ feeds admin ============

_FRIENDLY_NAME_LOOKUP = {
    "defector.com": "Defector", "lwn.net": "LWN",
    "natesilver.net": "Silver Bulletin (Nate Silver)",
    "greenwald.substack.com": "Glenn Greenwald",
    "nealstephenson.substack.com": "Graphomane (Neal Stephenson)",
    "americandebunk.substack.com": "American Debunk",
    "feeds.feedburner.com/TheRinger": "The Ringer",
    "krebsonsecurity.com": "Krebs on Security", "schneier.com": "Schneier on Security",
    "simonwillison.net": "Simon Willison's Weblog", "lilianweng.github.io": "Lil'Log (Lilian Weng)",
    "thegradient.pub": "The Gradient", "huggingface.co": "Hugging Face Blog",
    "bair.berkeley.edu": "Berkeley AI Research", "deepmind.google": "DeepMind Blog",
    "openai.com": "OpenAI Blog", "blogs.nvidia.com": "NVIDIA Blog",
    "rss.nytimes.com": "The New York Times", "feeds.bbci.co.uk": "BBC News",
    "feeds.npr.org": "NPR", "aljazeera.com": "Al Jazeera", "axios.com": "Axios",
    "politico.com": "Politico", "foxnews.com": "Fox News", "nypost.com": "New York Post",
    "techcrunch.com": "TechCrunch", "wired.com": "WIRED", "theverge.com": "The Verge",
    "arstechnica.com": "Ars Technica", "gizmodo.com": "Gizmodo",
    "hnrss.org": "Hacker News", "bleepingcomputer.com": "Bleeping Computer",
    "thehackernews.com": "The Hacker News", "espn.com": "ESPN",
    "cbssports.com": "CBS Sports", "sports.yahoo.com": "Yahoo Sports",
    "mashable.com": "Mashable", "lifehacker.com": "Lifehacker",
    "helpnetsecurity.com": "Help Net Security", "pitchfork.com": "Pitchfork",
}


def _friendly_name_for(url):
    u = url.lower()
    for key, name in _FRIENDLY_NAME_LOOKUP.items():
        if key in u:
            return name
    m = re.search(r"old\.reddit\.com/r/([^.]+)\.json", url)
    if m:
        return f"r/{m.group(1)}"
    m = re.search(r"https?://([^.]+)\.substack\.com", url)
    if m:
        return m.group(1).replace("_", " ").title() + " (Substack)"
    try:
        return url.split("/")[2].replace("www.", "").replace("feeds.", "")
    except IndexError:
        return url


def _section_for_url(url, source_sections):
    u = url.lower()
    for key, sid in source_sections.items():
        if key.lower() in u:
            return sid
    return None


def _volume_dial(active_state):
    states = [
        ("never",  "✕", "Never print stories from this source"),
        ("less",   "−", "Print less from this source"),
        ("normal", "·", "Default — let the editor decide"),
        ("more",   "+", "Print more from this source"),
        ("all",    "★", "Print every story from this source (bypasses the per-source variety cap)"),
    ]
    cells = "".join(
        f'<span class="{ "active " + s[0] if s[0] == active_state else "" }" title="{escape(s[2])}">{s[1]}</span>'
        for s in states
    )
    return f'<span class="dial">{cells}</span>'


_DEMO_VOLUME = {
    "defector.com": "all", "lwn.net": "more", "greenwald.substack.com": "more",
    "natesilver.net": "more", "krebsonsecurity.com": "more",
    "nealstephenson.substack.com": "more", "feeds.feedburner.com/TheRinger": "more",
    "helpnetsecurity": "never", "pitchfork": "never",
    "instapundit": "less", "townhall": "less", "phoronix": "less",
}


def _demo_volume_for(url):
    u = url.lower()
    for key, state in _DEMO_VOLUME.items():
        if key in u:
            return state
    return "normal"


def render_feeds_admin(masthead: Masthead):
    feeds = masthead.feeds
    rows = ""
    for url in feeds[:80]:
        friendly = _friendly_name_for(url)
        sec_pref = _section_for_url(url, masthead.source_sections)
        opts = (
            '<option value="">Let the editor decide</option>'
            + "".join(
                f'<option value="{escape(s["id"])}" {"selected" if sec_pref == s["id"] else ""}>'
                f'{escape(s["title"])} — {escape(s["id"])}</option>'
                for s in masthead.sections
            )
        )
        rows += f"""
<div class="feed-row">
  <div><div class="friendly">{escape(friendly)}</div><div class="url">{escape(url)}</div></div>
  <div><select>{opts}</select></div>
  <div class="volume-control"><span class="dial-label">volume</span>{_volume_dial(_demo_volume_for(url))}</div>
  <a class="remove" href="#" title="Drop this source from your paper">✕</a>
</div>"""

    return f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>{escape(masthead.name)} — Feeds</title><style>{CSS}</style></head>
<body>
  {_render_topnav("feeds")}
  <div class="shell">
    <header class="masthead">
      <div>
        <h1>Feeds</h1>
        <div class="dateline">{len(feeds)} sources in your paper · click to add, route, set volume, or drop</div>
      </div>
      <div class="editor-slot">
        <a class="signin-strip signed-in" href="#" style="cursor:pointer">+ Add a source</a>
      </div>
    </header>
    <section class="admin">
      <p class="muted" style="font-size: 0.92rem; line-height: 1.55; color: var(--refusal);">
        Each row is one source you read.
        <strong>Section</strong> says where this source's stories usually go — pick one, or <em>let the editor decide</em> based on each story's topic.
        <strong>Volume</strong> tells the editor how loud you want this source:
        <em>✕ never</em>, <em>− less</em>, <em>· default</em>, <em>+ more</em>,
        <em>★ all</em> (print every story it publishes, bypassing the per-source variety cap).
        The <strong>✕</strong> on the right removes the source entirely.
      </p>
      <div class="feed-row header"><div>source</div><div>section</div><div>volume</div><div>drop</div></div>
      {rows}
      <p class="muted" style="margin-top: 1rem;">Showing first 80 of {len(feeds)} feeds. <em>Demo — controls visible but inert. In production, every change you make here is filed in The Morgue.</em></p>
    </section>
  </div>
</body>
</html>"""


# ============ The Morgue (versioning UX over git, no 'git' in user copy) ============

def _git_log_entries(instance_dir):
    """Return list of {sha, short, date_iso, date_pretty, subject}.

    Filtered to commits that touched masthead.toml or dossier.md or
    policies.jsonl — so the Morgue shows only editorial state changes, not
    every source-code commit in the surrounding repo.
    """
    try:
        out = subprocess.run(
            ["git", "log",
             "--pretty=%H|%ad|%s", "--date=iso",
             "--", "masthead.toml", "dossier.md", "policies.jsonl"],
            cwd=str(instance_dir),
            capture_output=True, text=True, check=True
        ).stdout
    except Exception as e:
        log.warning("morgue: git log failed: %s", e)
        return []
    entries = []
    for line in out.strip().splitlines():
        parts = line.split("|", 2)
        if len(parts) < 3:
            continue
        sha, date, subject = parts
        try:
            dt = datetime.fromisoformat(date.replace(" ", "T", 1).rsplit(" ", 1)[0])
            date_pretty = dt.strftime("%A, %B %d, %Y · %H:%M")
        except Exception:
            date_pretty = date
        entries.append({"sha": sha, "short": sha[:7], "date_iso": date,
                        "date_pretty": date_pretty, "subject": subject})
    return entries


def _git_diff_between(instance_dir, sha_old, sha_new, filename):
    try:
        return subprocess.run(
            ["git", "diff", "--unified=2", sha_old, sha_new, "--", filename],
            cwd=str(instance_dir),
            capture_output=True, text=True, check=True
        ).stdout
    except Exception:
        return ""


def _render_diff_html(diff_text):
    if not diff_text.strip():
        return '<div class="muted">No changes to this file between these two versions.</div>'
    lines = []
    for line in diff_text.splitlines():
        if line.startswith("+++") or line.startswith("---"):
            continue
        if line.startswith("@@"):
            lines.append(f'<span class="muted">{escape(line)}</span>')
        elif line.startswith("+"):
            lines.append(f'<span class="add">{escape(line)}</span>')
        elif line.startswith("-"):
            lines.append(f'<span class="del">{escape(line)}</span>')
        else:
            lines.append(escape(line))
    return f'<div class="morgue-diff">{chr(10).join(lines)}</div>'


def render_morgue(masthead: Masthead):
    # Instance dir for git operations: the masthead's dir (i.e., where masthead.toml lives).
    # In the integrated demo, that's the fishwrap repo's demo/ directory.
    instance_dir = masthead.instance_dir
    entries = _git_log_entries(instance_dir)
    rows = ""
    for i, e in enumerate(entries):
        is_current = (i == 0)
        current_badge = (' <span style="background: var(--editor-on); color: var(--cream); '
                         'font-size: 0.6rem; padding: 0.1rem 0.4rem; margin-left: 0.4rem;">CURRENT</span>'
                         if is_current else '')
        if is_current:
            actions = '<div class="muted" style="font-family: iA Writer Mono, monospace; font-size: 0.72rem;">— in effect now —</div>'
        else:
            actions = (
                f'<div style="display:flex; gap:0.4rem;">'
                f'<a class="btn" href="morgue-view-{e["short"]}.html">view</a>'
                f'<a class="btn lead-pin" href="morgue-restore-{e["short"]}.html">republish</a>'
                f'</div>'
            )
        rows += f"""
<div class="feed-row" style="grid-template-columns: 1.5fr 4fr 1.5fr;">
  <div><div class="friendly">{escape(e['date_pretty'])}{current_badge}</div><div class="url">filed {escape(e['short'])}</div></div>
  <div>{escape(e['subject'])}</div>
  <div>{actions}</div>
</div>"""

    earliest = entries[-1]['date_pretty'].split(' · ')[0] if entries else 'today'
    return f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>{escape(masthead.name)} — The Morgue</title><style>{CSS}</style></head>
<body>
  {_render_topnav("morgue")}
  <div class="shell">
    <header class="masthead">
      <div>
        <h1>The Morgue</h1>
        <div class="dateline">every prior version of your paper · {len(entries)} editions on file</div>
      </div>
      <div class="editor-slot">
        <span class="label">— back issues —</span><br>
        <span class="editor-on">filed since {escape(earliest)}</span>
      </div>
    </header>
    <section class="admin">
      <p class="muted" style="font-size: 0.92rem; line-height: 1.55; color: var(--refusal);">
        Every change you (or the editor) makes to your <strong>masthead</strong> or <strong>dossier</strong> is filed here automatically.
        <strong>View</strong> opens a side-by-side: your current version on one side, the older version on the other, with every change highlighted.
        <strong>Republish</strong> brings an old version back as today's — without erasing any of the versions filed between then and now.
        Nothing in The Morgue is ever destroyed.
      </p>
      <div class="feed-row header" style="grid-template-columns: 1.5fr 4fr 1.5fr;">
        <div>filed</div><div>what changed</div><div></div>
      </div>
      {rows}
    </section>
  </div>
</body>
</html>"""


def render_morgue_view(masthead: Masthead, entries, idx):
    instance_dir = masthead.instance_dir
    entry = entries[idx]
    current = entries[0]
    masthead_diff = _git_diff_between(instance_dir, entry["sha"], current["sha"], "masthead.toml")
    dossier_diff = _git_diff_between(instance_dir, entry["sha"], current["sha"], "dossier.md")

    return f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>{escape(masthead.name)} — Viewing {escape(entry['short'])}</title><style>{CSS}</style></head>
<body>
  {_render_topnav("morgue")}
  <div class="shell">
    <header class="masthead">
      <div>
        <h1>Viewing back issue</h1>
        <div class="dateline">filed {escape(entry['date_pretty'])} · <a href="morgue.html">back to The Morgue</a></div>
      </div>
      <div class="editor-slot">
        <span class="label">— this version vs. today —</span><br>
        <a class="signin-strip signed-out" href="morgue-restore-{entry['short']}.html">Republish this version</a>
      </div>
    </header>
    <section class="admin">
      <p class="muted" style="font-size: 0.92rem; line-height: 1.55;">
        This is what changed between the version filed on <strong>{escape(entry['date_pretty'])}</strong> and your current version.
        <span style="background: rgba(11, 135, 89, 0.18); padding: 0.05rem 0.3rem;">Green</span> lines were added afterward.
        <span style="background: rgba(179, 38, 30, 0.18); padding: 0.05rem 0.3rem; text-decoration: line-through;">Red</span> lines were removed afterward.
        Restoring this version means going back to what's shown <em>without</em> the green lines, and <em>with</em> the red ones.
      </p>
      <h3 style="margin-top: 2rem;">Changes to your masthead</h3>
      {_render_diff_html(masthead_diff)}
      <h3 style="margin-top: 2rem;">Changes to your dossier</h3>
      {_render_diff_html(dossier_diff)}
    </section>
  </div>
</body>
</html>"""


def render_morgue_restore(masthead: Masthead, entries, idx):
    instance_dir = masthead.instance_dir
    entry = entries[idx]
    current = entries[0]
    masthead_diff = _git_diff_between(instance_dir, current["sha"], entry["sha"], "masthead.toml")
    dossier_diff = _git_diff_between(instance_dir, current["sha"], entry["sha"], "dossier.md")

    def count_changes(diff):
        adds = sum(1 for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++"))
        dels = sum(1 for l in diff.splitlines() if l.startswith("-") and not l.startswith("---"))
        return adds, dels

    m_adds, m_dels = count_changes(masthead_diff)
    d_adds, d_dels = count_changes(dossier_diff)
    earliest = entry['date_pretty'].split(' · ')[0]

    return f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>{escape(masthead.name)} — Republish {escape(entry['short'])}?</title><style>{CSS}</style></head>
<body>
  {_render_topnav("morgue")}
  <div class="shell">
    <header class="masthead">
      <div>
        <h1>Republish this version?</h1>
        <div class="dateline">filed {escape(entry['date_pretty'])} · <a href="morgue.html">back to The Morgue</a></div>
      </div>
    </header>
    <section class="admin">
      <div class="morgue-restore-confirm">
        <h3>What happens when you click Republish</h3>
        <ol>
          <li>Your <strong>masthead</strong> and <strong>dossier</strong> are reset to the state they were in when this version was filed: <em>{escape(entry['date_pretty'])}</em>.</li>
          <li>This change itself is filed in The Morgue as a new entry, dated today. Your current version (and every version filed since) stays in The Morgue forever — you can always come back.</li>
          <li>Your <strong>next edition</strong> is built against the restored configuration.</li>
          <li>If you change your mind, you can republish any other version — including your current one, which will still be filed.</li>
        </ol>
        <p><strong>What changes if you republish:</strong></p>
        <ul>
          <li>Masthead: <strong>{m_dels}</strong> {'lines' if m_dels != 1 else 'line'} added back, <strong>{m_adds}</strong> {'lines' if m_adds != 1 else 'line'} removed.</li>
          <li>Dossier: <strong>{d_dels}</strong> {'lines' if d_dels != 1 else 'line'} added back, <strong>{d_adds}</strong> {'lines' if d_adds != 1 else 'line'} removed.</li>
          <li><a href="morgue-view-{entry['short']}.html">See the full side-by-side</a> before deciding.</li>
        </ul>
        <p><strong>What does NOT happen:</strong></p>
        <ul>
          <li>Past editions of your paper are not unprinted. Yesterday's edition stays exactly as it was.</li>
          <li>No version in The Morgue is deleted or overwritten.</li>
          <li>Your reading history is not affected.</li>
        </ul>
        <a class="cta" href="#">Republish from {escape(earliest)}</a>
        <a class="cancel" href="morgue.html">Cancel — go back to The Morgue</a>
      </div>
    </section>
  </div>
</body>
</html>"""


# ============ CLI entry point ============

def run_printer():
    """Render the full demo: 2 edition pages + feeds-admin + morgue + per-commit pages.

    Reads the run sheet produced by the editor, loads the masthead, writes all
    HTML to the configured output directory.
    """
    masthead = _config.MASTHEAD

    # Re-run the pipeline so the printer has the same view the editor did.
    # This is cheap (~ms for 3k articles) and avoids persisting the full
    # candidate/rejects/funnel state to disk between editor and printer.
    from fishwrap import editor as fw_editor

    candidates, max_ts = fw_editor.load_pipeline_inputs(masthead, verbose=False)
    edition, rejects, funnel = fw_editor.select_edition(candidates, masthead)

    # Attach editor-mode rationales (pre-authored in this demo; in production
    # this is a Sonnet batched call per section grounded in dossier.md lines).
    rationales = fw_auditor.editor_rationales(masthead.dossier_lines)
    fw_auditor.attach_rationales(edition, rationales)

    out_dir = Path(_config.LATEST_HTML_FILE).parent
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "edition-reader.html").write_text(
        render_edition_page(masthead, edition, rejects, funnel, candidates, max_ts, "reader")
    )
    (out_dir / "edition-editor.html").write_text(
        render_edition_page(masthead, edition, rejects, funnel, candidates, max_ts, "editor")
    )
    (out_dir / "feeds-admin.html").write_text(render_feeds_admin(masthead))
    (out_dir / "morgue.html").write_text(render_morgue(masthead))

    entries = _git_log_entries(masthead.instance_dir)
    for i in range(1, len(entries)):
        e = entries[i]
        (out_dir / f"morgue-view-{e['short']}.html").write_text(
            render_morgue_view(masthead, entries, i)
        )
        (out_dir / f"morgue-restore-{e['short']}.html").write_text(
            render_morgue_restore(masthead, entries, i)
        )
    print(f"[PRINTER] Wrote 4 + {2*(len(entries)-1)} HTML pages to {out_dir}")


if __name__ == "__main__":
    run_printer()
