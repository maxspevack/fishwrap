# Fishwrap Architecture & Security Standards 🛡️

**Version:** 1.0 (Draft)
**Status:** Approved for Phase 1.5 Implementation
**Authority:** The "Paranoid Principal Engineer" Persona

---

## 1. The "No Raw SQL" Mandate (Injection & Portability)
*   **Risk:** SQL Injection attacks and "Vendor Lock-in" (rewriting SQL when moving from SQLite to Postgres).
*   **The Rule:** **Zero raw SQL strings.** All database interactions must go through an Object Relational Mapper (ORM) or Query Builder.
*   **The Stack:** **SQLAlchemy (Core + ORM)**.
*   **Enforcement:**
    *   Use `model.query()` or `select(Table)`.
    *   Never concatenate strings into a query (`f"SELECT * FROM users WHERE name = '{name}'"` is an automatic PR rejection).

## 2. The "Schema as Code" Pact (Integrity)
*   **Risk:** "It works on my machine" because your local DB has a column that the server is missing.
*   **The Rule:** The Database file is **NOT** the source of truth. The Code is.
*   **The Stack:** **Alembic**.
*   **Enforcement:**
    *   All schema changes must be version-controlled Migration Scripts.
    *   Never modify the SQLite file manually (e.g., using a GUI tool) to fix a bug. Write a migration.

## 3. Identity & Keys (Scalability)
*   **Risk:** Integer IDs (1, 2, 3) collide when merging databases or sharding. They also leak volume information.
*   **The Rule:** **UUIDs everywhere.**
*   **Enforcement:** Primary Keys are `UUIDv4` (stored as String or Binary, depending on DB).

## 4. The "12-Factor" Config (Secret Management)
*   **Risk:** Committing API keys to GitHub.
*   **The Rule:** Config is strictly separated from Code.
*   **The Stack:** **Pydantic Settings** (or equivalent env var loader).
*   **Enforcement:**
    *   Priority: Env Vars > `secrets.json` > Defaults.
    *   `secrets.json` MUST be in `.gitignore`.
    *   **GCP Alignment:** Compatible with Google Secret Manager injection.

## 5. The "Append-Only" Almanac (Data Safety)
*   **Risk:** Accidental deletion or corruption of history.
*   **The Rule:** The `chronicle.db` (Almanac) is effectively **WORM** (Write Once, Read Many).
*   **Enforcement:**
    *   The "Janitor" process (deletion) is strictly forbidden from touching the Chronicle. It only cleans the Buffer.
    *   Deletes in the Chronicle are "Soft Deletes" (`deleted_at` timestamp), never physical row removals.

## 6. Dependency Supply Chain (Phase 2 Requirement)
*   **Status:** DEFERRED until Cloud Migration.
*   **Risk:** Installing a malicious PyPI package.
*   **The Rule:** Deterministic Builds.
*   **Future Enforcement:** Move to `requirements.lock` with hash verification when Dockerizing.

---

## ☁️ The Cloud Path (Google Cloud Platform)

This architecture is designed to map directly to GCP services in Phase 2:

1.  **Compute:** **Cloud Run** (Serverless Containers). Stateless execution.
2.  **Database:** **Cloud SQL** (PostgreSQL). We simply swap the SQLAlchemy connection string.
3.  **Storage:** **Google Cloud Storage (GCS)**. Artifacts (HTML/PDF) are pushed to buckets, not local disk.
4.  **Secrets:** **Secret Manager**. Mapped to Environment Variables.
