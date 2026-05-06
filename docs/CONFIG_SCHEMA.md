# Fishwrap Config Schema

A fishwrap config is a Python file (typically `config.py`) that defines a set of top-level variables the engine reads. This document describes every variable the engine recognizes: which are required, which are optional, what types they accept, and what they do.

The validator (`fishwrap.validate_config`, run via `fishwrap-validate-config <path>`) is the source of truth for the schema. If this document and the validator ever disagree, the validator wins.

A typical workflow: edit your `config.py`, then before running the pipeline, validate it:

```bash
docker run --rm -v $(pwd):/cfg ghcr.io/maxspevack/fishwrap:2.0 \
    fishwrap-validate-config /cfg/config.py
```

If validation passes, the config is structurally sound. If it fails, the validator prints one error per line to stderr; fix and re-run.

---

## Minimal Valid Config

The smallest config that passes validation:

```python
FEEDS = ["https://example.com/feed.xml"]
SECTIONS = [{"id": "news", "title": "News"}]
```

This will run, but with `KEYWORDS = {}` (the default) every article gets fallback classification. To produce a meaningful edition, you almost certainly want the optional keys below.

---

## Required Keys

These two keys must be present. The engine's defaults for them are not useful: `FEEDS = []` means nothing to fetch, `SECTIONS = []` means no buckets to put articles in.

### `FEEDS`

**Type:** non-empty list of strings.

The URLs to fetch. Each is an HTTP(S) URL serving an RSS feed, JSON feed, or one of the supported variants (Reddit `.json` endpoints, hnrss.org URLs, etc.).

```python
FEEDS = [
    "https://hnrss.org/frontpage",
    "https://feeds.npr.org/1001/rss.xml",
    "https://old.reddit.com/r/news.json",
]
```

### `SECTIONS`

**Type:** non-empty list of dicts. Each entry must have `id` (string) and `title` (string). Other fields (e.g., `description`) are accepted but not required.

The output sections of the published edition. Each becomes a heading in the rendered HTML. Articles route into sections based on `KEYWORDS` (below) or `SOURCE_SECTIONS`.

```python
SECTIONS = [
    {"id": "news",    "title": "News",    "description": "What happened today."},
    {"id": "tech",    "title": "Tech",    "description": "Computers and the people who run them."},
    {"id": "culture", "title": "Culture"},
]
```

---

## Optional Keys — Structural

If absent, the engine uses the defaults defined in `fishwrap/_config.py`. If present, the type and shape are validated.

### `KEYWORDS`

**Type:** dict mapping section ID (string) to a list of keyword strings.

Used by the editor to classify articles. An article whose title or content contains a keyword matched to a section gets routed there. Default: `{}` (every article goes to fallback classification).

```python
KEYWORDS = {
    "news":    ["politics", "election", "government"],
    "tech":    ["software", "hardware", "ai"],
    "culture": ["film", "music", "book"],
}
```

### `EDITORIAL_POLICIES`

**Type:** list of dicts. Each entry must have `type` (string). Most types accept `boosts` (number) and other type-specific fields.

The editorial knobs: keyword boosts, source boosts, domain penalties, content boosts. Each policy is checked against every article and applied if it matches.

```python
EDITORIAL_POLICIES = [
    {"type": "keyword_boost",  "phrases": ["breaking"],                            "boosts": 5},
    {"type": "domain_penalty", "domains": ["lowqualitysource.example.com"],        "boosts": -10},
    {"type": "source_boost",   "match":   "krebsonsecurity.com",                   "boosts": 3},
]
```

Supported policy types (see `fishwrap/scoring.py` for the matching logic):

| `type` value | Matches on | Required fields |
|---|---|---|
| `keyword_boost` / `keyword_penalty` | Title + content text | `phrases` (list of strings), `boosts` (number) |
| `source_boost` | Source URL substring | `match` (string), `boosts` |
| `domain_penalty` | Source URL substring or domain list | `match` (string) and/or `domains` (list of strings), `boosts` |
| `content_boost` | Content text only | `phrases` (list of strings), `boosts` |

### `SCORING_PROFILES`

**Type:** dict with at least `dynamic` and `static` keys, each mapping to a dict of weights.

Profiles control how raw stats (upvotes, comments) translate into score points. The fetcher decides which profile applies per article based on whether the source provides stats.

```python
SCORING_PROFILES = {
    "dynamic": {"base_boosts": 0,  "score_weight": 1.0, "comment_weight": 1.0},
    "static":  {"base_boosts": 10, "score_weight": 0,   "comment_weight": 0},
}
```

The default ships with sensible values. Override only if you have specific tuning needs.

### `EDITION_SIZE`

**Type:** dict mapping section ID (string) to integer.

Caps how many articles each section publishes per edition. Articles ranked below the cap get cut. Default: `{}` (no caps; `EDITION_SIZE.get(section, 5)` is the engine's fallback).

```python
EDITION_SIZE = {"news": 15, "tech": 10, "culture": 5}
```

### `MIN_SECTION_SCORES`

**Type:** dict mapping section ID (string) to number.

Articles whose score is below this floor get filtered out of the section, even if they would otherwise fit under `EDITION_SIZE`. Default: `{}` (no minimum).

```python
MIN_SECTION_SCORES = {"news": 100, "tech": 50}
```

### `SOURCE_SECTIONS`

**Type:** dict mapping source-URL substring (string) to section ID (string).

Lets you override classification by source: any article from a feed whose URL contains the matching substring goes to the named section regardless of keyword match. Default: `{}`.

```python
SOURCE_SECTIONS = {
    "krebsonsecurity.com": "tech",
    "deadline.com":        "culture",
}
```

### `VISUAL_THRESHOLDS`

**Type:** dict.

Per-section thresholds that the printer uses to decide visual emphasis ("lead" vs "feature" vs "compact" article presentation). Implementation detail — consult `fishwrap/printer.py` for the current shape if you need to override.

---

## Optional Keys — Paths and Strings

| Key | Type | Default | Notes |
|---|---|---|---|
| `DATABASE_URL` | string | `'sqlite:///newsroom.db'` | SQLAlchemy URL. SQLite is the only tested backend. Relative SQLite paths resolve against process CWD |
| `LATEST_HTML_FILE` | string | `'index.html'` | Path where the rendered HTML edition is written |
| `LATEST_PDF_FILE` | string | `'edition.pdf'` | Path for PDF output. Currently inert in v2.0.x — the image does not include weasyprint, so PDF generation is silently skipped (logged as `PDF generation skipped: weasyprint not installed`). Setting this is harmless |
| `RUN_SHEET_FILE` | string | `'run_sheet.json'` | Where the editor writes the per-run record consumed by the auditor |
| `ENHANCED_ISSUE_FILE` | string | `'enhanced_issue.json'` | Intermediate artifact between the enhancer and printer |
| `STATS_FILE` | string | `'publication_stats.json'` | Aggregate publication statistics, appended on each run |
| `SECRETS_FILE` | string | `'secrets.json'` | JSON file mapping source-specific keys to auth material (cookies, API tokens). Absent = sources requiring auth fetch in degraded mode |
| `ARTICLES_DB_FILE` | string | `'articles_db.json'` | Deprecated; kept for backward compatibility. Has no effect when `DATABASE_URL` is a SQLite URL (default since v1.2) |
| `USER_AGENT` | string | engine default | HTTP User-Agent for the fetcher and enhancer. Be a polite citizen |
| `FOUNDING_DATE` | string | `'2024-01-01'` | ISO date the publication started; used to compute issue numbers (days since founding + 1) |
| `TIMEZONE` | string | `'UTC'` | Display timezone for timestamps in the rendered edition. Accepts IANA names (`'America/Los_Angeles'`); legacy aliases (`'US/Pacific'`) work in v2.0.x because the image ships `tzdata-legacy`, but a future release may drop the legacy package and require IANA-canonical names |
| `THEME` | string | `'basic'` | Path to the theme directory (templates + static). Relative paths resolve against process CWD |

---

## Optional Keys — Numeric

| Key | Type | Default | Notes |
|---|---|---|---|
| `BOOST_UNIT_VALUE` | number | `100` | The point value of one "boost unit." Editorial policies declare boosts as integer counts; each count multiplies by this value to produce the score delta |
| `FUZZY_BOOST_MULTIPLIER` | number | `1.5` | When deduplication merges two articles, the surviving article's score is incremented by this factor of `BOOST_UNIT_VALUE` to reflect the duplicate's signal |
| `EXPIRATION_HOURS` | number | `24` | Articles older than this are not considered for the published edition |
| `MAX_ARTICLE_LENGTH` | number | `10000` | Truncation cap for content fields |

---

## What the Validator Does NOT Check

The validator catches schema-shaped errors. It does not validate semantics. The following are runtime concerns; the engine surfaces them as errors when you actually run the pipeline:

- **Reachability of feed URLs.** The validator does not probe `FEEDS` URLs. A `FEEDS` entry that 404s passes validation; the fetcher will report the failure at runtime.
- **Timezone string validity.** `TIMEZONE = "Europe/Atlantis"` passes validation; it crashes at runtime when `ZoneInfo` looks it up.
- **File path existence.** Theme directories, secret files, output destinations — none are checked at validation time.
- **Cross-key consistency.** If `EDITION_SIZE = {"news": 10}` but `SECTIONS = [{"id": "tech", ...}]`, no section ID matches between the two; validation passes but no articles ever reach the printer.

If you find yourself wanting one of these checks, run the pipeline against the config in a development environment first and observe.

---

## Adding Your Own Keys

The validator is permissive on unknown keys: variables it does not recognize are ignored, not flagged. You can add your own top-level config variables and reference them from custom theme templates or downstream scripts. They simply won't be looked at by the engine itself.

```python
MY_PUBLICATION_NAME = "The Daily Clamour"
MY_FOUNDING_AUTHOR  = "Max Spevack"
```

These pass validation and travel through to wherever your downstream code reads them.
