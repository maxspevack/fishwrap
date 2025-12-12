# Fishwrap Roadmap 🗺️

Fishwrap is evolving from a personal script into a robust News Engine platform.

## 🟢 Phase 1: Stability & Observability
*Focus: "The Glass Box" - Making the engine's decisions transparent.*

*   **Observability Suite:**
    *   [x] Add console reporting for "Cut-Line" stories (what *almost* made it).
    *   [x] Add source volume histograms (Fetcher Dominance).
    *   [x] Add "Run Sheet Diversity" report (Output Dominance).
    *   [x] Drift Tracking (Classification overrides).
*   **Data Foundation:**
    *   [ ] Migrate from `articles_db.json` to SQLite (`fishwrap.db`).
    *   [ ] Build CLI tools for database management (`fw-db stats`, `fw-db clean`).

## 🔵 Phase 1.5: The Auditor & Persistence
*Focus: Structuralizing the Insights for the User.*

*   **The Auditor Module (`fishwrap.auditor`):**
    *   [ ] Implement "Funnel Analysis" (Input -> Pool -> Qualified -> Selected).
    *   [ ] Persist run statistics (`run_stats.json` or SQLite) for trend analysis.
    *   [ ] Generate user-facing `transparency.html` artifact.
*   **Architecture:**
    *   [ ] Refactor `config.py` to use Pydantic models for validation.
    *   [ ] Modularize `Scorer` and `Classifier` logic into a plugin system.

## 🟡 Phase 2: The Chronicle
*Focus: History and Artifacts.*

*   **Archival Modes:**
    *   [ ] Implement "Weekly" and "Monthly" edition generation based on historical data.
    *   [ ] Add `TimeWindow` logic to the Editor.
*   **PDF Engine v2:**
    *   [ ] Support **Full Text** embedding for top stories in PDF output.
    *   [ ] Improve multi-column newspaper layout (CSS Grid/Flexbox).

## 🔴 Phase 3: The Platform
*Focus: Democratization.*

*   **Web UI:** A local dashboard for configuring feeds and tuning weights visually.
*   **Granular Consent:** A UI for creating transparent scoring rules ("I dislike X because Y") to replace opaque "Thumbs Down" buttons.
*   **Multi-Tenancy:** Support for running multiple newsrooms from a single engine instance.
