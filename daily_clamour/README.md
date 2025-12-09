# The Daily Clamour 🗞️

This directory contains the production configuration and assets for [dailyclamour.com](https://dailyclamour.com).

## Overview

*   **Theme:** "Vintage Clamour" (Cream paper, Sepia ink, "Scoop" mascot).
*   **Feeds:** Highly curated list of Tech, Sports, and News (see `config.py`).
*   **Policies:** Specific boosts for "Defector", "NFL", and high-signal tech blogs.

## Deployment

The site is published via `auto_publish.sh` (located in the repo root or user home), which:
1.  Runs `make run-clamour`.
2.  Commits the generated `daily_clamour/output/latest.html` to the `gh-pages` branch.
3.  Pushes to GitHub.

## Local Development

To test changes to the Vintage theme or editorial scoring:

```bash
cd ..
make run-clamour
open daily_clamour/output/latest.html
```
