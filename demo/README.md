# Fishwrap Demo / Starter Kit

This directory contains a reference implementation of a Fishwrap publication. Use it as a template to build your own.

## Structure

A Fishwrap instance is a directory with three editorial files plus generated state:

*   **`masthead.toml`** — structured configuration. Identity (publication name, timezone), engine settings (expiration window), sections (titles, sizes, keywords), and feed URLs.
*   **`dossier.md`** — the editor's prose. Plain Markdown. Each line is citable by the auditor as the rationale for a section's editorial point of view.
*   **`policies.jsonl`** — append-only log of editorial decisions. One signed policy per line. Five primitives: `source_ban`, `title_pattern_ban`, `topic_ban`, `source_whitelist`, `section_lead_preference`. Strikes are events on prior policies, not deletions.
*   **`data/`** — SQLite database. The fetcher writes here; the editor reads from here. Gitignored.
*   **`output/`** — generated HTML, one directory per edition date (`output/YYYY-MM-DD/`): `index.html` (the paper), `edition-editor.html`, `feeds-admin.html`, `morgue.html`, plus `output/index.html`, a redirect to the newest edition. Gitignored.
*   **`themes/basic/`** — brand-asset reference (CSS + logo). Currently unused by the printer (the engine renders inline HTML) and held for the next Daily Clamour migration.

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

Add policies by appending to `policies.jsonl`. Each line is a JSON event:

```json
{"event": "create", "policy_id": "p1", "sentence": "Ban Pitchfork — owner conflict.", "policy": {"type": "source_ban", "match": "pitchfork.com"}}
{"event": "create", "policy_id": "p2", "sentence": "Whitelist Defector except crosswords.", "policy": {"type": "source_whitelist", "match": "defector.com"}}
{"event": "strike", "policy_id": "p1"}
```

Active policies are the create events whose `policy_id` has not been struck.
</content>
</invoke>