# Versioning Taxonomy

Fishwrap adheres to **Semantic Versioning 2.0.0**, using a `MAJOR.MINOR.PATCH` format (e.g., `v1.2.3`). This document defines what criteria trigger an increment in each part of the version number.

## Format: `vMAJOR.MINOR.PATCH`

---

### `MAJOR` Version: Breaking Changes & Significant Reworks

*   **When to increment:**
    *   **Incompatible API changes:** If a core module's (e.g., `fetcher.py`, `editor.py`, `printer.py`) public interface changes in a way that *requires users to modify their code or configurations* to continue using the engine.
    *   **Fundamental architectural shifts:** A complete overhaul of how themes are loaded, how configuration is structured (e.g., abandoning `exec()` for `importlib` if it changes user interaction).
    *   **Major data model changes:** If `articles_db.json` schema changes in a non-backward-compatible way, requiring migration tools or data loss.
*   **Reset:** Increments `MAJOR` version. Resets `MINOR` and `PATCH` to `0`.

---

### `MINOR` Version: New Features & Non-Breaking Enhancements

*   **When to increment:**
    *   **New features:** Adding a new module (e.g., a "Publisher" module), new policy types (e.g., a new `EDITORIAL_POLICIES` rule type).
    *   **Backward-compatible API additions:** Adding new functions or classes, or new optional parameters to existing functions, without breaking existing usage.
    *   **Significant internal improvements:** Major performance optimizations, extensive refactoring that doesn't change external APIs but improves maintainability.
    *   **New default theme:** Shipping a new default theme (e.g., "Matrix Theme") alongside "Basic".
*   **Reset:** Increments `MINOR` version. Resets `PATCH` to `0`.

---

### `PATCH` Version: Backward-Compatible Bug Fixes & Minor Tweaks

*   **When to increment:**
    *   **Bug fixes:** Correcting errors that cause crashes, incorrect behavior, or unexpected output.
    *   **Minor improvements:** Small performance tweaks, documentation corrections, build script fixes.
    *   **Styling fixes:** Adjustments to a default theme's CSS that don't introduce new features.
*   **Reset:** Increments `PATCH` version. Does not reset `MAJOR` or `MINOR`.

---

### Pre-release and Build Metadata (Optional)

*   **Pre-release identifiers:** Appended for unstable releases (e.g., `v1.0.0-alpha.1`, `v1.0.0-beta`, `v1.0.0-rc.1`).
*   **Build metadata:** Appended for specific build numbers or commit SHAs (e.g., `v1.0.0+20251211.gitsha`).
