---
layout: default
title: The Glass Box (Architecture)
nav_order: 3
---

# Inside the Glass Box

Fishwrap is designed to be auditable. Unlike proprietary feeds that hide their ranking logic, Fishwrap exposes every decision the engine makes.

## The Core Pipeline

The engine runs in four stateless stages:

1.  **Fetcher:** Collects raw items from RSS, JSON, or Reddit feeds.
2.  **Editor:** Classifies items into sections and calculates an **Impact Score**.
3.  **Enhancer:** Scrapes the full text and metadata for selected items.
4.  **Printer:** Generates the final artifact (HTML/PDF).

## Auditability: The "Why"

Every article in a Fishwrap edition includes a debug trace (visible in the "Fishbowl" UI or raw JSON logs) that explains its score.

### The Scoring Formula
The logic is defined in `scoring.py`. It is not a machine learning black box; it is a linear algebraic formula you can tune.

```python
Final Score = (Stats Score * Weight) + (Boosts * Unit Value)
```

*   **Stats Score:** Derived from raw metrics (upvotes, comments, velocity).
*   **Boosts:** Editorial policies you define (e.g., "Boost `github.com` by 10 units", "Penalty `marketing` by -20 units").

### Dynamic Verticalization
The **Editor** (`editor.py`) is vertical-agnostic. It does not hardcode "News" or "Sports."
Instead, it reads your `config.py` to define:
*   **Sections:** (e.g., "Zero-Days", "Research", "Gossip")
*   **Keywords:** (e.g., "CVE-", "Arxiv", "Spoiler")

This allows Fishwrap to transform from a **General News** reader into a **Cybersecurity Threat Briefing** or an **AI Research Assistant** simply by swapping the configuration file.

## Data Transparency

Fishwrap stores its state in simple JSON files in the `data/` directory:
*   `articles_db.json`: The complete history of every item seen.
*   `run_sheet.json`: The "Editorial Decisions" for the current edition.
*   `enhanced_issue.json`: The full content ready for printing.

You can inspect these files at any time to see exactly what the engine "knows."
