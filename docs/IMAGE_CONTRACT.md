# Fishwrap Image Contract

This document is the public contract for consumers of the fishwrap engine. If you depend on fishwrap, you depend on this contract — and only this contract. Anything not described here is an implementation detail that may change at any time.

If you are looking for the *internal* decision record of why fishwrap publishes as a container image, see [ADR-001](adr/001-release-artifact.md). This document is the *external* face of that decision.

The canonical example consumer is [Daily Clamour](https://github.com/maxspevack/dailyclamour.com). Fork it as a starting template.

---

## 1. The Artifact

Every fishwrap release publishes one signed OCI container image to GitHub Container Registry:

```
ghcr.io/maxspevack/fishwrap:<tag>
```

- **Architectures:** `linux/amd64`. (arm64 is not currently published.)
- **Where it's built:** images are built and published exclusively by the release workflow at https://github.com/maxspevack/fishwrap/blob/main/.github/workflows/release.yml on tag pushes. The image's source is whatever commit the corresponding git tag points at.

Every release publishes **two** tags:

| Tag form | Example | Mutability |
|---|---|---|
| Exact | `v2.0.2` | Immutable. Recommended for production pinning. |
| Floating minor | `v2.0` | Republished on every patch within the minor line. Useful for development. **Do not pin production deploys to floating tags** — see §6 (Pinning). |

Pre-release tags (`-rc1`, `-alpha.1`, etc.) publish only the exact tag and do **not** update floating tags.

---

## 2. Inputs — What You Mount In

The image expects two mount points:

### `/cfg` (required)

Your configuration directory. The engine looks for these files inside it:

| Path | Required | Purpose |
|---|---|---|
| `/cfg/config.py` | Yes | Editorial configuration. See `docs/CONFIG_SCHEMA.md` for the schema. |
| `/cfg/secrets.json` | No | JSON object mapping source-specific keys to auth material (cookies, API tokens). Absent = sources requiring auth fetch in degraded mode. The engine reads only the keys it needs and ignores the rest. |

Beyond these two, anything else you place under `/cfg` is yours — typically your theme directory, About-page content, or other consumer-specific assets your config references.

### `/output` (required, writable)

The directory the engine writes to. Mount this writable. The engine produces the files described in §3.

### What is **not** part of the input contract

- Process working directory. The engine works from any CWD. **Do not** assume it is `/app`, `/cfg`, or anywhere else — it is unspecified.
- Environment variables. The engine reads `FISHWRAP_CONFIG` internally; `entrypoint.sh` sets it for you when you use `fishwrap-build --config <path>`. Other environment variables are implementation detail.
- Anything outside `/cfg` and `/output`. The container's filesystem layout is implementation detail.

---

## 3. Outputs — What You Get Back

After `fishwrap-build` completes successfully, `/output` contains the following files at stable paths:

| Path | Format | Stability |
|---|---|---|
| `/output/index.html` | UTF-8 HTML (rendered Jinja2 against your theme) | Stable across patch and minor versions. |
| `/output/transparency_fragment.html` | UTF-8 HTML fragment (the audit/transparency report block) | Stable across patch and minor versions. Designed to be embedded in an "About" or "Methodology" page. |
| `/output/run_sheet.json` | UTF-8 JSON (machine-readable record of the published edition) | Stable across patch and minor versions. The schema may grow (additive fields), never shrink. |
| `/output/edition.pdf` | PDF | **Currently not produced** in v2.0.x. PDF generation is out of scope until a future release; configs may declare `LATEST_PDF_FILE` but the file will not be written. Setting the path is harmless. |

### What is **not** part of the output contract

- Exact byte counts of any output file. Output content varies based on input feeds, scoring, and timestamps.
- Filesystem permissions of output files (consumers should not depend on specific ownership beyond "writable by the user that ran the container").
- Order of fields within `run_sheet.json` (treat as an unordered JSON object).
- Side-effect files inside `/cfg` (e.g., the engine writes the SQLite newsroom database alongside the config if the config's `DATABASE_URL` resolves there). State persistence is implementation detail; the only durable artifact is what lands in `/output`.

---

## 4. Invocation — How You Run It

The image exposes four documented invocations.

### `fishwrap-build --config <path>`

Runs the full editorial pipeline (fetch → edit → enhance → print) against the config at `<path>`.

```bash
podman run --rm \
    -v $(pwd)/my-config-dir:/cfg \
    -v $(pwd)/my-output-dir:/output \
    ghcr.io/maxspevack/fishwrap:v2.0.0 \
    fishwrap-build --config /cfg/config.py
```

Exit codes:

| Code | Meaning |
|---|---|
| 0 | Pipeline completed; outputs produced. |
| 2 | Argument error (missing `--config`, file not found). |
| Non-zero (other) | Engine error. Stderr contains diagnostic detail. |

### `fishwrap-version`

Prints the running image's version to stdout, as a single line, parseable as a semver string. Nothing else — no banner, no whitespace surprises.

```bash
$ podman run --rm ghcr.io/maxspevack/fishwrap:v2.0.0 fishwrap-version
2.0.0
```

This is the **only** supported way to read the version. Do not import the Python package and read `__version__`; the Python module layout is implementation detail.

### `fishwrap-validate-config <path>` *(future feature)*

A config-validation command is planned for a future release (tracked in [#4](https://github.com/maxspevack/fishwrap/issues/4)). It will accept a config file path and exit 0 / 1 based on whether the config matches the schema documented in `docs/CONFIG_SCHEMA.md`. Until that lands, validate config correctness by running `fishwrap-build` against it and observing whether the pipeline completes; bad configs will surface as engine errors at the relevant pipeline stage.

### Generic Python via `--entrypoint python`

For downstream scripts that need to call into the fishwrap library, override the entrypoint. The image's Python interpreter has fishwrap on `PYTHONPATH`.

```bash
podman run --rm \
    --entrypoint python \
    -v $(pwd):/cfg \
    ghcr.io/maxspevack/fishwrap:v2.0.0 \
    /cfg/your-script.py
```

This is how Daily Clamour runs its `publish_about.py` glue script. The library surface inside the image (e.g., `from fishwrap.db.repository import ...`) is **not** part of the public contract — it may change between minor versions. If you find yourself relying on a specific internal API, file an issue: that is a signal we should be exposing a CLI for it instead.

---

## 5. Versioning Policy

Fishwrap follows [Semantic Versioning 2.0.0](https://semver.org/) per [`docs/VERSIONING.md`](VERSIONING.md). For consumers of this image, the policy means:

| Bump type | Example | What changes | What you should do |
|---|---|---|---|
| **Patch** | `v2.0.1` → `v2.0.2` | Bug fixes only. Output is stable on identical input. | Adopt automatically (e.g., via Dependabot PRs that pass CI). |
| **Minor** | `v2.0.x` → `v2.1.0` | New features. Output may change in non-breaking ways (e.g., new fields in `run_sheet.json`, new optional config keys). | Review release notes before adopting. Run your own validation. |
| **Major** | `vX.x.x` → `v(X+1).0.0` | Breaking changes to the image contract: input/output paths, file formats, entrypoints, or invocation. | Read the migration notes. Expect to modify your config, scripts, or CI. |

**Pre-release identifiers** (`-rc1`, `-alpha.1`, `-beta`) are unstable and do not move floating tags. Treat them as preview-only.

---

## 6. Pinning Recommendation

**Pin to exact tags** (e.g., `v2.0.2`), not floating minors (e.g., `v2.0`).

Reasoning:

- The same git SHA in your repo should produce the same deployed image, every time. Floating tags break that property by definition — same source, different image, depending on when CI runs.
- Adopting new patches via reviewed PRs (e.g., from Dependabot) lets you see the upgrade work *before* it hits production, by running your own pipeline against the candidate image as a required check.

Daily Clamour's pinning setup (Dockerfile-tracked pin + Dependabot + production-refresh as required check) is documented in [its own version policy](https://github.com/maxspevack/dailyclamour.com) and is the canonical example.

---

## 7. Stability Guarantees

The following are part of the contract. Changes to any of them require at minimum a minor version bump (or a major bump if the change is breaking):

- The two mount points: `/cfg` and `/output`.
- The invocations described in §4 (`fishwrap-build`, `fishwrap-version`, generic Python entrypoint). `fishwrap-validate-config` is a future addition tracked in [#4](https://github.com/maxspevack/fishwrap/issues/4); when it lands it will be added to this stability list.
- The output file paths and formats described in §3.
- The image's identifier (`ghcr.io/maxspevack/fishwrap`).
- The image running as a non-root user. (UID is currently 1000; the *non-rootness* is contract, the specific UID is implementation detail.)

The following are **not** part of the contract. They may change at any time, including in patch releases, with no notice:

- The base image (`python:3.12-slim` today).
- The Python version (3.12 today).
- The exact list of installed system packages.
- The internal filesystem layout (paths under `/usr`, `/opt`, `/app`, etc.).
- The `__version__` attribute on the `fishwrap` Python package — use `fishwrap-version` instead.
- The internal Python module layout (`fishwrap.fetcher`, `fishwrap.db.models`, etc.).
- The image size, layer structure, or build cache topology.
- The exact entropy of timestamps, run IDs, or other monotonic fields in output files.

---

## 8. Canonical Consumer Template

[Daily Clamour](https://github.com/maxspevack/dailyclamour.com) is the reference implementation for "consume fishwrap as an image." It demonstrates:

- Pinning the image version in a `Dockerfile` so Dependabot can track upgrades.
- Mounting a config directory at `/cfg` and an output directory at `/output`.
- Running `fishwrap-build` from GitHub Actions on a daily cron.
- Capturing `fishwrap-version` for downstream metadata injection (no Python imports of fishwrap).
- Output validation as a deploy gate.
- Secrets travel via GitHub Actions secrets, written to a temp file and mounted at `/cfg/secrets.json`.

To start your own fishwrap-powered publication, fork the Daily Clamour repository and replace the config, theme, and content. You should not need to read fishwrap source code at any point.

---

## 9. Cross-References

- [ADR-001 — Release Artifact Contract](adr/001-release-artifact.md) — internal decision record this contract derives from
- [`docs/VERSIONING.md`](VERSIONING.md) — SemVer policy
- [`docs/CONFIG_SCHEMA.md`](CONFIG_SCHEMA.md) — full config schema (companion document)
- [`docs/RELEASING.md`](RELEASING.md) — release process used to produce these images
- [Daily Clamour](https://github.com/maxspevack/dailyclamour.com) — canonical consumer
- [GitHub Releases](https://github.com/maxspevack/fishwrap/releases) — release notes for each version
