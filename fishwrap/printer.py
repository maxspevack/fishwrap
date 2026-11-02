"""
fishwrap.printer — HTML rendering from the runsheet.

Reads the newest runsheet and recomputes nothing. Writes into
demo/output/<YYYY-MM-DD>/:

  index.html              the paper, with a per-story audit drawer
  runsheet.html           the edition as a document: what came in, what was
                          cut and why, what led and why, every feed's yield
  feeds.html              every source: routing, policies, today's yield
  morgue.html             every prior version of masthead + dossier
  morgue-view-<sha>.html  one prior version against the current one

and demo/output/index.html, the pointer to the newest edition, written last.
CSS is inlined. No external assets. The word 'git' never appears in user copy.
"""
from __future__ import annotations

import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo

from fishwrap import _config
from fishwrap import runsheet
from fishwrap.log import get_logger
from fishwrap.masthead import Masthead

log = get_logger(__name__)


# ============ palette + CSS ============

CSS = """
:root {
  --cream: #f6efe3; --refusal: #16110b; --cardinal: #b3261e; --lead: #4d4438;
  --bone: #d4caba; --folio: #a8852c; --margin: #2a2520; --green: #0B8759;
}
* { box-sizing: border-box; }
body { font-family: 'Libre Baskerville', Georgia, serif; background: var(--cream); color: var(--refusal); margin: 0; padding: 0; line-height: 1.5; }
.shell { max-width: 1080px; margin: 0 auto; padding: 2rem; }
.mono { font-family: 'iA Writer Mono', ui-monospace, monospace; }
nav.top { background: var(--refusal); color: var(--cream); padding: 0.5rem 2rem; font-family: 'iA Writer Mono', ui-monospace, monospace; font-size: 0.78rem; }
nav.top a { color: var(--cream); text-decoration: none; margin-right: 1.5rem; }
nav.top a.active { color: var(--green); font-weight: bold; }
nav.top .right { float: right; }
header.masthead { border-bottom: 3px double var(--refusal); padding: 1.5rem 0 1rem; display: grid; grid-template-columns: 1fr auto; align-items: end; gap: 1rem; }
header.masthead h1 { font-size: 3rem; margin: 0; letter-spacing: -0.02em; }
header.masthead .dateline { font-style: italic; color: var(--lead); font-size: 0.95rem; }
header.masthead .slot { font-family: 'iA Writer Mono', ui-monospace, monospace; font-size: 0.78rem; text-align: right; color: var(--margin); }
header.masthead .slot a { color: var(--refusal); }
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
.tier-label { display: inline-block; padding: 0.05rem 0.4rem; font-size: 0.66rem; font-family: 'iA Writer Mono', ui-monospace, monospace; background: var(--folio); color: var(--cream); vertical-align: middle; margin-left: 0.3rem; }
.tier-label.lead { background: var(--cardinal); }
.tier-label.standard { background: var(--lead); }
details.audit { margin-top: 0.6rem; background: rgba(0,0,0,0.02); padding: 0.6rem 0.85rem; border-left: 2px solid var(--folio); }
details.audit[open] { background: rgba(168, 133, 44, 0.08); }
details.audit summary { cursor: pointer; color: var(--lead); font-family: 'iA Writer Mono', ui-monospace, monospace; font-size: 0.78rem; }
details.audit summary:hover { color: var(--cardinal); }
.audit-body { margin-top: 0.75rem; font-size: 0.88rem; line-height: 1.55; }
.audit-step { margin: 0.5rem 0; padding-left: 2.2rem; position: relative; }
.audit-step .num { position: absolute; left: 0; top: 0; width: 1.6rem; height: 1.6rem; text-align: center; line-height: 1.6rem; border-radius: 50%; background: var(--folio); color: var(--cream); font-family: 'iA Writer Mono', monospace; font-size: 0.75rem; font-weight: bold; }
.audit-step .label { font-family: 'iA Writer Mono', monospace; font-size: 0.7rem; color: var(--margin); letter-spacing: 0.04em; text-transform: uppercase; }
.audit-step .check { color: var(--green); font-weight: bold; }
section.nerds, section.doc { margin-top: 3rem; padding-top: 1.5rem; border-top: 3px double var(--refusal); }
section.doc:first-of-type { margin-top: 1.5rem; border-top: none; }
section.nerds h2, section.doc h2 { font-size: 1.4rem; }
section.nerds h3, section.doc h3 { font-size: 1rem; margin-top: 1.5rem; border-bottom: 1px dotted var(--bone); }
table { width: 100%; font-family: 'iA Writer Mono', ui-monospace, monospace; font-size: 0.76rem; border-collapse: collapse; }
th, td { text-align: left; padding: 0.25rem 0.5rem; border-bottom: 1px dotted var(--bone); vertical-align: top; }
th { color: var(--margin); font-weight: normal; text-transform: uppercase; font-size: 0.66rem; letter-spacing: 0.04em; }
td.num, th.num { text-align: right; }
tr.flag td { color: var(--cardinal); }
.scroll-wrap { max-height: 480px; overflow-y: auto; border: 1px solid var(--bone); }
.muted { color: var(--margin); }
.lede { font-size: 1.0rem; line-height: 1.6; }
.lede strong { color: var(--cardinal); }
details.cut { margin: 0.6rem 0; }
details.cut summary { cursor: pointer; font-family: 'iA Writer Mono', monospace; font-size: 0.78rem; color: var(--lead); }
details.cut summary:hover { color: var(--cardinal); }
footer { margin: 3rem 0 0; padding-top: 1rem; border-top: 1px solid var(--bone); font-family: 'iA Writer Mono', monospace; font-size: 0.7rem; color: var(--margin); }
.feed-row { display: grid; grid-template-columns: 1.5fr 4fr 1.5fr; gap: 0.8rem; padding: 0.55rem 0; border-bottom: 1px dotted var(--bone); align-items: center; }
.feed-row.header { font-family: 'iA Writer Mono', monospace; font-size: 0.7rem; color: var(--margin); text-transform: uppercase; letter-spacing: 0.04em; border-bottom: 1px solid var(--refusal); padding-bottom: 0.5rem; }
.feed-row .friendly { font-weight: bold; font-size: 0.95rem; }
.feed-row .url { font-family: 'iA Writer Mono', monospace; font-size: 0.68rem; color: var(--margin); margin-top: 0.15rem; word-break: break-all; }
.btn { font-family: 'iA Writer Mono', monospace; font-size: 0.72rem; border: 1px solid var(--lead); background: var(--cream); color: var(--refusal); padding: 0.2rem 0.5rem; text-decoration: none; }
.badge { background: var(--green); color: var(--cream); font-size: 0.6rem; padding: 0.1rem 0.4rem; margin-left: 0.4rem; font-family: 'iA Writer Mono', monospace; }
.morgue-diff { font-family: 'iA Writer Mono', monospace; font-size: 0.78rem; background: rgba(0,0,0,0.03); padding: 0.8rem 1rem; margin: 0.5rem 0; border-left: 2px solid var(--folio); white-space: pre-wrap; }
.morgue-diff .add { background: rgba(11, 135, 89, 0.18); display: block; }
.morgue-diff .del { background: rgba(179, 38, 30, 0.18); display: block; text-decoration: line-through; text-decoration-color: var(--cardinal); }
"""


# ============ shared chrome ============

NAV = [("Paper", "index.html", "paper"), ("Runsheet", "runsheet.html", "runsheet"),
       ("Feeds", "feeds.html", "feeds"), ("The Morgue", "morgue.html", "morgue")]


def _topnav(active):
    links = "".join(f'<a class="{"active" if key == active else ""}" href="{href}">{label}</a>'
                    for label, href, key in NAV)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f'<nav class="top">{links}<span class="right">fishwrap · built {stamp}</span></nav>'


def _page(title, active, body):
    return (f'<!doctype html>\n<html lang="en">\n<head>\n  <meta charset="utf-8">\n  <title>{escape(title)}</title>\n'
            f'  <style>{CSS}</style>\n</head>\n<body>\n  {_topnav(active)}\n  <div class="shell">\n{body}\n  </div>\n</body>\n</html>')


def _header_block(h1, dateline, slot=""):
    return (f'<header class="masthead"><div><h1>{h1}</h1><div class="dateline">{dateline}</div></div>'
            f'<div class="slot">{slot}</div></header>')


def fresh_age(ts, anchor_ts) -> str:
    """Human-friendly age relative to the window's end."""
    if not ts:
        return "?"
    age = anchor_ts - ts
    if age < 0:
        return "0m"
    if age < 3600:
        return f"{int(age / 60)}m"
    if age < 86400:
        return f"{age / 3600:.1f}h"
    return f"{age / 86400:.1f}d"


def _local(ts, tz):
    return datetime.fromtimestamp(ts, ZoneInfo(tz)).strftime("%A, %B %d, %Y · %H:%M %Z")


def _section_index(header):
    return {s["id"]: s for s in header["sections"]}


def _published_by_section(records):
    out = defaultdict(list)
    for r in records:
        if r["fate"]["published"]:
            out[r["fate"]["section"]].append(r)
    for sid in out:
        out[sid].sort(key=lambda r: r["fate"]["seed"])
    return out


def _why_section(r, sec):
    reason = r.get("section_reason") or {}
    title = escape(sec["title"])
    if reason.get("path") == "source_default":
        return f"This source is set to route to <strong>{title}</strong> by default."
    if reason.get("path") == "keyword_fallback":
        terms = reason.get("matched_terms", [])
        if terms:
            shown = ", ".join(f'<em>"{escape(t)}"</em>' for t in terms[:5])
            more = f", and {len(terms) - 5} more." if len(terms) > 5 else "."
            return (f"Source had no default section. The story's text matched {len(terms)} keywords "
                    f"that route to <strong>{title}</strong>: {shown}{more}")
        return f"Source had no default. Routed to <strong>{title}</strong> as the catch-all."
    return f"No source default, no keyword match. Routed to <strong>{title}</strong> (catch-all)."


def _why_short(r):
    reason = r.get("section_reason") or {}
    if reason.get("path") == "source_default":
        return "source default"
    if reason.get("path") == "keyword_fallback":
        terms = reason.get("matched_terms", [])
        return "keywords: " + ", ".join(terms[:3]) + (" …" if len(terms) > 3 else "")
    return "catch-all"


# ============ the paper ============

def _render_audit(r, sec, header, by_link):
    fate, sig, cl = r["fate"], r["signals"], r["cluster"]
    seed, tier = fate["seed"], fate["tier"]
    size, lead_count, feature_count = sec["edition_size"], sec["lead_count"], sec["feature_count"]
    cap = sec["max_per_source"]
    domain = escape(r["domain"])
    age = fresh_age(r["ts"], header["anchor_ts"])
    pool, rank = sig.get("pool") or 0, sig.get("recency_rank") or 0

    bypass = next((p for p in r["policies"] if p["effect"] == "cap_bypass"), None)
    if bypass:
        wl = (f"<span class='check'>✓</span> Diversity check skipped: this source ({domain}) is set to "
              f"<strong>print all</strong> by the policy <em>{escape(bypass.get('sentence') or '')}</em>, "
              f"so it bypasses the per-source cap.")
    else:
        wl = (f"<span class='check'>✓</span> Diversity check passed "
              f"(no more than <strong>{cap}</strong> stories per source per section).")
    lp = ""
    if any(p["effect"] == "lead_promoted" for p in r["policies"]) and tier == "lead":
        lp = ("<br><span class='check'>✓</span> Promoted into the lead slot because the title matched "
              "a lead-preference keyword in the masthead.")
    tier_explain = {
        "lead": f"The top <strong>{lead_count}</strong> stories in each section become the leads.",
        "feature": f"Stories ranked {lead_count + 1} through {lead_count + feature_count} become features.",
        "standard": f"Stories ranked {lead_count + feature_count + 1} through {size} are standard.",
    }.get(tier, "")

    if cl.get("size", 1) > 1:
        others = sorted({by_link[m]["domain"] for m in cl.get("members", []) if m in by_link})
        coverage = (f"Carried by <strong>{cl['sources']}</strong> sources. The same story also arrived from "
                    f"{escape(', '.join(others))}; those copies were folded into this one.")
    else:
        coverage = "No other feed carried this story in the window."

    return f"""
<div class="audit-body">
  <div class="audit-step"><div class="num">1</div><div class="label">Where it came from</div>
    <div>Pulled from <strong>{domain}</strong>. {_why_section(r, sec)}</div></div>
  <div class="audit-step"><div class="num">2</div><div class="label">When it arrived</div>
    <div>{age} before the window closed.</div></div>
  <div class="audit-step"><div class="num">3</div><div class="label">How it competed</div>
    <div><strong>{pool}</strong> stories competed for the <strong>{size}</strong> {escape(sec['title'])} slots.<br>By freshness, this story ranked <strong>{rank} of {pool}</strong>.<br>{wl}{lp}</div></div>
  <div class="audit-step"><div class="num">4</div><div class="label">Where it landed</div>
    <div>Printed at rank <strong>{seed} of {size}</strong> in {escape(sec['title'])}. Tier: <strong>{tier}</strong>. {tier_explain}</div></div>
  <div class="audit-step"><div class="num">5</div><div class="label">Coverage</div>
    <div>{coverage}</div></div>
  <div class="audit-step"><div class="num">i</div><div class="label">Source</div>
    <div><a href="{escape(r['source'])}">source feed</a> · <a href="runsheet.html#s-{escape(sec['id'])}">this section in the runsheet</a></div></div>
</div>"""


def _render_article(r, sec, header, by_link):
    fate = r["fate"]
    tier, seed = fate["tier"], fate["seed"]
    age = fresh_age(r["ts"], header["anchor_ts"])
    cov = r["cluster"].get("sources", 1)
    cov_txt = f" · carried by {cov} sources" if cov > 1 else ""
    return f"""
<article class="{tier}">
  <div class="seed">{seed}</div>
  <div>
    <h3><a href="{escape(r['link'])}" target="_blank" rel="noopener">{escape(r['title'] or '(untitled)')}</a> <span class="tier-label {tier}">{tier}</span></h3>
    <div class="meta">{escape(r['domain'])} · {age} old · section rank {seed} of {sec['edition_size']}{cov_txt}</div>
    <details class="audit"><summary>How did this story end up here? (step-by-step)</summary>{_render_audit(r, sec, header, by_link)}</details>
  </div>
</article>"""


def _render_nerds(header, records):
    f = header["funnel"]
    secs = header["sections"]
    pub = _published_by_section(records)
    cut = Counter((r["fate"].get("section"), r["fate"]["step"]) for r in records
                  if not r["fate"]["published"] and r.get("section"))
    yield_rows = "".join(
        f'<tr><td>{escape(s["title"])} ({escape(s["id"])})</td><td class="num">{len(pub.get(s["id"], []))} of {s["edition_size"]}</td>'
        f'<td class="num">{cut[(s["id"], "diversity_cap")]}</td><td class="num">{cut[(s["id"], "capacity")]}</td></tr>'
        for s in secs)
    zero = sorted(u for u, n in header["feeds"].items() if not n)
    zero_html = ("".join(f'<tr class="flag"><td>{escape(u)}</td><td class="num">0</td></tr>' for u in zero)
                 if zero else '<tr><td class="muted">every feed delivered at least one story</td><td></td></tr>')
    return f"""
<section class="nerds">
  <h2>Stats for nerds — the honest funnel</h2>
  <p class="muted">The whole record is on the <a href="runsheet.html">runsheet page</a>, or as data: <a href="runsheet.jsonl.gz">runsheet.jsonl.gz</a>.</p>
  <h3>Funnel</h3>
  <table>
    <tr><th>candidates in the window (last {header['window_hours']}h)</th><td class="num">{f['intake']:,}</td></tr>
    <tr><th>excluded by your policies</th><td class="num">{f['policy']:,}</td></tr>
    <tr><th>duplicates folded into another story</th><td class="num">{f['duplicate']:,}</td></tr>
    <tr><th>competed for slots</th><td class="num">{f['competed']:,}</td></tr>
    <tr><th>cut by the per-source cap</th><td class="num">{f['diversity_cap']:,}</td></tr>
    <tr><th>cut by section capacity</th><td class="num">{f['capacity']:,}</td></tr>
    <tr><th>printed</th><td class="num">{f['published']:,}</td></tr>
  </table>
  <h3>Per-section yield</h3>
  <table><tr><th>section</th><th class="num">filled</th><th class="num">cut: per-source cap</th><th class="num">cut: capacity</th></tr>{yield_rows}</table>
  <h3>Feeds that delivered nothing ({len(zero)} of {len(header['feeds'])})</h3>
  <div class="scroll-wrap"><table><tr><th>feed</th><th class="num">items</th></tr>{zero_html}</table></div>
</section>"""


def render_paper(masthead: Masthead, header: dict, records: list[dict]) -> str:
    secs = header["sections"]
    pub = _published_by_section(records)
    by_link = {r["link"]: r for r in records}
    body = _header_block(escape(masthead.name),
                         f"{_local(header['anchor_ts'], header['timezone']).split(' · ')[0]} · edition {escape(header['edition'])}",
                         f"{header['funnel']['published']} stories from {header['funnel']['intake']:,} candidates<br>"
                         f"<a href=\"runsheet.html\">how this edition was made</a>")
    for s in secs:
        arts = pub.get(s["id"], [])
        standard = max(0, len(arts) - s["lead_count"] - s["feature_count"])
        desc = (masthead.section_by_id(s["id"]) or {}).get("description", "")
        body += f"""
<section class="deck" id="sec-{escape(s['id'])}">
  <h2>{escape(s['title'])} <span class="pill">{escape(desc)}</span>
    <span class="pill tier">{s['lead_count']} leads · {s['feature_count']} features · {standard} standard</span></h2>
  {"".join(_render_article(r, s, header, by_link) for r in arts)}
</section>"""
    body += _render_nerds(header, records)
    body += (f'<footer>fishwrap · edition {escape(header["edition"])} · engine {escape(header["engine"])} · '
             f'window closed {escape(_local(header["anchor_ts"], header["timezone"]))}</footer>')
    return _page(f"{masthead.name} — {header['edition']}", "paper", body)


# ============ the runsheet page ============

def _n(n, word="story"):
    return f"{n} {word if n == 1 else word[:-1] + 'ies' if word.endswith('y') else word + 's'}"


def _story_cell(r):
    return f'<a href="{escape(r["link"])}" target="_blank" rel="noopener">{escape(r["title"] or "(untitled)")}</a>'


def render_runsheet_page(masthead: Masthead, header: dict, records: list[dict]) -> str:
    f = header["funnel"]
    secs = header["sections"]
    anchor = header["anchor_ts"]
    by_link = {r["link"]: r for r in records}
    pub = _published_by_section(records)
    dd = header.get("dedup") or {}
    thr = dd.get("threshold")
    thr_pct = f"{int(round(thr * 100))}%" if isinstance(thr, (int, float)) else "?"

    # 1. provenance
    fp = " · ".join(f"{name} {escape(str(header.get(key) or 'none'))}"
                    for name, key in (("masthead", "masthead_sha"), ("dossier", "dossier_sha"), ("policies", "policies_sha")))
    body = _header_block("Runsheet",
                         f"edition {escape(header['edition'])} · the whole record of how today's paper was made",
                         f"engine {escape(header['engine'])} · built {escape(header['built_at'])}<br>{fp}")
    body += f"""
<section class="doc">
  <p class="lede">The window closed at <strong>{escape(_local(anchor, header['timezone']))}</strong> and covered the
  <strong>{header['window_hours']} hours</strong> before it. <strong>{f['intake']:,}</strong> stories arrived from
  <strong>{sum(1 for n in header['feeds'].values() if n)}</strong> of {len(header['feeds'])} feeds.
  Your policies excluded <strong>{f['policy']:,}</strong>. <strong>{f['duplicate']:,}</strong> were the same story as another one
  (titles more than {thr_pct} alike within {dd.get('window_hours', '?')} hours) and were folded into it.
  That left <strong>{f['competed']:,}</strong> to compete for <strong>{sum(s['edition_size'] for s in secs)}</strong> slots
  in {len(secs)} sections. The per-source cap cut <strong>{f['diversity_cap']:,}</strong>, section capacity cut
  <strong>{f['capacity']:,}</strong>, and <strong>{f['published']:,}</strong> were printed.</p>
</section>"""

    # 2. per section
    for s in secs:
        sid = s["id"]
        printed = pub.get(sid, [])
        rows = "".join(
            f'<tr><td class="num">{r["fate"]["seed"]}</td><td>{r["fate"]["tier"]}</td><td>{_story_cell(r)}</td>'
            f'<td>{escape(r["domain"])}</td><td class="num">{fresh_age(r["ts"], anchor)}</td>'
            f'<td class="num">{r["cluster"].get("sources", 1)}</td><td>{escape(_why_short(r))}'
            f'{" · lead by preference" if any(p["effect"] == "lead_promoted" for p in r["policies"]) else ""}'
            f'{" · print all" if any(p["effect"] == "cap_bypass" for p in r["policies"]) else ""}</td></tr>'
            for r in printed)
        cut_cap = [r for r in records if not r["fate"]["published"] and r.get("section") == sid and r["fate"]["step"] == "diversity_cap"]
        cut_cap.sort(key=lambda r: r["signals"].get("recency_rank") or 0)
        cut_full = [r for r in records if not r["fate"]["published"] and r.get("section") == sid and r["fate"]["step"] == "capacity"]
        cut_full.sort(key=lambda r: r["signals"].get("recency_rank") or 0)
        by_dom = Counter(r["domain"] for r in cut_cap)
        cap_rows = "".join(
            f'<tr><td class="num">{r["signals"].get("recency_rank") or ""}</td><td>{_story_cell(r)}</td><td>{escape(r["domain"])}</td>'
            f'<td>{escape(r["fate"]["detail"])}: this source already had its {s["max_per_source"]} stories</td></tr>'
            for r in cut_cap)
        full_rows = "".join(
            f'<tr><td class="num">{r["signals"].get("recency_rank") or ""}</td><td>{_story_cell(r)}</td><td>{escape(r["domain"])}</td>'
            f'<td>the {s["edition_size"]} slots were already filled by fresher stories</td></tr>'
            for r in cut_full)
        dom_summary = ", ".join(f"{escape(d)} ({n})" for d, n in by_dom.most_common(8))
        pool = next((r["signals"].get("pool") for r in printed + cut_cap + cut_full if r["signals"].get("pool")), 0)
        body += f"""
<section class="doc" id="s-{escape(sid)}">
  <h2>{escape(s['title'])} <span class="muted mono" style="font-size:0.8rem">{len(printed)} printed of {pool} candidates · {s['lead_count']} leads · {s['feature_count']} features · cap {s['max_per_source']} per source</span></h2>
  <table><tr><th class="num">#</th><th>tier</th><th>story</th><th>source</th><th class="num">age</th><th class="num">sources</th><th>how it got here</th></tr>{rows}</table>
  <details class="cut"><summary>Cut by the per-source cap: {_n(len(cut_cap))}{(" · " + dom_summary) if dom_summary else ""}</summary>
    <table><tr><th class="num">freshness rank</th><th>story</th><th>source</th><th>why</th></tr>{cap_rows}</table></details>
  <details class="cut"><summary>Cut by capacity: {_n(len(cut_full))}</summary>
    <table><tr><th class="num">freshness rank</th><th>story</th><th>source</th><th>why</th></tr>{full_rows}</table></details>
</section>"""

    # 3. excluded by policy
    excluded = [r for r in records if not r["fate"]["published"] and r["fate"].get("step") == "policy"]
    by_policy = defaultdict(list)
    for r in excluded:
        by_policy[r["fate"]["detail"]].append(r)
    pol_html = "".join(
        f'<details class="cut"><summary>{escape(sentence)} · {_n(len(rs))}</summary><table>'
        + "".join(f'<tr><td>{_story_cell(r)}</td><td>{escape(r["domain"])}</td></tr>' for r in rs)
        + "</table></details>"
        for sentence, rs in sorted(by_policy.items(), key=lambda kv: -len(kv[1])))
    body += f"""
<section class="doc" id="policies">
  <h2>Excluded by your policies <span class="muted mono" style="font-size:0.8rem">{_n(len(excluded))}</span></h2>
  {pol_html or '<p class="muted">No policy excluded anything today.</p>'}
</section>"""

    # 4. duplicates
    leaders = [r for r in records if r["cluster"].get("leader") and r["cluster"].get("size", 1) > 1]
    leaders.sort(key=lambda r: -r["cluster"]["size"])
    dup_html = ""
    for L in leaders:
        fate = L["fate"]
        where = (f'printed as #{fate["seed"]} in {escape(_section_index(header).get(fate["section"], {}).get("title", fate["section"]))}'
                 if fate["published"] else f'cut ({escape(fate["step"])})')
        members = "".join(f'<tr><td>{_story_cell(by_link[m])}</td><td>{escape(by_link[m]["domain"])}</td></tr>'
                          for m in L["cluster"]["members"] if m in by_link)
        dup_html += (f'<details class="cut"><summary>{escape(L["title"])} · {escape(L["domain"])} · {where} · '
                     f'{L["cluster"]["size"]} copies from {L["cluster"]["sources"]} sources</summary>'
                     f'<table>{members}</table></details>')
    body += f"""
<section class="doc" id="duplicates">
  <h2>Folded duplicates <span class="muted mono" style="font-size:0.8rem">{f['duplicate']} copies into {len(leaders)} stories</span></h2>
  <p class="muted">The newest copy is kept and the rest are folded into it. The count of distinct sources is the story's coverage.</p>
  {dup_html or '<p class="muted">No two feeds carried the same story today.</p>'}
</section>"""

    # 5. feeds
    printed_by_source = Counter(r["source"] for r in records if r["fate"]["published"])
    feed_rows = "".join(
        f'<tr class="{"flag" if not n else ""}"><td>{escape(u)}</td><td class="num">{n}</td><td class="num">{printed_by_source.get(u, 0)}</td></tr>'
        for u, n in sorted(header["feeds"].items(), key=lambda kv: (-kv[1], kv[0])))
    zero = sum(1 for n in header["feeds"].values() if not n)
    body += f"""
<section class="doc" id="feeds">
  <h2>Every feed <span class="muted mono" style="font-size:0.8rem">{len(header['feeds'])} feeds · {zero} delivered nothing</span></h2>
  <div class="scroll-wrap"><table><tr><th>feed</th><th class="num">in window</th><th class="num">printed</th></tr>{feed_rows}</table></div>
</section>"""
    body += (f'<footer>fishwrap · edition {escape(header["edition"])} · engine {escape(header["engine"])} · '
             f'data: <a href="runsheet.jsonl.gz">runsheet.jsonl.gz</a></footer>')
    return _page(f"{masthead.name} — runsheet {header['edition']}", "runsheet", body)


# ============ feeds (read-only) ============

def _policies_for_feed(url, policies):
    u = url.lower()
    out = []
    for p in policies:
        pp = p.get("policy", {})
        if pp.get("type") in ("source_ban", "source_whitelist") and pp.get("match", "").lower() in u:
            out.append(("never" if pp["type"] == "source_ban" else "print all") + f": {p.get('sentence', '')}")
    return out


def render_feeds(masthead: Masthead, header: dict, records: list[dict]) -> str:
    sections = _section_index(header)
    printed_by_source = Counter(r["source"] for r in records if r["fate"]["published"])
    rows = ""
    for url in masthead.feeds:
        sid = next((s for key, s in masthead.source_sections.items() if key.lower() in url.lower()), None)
        routed = escape(sections.get(sid, {}).get("title", sid)) if sid else '<span class="muted">by keywords</span>'
        n = header["feeds"].get(url, 0)
        pol = "<br>".join(escape(x) for x in _policies_for_feed(url, masthead.policies))
        rows += (f'<tr class="{"flag" if not n else ""}"><td>{escape(runsheet.domain_of(url))}<div class="url muted">{escape(url)}</div></td>'
                 f'<td>{routed}</td><td class="num">{n}</td><td class="num">{printed_by_source.get(url, 0)}</td><td>{pol}</td></tr>')
    zero = sum(1 for n in header["feeds"].values() if not n)
    body = _header_block("Feeds", f"{len(masthead.feeds)} sources in your paper · {zero} delivered nothing in this window",
                         "read-only · the masthead is the control")
    body += f"""
<section class="doc">
  <p class="muted">Each row is one source you read. <strong>Routed to</strong> is where its stories go unless a keyword says otherwise.
  Changing any of this means editing your masthead; every change to it is filed in The Morgue.</p>
  <table><tr><th>source</th><th>routed to</th><th class="num">in window</th><th class="num">printed</th><th>policies</th></tr>{rows}</table>
</section>"""
    return _page(f"{masthead.name} — Feeds", "feeds", body)


# ============ The Morgue (versioning UX, no 'git' in user copy) ============

def _git_log_entries(instance_dir):
    """Return list of {sha, short, date_iso, date_pretty, subject} for commits
    that touched the three editorial files."""
    try:
        out = subprocess.run(
            ["git", "log", "--pretty=%H|%ad|%s", "--date=iso", "--", "masthead.toml", "dossier.md", "policies.jsonl"],
            cwd=str(instance_dir), capture_output=True, text=True, check=True,
        ).stdout
    except Exception as e:
        log.warning("morgue: history unavailable: %s", e)
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
        entries.append({"sha": sha, "short": sha[:7], "date_iso": date, "date_pretty": date_pretty, "subject": subject})
    return entries


def _git_diff_between(instance_dir, sha_old, sha_new, filename):
    try:
        return subprocess.run(["git", "diff", "--unified=2", sha_old, sha_new, "--", filename],
                              cwd=str(instance_dir), capture_output=True, text=True, check=True).stdout
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


def render_morgue(masthead: Masthead, entries=None) -> str:
    entries = _git_log_entries(masthead.instance_dir) if entries is None else entries
    rows = ""
    for i, e in enumerate(entries):
        badge = '<span class="badge">CURRENT</span>' if i == 0 else ""
        action = ('<span class="muted mono" style="font-size:0.72rem">— in effect now —</span>' if i == 0
                  else f'<a class="btn" href="morgue-view-{e["short"]}.html">view</a>')
        rows += (f'<div class="feed-row"><div><div class="friendly">{escape(e["date_pretty"])}{badge}</div>'
                 f'<div class="url">filed {escape(e["short"])}</div></div><div>{escape(e["subject"])}</div><div>{action}</div></div>')
    earliest = entries[-1]["date_pretty"].split(" · ")[0] if entries else "today"
    body = _header_block("The Morgue", f"every prior version of your paper · {len(entries)} on file",
                         f"filed since {escape(earliest)}")
    body += f"""
<section class="doc">
  <p class="muted">Every change to your <strong>masthead</strong>, <strong>dossier</strong>, or <strong>policies</strong> is filed here.
  <strong>View</strong> shows an older version against the current one with every change highlighted. Nothing in The Morgue is ever destroyed.</p>
  <div class="feed-row header"><div>filed</div><div>what changed</div><div></div></div>
  {rows}
</section>"""
    return _page(f"{masthead.name} — The Morgue", "morgue", body)


def render_morgue_view(masthead: Masthead, entries, idx) -> str:
    inst = masthead.instance_dir
    entry, current = entries[idx], entries[0]
    body = _header_block("Viewing back issue",
                         f'filed {escape(entry["date_pretty"])} · <a href="morgue.html">back to The Morgue</a>',
                         "this version vs. today")
    body += f"""
<section class="doc">
  <p class="muted">What changed between the version filed on <strong>{escape(entry['date_pretty'])}</strong> and the current one.
  <span style="background: rgba(11, 135, 89, 0.18); padding: 0.05rem 0.3rem;">Green</span> lines were added afterward.
  <span style="background: rgba(179, 38, 30, 0.18); padding: 0.05rem 0.3rem; text-decoration: line-through;">Red</span> lines were removed afterward.</p>
  <h3>Masthead</h3>{_render_diff_html(_git_diff_between(inst, entry["sha"], current["sha"], "masthead.toml"))}
  <h3>Dossier</h3>{_render_diff_html(_git_diff_between(inst, entry["sha"], current["sha"], "dossier.md"))}
  <h3>Policies</h3>{_render_diff_html(_git_diff_between(inst, entry["sha"], current["sha"], "policies.jsonl"))}
</section>"""
    return _page(f"{masthead.name} — viewing {entry['short']}", "morgue", body)


# ============ the 'today' pointer ============

def write_pointer(base: Path, date: str) -> Path:
    """Write base/index.html, a redirect to base/<date>/.

    This is the 'today' pointer. It is written last, after every page of the
    edition exists, so a build that dies halfway leaves it pointing at the
    previous good edition.
    """
    target = f"{date}/"
    html = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<meta http-equiv="refresh" content="0; url={target}">'
            f'<title>{escape(date)}</title></head>'
            f'<body><a href="{target}">{escape(date)}</a></body></html>\n')
    p = Path(base) / "index.html"
    p.write_text(html, encoding="utf-8")
    return p


# ============ CLI entry point ============

def write_edition(masthead: Masthead, header: dict, records: list[dict], out_dir: Path) -> list[Path]:
    """Render every page of one edition into out_dir. Returns the paths written."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []

    def put(name, html):
        p = out_dir / name
        p.write_text(html, encoding="utf-8")
        written.append(p)

    put("index.html", render_paper(masthead, header, records))
    put("runsheet.html", render_runsheet_page(masthead, header, records))
    put("feeds.html", render_feeds(masthead, header, records))
    entries = _git_log_entries(masthead.instance_dir)
    put("morgue.html", render_morgue(masthead, entries))
    for i in range(1, len(entries)):
        put(f"morgue-view-{entries[i]['short']}.html", render_morgue_view(masthead, entries, i))
    return written


def run_printer():
    masthead = _config.MASTHEAD
    base = Path(_config.OUTPUT_DIR)
    path = runsheet.latest(base)
    if path is None:
        raise SystemExit(f"[PRINTER] no runsheet under {base}; run the editor first")
    header, records = runsheet.read(path)
    written = write_edition(masthead, header, records, path.parent)
    write_pointer(base, header["edition"])
    print(f"[PRINTER] Wrote {len(written)} pages to {path.parent} from {path.name}; "
          f"{base / 'index.html'} -> {header['edition']}/")


if __name__ == "__main__":
    run_printer()
