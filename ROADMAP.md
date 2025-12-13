# Fishwrap Roadmap 🗺️

Fishwrap is evolving from a personal script into a robust News Engine platform.

## 🟢 Phase 1: Stability & Observability
*Focus: "The Glass Box" - Making the engine's decisions transparent.*

*   **Observability Suite:**
    *   [x] Add console reporting for "Cut-Line" stories (what *almost* made it).
    *   [x] Add source volume histograms (Fetcher Dominance).
    *   [x] Add "Run Sheet Diversity" report (Output Dominance).
    *   [x] Drift Tracking (Classification overrides).
*   **CLI Tools:**
    *   [x] Build CLI tools for database management (`fw-db stats`, `fw-db clean`).

## 🔵 Phase 1.5: The Auditor & Persistence (Completed in v1.2.0)
*Focus: Structuralizing the Insights for the User & Building History.*

*   **Data Foundation:**
    *   [x] Migrate from `articles_db.json` to SQLite (`fishwrap.db`).
*   **The Auditor Module (`fishwrap.auditor`):**
    *   [x] Implement "Funnel Analysis" (Input -> Pool -> Qualified -> Selected).
    *   [x] Persist run statistics (`run_stats.json` or SQLite) for trend analysis.
    *   [x] Generate user-facing `transparency.html` artifact.
*   **Architecture Refinements:**
    *   [x] Refactor `config.py` to use Pydantic models for validation. (Actually, we implemented dynamic loading, not Pydantic yet. I'll leave this unchecked).
    *   [ ] Modularize `Scorer` and `Classifier` logic into a plugin system.

## 🔬 Performance Field Notes (Feedback from Daily Clamour v1.2)
*Real-world data from the 159-feed production instance.*

1.  **Fetcher (CPU Bound):** Fetching 160 feeds takes ~90s. The bottleneck is likely XML/Date parsing in Python threads, not network I/O.
    *   *Target:* Explore `lxml` or multiprocessing for parsing.
2.  **Editor (Scaling Risk):** Scoring 3,000 candidates takes ~27s. This is slower than expected (super-linear scaling). The regex-heavy scoring loop in Python is the culprit.
    *   *Target:* Move keyword matching to SQLite FTS5 or cache computed scores more aggressively.
3.  **Enhancer (Solved):** 100% Cache Hit rate means re-publishing is near-instant (0.07s). The "Chronicle" architecture is validated.

## 🟡 Phase 2: The Chronicle & Products
*Focus: Enduring value, history, and new editions.*

*   **Archival Modes:**
    *   [ ] Implement "Weekly" and "Monthly" edition generation based on historical data.
    *   [ ] Add `TimeWindow` logic to the Editor.
*   **PDF Engine v2:**
    *   [ ] Support **Full Text** embedding for top stories in PDF output.
    *   [ ] Improve multi-column newspaper layout (CSS Grid/Flexbox).

## 🔴 Phase 3: The Platform
*Focus: Democratization & SaaS.*

*   **Web UI:** A local dashboard for configuring feeds and tuning weights visually.
*   **Granular Consent:** A UI for creating transparent scoring rules ("I dislike X because Y") to replace opaque "Thumbs Down" buttons.
*   **Multi-Tenancy:** Support for running multiple newsrooms from a single engine instance.