<div align="center">
  <img src="docs/static/images/fishwrap_logo.svg" alt="Fishwrap" width="400">
  <br>
  <b>The algorithm you can read. The feed that ends.</b>
</div>

<br>

Fishwrap is the engine for the morning paper. RSS feeds, Reddit threads, and Hacker News go in. One edition of HTML comes out. Then it stops. Every editorial decision is recorded in an audit log the reader can open.

The engine is a signed OCI image at `ghcr.io/maxspevack/fishwrap`. A publication is a config file and a theme. [Daily Clamour](https://dailyclamour.com) is the worked example; everything else is yours.

**One edition is live. One reference demo runs alongside it:**
*   [The Daily Clamour](https://dailyclamour.com). The flagship instance. One edition a day at 04:00 Pacific.
*   [The Vanilla](https://fishwrap.org/demo/vanilla/). The reference demo, rebuilt every day from the `main` branch. This is the engine's integration environment, not a release.

---

## Quickstart

You need Docker or Podman.

```bash
git clone https://github.com/maxspevack/fishwrap.git
cd fishwrap
mkdir -p output
docker run --rm \
    -v $(pwd)/demo:/cfg \
    -v $(pwd)/output:/output \
    ghcr.io/maxspevack/fishwrap:2.0 \
    fishwrap-build --config /cfg/config.py
```

The rendered edition lands at `output/index.html`. Open it.

The full consumer contract (every input, every output path, every CLI surface, the versioning policy, the pinning recommendation) is in [`docs/IMAGE_CONTRACT.md`](docs/IMAGE_CONTRACT.md).

---

## The Glass Box

The Glass Box is what we call the working surfaces. Every editorial decision is named and logged. The reader can open the log.

*   **The Fetcher** scours your defined feeds (RSS, JSON, Reddit) using concurrent I/O. Failed feeds are logged, not hidden.
*   **The Editor** classifies each article into a section (by source-default or keyword fallback), folds duplicates into the newest copy and counts how many sources carried the story, applies the diversity cap per source per section, truncates to the section's edition size, and assigns each item a tier (lead / feature / standard). The signed policies in your masthead can drop articles (source/title/topic bans), bypass diversity caps (whitelist), or promote stories to the lead tier (section_lead_preference) — every policy that fires is named on the story. It writes **the runsheet**: one record per candidate (where it came from, how it competed, where it landed) plus a header naming the engine commit, the window, and the fingerprints of your three editorial files. Nothing downstream recomputes a decision.
*   **The Enhancer** scrapes full text for the stories that made the paper. Rate-limited.
*   **The Printer** renders from the runsheet alone: the paper with a per-story audit drawer, the runsheet as a readable page (what came in, what was cut and why, what led and why, every feed's yield), a read-only feeds page, and The Morgue (every prior version of your masthead, dossier, and policies).
*   **Replay** re-runs any archived runsheet's candidates under your masthead as it is now and prints what moved. Change a dial, replay yesterday, read the consequence. `make replay DATE=YYYY-MM-DD`.

The user-facing config is two files: `masthead.toml` (the structured data: sections, feeds, source-section routing, signed policies) and `dossier.md` (the editor's voice in prose — read by the LLM editor in Editor mode). The same data drives both modes.

Behind the scenes is a SQLite "Newsroom" database that stores the article corpus during a run. In containerized contexts the database is ephemeral; every run starts fresh.

---

## Run your own

Fishwrap is the engine. A publication is the config and the theme. Fork [Daily Clamour](https://github.com/maxspevack/dailyclamour.com), replace the config and the theme, and you have your own paper.

The two contracts that govern a fork:

1. [`docs/IMAGE_CONTRACT.md`](docs/IMAGE_CONTRACT.md). What the image expects and produces.
2. [`docs/CONFIG_SCHEMA.md`](docs/CONFIG_SCHEMA.md). Every key the engine recognizes.

---

## Repository structure

*   `fishwrap/`. The stateless engine.
*   `demo/`. The reference configuration (`config.py`) and the `basic` theme.
*   `docs/`. The source for [fishwrap.org](https://fishwrap.org), plus the consumer contract, ADRs, schema reference, and release notes.
*   `Dockerfile`. The release artifact recipe.
*   `.github/workflows/`. Release and demo refresh workflows.

---

## Documentation

| | |
|---|---|
| [Brand Bible](docs/BRAND.md) | The voice and visual standard the rest of the corpus answers to |
| [Image Contract](docs/IMAGE_CONTRACT.md) | Public contract for image consumers |
| [Config Schema](docs/CONFIG_SCHEMA.md) | Every key the engine recognizes |
| [Release Notes](docs/RELEASE_NOTES.md) | Version history |
| [Releasing](docs/RELEASING.md) | Runbook for cutting new versions |
| [Architecture Decisions](docs/adr/) | ADRs for significant decisions |
| [Versioning Policy](docs/VERSIONING.md) | What patch / minor / major mean |

---

## Roadmap

The roadmap lives in GitHub. There is no separate roadmap document.

| | |
|---|---|
| [Issues](https://github.com/maxspevack/fishwrap/issues) | Everything open, in progress, and recently closed |
| [Milestones](https://github.com/maxspevack/fishwrap/milestones) | Versioned groupings of issues currently being worked on |

---

## License

Apache License 2.0.
