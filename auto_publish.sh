#!/bin/bash

# Absolute path to project root
PROJECT_DIR="/Users/max/Documents/Gemini/fishwrap"
VENV_PYTHON="$PROJECT_DIR/venv/bin/python3"

cd "$PROJECT_DIR" || exit 1

echo "Starting automated run: $(date)"

# Run the pipeline
"$VENV_PYTHON" -m fishwrap.fetcher && \
"$VENV_PYTHON" -m fishwrap.editor && \
"$VENV_PYTHON" -m fishwrap.enhancer && \
"$VENV_PYTHON" -m fishwrap.printer

echo "Run complete: $(date)"

