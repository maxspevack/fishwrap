# Fishwrap Demo / Starter Kit

This directory contains a reference implementation of a Fishwrap publication. Use it as a template to build your own.

## Structure

A Fishwrap instance is a directory with three editorial files plus generated state:

*   **`masthead.toml`** — structured configuration. Identity (publication name, timezone), engine settings (expiration window), sections (titles, sizes, keywords), and feed URLs.
*   **`dossier.md`** — the editor's prose. Plain Markdown. Each line is citable by the auditor as the rationale for a section's editorial point of view.
*   **`policies.jsonl`** — append-only log of editorial decisions. One signed policy per line. Five primitives: `source_ban`, `title_pattern_ban`, `topic_ban`, `source_whitelist`, `section_lead_preference`. Strikes are events on prior policies, not deletions.
*   **`data/`** — SQLite database. The fetcher writes here; the editor reads from here. Gitignored.
*   **`output/`** — one directory per edition date (`output/YYYY-MM-DD/`): `runsheet.jsonl.gz` (the editor's record), `index.html` (the paper), `runsheet.html`, `feeds.html`, `morgue.html`; plus `output/index.html`, a redirect to the newest edition. Gitignored.
*   **`themes/basic/`** — brand-asset reference (CSS + logo). Currently unused by the printer (the engine renders inline HTML) and held for the next Daily Clamour migration.

## The Vanilla and the Daily Clamour

This instance publishes as [The Vanilla](https://fishwrap.org/demo/vanilla/), and it is the [Daily Clamour](https://dailyclamour.com)'s dev edition. The Vanilla builds from `main` every day. The Clamour builds from a released image. The two carry the same feed list and the same source-to-section routing, so what a feed does here predicts what it does there, and a feed or routing change is tried here before the Clamour prints it.

1. Change `[feeds]` or `[source_sections]` here first.
2. Make the same change in the Clamour's `config.py` (`FEEDS` and `SOURCE_SECTIONS`). `make feeds-check` in the Clamour's repository (`maxspevack/dailyclamour.com`, private) compares the two and exits 1 on any difference.

The feeds page counts the consecutive editions a feed delivered nothing and says "dead?" at seven. That is a prompt to look at the feed, not a verdict:

| What you find | What to do |
|---|---|
| Unreachable, unparseable, undated, or no new item in 90 days | Remove it. |
| Fresh items from your own machine; nothing on the GitHub Actions runner in every edition | Remove it. The site refuses GitHub's addresses, and the Clamour builds on the same runners. Add it back if that changes. |
| The runner fetches it and its newest item is under 90 days old | Keep it. It posts rarely. |

What differs between the two papers is the engine version, the theme, each paper's policies, the Clamour's scoring rules, and Defector, which the Clamour fetches with a logged-in session cookie and the Vanilla without one.

## Customization

### Adding feeds

Edit the `[feeds]` table in `masthead.toml`:

```toml
[feeds]
urls = [
    "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "https://your-favorite-blog.com/feed.xml",
]
```

### Setting your timezone

Use an IANA timezone name in the `[identity]` table:

```toml
[identity]
name = "Your Paper"
timezone = "America/New_York"
```

### Defining sections

Each `[[section]]` block becomes a heading in the rendered edition:

```toml
[[section]]
id = "news"
title = "News"
description = "What happened today."
edition_size = 5
lead_count = 1
feature_count = 2
max_per_source = 3
keywords = ["politics", "election"]
```

### Editorial decisions

File policies with `make policy ARGS='<verb> ... --because "<your sentence>"'` (verbs: `ban-source`, `ban-title`, `ban-topic`, `print-all`, `prefer-lead`, `strike`, `list`), then `make replay DATE=<edition>` to see what the policy would have changed. Each line of `policies.jsonl` is a JSON event:

```json
{"event": "create", "policy_id": "p1", "sentence": "Ban Pitchfork — owner conflict.", "policy": {"type": "source_ban", "match": "pitchfork.com"}}
{"event": "create", "policy_id": "p2", "sentence": "Whitelist Defector except crosswords.", "policy": {"type": "source_whitelist", "match": "defector.com"}}
{"event": "strike", "policy_id": "p1"}
```

Active policies are the create events whose `policy_id` has not been struck.
</content>
</invoke>