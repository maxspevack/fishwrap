#!/bin/bash

# usage: ./publish_demo.sh [vertical]
# example: ./publish_demo.sh vanilla

VERTICAL=$1

if [ -z "$VERTICAL" ]; then
    echo "Usage: $0 [vertical]"
    exit 1
fi

REPO_ROOT=$(pwd)
DOCS_DIR="$REPO_ROOT/docs/demo/$VERTICAL"

# Define Source Paths based on Vertical
case "$VERTICAL" in
    "vanilla")
        OUTPUT_FILE="$REPO_ROOT/demo/output/index.html"
        THEME_STATIC="$REPO_ROOT/demo/themes/basic/static"
        ;;
    "cyber")
        OUTPUT_FILE="$REPO_ROOT/demo/output/cyber_index.html"
        THEME_STATIC="$REPO_ROOT/demo/themes/basic/static"
        ;;
    "ai")
        OUTPUT_FILE="$REPO_ROOT/demo/output/ai_index.html"
        THEME_STATIC="$REPO_ROOT/demo/themes/basic/static"
        ;;
    *)
        echo "Unknown vertical: $VERTICAL"
        exit 1
        ;;
esac

# 1. Check if Source exists
if [ ! -f "$OUTPUT_FILE" ]; then
    echo "Error: Output file not found at $OUTPUT_FILE"
    echo "Please run 'make run-vanilla' first."
    exit 1
fi

# 2. Prepare Destination
echo "Publishing '$VERTICAL' to $DOCS_DIR..."
mkdir -p "$DOCS_DIR"

# 3. Copy HTML
cp "$OUTPUT_FILE" "$DOCS_DIR/index.html"
echo "  -> Copied index.html"

# 3.5 Copy Transparency Report (if exists)
TRANSPARENCY_FILE="$(dirname "$OUTPUT_FILE")/transparency.html"
if [ -f "$TRANSPARENCY_FILE" ]; then
    cp "$TRANSPARENCY_FILE" "$DOCS_DIR/transparency.html"
    echo "  -> Copied transparency.html"
fi

# 4. Copy Static Assets (if they exist)
if [ -d "$THEME_STATIC" ]; then
    # We copy the CONTENTS of static into docs/demo/vanilla/static
    mkdir -p "$DOCS_DIR/static"
    cp -R "$THEME_STATIC/" "$DOCS_DIR/static/"
    echo "  -> Copied static assets from $THEME_STATIC"
fi

echo "✅ Published '$VERTICAL' demo successfully."
