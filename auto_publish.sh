#!/bin/bash

# Absolute path to project root
PROJECT_DIR="/Users/max/Documents/Gemini"
VENV_PYTHON="$PROJECT_DIR/venv/bin/python3"

cd "$PROJECT_DIR" || exit 1

echo "Starting automated run: $(date)"

# Run the pipeline
"$VENV_PYTHON" -m press.fetcher && \
"$VENV_PYTHON" -m press.editor && \
"$VENV_PYTHON" -m press.enhancer && \
"$VENV_PYTHON" -m press.printer

echo "Run complete: $(date)"

