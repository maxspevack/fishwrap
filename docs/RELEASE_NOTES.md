# Fishwrap Release History

## v1.1.0: "Speed & Stability" (2025-12-12)

**The Narrative:**
After establishing the core architecture in v1.0, we hit a wall. Our I/O was sequential, meaning the engine was only as fast as the slowest RSS feed. We also discovered "Zombie Articles" rising from the dead due to naive retention logic. This release focuses entirely on crushing latency and ensuring data consistency.

### ⚡ Performance & Infrastructure
*   **Parallel I/O:** Refactored `fetcher.py` and `enhancer.py` to use `ThreadPoolExecutor`. Network operations are now concurrent, yielding a **~7.5x speedup** (Total I/O reduced from ~51s to ~7s).
*   **Rate Limiting:** Implemented a polite "Token Bucket" rate limiter in `utils.py` to prevent DDoS-ing sources like Reddit (HTTP 429).
*   **State Preservation:** Fixed a critical regression where the Fetcher would overwrite expensive scraped data. Updates are now merged, ensuring a **100% cache hit rate** on subsequent runs.
*   **Zombie Defense:** Decoupled database retention (48h) from publication (24h). We now remember history to deduplicate, but only print fresh news.

### 🎨 UX & Documentation
*   **Professional Dark Theme:** The "Basic" theme has been upgraded to a polished dark mode with a custom Fishwrap SVG logo.
*   **Engineering Series:** Published [Scaling the School](engineering/index.html), a 3-part deep dive into our optimization journey.

---

## v1.0.0: "The Foundation" (2025-12-11)

**The Narrative:**
The initial major release. We took a script and turned it into an engine. This release established the "Glass Box" philosophy, separated the core logic from specific implementations, and introduced the "Newsroom" metaphor.

### 🏗️ Core Architecture
*   **Modular Engine:** Separated `fishwrap` (core) from `demo/` (reference) and `daily_clamour/` (product).
*   **Config Injection:** Dynamic configuration loading via `FISHWRAP_CONFIG`, allowing the engine to be stateless and reusable.
*   **Theming System:** Externalized templates (`basic`, `vintage`) and static asset pipelines.

### 🚀 Features
*   **The Editor:** An O(N) scoring and deduplication engine using Jaccard Indices.
*   **The Fetcher:** A robust RSS/JSON ingestion module.
*   **The Printer:** A Jinja2-based renderer for HTML and PDF artifacts.
*   **The Demos:** Three reference implementations (Vanilla, Cyber, AI) to showcase versatility.

---

## v0.9.0: "The Demo Fleet" (2025-12-10)

**The Narrative:**
The "Release Candidate" phase. We proved the engine's versatility by launching three distinct verticals. This phase exposed the need for vertical-specific configuration and better editorial controls.

### 🧪 Experiments
*   **Vertical Expansion:** Launched "The Zero Day" (Cybersecurity) and "The Hallucination" (AI) alongside the "Vanilla" general news demo.
*   **Editorial Controls:** Introduced per-vertical `editorial_config` to handle different content densities and update frequencies.
*   **Documentation:** Initial draft of the "Glass Box" manifesto and technical architecture specs.

---

## v0.3.0: "The Great Schism" (2025-12-09)

**The Narrative:**
The moment Fishwrap became a platform. We realized [The Daily Clamour](https://dailyclamour.com) was just *one* implementation of the engine. We aggressively refactored to decouple the "Product" from the "Press."

### 💔 Decoupling
*   **Repo Split:** Moved `daily_clamour` into its own directory (eventually its own repo strategy).
*   **Theme Abstraction:** Created the "Basic" system theme as a neutral default, separating it from the "Vintage" brand identity of the Clamour.
*   **Makefile logic:** Split build targets into `run-core` vs `run-clamour`.

---

## v0.2.0: "The Daily Clamour" (2025-12-08)

**The Narrative:**
The first coherent product. We moved from a script to a brand. This release focused on visual identity and the initial automated publishing pipeline.

### 📰 Productization
*   **Visual Identity:** Implementation of the "Vintage" CSS theme, evocative of 19th-century broadsheets for [The Daily Clamour](https://dailyclamour.com).
*   **Assets:** Added paper textures, Gothic fonts, and the layout engine.
*   **Automation:** Created the initial `auto_publish.sh` (precursor to the modern `deploy.sh`).

---

## v0.1.0: "The Genesis" (2025-12-07)

**The Narrative:**
In the beginning, there was `press.py`. A simple, monolithic script to fetch RSS feeds and dump them into an HTML file.

### 🥚 Origins
*   **Project Name:** "Press" (renamed to "Fishwrap").
*   **Core Logic:** Basic sequential fetching and Jinja2 templating.
*   **License:** BSD 3-Clause established.