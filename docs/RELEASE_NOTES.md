# Release Notes

## v1.2.0 (The Persistence Release) - Dec 13, 2025

**"The Glass Box"**

This release transforms Fishwrap from a script into a platform by introducing a database backend and a comprehensive observability suite.

### 🚀 New Features
*   **The Auditor:** A new module that snapshots run metrics and generates a user-facing **Transparency Report**.
*   **Glass Box UI:** An integrated dark-mode modal (`transparency.html`) that shows the "Funnel" (Input vs Output), "Source Efficiency" (Signal vs Noise), and "The Bubble" (Cut-Line).
*   **SQLite Backend:** Replaced the JSON file system with a robust SQLite database using **SQLAlchemy** and **Alembic**.
    *   ACID compliance for concurrent fetching.
    *   10x performance improvement on large archives.
    *   Indexed Timestamps for fast historical queries.
*   **`fw-db` CLI:** A utility for managing the database (`status`, `runs`, `prune`).
*   **Performance Telemetry:** The engine now tracks and reports execution time for each stage.

### 🛡️ Operational Changes
*   **License:** Switched to **Apache 2.0**.
*   **Demo Isolation:** Each demo (`vanilla`, `cyber`, `ai`) now runs on a completely isolated database to prevent data contamination.
*   **Console Cleanup:** Reduced log verbosity in favor of the HTML report.

---

## v1.1.0 (Concurrency) - Dec 11, 2025
*   Implemented `ThreadPoolExecutor` for Fetcher/Enhancer (7x speedup).
*   Fixed caching bugs (Memento).
*   Implemented Token Bucket Rate Limiting.

## v1.0.0 (Initial Release) - Dec 11, 2025
*   Core Engine (Fetcher, Editor, Enhancer, Printer).
*   JSON-based storage.
*   Basic PDF generation.
