# Contributing to Fishwrap 🐟

Welcome to the newsroom! Fishwrap is an open-source Glass-Box news engine. This guide is for **engine contributors** — people changing how fishwrap itself works.

If you're instead trying to **consume fishwrap to publish your own news page**, you don't need this guide. Read [`docs/IMAGE_CONTRACT.md`](docs/IMAGE_CONTRACT.md) and fork [Daily Clamour](https://github.com/maxspevack/dailyclamour.com) instead.

## Getting Started (Engine Development)

1.  **Clone and set up a development venv:**
    ```bash
    git clone https://github.com/maxspevack/fishwrap.git
    cd fishwrap
    make setup
    ```

2.  **Run a demo locally:**
    ```bash
    make run-vanilla
    ```
    This builds the default edition in `demo/output/`.

3.  **Run tests:**
    ```bash
    make test
    ```
    Always run the test suite before pushing changes that touch engine code.

## Engineering Standards

### 1. Architecture
*   **Modules:** Keep `fetcher`, `editor`, `auditor`, and `printer` decoupled.
*   **State:** The SQLite database (`newsroom.db`) is the single source of truth for history *during a single run*. In containerized contexts the database is ephemeral.
*   **No Magic:** Prefer explicit logic over implicit framework magic. Use `Makefile` for tasks.
*   **Decisions:** Significant architectural decisions are recorded as ADRs in [`docs/adr/`](docs/adr/). Read them to understand *why* fishwrap is structured the way it is. Start with [ADR-001 — Release Artifact Contract](docs/adr/001-release-artifact.md).

### 2. Code Style
*   **Python:** Target Python 3.12+.
*   **Dependencies:** Keep `requirements.txt` minimal. No compiled extensions unless absolutely necessary (avoid build hell).
*   **The Glass Box Rule:** If logic is hidden, it's wrong. Expose scores and decisions in the audit log.

### 3. Release Process
If you are a maintainer cutting a new version, see [**`docs/RELEASING.md`**](docs/RELEASING.md).

## The Philosophy
*   **Finite > Infinite:** We build ends, not scrolls.
*   **Transparent > Opaque:** We explain scores, we don't hide them.
*   **User > Algo:** The user is the editor-in-chief.
