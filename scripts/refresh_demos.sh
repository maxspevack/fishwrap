#!/bin/bash
# refresh_demos.sh
# Automates the refresh of all Fishwrap demos.
# Called by launchd.

# Ensure we are in the project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$REPO_ROOT" || exit 1

echo "[$(date)] Starting Fishwrap Demo Refresh..." >> logs/refresh.log

# Ensure Venv exists (safety check)
if [ ! -d "venv" ]; then
    echo "Error: venv not found. Run 'make setup' first." >> logs/refresh.log
    exit 1
fi

# Run the Build Pipeline (skip heavy setup/test, just build & publish)
make run-vanilla run-cyber run-ai run-showrunner publish >> logs/refresh.log 2>&1

EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
    echo "[$(date)] Refresh Complete. Success." >> logs/refresh.log
else
    echo "[$(date)] Refresh Failed. Exit Code: $EXIT_CODE" >> logs/refresh.log
fi

exit $EXIT_CODE
