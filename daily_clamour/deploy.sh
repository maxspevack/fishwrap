#!/bin/bash

# Configuration
# Resolve the project root (one level up from this script)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

REPO_URL="https://github.com/maxspevack/fishwrap.git"
DOMAIN="dailyclamour.com"
DEPLOY_BRANCH="gh-pages"

# Move to project dir
cd "$PROJECT_DIR" || exit 1

echo "Starting automated run: $(date)" 

# 1. Run the Pipeline via Makefile (Ensures Config Injection)
# We rely on the Makefile to handle the python invocation and config paths
make run-clamour

PIPE_STATUS=$?

if [ $PIPE_STATUS -eq 0 ]; then
    echo "Pipeline successful. Starting deployment to $DOMAIN..."

    # 2. Prepare Deployment in a temporary directory
    DEPLOY_DIR=$(mktemp -d)
    
    # Source Paths (The new location in daily_clamour)
    OUTPUT_DIR="$PROJECT_DIR/daily_clamour/output"
    
    # Copy the output file to index.html
    if [ -f "$OUTPUT_DIR/latest.html" ]; then
        cp "$OUTPUT_DIR/latest.html" "$DEPLOY_DIR/index.html"
    else
        echo "Error: Output file $OUTPUT_DIR/latest.html not found!"
        exit 1
    fi
    
    # Copy Static Assets
    if [ -d "$OUTPUT_DIR/static" ]; then
        cp -r "$OUTPUT_DIR/static" "$DEPLOY_DIR/static"
    fi
    
    # Create CNAME file
    echo "$DOMAIN" > "$DEPLOY_DIR/CNAME"
    
    # 3. Git Operations (The "Kiosk" Method)
    cd "$DEPLOY_DIR" || exit 1
    git init -b "$DEPLOY_BRANCH"
    git config user.name "Max Spevack"
    git config user.email "max.spevack@gmail.com"
    
    git add .
    git commit -m "Deploy issue: $(date)"
    
    # Force push to the gh-pages branch of the remote
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