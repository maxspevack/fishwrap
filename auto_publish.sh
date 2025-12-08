#!/bin/bash

# Configuration
PROJECT_DIR="/Users/max/Documents/Gemini/fishwrap"
VENV_PYTHON="$PROJECT_DIR/venv/bin/python3"
REPO_URL="https://github.com/maxspevack/fishwrap.git"
DOMAIN="dailyclamour.com"
DEPLOY_BRANCH="gh-pages"

# Move to project dir
cd "$PROJECT_DIR" || exit 1

echo "Starting automated run: $(date)" 

# 1. Run the Pipeline
# We chain them with && so we don't publish if a step fails
"$VENV_PYTHON" -m fishwrap.fetcher && \
"$VENV_PYTHON" -m fishwrap.editor && \
"$VENV_PYTHON" -m fishwrap.enhancer && \
"$VENV_PYTHON" -m fishwrap.printer

PIPE_STATUS=$?

if [ $PIPE_STATUS -eq 0 ]; then
    echo "Pipeline successful. Starting deployment to $DOMAIN..."

    # 2. Prepare Deployment in a temporary directory
    DEPLOY_DIR=$(mktemp -d)
    
    # Copy the output file to index.html
    cp "$PROJECT_DIR/fishwrap/latest.html" "$DEPLOY_DIR/index.html"
    
    # Create CNAME file
    echo "$DOMAIN" > "$DEPLOY_DIR/CNAME"
    
    # 3. Git Operations (The "Kiosk" Method)
    # We initialize a fresh repo to avoid history bloat
    cd "$DEPLOY_DIR" || exit 1
    git init -b "$DEPLOY_BRANCH"
    git config user.name "Max Spevack"
    git config user.email "max.spevack@gmail.com"
    
    git add .
    git commit -m "Deploy issue: $(date)"
    
    # Force push to the gh-pages branch of the remote
    # We use --quiet to reduce noise, but you can remove it to see progress
    git push --force --quiet "$REPO_URL" "$DEPLOY_BRANCH"
    
    echo "Deployed successfully to https://$DOMAIN"
    
    # Cleanup
    cd "$PROJECT_DIR"
    rm -rf "$DEPLOY_DIR"

else
    echo "Pipeline failed. Skipping deployment."
    exit $PIPE_STATUS
fi

echo "Run complete: $(date)"