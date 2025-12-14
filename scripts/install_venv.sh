#!/bin/bash
set -euo pipefail # Exit on error, unset variables, pipefail

VENV_PATH=$(dirname "$0")/../venv # Relative to script location (fishwrap/scripts/ -> fishwrap/venv)
REQUIREMENTS_TXT=$(dirname "$0")/../requirements.txt

echo "Setting up Python virtual environment and installing dependencies..."
python3 -m venv "$VENV_PATH"
"$VENV_PATH/bin/pip" install --upgrade pip
"$VENV_PATH/bin/pip" install -r "$REQUIREMENTS_TXT"
echo "Setup complete."
