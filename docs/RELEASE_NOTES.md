# Fishwrap Release Notes

This document chronicles the notable changes across versions of the Fishwrap engine.

## v1.1.0 (2025-12-11)

### Summary
The "Speed & Stability" release. This version introduces massive performance improvements through parallelization while ensuring robust behavior via rate limiting and improved state management. It solves critical issues with data persistence ("Zombie Articles") and significantly reduces pipeline execution time.

### Features & Performance
*   **Parallel Execution:** Refactored `fetcher.py` and `enhancer.py` to use `ThreadPoolExecutor`. Network I/O is now concurrent, resulting in a **~7.5x speedup** (Total I/O reduced from ~51s to ~7s in tests).
*   **Rate Limiting:** Implemented a domain-based "Token Bucket" rate limiter in `utils.py` to prevent HTTP 429 errors. Requests to sensitive domains (e.g., `reddit.com`) are serialized and throttled while others remain parallel.
*   **Professional Dark Theme:** The "Basic" theme (`demo/themes/basic`) has been upgraded to a polished "Professional Dark" mode with improved typography, layout, and a custom SVG logo.

### Bug Fixes & Logic
*   **State Preservation (The "Memento" Fix):** Fixed a critical regression where the Fetcher would overwrite expensive enhanced data (full text, comments) with raw RSS data on subsequent runs. Updates are now merged, ensuring a **100% cache hit rate** for previously processed items.
*   **Zombie Defense:** Decoupled database retention from publication logic. We now retain data for 48 hours (to detect and deduplicate updates) but strictly filter for 24-hour freshness during publication. This prevents old articles from "rising from the dead" as new items.

### Documentation
*   **Engineering Series:** Refactored the monolithic "Scaling" paper into a 3-part Engineering Case Study series (`docs/engineering/`) covering Algorithms, Concurrency, and Consistency.
*   **Branding:** Updated all documentation and demos to use consistent Fishwrap branding.
*   **Deployment:** Introduced the `/ship` "Golden Rule" workflow for automated testing and deployment.

---

## v1.0.0 (2025-12-11)

### Summary
Initial major release of the refactored Fishwrap engine. This version introduces a clear architectural separation between the core engine, a standalone demo implementation, and product-specific instances (like The Daily Clamour). It includes a robust theming system, configurable pipelines, and improved documentation for developers and users.

### Features
*   **Architectural Separation:** Implemented a clean separation between the `fishwrap/fishwrap` engine, `demo/` (reference implementation), and `daily_clamour/` (product instance).
*   **Configurable Engine:** Introduced dynamic configuration loading via `FISHWRAP_CONFIG` environment variable, allowing external Python files to customize pipeline settings.
*   **Modular Theming System:** Themes (`basic`, `vintage`) are now externalized from the core rendering logic and loaded dynamically.
*   **Static Asset Pipeline:** Static assets (images, textures) are automatically copied from the active theme's directory to the output directory during printing.
*   **Enhanced Demo (`demo/`):** A fully functional, unbranded demo newspaper, complete with diverse feeds, debug functionality, and a dedicated `README.md`.
*   **Granular Cleanup:** Added `make clean-demo` and `make clean-clamour` targets for specific artifact removal.

### Enhancements
*   **Improved Documentation:** Revamped Root, Engine, and Demo READMEs for clarity, user-friendliness, and architectural overview.
*   **Newsroom Metaphor:** Root README architecture explanation now uses a more engaging newsroom metaphor.
*   **Responsive Styling:** Refined mobile responsiveness for the "Vintage" theme (2-column layout on tablets).
*   **Polished Basic Theme:** Added sticky sidebar, debug toggle, and a generic SVG logo to the "Basic" theme.
*   **Makefile Streamlining:** Cleaned up Makefile with explicit `run-clamour` and `run-vanilla` targets.

### Bug Fixes
*   Corrected `Makefile` syntax error (`run-fishwrap` duplication).
*   Restored `MIN_SECTION_SCORES` to `_config.py` in the default config.
*   Fixed recursive config loading issue in `demo/config.py`.

### Architecture
*   **Clean Engine:** `fishwrap/fishwrap/_config.py` now serves as an empty schema/loader, with all specific settings moved to instance configurations.
*   **Isolated Data/Output:** `demo/` and `daily_clamour/` now manage their own data (`.json`) and output (`.html`, `.pdf`) files.
*   **Git Hygiene:** Untracked generated files, added `.gitkeep`, and cleaned up extraneous artifacts.

---