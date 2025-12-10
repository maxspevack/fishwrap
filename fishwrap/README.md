# Fishwrap Engine ⚙️

This directory contains the core source code for Fishwrap.

## Pipeline Modules

The system is designed to be run as a sequence of modules:

```mermaid
graph LR
    A[feeds.json] -->|Fetch| B(Articles DB)
    B -->|Edit| C(Run Sheet)
    C -->|Enhance| D(Enhanced Issue)
    D -->|Print| E[latest.html / .pdf]
```

### 1. `fishwrap.fetcher`
*   **Input:** RSS Feeds defined in your config.
*   **Process:** Downloads feeds, parses entries, and performs "upserts" into the `articles_db.json`.
*   **Smart Features:** Prioritizes Hacker News comments over link targets.

### 2. `fishwrap.editor`
*   **Input:** `articles_db.json`.
*   **Process:** Scans candidates, scores them based on **Impact** (Votes + Comments + Freshness) and your `EDITORIAL_POLICIES`. Selects the top $N$ stories per section.
*   **Output:** `run_sheet.json` (The "Front Page" plan).

### 3. `fishwrap.enhancer`
*   **Input:** `run_sheet.json`.
*   **Process:** Uses `newspaper3k` to download full article text and authors.
*   **Output:** `enhanced_issue.json`.

### 4. `fishwrap.printer`
*   **Input:** `enhanced_issue.json`.
*   **Process:** Loads the active **Theme** (defined in config) and renders the HTML.
*   **Output:** `latest.html`.

## Configuration

Fishwrap relies on a configuration file injected at runtime via the `FISHWRAP_CONFIG` environment variable.

If `FISHWRAP_CONFIG` is not set, it defaults to an internal schema that defines:
*   `FEEDS`: List of RSS URLs.
*   `THEME`: Path to the theme directory.
*   `EDITION_SIZE`: How many articles per section.
*   `VISUAL_THRESHOLDS`: Score cutoffs for "Lead" vs "Standard" cards.

## Theming

Themes are located in directories containing:
*   `css/style.css`
*   `templates/layout.html`, `card.html`, etc.
*   `static/` (Images/Assets)

The engine automatically loads the theme specified in `config.THEME`.
