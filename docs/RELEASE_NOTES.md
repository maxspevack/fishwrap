# Fishwrap Release Notes

This document chronicles the notable changes across versions of the Fishwrap engine.

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
