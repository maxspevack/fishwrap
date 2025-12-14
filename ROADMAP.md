# Product Roadmap

Fishwrap is evolving from a personal script into a robust News Engine platform.

## Phase 1: Core Engine Stability (v1.0 - v1.3) ✅
*   **Sequential Pipeline:** Fetch -> Edit -> Enhance -> Print. (Completed)
*   **Performance:** Parallel fetching and enhancement (ThreadPool). (Completed)
*   **Observability:** "Glass Box" Audit Logs and Transparency Report. (Completed v1.2)
*   **Release Engineering:** Automated release scripts, hygiene checks, and Calendar Versioning for downstream products. (Completed v1.3)

## Phase 2: The Platform (v1.4+)
*   **Smart Build System:** Move the incremental build logic (dependency graph) from the downstream `Makefile` into the core `fishwrap` engine. Ideally `python -m fishwrap.build`.
*   **Plugin Architecture:** Decouple `Scorer` and `Classifier` logic so users can inject custom rules without editing source code.
*   **Config v2:** Refactor `config.py` to use a safer schema (Pydantic or similar), but learn from the v1.2 disaster—ensure compatibility with target Python versions (3.14).

## Phase 3: The Service (v2.0)
*   **API Mode:** Expose `run_sheet.json` via a lightweight REST/GraphQL API.
*   **Frontend Separation:** Build a React/Vue frontend that consumes the API, replacing the static HTML generator (optional).

## 🔬 Performance Field Notes (Feedback from Daily Clamour v1.2)
*   **Memory:** RSS parsing can spike memory usage. Consider streaming parsers for massive feeds.
*   **Database:** SQLite is robust, but we need automated vacuuming/pruning for long-running instances. (Added `fw-db` tool).