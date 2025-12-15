# Contributing to Fishwrap 🐟

Welcome to the newsroom! Fishwrap is an open-source "Glass Box" news engine. We value transparency, code quality, and the "Anti-Feed" philosophy.

## Getting Started

1.  **Clone & Install:**
    ```bash
    git clone https://github.com/maxspevack/fishwrap.git
    cd fishwrap
    make setup
    ```
2.  **Run a Demo:**
    ```bash
    make run-vanilla
    ```
    This builds the default edition in `demo/output/`.

3.  **Run Tests:**
    ```bash
    make test
    ```
    Always run the test suite before submitting a PR.

## Engineering Standards

### 1. Architecture
*   **Modules:** Keep `fetcher`, `editor`, `auditor`, and `printer` decoupled.
*   **State:** The SQLite database (`newsroom.db`) is the single source of truth for history.
*   **No Magic:** We prefer explicit logic over implicit framework magic. Use `Makefile` for tasks.

### 2. Code Style
*   **Python:** We target modern Python (3.12+).
*   **Dependencies:** Keep `requirements.txt` minimal. No compiled extensions unless absolutely necessary (to avoid build hell).
*   **The Glass Box Rule:** If logic is hidden, it's wrong. Expose scores and decisions in the Audit Log.

### 3. Release Process
If you are a maintainer, please refer to the [**Release Runbook**](docs/RELEASING.md) before cutting a new version. We use a strict automated pipeline (`scripts/release.sh`) to ensure hygiene.

## The Philosophy
We are building the "Anti-Feed."
*   **Finite > Infinite:** We build ends, not scrolls.
*   **Transparent > Opaque:** We explain scores, we don't hide them.
*   **User > Algo:** The user is the Editor-in-Chief.