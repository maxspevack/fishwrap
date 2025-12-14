---
layout: default
title: Vol 5. The Release
parent: The Architect's Log
nav_order: 5
---

# Vol 5. The Release
## Stabilizing the Press: A Case Study in Release Engineering

**Date:** December 13, 2025

Today, we faced a crisis. Fishwrap, the engine powering the Daily Clamour, had become unstable. We were deploying "v1.2.x" tags rapidly, trying to hotfix a build issue caused by a Python 3.14 incompatibility. We were editing Makefiles in production. We were tired.

We realized that our problem wasn't code; it was **Process**.

## The Split Brain

Fishwrap uses a **Federated Architecture**:
*   **The Engine (`fishwrap`):** The core logic. Ideally stable, versioned, and boring.
*   **The Product (`dailyclamour.com`):** The implementation. Branded, customized, and deployed daily.

The Product installs the Engine as a dependency. But we were treating the Engine like a local library, constantly "reaching across" the repository boundary to fix bugs. This created a Split Brain: The engine code on my laptop worked, but the engine code in the production build environment failed.

## The Solution: Strict Hygiene

We stopped coding and started engineering. We implemented three key protocols to stabilize the platform.

### 1. The "Runbook"
We wrote a [Release Runbook](../RELEASING.md). It dictates that you cannot tag a release until you have passed a "Smoke Test" in a clean environment. We built automation (`release.sh`) to enforce this. If the tests don't pass, the tag is rejected.

### 2. Forward Compatibility (The Time Travel Problem)
We wanted to add a "Publication Timestamp" to the sidebar.
*   **Engine:** Needs to calculate the time.
*   **Theme:** Needs to display it.

If we updated the Theme first, it would be buggy (missing variable). If we updated the Engine first, the timestamp would be invisible.
We adopted a **Forward Compatibility** policy: The Theme checks `{% raw %}{% if time_str %}{% endraw %}`. This allows us to deploy the Theme change *today*, and have the feature "light up" automatically when the Engine is upgraded next week.

### 3. Smart Builds (Makefiles are DAGs)
We realized we were re-fetching RSS feeds (expensive!) just to fix a CSS padding issue.
We rewrote our build system to be a **Dependency Graph**.
*   If `config.py` changes -> Re-run Fetcher.
*   If `style.css` changes -> Re-run Printer (Instant).

## The Result: v1.3.2

We shipped **Fishwrap v1.3.2**. It is clean. It is tested. It has a shiny new "Glass Box" UI.
And most importantly, we shipped it without touching the production server manually.

We moved from "It works on my machine" to "It works."