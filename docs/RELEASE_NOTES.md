# Release Notes

Fishwrap is evolving from a personal script into a robust "Anti-Feed" platform. Here is the history of that evolution.

---

## v1.2.0 (The Glass Box) - Dec 13, 2025
**Commit:** `2b59503`

This release marks the transition from "Script" to "System." We realized that speed wasn't enough; we needed **Trust**. We rebuilt the engine to be auditable, persistent, and transparent.

### 🏛️ The Architecture
*   **SQLite Migration:** We moved from atomic JSON files to a robust **SQLite** backend (`fishwrap.db`). This enables long-term history ("The Chronicle") and prevents data corruption during concurrent fetches.
*   **The Auditor:** A new forensic module that runs after every edition. It generates a **Transparency Report** (`transparency.html`) that proves the algorithm isn't just a mirror of the most popular links.
*   **Anti-Feed Metrics:** We introduced the "Anti-Feed Protection" score (Yield Rate) and "Source Efficiency" metrics to quantify how much noise we filter out.

### 🔭 Observability
*   **The HUD:** New console reporting for "Cut-Line" stories (what almost made it) and "Drift" (when a story is forced into a different section).
*   **Database CLI:** Introduced `fw-db`, a command-line tool for managing the newsroom database (`status`, `prune`, `vacuum`).

### 📚 Documentation
*   **The Architect's Log:** Launched the engineering blog with case studies on Algorithms, Concurrency, and Consistency.
*   **Brand Identity:** Established the "Digital Origami" design language.

---

## v1.1.0 (The Parallel Press) - Dec 11, 2025
**Commit:** `ce6cb5b`

The "Speed" update. We realized our sequential processing was too slow for the scale of the web. We broke the single-lane highway and built a ten-lane freeway.

### ⚡ Performance
*   **Concurrency:** Implemented `ThreadPoolExecutor` for the Fetcher and Enhancer. Pipeline runtime dropped from **~51s** to **~15s** (3.5x speedup).
*   **Rate Limiting:** We flew too close to the sun and DDoS'd Reddit. We implemented **Token Bucket** rate limiting to be polite citizens of the open web.

### 🧠 Logic
*   **The "Memento" Fix:** Solved a critical bug where the engine would forget scraped text every hour. We now merge new data with existing cache, ensuring 100% cache hit rates on subsequent runs.
*   **The Jaccard Hatchet:** Optimized deduplication from O(N²) to effective O(N) by pre-filtering candidates with Set Intersection before running expensive fuzzy matching.

---

## v1.0.0 (The Foundation) - Dec 11, 2025
**Commit:** `346d16d`

The initial release. A proof-of-concept that a Python script could replace a doomscroll.

*   **Core Engine:** The four-stage pipeline (Fetcher -> Editor -> Enhancer -> Printer).
*   **JSON Storage:** Simple file-based persistence (`articles_db.json`).
*   **Basic Output:** Generation of a static HTML edition and a rudimentary PDF.