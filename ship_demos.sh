#!/bin/bash
# Fishwrap Demos Automation
# This script rebuilds all demos (Vanilla, Cyber, AI, ShowRunner)
# and commits the changes to the repository.

set -e

# Ensure we are in the fishwrap root
cd "$(dirname "$0")"

echo "--- Starting Fishwrap Demos Auto-Ship: $(date) ---"

MAX_RETRIES=3
COUNT=0
SUCCESS=0

while [ $COUNT -lt $MAX_RETRIES ]; do
    echo "Attempt $((COUNT+1)) of $MAX_RETRIES..."
    
    # 1. Run the Build & Publish pipeline
    if make ship; then
        # 2. Commit & Push (if there are changes in docs/)
        if [[ -n $(git status --porcelain docs/) ]]; then
            echo "Changes detected in docs/. Committing..."
            git add docs/
            git commit -m "Auto-ship demos: $(date)"
            if git push origin main; then
                echo "✅ Demos pushed to origin main."
                SUCCESS=1
                break
            else
                echo "⚠️ Git push failed."
            fi
        else
            echo "No changes in demos."
            SUCCESS=1
            break
        fi
    else
        echo "⚠️ Build failed."
    fi

    COUNT=$((COUNT+1))
    echo "Retrying in 60 seconds..."
    sleep 60
done

if [ $SUCCESS -eq 0 ]; then
    echo "❌ Fishwrap Demos Ship failed after $MAX_RETRIES attempts."
    exit 1
fi

echo "--- Finished Fishwrap Demos Auto-Ship: $(date) ---"