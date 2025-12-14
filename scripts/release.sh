#!/bin/bash
set -euo pipefail

# Usage: ./scripts/release.sh <version> [codename]
# Example: ./scripts/release.sh 1.4.0 "The Big Update"

VERSION=$1
CODENAME=${2:-"Release $VERSION"}

if [ -z "$VERSION" ]; then
    echo "Usage: $0 <version> [codename]"
    exit 1
fi

# Ensure we are in the repo root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
REPO_ROOT="$SCRIPT_DIR/.."
cd "$REPO_ROOT"

echo "--- Preparing Release v$VERSION ($CODENAME) ---"

# 1. Update __init__.py
INIT_FILE="fishwrap/__init__.py"
echo "Updating $INIT_FILE..."
# Regex to replace __version__ = "..." with new version
# Using temp file for cross-platform sed compatibility
sed "s/__version__ = ".*"/__version__ = \"$VERSION\"/" "$INIT_FILE" > "$INIT_FILE.tmp" && mv "$INIT_FILE.tmp" "$INIT_FILE"

# 2. Smoke Test (The Golden Rule)
echo "--- Running Smoke Test ---"
echo "Cleaning environment..."
make clean-all
echo "Setting up environment..."
make setup
echo "Building Vanilla Demo..."
make run-vanilla

# Check result (redundant with set -e, but explicit is good)
if [ ! -f "demo/output/index.html" ]; then
    echo "❌ Build failed! demo/output/index.html not found."
    # Revert init file? No, let user fix it.
    exit 1
fi

echo "✅ Smoke Test Passed."

# 3. Git Operations
echo "--- Committing & Tagging ---"
git add "$INIT_FILE" "docs/RELEASE_NOTES.md" # Assume user updated notes manually
git commit -m "release: Bump version to v$VERSION"

echo "Tagging v$VERSION..."
git tag -a "v$VERSION" -m "Release v$VERSION: $CODENAME"

# 4. Push
echo "--- Pushing to Origin ---"
git push origin main
git push origin "v$VERSION"

echo "🎉 Release v$VERSION Shipped!"
echo "Now go update dailyclamour.com:"
echo "  cd ../dailyclamour.com && make install-stable VERSION=v$VERSION && make deploy"
