# Fishwrap Release History

## v1.1.0: "Speed & Stability" (2025-12-11)

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
