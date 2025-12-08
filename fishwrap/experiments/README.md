# Experiments & Investigations

This directory contains temporary scripts and one-off investigations to help tune the "Daily Clamour" algorithms.

## Scripts

### `hn_analysis.py`
Fetches top stories from Hacker News (via Algolia) for the last 14 days and simulates different scoring algorithms.
Use this to determine the optimal weights for `score` vs `comments` to normalize HN against Reddit.

**Usage:**
```bash
python3 -m press.experiments.hn_analysis
```
