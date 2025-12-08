# Press Package 🗞️

The core engine for **The Daily Clamour**.

## Directory Structure

*   **`_config.py`**: Central configuration (Feeds, Scoring Rules, Thresholds).
*   **`fetcher.py`**: Ingestion engine. Fetches RSS/JSON, standardizes data, parses HN comments, and performs upserts.
*   **`editor.py`**: Logic core. Handles Classification, Scoring, Clustering, and Selection.
*   **`enhancer.py`**: Content enricher. Scrapes full text and fetches comments.
*   **`printer.py`**: Output orchestrator.
*   **`scoring.py`**: Algorithms for calculating article Impact Score.
*   **`utils.py`**: Shared helpers (Network, Date Parsing, HTML Cleaning).
*   **`renderers/`**:
    *   **`html.py`**: Generates the "Bento Grid" HTML dashboard with Dracula theme.
    *   **`pdf.py`**: Generates the PDF edition.

## Key Features

### The "Smart Grid" (HTML)
The HTML renderer uses a strict CSS Grid system to prevent "masonry gaps" and enforce visual hierarchy.
*   **Lead Cards:** 2 cols x 2 rows. Large font. Max 2 per section.
*   **Feature Cards:** 1 col x 2 rows. Medium font. Max 4 per section.
*   **Compact Cards:** 1 col x 1 row. Small font. Unlimited.
*   **Logic:** Scores determine size, but strict quotas prevent layout breakage. If a "Lead" quota is full, the article is gracefully downgraded to "Feature" styling.

### Debug Mode v2
The generated HTML includes a hidden debug layer. Click the ⚙️ icon in the sidebar to toggle "Debug Active" state.
*   **Absolute Overlay:** Hovering/Clicking a card in debug mode reveals a semi-transparent absolute overlay covering the card.
*   **Data Exposed:**
    *   **Classification:** Rules triggered (Keywords, Source affinity).
    *   **Score Breakdown:** Exact math for Base points, Policy boosts, and Dynamic stats (Votes/Comments).
    *   **Cluster Info:** Which duplicate headlines were merged into this story.

### Hacker News Integration
The engine treats Hacker News and `hnrss.org` feeds specially.
*   **Linking:** Articles preferentially link to the *comments* page (the discussion) rather than the target URL, as the value often lies in the thread.
*   **Scoring:** Scores are derived dynamically from Points and Comment counts.

## Developer Notes
*   **Timezones:** All internal timestamps are UTC. Output is rendered in the configured local timezone (`US/Pacific`).
*   **Persistence:** `articles_db.json` is the source of truth. Delete it to force a fresh fetch of all feeds.
*   **Execution:** Run via `/newspaper` (which triggers `~/gemini_publish.sh`) or `python3 -m press.fetcher` etc.