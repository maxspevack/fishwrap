#!/bin/bash
# Fishwrap Demos Automation
# This script rebuilds all demos (Vanilla, Cyber, AI, ShowRunner)
# and commits the changes to the repository.

set -e

# Ensure we are in the fishwrap root
cd "$(dirname "$0")"

echo "--- Starting Fishwrap Demos Auto-Ship: $(date) ---"

# 1. Run the Build & Publish pipeline
make ship

# 2. Commit & Push (if there are changes in docs/)
if [[ -n $(git status --porcelain docs/) ]]; then
    echo "Changes detected in docs/. Committing..."
    git add docs/
    git commit -m "Auto-ship demos: $(date)"
    git push origin main
    echo "✅ Demos pushed to origin main."
else
    echo "No changes in demos."
fi

echo "--- Finished Fishwrap Demos Auto-Ship: $(date) ---"
