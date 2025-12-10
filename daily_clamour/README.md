# The Daily Clamour 🗞️

This directory contains the production configuration and assets for [dailyclamour.com](https://dailyclamour.com).

## Overview

*   **Theme:** "Vintage Clamour" (Cream paper, Sepia ink, "Scoop" mascot).
*   **Feeds:** Highly curated list of Tech, Sports, and News (see `config.py`).
*   **Policies:** Specific boosts for "Defector", "NFL", and high-signal tech blogs.

## Automation

The Daily Clamour runs automatically 4 times a day via a macOS `launchd` service (`com.maxspevack.gemini.gazette`):

*   **Schedule:** 7:00 AM, 12:00 PM, 5:00 PM, 10:00 PM.
*   **Script:** `fishwrap/daily_clamour/deploy.sh` (symlinked to `~/gemini_publish.sh`).

This script runs the full `make run-clamour` pipeline and handles the git-push to the `gh-pages` branch.

## Deployment

The site is published via `deploy.sh`, which:
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
