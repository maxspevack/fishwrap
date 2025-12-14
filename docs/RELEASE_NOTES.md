# Release Notes

Fishwrap is evolving from a personal script into a robust "Anti-Feed" platform. Here is the history of that evolution.

---

## v1.3.0 (Digital Origami) - Dec 13, 2025
**Commit:** `b4627de`

This release focuses on **Experience and Stability**. We polished the "Glass Box" UI, overhauled the documentation identity, and hardened the build system to survive bleeding-edge environments (Python 3.14).

### 🎨 UX & Branding
*   **Tabbed Transparency UI:** The "Glass Box" modal now features a clean, tabbed interface separating "Vitals" (The Funnel), "Sources" (Efficiency), and "The Bubble" (Cut-Line).
*   **Digital Origami:** Rolled out the new brand identity across the documentation.
*   **Sidebar Restoration:** Fixed a regression in the demo themes where the sidebar navigation was lost.

### 📚 Documentation
*   **The Architect's Log:** Reorganized the engineering docs into a proper blog structure.
*   **Brand Bible:** Added comprehensive brand guidelines and GenAI prompts for assets.

### 🛡️ Engineering
*   **Robust Build System:** Updated `Makefile` to explicitly handle shell environments (`bash`) and simplify dependency installation (`install_venv.sh`), fixing deployment issues on modern macOS.
*   **Dependencies:** Cleaned up the dependency tree, reverting the experimental Pydantic refactor to maintain compatibility with Python 3.14.

---

## v1.2.0 (The Glass Box) - Dec 12, 2025
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

## v1.1.0 (The Parallel Press) - Dec 12, 2025
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

---

## Pre-History (The Prototype Era)

Before v1.0, we were figuring out what we were actually building.

### v0.9.0 (The Fleet) - Dec 10, 2025
**Commit:** `65b49aa`
**Theme:** "Verticalization." We proved the platform thesis by launching specific verticals.
*   **The Zero Day:** A cybersecurity-focused briefing.
*   **The Hallucination:** An AI research briefing.
*   This proved Fishwrap wasn't just a news reader; it was a generic engine for *any* stream of information.

### v0.3.0 (The Schism) - Dec 9, 2025
**Commit:** `5e9a5cb`
**Theme:** "Separation of Concerns."
*   We extracted the "Engine" (`fishwrap`) from the "Product" (`dailyclamour.com`).
*   This architecture allowed us to treat the Daily Clamour as just one *instance* of the Fishwrap technology.

### v0.2.0 (The Identity) - Dec 8, 2025
**Commit:** `3f26894`
**Theme:** "Ink & Grit."
*   Established the "Vintage" aesthetic.
*   Introduced "Scoop the Pearl" as the mascot.
*   Moved from a generic HTML list to the "Bento Grid" layout.

### v0.1.0 (The Seed) - Dec 07, 2025
**Commit:** `e0c55b0`
**Theme:** "The Genesis."
*   The very first commit of the Fishwrap project. A simple script to fetch, process, and print basic news headlines.
*   This was the day the "Anti-Feed" began.