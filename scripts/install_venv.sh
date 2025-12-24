#!/bin/bash
set -euo pipefail # Exit on error, unset variables, pipefail

VENV_PATH=$(dirname "$0")/../venv # Relative to script location (fishwrap/scripts/ -> fishwrap/venv)
REQUIREMENTS_TXT=$(dirname "$0")/../requirements.txt

echo "Setting up Python virtual environment and installing dependencies..."
python3 -m venv "$VENV_PATH"
"$VENV_PATH/bin/pip" install --upgrade pip
"$VENV_PATH/bin/pip" install -r "$REQUIREMENTS_TXT"

# Install NLTK data locally to keep the project self-contained
NLTK_DATA_DIR=$(dirname "$0")/../nltk_data
mkdir -p "$NLTK_DATA_DIR"
"$VENV_PATH/bin/python3" -m nltk.downloader -d "$NLTK_DATA_DIR" punkt

echo "Setup complete."
