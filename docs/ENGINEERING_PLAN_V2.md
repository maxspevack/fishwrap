# Fishwrap Engineering Plan (v2.0) 🏗️

**Date:** December 12, 2025
**Status:** Approved for Implementation
**Goal:** Transition from "MVP Script" to "Scalable Platform".

---

## 1. The Core Shift: "The Dawn Edition"
*   **Schedule:** Once Daily at 04:00 AM (Local Time).
*   **Philosophy:** Scarcity drives quality. A single, definitive record of the day's news.
*   **Impact:** Simplifies Volume/Issue logic (1 Day = 1 Issue). Eliminates "intra-day drift."

---

## 2. Data Architecture: "Buffer & Chronicle"
We move from a single JSON file to a **Federated SQLite** architecture.

### A. `newsroom.db` (The Buffer)
*   **Purpose:** The high-velocity working memory.
*   **Contents:** Raw feed intake, current processing queue.
*   **Lifecycle:** **Ephemeral.** Data flows in from feeds and is flushed after ~72 hours.
*   **Technology:** SQLite (Phase 1.5) $\to$ Cloud SQL (Phase 2).

### B. `almanac.db` (The Chronicle)
*   **Purpose:** The permanent historical record.
*   **Contents:**
    *   **The Artifacts:** Full text/metadata of every article *published* in a Run Sheet.
    *   **The Intelligence:** Source performance stats (Yield, Impact, Consistency).
    *   **The Audit Trail:** Run logs and scoring breakdowns.
*   **Lifecycle:** **Permanent (WORM).** We append to this; we rarely delete.
*   **Technology:** SQLite (Phase 1.5) $\to$ Cloud SQL (Phase 2).

---

## 3. The "Auditor" Module (Phase 1.5)
A new component that runs *after* the Editor and *before* the Printer.

*   **Role:** The Accountant.
*   **Responsibilities:**
    1.  **Funnel Analysis:** Calculate Input $\to$ Pool $\to$ Qualified $\to$ Selected ratios.
    2.  **Stat Persistence:** Write daily stats to `almanac.db`.
    3.  **Transparency:** Generate `transparency.html` for the user.
*   **Impact:** Transforms "console logs" into a usable product feature.

---

## 4. Cloud Migration Strategy (Phase 2)
We break the "Laptop Ceiling" by moving to Google Cloud Platform (GCP).

### The Stack
*   **Compute:** **Cloud Run**. Stateless containers. Scales to zero.
*   **Database:** **Cloud SQL (PostgreSQL)**. We swap SQLite for Postgres.
*   **Storage:** **Google Cloud Storage (GCS)**. Hosting the generated HTML/PDFs.
*   **Secrets:** **Google Secret Manager**.

### The "Cloud-Ready" Standards
To ensure this move is painless, we adhere to `docs/ARCHITECTURE_STANDARDS.md`:
1.  **No Raw SQL:** Use SQLAlchemy ORM.
2.  **Schema as Code:** Use Alembic Migrations.
3.  **UUIDs:** Use UUIDv4 for Primary Keys.
4.  **12-Factor Config:** Secrets via Environment Variables.

---

## 5. Immediate Next Steps (The Checklist)

1.  **Scaffold the DB Layer:**
    *   Set up `fishwrap/db/` with SQLAlchemy and Alembic.
    *   Define models for `Article`, `Source`, `Run`.
2.  **Build the Migrator:**
    *   Script to ingest `articles_db.json` into the new SQLite schema.
3.  **Implement the Auditor:**
    *   Build the logic to populate the `Run` stats table.
4.  **Wire it Up:**
    *   Update Fetcher/Editor to use the DB layer instead of JSON.

---

**Signed:** The Engineering Team
