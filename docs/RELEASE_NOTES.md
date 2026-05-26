# Release Notes

## v2.0.2 (The Masthead) - May 25, 2026

Patch release. The headline correctness story is the classifier bug fix; the broader story is the brand redesign that aligns fishwrap.org with its own thesis. No engine API changes; no breaking changes; the v2.0 image contract holds.

### 🐛 Engine Correctness
*   **Classifier silently dropped every mixed-case keyword (#28).** `editor.py:classify_article` lowercased the article text but compared keywords as-given. Every demo config's proper-case keyword list was dead code; section routing was carried entirely by `SOURCE_SECTIONS` and the last-section fallback.
*   **Classifier word-boundary check missed punctuation-adjacent matches (#29).** `editor.py:score_keywords` and the parallel keyword-policy loop in `scoring.py` used `f" {k} " in f" {text_blob} "`, which only treats the literal space character as a boundary. Headlines like `NCIS: Origins`, `'Bridgerton,' Netflix renews`, and `The Pitt. Noah Wyle interview` failed to match show-name keywords.
*   **Unified fix:** `re.search(rf"\b{re.escape(k.lower())}\b", text_blob)` applied to both `editor.py` and `scoring.py`. Lowercases the keyword and uses regex `\b` word boundaries that match at any `\w`/`\W` transition. New regression test at `scripts/test_classifier_matching.py` covers case-mismatch, colon/comma/period boundaries, apostrophe-bearing keywords (`grey's anatomy`), embedded-substring negatives, and the parallel `scoring.py` policy boundary.

### 🧹 Architecture Cleanup
*   **Alembic infrastructure removed (follow-up to #15).** Issue #15 dropped alembic from runtime requirements, but the `alembic/` directory, migrations, and `alembic.ini` were left in tree. The runtime path (`fishwrap/db/repository.py:_initialize_engine`) bootstraps via `Base.metadata.create_all` and never invokes alembic. The migrations were dead code. The old `scripts/test_schema_integrity.py` pointed at a gitignored local SQLite file and could not pass on a fresh clone. Replaced with a self-contained test that creates a tempfile SQLite, runs `Base.metadata.create_all`, and verifies the expected tables, columns, and foreign keys via `sqlalchemy.inspect`.

### 🎨 Brand Redesign
*   **`docs/BRAND.md` rewritten wholesale.** The Digital Origami direction (origami fish, Deep Ocean Blue + Newsprint Cream + Salmon/Coral, "Enlightened Architect" voice) is retired. The new architecture is one brand with two voice registers under one visual home: REFUSAL (acquisition surfaces, broadsheet declarative) and EDITOR (working surfaces, magazine-warm second-person). Appendix A maps every engine surface to its required register.
*   **Wordmark: `Fishwra¶`** in Libre Baskerville Bold. The pilcrow takes the place of the closing P; the pilcrow's morphology is a P with a doubled vertical stem, the medieval scribal mark for a new paragraph. The pilcrow renders in Cardinal Red (`#9C1B14`), the editor's pencil; the rest of the letterforms in Refusal Black (`#0E0D0C`). The substitution is announced typographically and chromatically.
*   **Glyph and favicon:** bare pilcrow in Libre Baskerville Bold, Refusal Black on Smoke Cream. Path-only SVG plus PNG raster set (16/32/48/64/96/128/180/192/256/512) plus multi-resolution ICO at site root.
*   **Type stack:** Libre Baskerville + iA Writer Mono. Both SIL OFL, free, self-hosted under `docs/static/fonts/`. No paid foundry. No third face. The voice differentiation between registers comes from prose, not from a second body face.
*   **Asset production pipeline:** `docs/static/brand/generate-assets.py` produces wordmark SVG, favicon SVG, PNG raster set, multi-resolution ICO, and Open Graph card from the live fonts via `fontTools` and ImageMagick. No generative AI in the pipeline; the brand thesis (*the algorithm you can read*) is preserved by producing the brand's own marks through extant, auditable tooling.
*   **Open Graph card:** 1200×630 PNG with the wordmark, the masthead phrase (*The peasants scroll. The elite read.*), a placeholder edition line in iA Writer Mono, and the `fishwrap.org` URL.
*   **Jekyll wire-up:** `docs/_includes/head_custom.html` adds favicon links, og:image meta, and twitter:card meta. `docs/_config.yml` got `url: https://fishwrap.org` so absolute URLs resolve in social-share meta.

### 📚 Documentation
*   **`docs/index.md` rewritten.** The Stephenson epigraphs from *The Diamond Age* and *Anathem* survive as the page's literary frame; the REFUSAL-register §1 / HYBRID §2 / EDITOR §3 prose is lifted from BRAND.md with home-page warmth. Second-person warmth ("you know who you are") replaces the bible's clinical third person.
*   **`README.md` rewritten** in REFUSAL register. The Mailchimp opener (`Fishwrap is a Glass-Box news engine. It transforms RSS feeds, Reddit threads, and Hacker News into finite, auditable HTML editions`) is gone. Section emojis stripped. The brand bible added to the documentation table.
*   **Engineering blog retired.** Five posts and the index (`docs/blog/01_algorithms.md` through `05_release_engineering.md` and `docs/blog/index.md`) deleted. The bulk of the corpus's off-register prose — Blade Runner / Memento / fish-judging metaphors — lived there. Engineering content lives in the code; the manifesto work the blog tried to do is now in BRAND.md §2.
*   **`docs/RELEASE_NOTES.md`** v1.x and v0.x entries rewritten to strip Digital-Origami-era lyrical voice while preserving every codename, date, and feature.
*   **`docs/RELEASING.md`** runbook surgery (path bug fixes, anthropomorphism cleanup, em-dash flanker removal).
*   **`docs/VERSIONING.md`, `docs/IMAGE_CONTRACT.md`, `docs/CONFIG_SCHEMA.md`, `docs/adr/001-release-artifact.md`** light surgery against the Klausner bar.

### 🧹 Project Ops
*   **`CONTRIBUTING.md` deleted.** 250 of 250 commits in the project's lifetime are from a single author. Zero external PRs, issues, forks, stars, or watchers. The file documented a contribution workflow that has not run. The README's documentation-table reference was also removed. Reintroduce when an external contributor first earns one.

### 🛠️ Release Engineering
*   **`docs/RELEASING.md` step 3 path bug.** `cd ~/gemini/fishwrap` was a stale path from a different machine setup. Corrected to `cd ~/dev/fishwrap`.

### 🧪 Tests
*   `scripts/test_classifier_matching.py` — 10 cases covering #28 and #29 across both `editor.py` and `scoring.py`.
*   `scripts/test_schema_integrity.py` — rewritten to test the actual runtime bootstrap path (`Base.metadata.create_all`) via a tempfile, replacing the prior test that depended on a gitignored local artifact.

---

## v2.0.1 (The Audit Pass) - May 24, 2026

Point release driven by a top-to-bottom code and bandwidth review of the deployed fishwrap.org site. Every change traces to a GitHub issue (#17–#26) so the audit lineage stays visible in `git log`.

### 🔒 Security
*   **Re-enable TLS certificate verification (#20).** `utils.fetch_url` was disabling `check_hostname` and forcing `verify_mode = CERT_NONE` on the shared SSL context. Every HTTPS fetch accepted any peer certificate. Restored to `ssl.create_default_context()` defaults.
*   **Parse RSS/Atom via defusedxml (#21).** `xml.etree.ElementTree` is documented as vulnerable to entity-expansion attacks; RSS feeds are untrusted by definition. Swapped to `defusedxml.ElementTree`. Regression test `scripts/test_xml_safety.py` feeds a billion-laughs payload and asserts the fetcher refuses it.

### 📡 Engine Reliability
*   **Wire a real logger across the engine (#19).** Seven `except: pass` and silent `return []`/`return None` sites across `fetcher.py`, `utils.py`, `auditor.py`, `editor.py`, `printer.py`, and `db/repository.py` were swallowing errors against the README's "Failed feeds are logged, not hidden" claim. New `fishwrap/log.py` (stdlib `logging`, level via `FISHWRAP_LOG_LEVEL`, stderr) replaces them. Bare `except:` clauses narrowed to specific exception types so `KeyboardInterrupt` and `SystemExit` no longer get eaten mid-build.
*   **Configurable fetcher concurrency + per-host rate limit default (#23).** Hardcoded `MAX_WORKERS = 30` becomes config-driven `FETCH_WORKERS` (default 10). New `FETCH_DEFAULT_RATE_LIMIT_SECONDS` (default 0.0) provides a global floor for hosts not enumerated in `utils.RATE_LIMITS`.
*   **Code hygiene sweep (#26).** Every `open()` that handles text now specifies `encoding='utf-8'` explicitly. `editor.py` and `printer.py` switched from `str.replace`-based fragment path math to `os.path.join` + `os.path.dirname`.
*   **Delete dead renderer code (#18).** `fishwrap/renderers/{html,pdf}.py` (412 lines) was unreachable in the production pipeline. The HTML renderer used `random.choice` at render time (non-reproducible, manifesto violation) and unsafe `str.format` on raw template strings.

### 🌐 fishwrap.org Bandwidth
*   **Showrunner image weight: 4.5 MB → ~18 KB on AVIF-capable browsers (#17).** Three 1024×1024 PNGs (~4.5 MB total) replaced with AVIF + WebP + JPEG/PNG fallback via `<picture>` (logo) and CSS `image-set()` (section heroes). Source PNGs preserved in `static/images/sources/`. `scripts/optimize-theme-images.sh` regenerates derivatives from sources.
*   **Externalize basic-theme CSS (#22).** The basic theme inlined 21 KB of CSS in `layout.html` plus appended a dark-theme override from a separate file. Consolidated into one external `static/css/style.css`. Per-page HTML drops from ~24 KB to ~3 KB, and the three demos that share the theme (vanilla/cyber/ai) now hit a single cached file.

### 📦 Supply Chain
*   **SLSA build provenance + CycloneDX SBOM on every release (#24).** Closes the gap that #5 (A3) left open. `release.yml` now uses `actions/attest-build-provenance@v3` to attest the image digest and `anchore/sbom-action@v0` + `actions/attest-sbom@v3` to ship a verifiable SBOM. `docs/IMAGE_CONTRACT.md` documents `gh attestation verify`.

### 📝 Documented (Not Implemented)
*   **#25 — fishwrap.org security response headers.** HSTS, CSP, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy` are missing. Issue captures the recommended header set and Cloudflare Transform Rules path; no code change was the right vehicle.

### 🧪 Tests
*   `scripts/test_logging_wiring.py` — asserts garbage XML and unparseable Reddit JSON produce WARNING log entries.
*   `scripts/test_xml_safety.py` — asserts a billion-laughs payload is rejected by defusedxml and logged.

---

## v2.0.0 (The Newsstand) - May 5, 2026

This release marks the transition from "code you clone" to "image you pull." Fishwrap now ships as a signed OCI image at `ghcr.io/maxspevack/fishwrap`. Downstream products pull the pinned image, mount a config, and run it.

**This is a major version bump** per `docs/VERSIONING.md`'s "fundamental architectural shifts" criterion. The way consumers integrate with fishwrap changes structurally. If you were cloning fishwrap into a `vendor/` directory and running its venv install, that path no longer works. Switch to `docker pull ghcr.io/maxspevack/fishwrap:2.0` and run via `docker run`. See [`docs/IMAGE_CONTRACT.md`](IMAGE_CONTRACT.md) for the full new integration shape, and [Daily Clamour](https://github.com/maxspevack/dailyclamour.com) for a worked example.

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
*   **Action versions current:** release and demo workflows use the latest major versions of `actions/checkout`, `docker/build-push-action`, `docker/login-action`, `docker/metadata-action`, and `docker/setup-buildx-action`. Node 24-compatible ahead of GitHub's June 2026 deprecation.
*   **No `:latest` tag:** `flavor: latest=false` suppresses the auto-generated `:latest` tag that would otherwise be a footgun for consumers who pin loosely.

---

## v1.3.3 (The Synchronization) - Dec 14, 2025

Maintenance release to synchronize documentation updates and ensure all downstream artifacts build from the latest stable baseline.

*   Documentation refinements clarifying the separation of concerns between Engine and Product in deployment documentation.

---

## v1.3.2 (The Chronos Update) - Dec 13, 2025

Added precise publication-time metadata to the template context.

*   **Publication timestamp:** the engine now injects the precise generation time into the template context as `time_str` (e.g., `08:00 AM PST`).
*   **Forward compatibility:** themes updated to conditionally render the timestamp.

---

## v1.3.1 (The Polish) - Dec 13, 2025

Maintenance release covering UI refinement, build stability, and release engineering.

### Bug fixes and polish
*   Fixed the tab-flashing bug in the transparency modal and enforced high-contrast text colors.
*   Updated the score badges to fixed widths for alignment.
*   Renamed "Signal Delta" to "Delta" and reordered the Source Efficiency table (Input → Output → Delta) for logical flow.
*   Replaced the text-based version string in the footer with a GitHub icon + version badge.

### Release engineering
*   Introduced `scripts/release.sh` to automate the version bump, build verification, and tagging process.
*   The release pipeline now enforces a `make test` pass before allowing a release.
*   Updated `Makefile` to suppress legacy `SyntaxWarning` noise and use `install_venv.sh` for environment setup.
*   Published `docs/RELEASING.md` as the runbook for shipping new versions.

---

## v1.3.0 (Digital Origami) - Dec 13, 2025

Tabbed Transparency UI, a brand identity that has since been retired, and build hardening against Python 3.14. The brand work this release introduced (the original "Digital Origami" direction) has been superseded by the bible at `docs/BRAND.md`; see the README and §6 of the bible for the current visual identity.

### Engineering
*   Tabbed transparency modal separating Vitals (The Funnel), Sources (Efficiency), and The Bubble (Cut-Line).
*   Sidebar navigation regression fixed in the demo themes.
*   `Makefile` updated to handle shell environments explicitly (`bash`); `install_venv.sh` simplifies dependency installation.
*   Dependencies cleaned up; the experimental Pydantic refactor was reverted to maintain Python 3.14 compatibility.

### Documentation (now superseded)
*   Reorganized the engineering documentation into a blog structure. The blog was retired in May 2026; engineering content now lives alongside the code.
*   Added the first version of the brand bible. This bible was rewritten in May 2026 and replaced with the current `docs/BRAND.md`.

---

## v1.2.0 (The Glass Box) - Dec 12, 2025

v1.2 added an audit log so the reader could check the engine's working. The previous file-based store (JSON) was replaced with SQLite, and the Auditor module was introduced.

### Architecture
*   **SQLite migration:** moved from atomic JSON files to a SQLite backend (`fishwrap.db`). Enables long-term history and prevents corruption during concurrent fetches.
*   **The Auditor:** new module that runs after every edition, generates a Transparency Report (`transparency.html`), and records what the engine considered, scored, and cut.
*   **Funnel metrics:** introduced Anti-Feed Protection (yield rate) and Source Efficiency metrics to quantify what the engine filtered out.

### Observability
*   Console reporting for cut-line stories (what almost made the edition) and drift (when a story was reclassified into a different section).
*   `fw-db` command-line tool for managing the newsroom database (`status`, `prune`, `vacuum`).

---

## v1.1.0 (The Parallel Press) - Dec 12, 2025

v1.1 added concurrent fetching and per-domain rate limiting after the unthrottled fetcher tripped Reddit's 429.

### Performance
*   **Concurrency:** `ThreadPoolExecutor` for the Fetcher and Enhancer. Pipeline runtime dropped from ~51s to ~15s (3.5x speedup).
*   **Rate limiting:** token-bucket rate limiting introduced after the concurrent fetcher exceeded Reddit's per-host limit. Per-host rate limits are now configurable via `utils.RATE_LIMITS`.

### Logic
*   v1.1 fixed a regression where the Fetcher overwrote scraped text with raw RSS data on each cycle. Subsequent runs now hit the cache for previously-enhanced articles.
*   Deduplication optimized from O(N²) to effective O(N) by pre-filtering candidates with set intersection before running fuzzy matching.

---

## v1.0.0 (The Foundation) - Dec 11, 2025

The initial release.

*   Four-stage pipeline: Fetcher → Editor → Enhancer → Printer.
*   JSON-file persistence (`articles_db.json`).
*   Static HTML and rudimentary PDF output.

---

## Pre-history

Single-line entries. Pre-v1 work was prototype territory.

*   **v0.9.0** — 2025-12-10. Added per-vertical configurations: cybersecurity (The Zero Day) and AI research (The Hallucination). Proved the engine was not bound to a single publication.
*   **v0.3.0** — 2025-12-09. Extracted the engine (`fishwrap`) from the consumer publication (`dailyclamour.com`). Established the architectural separation that makes Fishwrap a substrate, not a product.
*   **v0.2.0** — 2025-12-08. First publication-side visual identity for Daily Clamour, including the bento-grid layout. Engine-side branding came later and was rewritten in May 2026.
*   **v0.1.0** — 2025-12-07. First commit. A script to fetch, process, and print headlines.
