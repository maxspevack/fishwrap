# Release Runbook

This document describes the process for cutting a new stable release of the Fishwrap Engine (`fishwrap`).

**Objective:** To tag a clean, tested version that downstream consumers (like `dailyclamour.com`) can pin to.

---

## 1. The Pre-Flight Check

Before you release, ensure:
*   The `main` branch is clean.
*   You have documented the changes in `docs/RELEASE_NOTES.md`.

### Writing Release Notes
Edit `docs/RELEASE_NOTES.md`. Add a new section at the top:

```markdown
## vX.Y.Z (Codename) - YYYY-MM-DD

Summary of the release...

### 🚀 New Features
*   ...
```

**Do not** include the Commit Hash yet. The tag itself is the source of truth.

---

## 2. The Release Script

We use an automated script to enforce hygiene. This script will:
1.  Update `fishwrap/__init__.py`.
2.  Wipe the `venv` and rebuild it from scratch (`make clean-all && make setup`).
3.  Run the pipeline (`make run-vanilla`) to prove it works.
4.  Commit, Tag, and Push.

**Command:**
```bash
./scripts/release.sh <version> "<codename>"
```

**Example:**
```bash
./scripts/release.sh 1.4.0 "The Velocity Update"
```

If the smoke test fails, the script aborts before tagging.

---

## 3. Downstream Deployment (Daily Clamour)

Once the tag is live on GitHub, update the production site.

1.  Go to the product repo:
    ```bash
    cd ../dailyclamour.com
    ```
2.  Install the new stable engine:
    ```bash
    make install-stable VERSION=v1.4.0
    ```
3.  Deploy:
    ```bash
    make deploy
    ```

---

## 4. Hotfixes & YOLO Mode

If you need to ship a critical fix *right now* without a tag:

1.  **YOLO Mode:**
    ```bash
    cd dailyclamour.com
    make install-yolo  # Symlinks to your local dev repo
    make deploy
    ```
    *Warning:* This deploys whatever dirty state is on your laptop. Use with caution.

2.  **To Return to Stable:**
    ```bash
    make install-stable VERSION=v1.4.0
    ```
