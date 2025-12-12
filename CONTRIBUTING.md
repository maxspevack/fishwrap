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

## How to Contribute

### 1. Adding Feeds (The Daily Clamour)
If you want to suggest a source for the flagship [Daily Clamour](https://dailyclamour.com) instance, please open an Issue with the tag `[Source Request]`.
*   Provide the RSS URL.
*   Suggest the appropriate Section (News, Tech, Sports, Culture).

### 2. Engineering
We are currently focused on **Phase 1 (Observability)**.
*   **Good First Issues:**
    *   Adding logging metrics to `fetcher.py`.
    *   Writing unit tests for `scoring.py`.
    *   Improving the PDF CSS layout.

### 3. Code Style
*   We use Python 3.12+.
*   We prioritize **readability** over cleverness.
*   **The Glass Box Rule:** If logic is hidden or "magical," it's wrong. Expose it.

## The Philosophy
We are building the "Anti-Feed."
*   **Finite > Infinite:** We build ends, not scrolls.
*   **Transparent > Opaque:** We explain scores, we don't hide them.
*   **User > Algo:** The user is the Editor-in-Chief.
