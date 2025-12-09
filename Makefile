.PHONY: setup update run-fishwrap generate-pdf publish-resume clean

VENV_PATH := $(CURDIR)/venv
PYTHON := $(VENV_PATH)/bin/python3
PIP := $(VENV_PATH)/bin/pip

# --- Setup & Environment ---
setup:
	@echo "Setting up Python virtual environment and installing dependencies..."
	@# Check for Homebrew and install system dependencies if needed
	@if command -v brew >/dev/null 2>&1; then \
		echo "Installing system dependencies via Homebrew..."; \
		brew install python3 cairo pango gdk-pixbuf libffi || true; \
	else \
		echo "Homebrew not found. Skipping system dependency install."; \
	fi
	@python3 -m venv $(VENV_PATH)
	@$(PIP) install --upgrade pip
	@$(PIP) install -r requirements.txt
	@echo "Setup complete. To activate the venv, run 'source venv/bin/activate'."

update:
	@echo "Updating Python dependencies..."
	@$(PIP) install --upgrade -r requirements.txt

# --- Daily Clamour (Newspaper) ---
run-fishwrap:
	@echo "Running the Daily Clamour pipeline..."
	@$(PYTHON) -m fishwrap.fetcher
	@$(PYTHON) -m fishwrap.editor
	@$(PYTHON) -m fishwrap.enhancer
	@$(PYTHON) -m fishwrap.printer



# --- Cleanup ---
clean:
	@echo "Cleaning up build artifacts..."
	rm -rf fishwrap/logs/*.log fishwrap/logs/*.err fishwrap/run_sheet.json fishwrap/enhanced_issue.json
	rm -f fishwrap/latest.html fishwrap/latest.pdf
	# Note: articles_db.json is preserved intentionally as it contains the persistent history.
	@echo "Cleanup complete."
