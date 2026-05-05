# ADR-001: Release Artifact Contract

**Status:** Accepted
**Date:** 2026-05-05
**Milestone:** [v2.0 — Image-Based Pipeline & DC Cutover](https://github.com/maxspevack/fishwrap/milestone/1)

## Context

Today, a fishwrap release is a git tag with nothing shippable attached. Downstream consumers — most notably [Daily Clamour](https://github.com/maxspevack/dailyclamour.com) — clone `fishwrap.git`, check out a tag into `vendor/fishwrap`, run the engine's own venv install, and invoke Python modules directly. The contract is held together by convention: install scripts, Python module names, the existence of a `__version__` attribute on the package, filesystem layout assumptions. Six implicit contracts pretending to be one.

For fishwrap to be consumable by anyone other than its author, the contract must be explicit, documented, and stable. This ADR establishes what a fishwrap release *is* and what guarantees it makes to downstream consumers. It is the foundation that the rest of milestone v2.0 builds on.

This is the first ADR in the project. Future significant architectural decisions follow the same numbered-record pattern — see [`docs/adr/`](.).

## Decision

A fishwrap release is a signed, multi-arch OCI container image, published to GHCR, with documented inputs, outputs, and CLI entrypoints. Eight components:

### 1. Artifact format

OCI container image, published to `ghcr.io/maxspevack/fishwrap`. The image *is* the release; git tags exist to identify image builds, not as standalone artifacts.

### 2. Architectures

Multi-arch manifest covering `linux/amd64` and `linux/arm64`.

### 3. Image surface (entrypoints)

Four documented invocations:

- `fishwrap-build --config /cfg/config.py` — runs the full pipeline (fetcher → editor → enhancer → printer).
- `fishwrap-version` — prints the running version's semver string to stdout. **Stable contract:** stdout is always parseable as a semver string. Consumers must use this rather than `import fishwrap` to read version metadata.
- `fishwrap-validate-config /cfg/config.py` — validates a config against the documented schema; exits non-zero on schema violation with a human-readable error.
- Generic `python` (via `--entrypoint python`) — for downstream scripts that need the fishwrap library; e.g., Daily Clamour's `publish_about.py`.

### 4. Inputs (mount points)

- `/cfg` — config directory. The engine looks for `/cfg/config.py` by default.
- `/cfg/secrets.json` — optional auth/cookie file. Absent is fine; the engine operates in degraded mode for sources that require authentication.
- `/output` — output write target.

### 5. Outputs (stable paths)

- `/output/index.html` — rendered edition.
- `/output/transparency_fragment.html` — for downstream "About"-page composition.
- `/output/run_sheet.json` — machine-readable run record.
- `/output/edition.pdf` — present when PDF generation is enabled in the config.

These paths are part of the contract. Consumers can rely on them across patch and minor versions.

### 6. State model

The newsroom SQLite database is **ephemeral** in CI environments. No cache restore between runs. The once-daily refresh cadence makes cache restoration not worth its bug surface.

Local development can persist `data/` if the operator wants smart-build behavior; that is outside the consumer contract.

### 7. Versioning policy

Per [`docs/VERSIONING.md`](../VERSIONING.md):

- **Patch** (`v2.0.x`): bug fixes; output-stable on identical input; additive only.
- **Minor** (`v2.x.0`): new features; output may differ in non-breaking ways.
- **Major** (`vX.0.0`): breaking changes to image surface, output paths, or output formats.

This ADR establishes `v2.0.0` as the first release under the new contract. The bump from `v1.3.3` → `v2.0.0` is justified per `docs/VERSIONING.md`'s MAJOR criteria: a fundamental architectural shift in how the engine is consumed (release artifact moves from "git tag + clone-and-install" to "signed OCI image + `docker run`") that requires downstream consumers to modify their code and configurations to upgrade. [Daily Clamour's seven-issue cutover](https://github.com/maxspevack/dailyclamour.com/milestone/1) is direct evidence that the change is consumer-breaking and therefore MAJOR.

### 8. Tag publishing

Every stable release publishes both:

- The exact tag (e.g., `v2.0.2`).
- The floating minor (e.g., `v2.0`) — republished on every patch within that minor line.

Pre-release tags (`-rc1`, `-alpha.1`, etc.) publish only the exact tag; they do not update floating tags.

The recommended consumer pinning policy (exact tag, with bumps via reviewed PRs) lives in the consumer-facing [`docs/IMAGE_CONTRACT.md`](../IMAGE_CONTRACT.md) (issue [#3](https://github.com/maxspevack/fishwrap/issues/3)). This ADR records what the project *publishes*; that document records what consumers should *pin to*.

## Consequences

**Positive**

- **Reproducibility.** The artifact is dependency-frozen at build time. Same image SHA → same behavior, indefinitely.
- **Provenance.** GHCR + GitHub Actions provides SLSA-Level-3 build attestations and CycloneDX SBOMs as side effects of the publish workflow (issue [#5](https://github.com/maxspevack/fishwrap/issues/5)).
- **Boundary.** Downstream consumers depend only on the documented contract — not on Python module layout, install-script behavior, or filesystem conventions.
- **Marketability.** Third parties can pull, configure, and run fishwrap without reading fishwrap source. This is the precondition for fishwrap being a *product* rather than a private tool with a downstream.

**Negative**

- **Migration cost.** Existing downstream consumers must rewrite their integration. Daily Clamour's cutover is non-trivial — see [milestone v2.0](https://github.com/maxspevack/dailyclamour.com/milestone/1).
- **Release-critical CI.** Image-build CI is now release-critical infrastructure. A broken release workflow blocks releases entirely. Mitigated by issue [#6](https://github.com/maxspevack/fishwrap/issues/6) (PR-time build verification catches regressions before tag time).
- **Registry dependency.** GHCR availability is now a fishwrap dependency. Low risk, worth naming.

**Neutral**

- The Python package remains importable from source for contributors and developers. The development workflow is unchanged.
- The existing `docs/VERSIONING.md` SemVer policy is preserved unchanged. This ADR cites it rather than amending it.

## References

- [`docs/VERSIONING.md`](../VERSIONING.md) — SemVer policy
- [`docs/IMAGE_CONTRACT.md`](../IMAGE_CONTRACT.md) — consumer-facing contract document (issue [#3](https://github.com/maxspevack/fishwrap/issues/3), pending)
- [Milestone v2.0 — Image-Based Pipeline & DC Cutover](https://github.com/maxspevack/fishwrap/milestone/1)
- [Daily Clamour cutover milestone](https://github.com/maxspevack/dailyclamour.com/milestone/1)
- Michael Nygard, ["Documenting Architecture Decisions"](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) (2011) — the original ADR proposal
