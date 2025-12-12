# Fishwrap Strategy & Vision 🔭

**Last Updated:** December 12, 2025
**Status:** Living Document

---

## 1. The Core Philosophy: "The Glass Box"

Fishwrap is not just a news aggregator; it is a **Trust Engine**.
In an era of algorithmic opacity, our differentiator is **Radical Transparency**. We don't just show you the news; we show you *why* it's the news.

### The "Show Your Work" Promise
Every edition of a Fishwrap publication (like *The Daily Clamour*) must be accompanied by a user-visible **Transparency Report**.
*   **Input:** What did we see? (e.g., "1,500 stories scanned")
*   **Process:** How did we filter it? (e.g., "Keyword 'AI' boosted score by 20%")
*   **Output:** Why did this win? (e.g., "Score: 9800 - High Velocity + Trusted Source")

---

## 2. The "Moneyball" Metrics (Source Intelligence)

We are building a **Source Performance Index**. By tracking the "funnel" of content over time, we generate a second layer of value: **Meta-News**.

### The Pipeline Funnel
We track a source's journey through four stages:
1.  **Input:** Raw volume (Feed Dominance).
2.  **Classification:** Relevance to specific topics (Pool Dominance).
3.  **Scoring:** Quality/Impact (Qualified Dominance).
4.  **Selection:** Final Cut (Run Sheet Dominance).

### Key Performance Indicators (KPIs)
*   **Batting Average (Yield):** `(Selected / Fetched) %`. High yield = High Signal/Noise ratio.
*   **Impact Factor:** Average score of selected articles.
*   **Versatility:** Breadth of sections covered.
*   **Consistency:** Variance in scoring over time.

---

## 3. The "Performance Engine" (Enterprise Pivot)

The underlying engine (Source -> Scorer -> Selector -> Report) is abstract. It applies to **any** stream of high-volume event data.

### Use Case: The Corporate "Daily Clamour"
*   **Sources:** GitHub Commits, Jira Tickets, Slack Channels, PagerDuty Alerts.
*   **Scoring:** Impact on ship date, severity of bug, executive visibility.
*   **Product:** "The Daily Standup" (A generated newspaper of what actually mattered yesterday).

### Use Case: Automated Performance Reviews
*   **Metric:** Track an employee's "Batting Average" (Merged PRs / Open PRs).
*   **Metric:** Track "Impact Factor" (Severity of bugs fixed).
*   **Result:** A pre-written, data-backed performance narrative.

---

## 4. Immediate Engineering Roadmap (Phase 1.5)

To realize this, we must move from "Console Logging" to **Structured Auditing**.

### The "Auditor" Module (`fishwrap.auditor`)
A dedicated component responsible for:
1.  **Funnel Calculation:** Computing the input/output ratios per run.
2.  **Persistence:** Saving `run_stats.json` for historical trend analysis.
3.  **Rendering:** Generating the public `transparency.html` artifact.

### The "Natural Cut-Line"
*   **Goal:** Move away from artificial `EDITION_SIZE` (e.g., "Top 10").
*   **Method:** Analyze score distributions to find the "knee in the curve"—the natural drop-off point where quality significantly degrades.
