# Release Notes

Fishwrap is evolving from a personal script into a robust "Anti-Feed" platform. Here is the history of that evolution.

---

## v2.0.0 (The Newsstand) - May 5, 2026

This release marks the transition from "code you clone" to "image you pull." Fishwrap now ships as a signed OCI image at `ghcr.io/maxspevack/fishwrap`. Downstream products pull the pinned image, mount a config, and run it.

**This is a major version bump** per `docs/VERSIONING.md`'s "fundamental architectural shifts" criterion. The way consumers integrate with fishwrap changes structurally. If you were cloning fishwrap into a `vendor/` directory and running its venv install, that path no longer works — switch to `docker pull ghcr.io/maxspevack/fishwrap:2.0` and run via `docker run`. See [`docs/IMAGE_CONTRACT.md`](IMAGE_CONTRACT.md) for the full new integration shape, and [Daily Clamour](https://github.com/maxspevack/dailyclamour.com) for a worked example.

### 📦 The Artifact
*   **OCI image release:** every `v*` tag push triggers `.github/workflows/release.yml`, which builds and publishes the image to GHCR. Stable tags publish both the exact tag (`:2.0.0`) and the floating minor (`:2.0`); pre-release tags (`-rc1`, `-alpha.1`, etc.) publish only the exact tag.
*   **Documented consumer contract:** `docs/IMAGE_CONTRACT.md` describes inputs, outputs, entrypoints, versioning policy, and pinning recommendations. The contract surface is the only thing consumers should depend on.

### ✨ New CLI Surface
*   **`fishwrap-build --config <path>`:** runs the full pipeline. Replaces the four-step `python -m fishwrap.{fetcher,editor,enhancer,printer}` sequence.
*   **`fishwrap-version`:** prints the running image's semver to stdout. The only supported way for downstream consumers to read the version.
*   **`fishwrap-validate-config <path>`:** schema-checks a config file in ~100 ms before the pipeline runs. Catches missing keys and wrong types up-front instead of mid-fetch crashes.

### 🤖 Production CI
*   **Daily demo refresh:** `.github/workflows/demos.yml` runs at 12:00 UTC daily, rebuilds all four reference demos against the published image, validates output size (≥10 KB), and deploys to fishwrap.org via `actions/deploy-pages`. Per-vertical isolation: one bad feed does not block other demos.

### 🏗️ Engine Improvements
*   **Self-bootstrapping schema:** the engine now self-initializes its SQLite schema via `Base.metadata.create_all` in `_initialize_engine`. Ephemeral DBs in CI just work; fresh local clones no longer crash with "no such table: articles."
*   **Lazy weasyprint:** PDF generation is optional. `printer.py` lazy-imports weasyprint inside the PDF code path, gated by `ImportError`. The v2.0 image ships without weasyprint and its ~80 MB native dependency stack; PDF returns when a real consumer asks.

### 🧹 Decommissioned
*   **The launchd ship pipeline retired:** `ship_demos.sh`, `publish_demo.sh`, `scripts/refresh_demos.sh`, the launchd plist, and the `make ship` / `make publish` / `make run-clamour` Makefile targets all removed. CI replaces them.
*   **`ROADMAP.md` removed:** roadmap state lives in [GitHub Issues](https://github.com/maxspevack/fishwrap/issues) and [Milestones](https://github.com/maxspevack/fishwrap/milestones) to prevent drift between the file and reality.

### 📚 Documentation
*   **`docs/CONFIG_SCHEMA.md`:** every config key the engine recognizes, mirrored from the validator.
*   **`docs/adr/001-release-artifact.md`:** internal decision record for the image-based release artifact.
*   **`docs/RELEASING.md`:** rewritten as a procedural runbook for cutting future releases.
*   **`README.md`:** rewritten around the image-based quick-start (`docker run …` instead of `make setup`).
*   **`CONTRIBUTING.md`:** updated with a Two Audiences framing — engine contributors vs. image consumers.

### 🛠️ Release Engineering
*   **Action versions current:** release and demo workflows use the latest major versions of `actions/checkout`, `docker/build-push-action`, `docker/login-action`, `docker/metadata-action`, and `docker/setup-buildx-action` — Node 24-compatible ahead of GitHub's June 2026 deprecation.
*   **No `:latest` tag:** `flavor: latest=false` suppresses the auto-generated `:latest` tag that would otherwise be a footgun for consumers who pin loosely.

---

## v1.3.3 (The Synchronization) - Dec 14, 2025

A maintenance release to synchronize documentation updates and ensure all downstream artifacts are built from the latest stable baseline.

### 📚 Documentation
*   **Blog Vol 5:** Added "The Release" (Release Engineering Case Study).
*   **Runbook Refinements:** Clarified the separation of concerns between Engine and Product in deployment documentation.

---

## v1.3.2 (The Chronos Update) - Dec 13, 2025

A feature release enabling high-precision publication metadata.

### 🚀 New Features
*   **Publication Timestamp:** The engine now injects the precise generation time (e.g., `08:00 AM PST`) into the template context (`time_str`). This reinforces the "Snapshot in Time" philosophy of the Anti-Feed.
*   **Forward Compatibility:** Themes have been updated to conditionally render this timestamp, ensuring smooth upgrades.

---

## v1.3.1 (The Polish) - Dec 13, 2025

A maintenance release focused on UI refinement, build stability, and release engineering.

### 🐛 Bug Fixes & Polish
*   **Transparency UI:** Fixed the "Tab Flashing" bug in the Glass Box modal and enforced high-contrast text colors for readability.
*   **Visuals:** Updated the "Bubble" score badges to have fixed widths for better alignment.
*   **Data Clarity:** Renamed "Signal Delta" to "Delta" and reordered the "Source Efficiency" table (Input → Output → Delta) for better logical flow.
*   **Footer:** Replaced the text-based version string with a clean GitHub icon + version badge (e.g., `v1.3.1`).

### 🛠️ Release Engineering
*   **Automated Release Script:** Introduced `scripts/release.sh` to automate the version bump, build verification, and tagging process.
*   **Test Gate:** The release pipeline now enforces a `make test` pass, running the full unit test suite before allowing a release.
*   **Build Hardening:** Updated `Makefile` to suppress legacy `SyntaxWarning` noise and use a robust `install_venv.sh` script for environment setup.
*   **Runbook:** Published `docs/RELEASING.md` as the definitive guide for shipping new versions.

---

## v1.3.0 (Digital Origami) - Dec 13, 2025

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

The "Speed" update. We realized our sequential processing was too slow for the scale of the web. We broke the single-lane highway and built a ten-lane freeway.

### ⚡ Performance
*   **Concurrency:** Implemented `ThreadPoolExecutor` for the Fetcher and Enhancer. Pipeline runtime dropped from **~51s** to **~15s** (3.5x speedup).
*   **Rate Limiting:** We flew too close to the sun and DDoS'd Reddit. We implemented **Token Bucket** rate limiting to be polite citizens of the open web.

### 🧠 Logic
*   **The "Memento" Fix:** Solved a critical bug where the engine would forget scraped text every hour. We now merge new data with existing cache, ensuring 100% cache hit rates on subsequent runs.
*   **The Jaccard Hatchet:** Optimized deduplication from O(N²) to effective O(N) by pre-filtering candidates with Set Intersection before running expensive fuzzy matching.

---

## v1.0.0 (The Foundation) - Dec 11, 2025

The initial release. A proof-of-concept that a Python script could replace a doomscroll.

*   **Core Engine:** The four-stage pipeline (Fetcher -> Editor -> Enhancer -> Printer).
*   **JSON Storage:** Simple file-based persistence (`articles_db.json`).
*   **Basic Output:** Generation of a static HTML edition and a rudimentary PDF.

---

## Pre-History (The Prototype Era)

Before v1.0, we were figuring out what we were actually building.

### v0.9.0 (The Fleet) - Dec 10, 2025
**Theme:** "Verticalization." We proved the platform thesis by launching specific verticals.
*   **The Zero Day:** A cybersecurity-focused briefing.
*   **The Hallucination:** An AI research briefing.
*   This proved Fishwrap wasn't just a news reader; it was a generic engine for *any* stream of information.

### v0.3.0 (The Schism) - Dec 9, 2025
**Theme:** "Separation of Concerns."
*   We extracted the "Engine" (`fishwrap`) from the "Product" (`dailyclamour.com`).
*   This architecture allowed us to treat the Daily Clamour as just one *instance* of the Fishwrap technology.

### v0.2.0 (The Identity) - Dec 8, 2025
**Theme:** "Ink & Grit."
*   Established the "Vintage" aesthetic.
*   Introduced "Scoop the Pearl" as the mascot.
*   Moved from a generic HTML list to the "Bento Grid" layout.

### v0.1.0 (The Seed) - Dec 07, 2025
**Theme:** "The Genesis."
*   The very first commit of the Fishwrap project. A simple script to fetch, process, and print basic news headlines.
*   This was the day the "Anti-Feed" began.