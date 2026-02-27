#!/usr/bin/env bash

# Smoke Test for fw-db utility
# Ensures it can load a config and query the database without crashing.

set -e # Exit on error

REPO_ROOT="$(dirname "$0")/.."
cd "$REPO_ROOT"

echo "[TEST] Running fw-db status with Vanilla config..."
./venv/bin/python3 scripts/fw-db.py --config demo/config.py status

echo "[TEST] Running fw-db runs with Vanilla config..."
./venv/bin/python3 scripts/fw-db.py --config demo/config.py runs --limit 1

echo "[TEST] Running fw-db status without config (Expect Warning)..."
./venv/bin/python3 scripts/fw-db.py status

echo "✅ fw-db Smoke Test Passed."
