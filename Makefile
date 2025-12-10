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

# --- Production: The Daily Clamour ---
# Aliased to 'run-fishwrap' for backward compatibility with launchd scripts
run-fishwrap: run-clamour

run-clamour:
	@echo "Running The Daily Clamour..."
	@export FISHWRAP_CONFIG=$(CURDIR)/daily_clamour/config.py && \
	$(PYTHON) -m fishwrap.fetcher && \
	$(PYTHON) -m fishwrap.editor && \
	$(PYTHON) -m fishwrap.enhancer && \
	$(PYTHON) -m fishwrap.printer

# --- Demo: Vanilla Fishwrap ---
run-vanilla:
	@echo "Running Vanilla Fishwrap Demo..."
	@export FISHWRAP_CONFIG=$(CURDIR)/demo/config.py && \
	$(PYTHON) -m fishwrap.fetcher && \
	$(PYTHON) -m fishwrap.editor && \
	$(PYTHON) -m fishwrap.enhancer && \
	$(PYTHON) -m fishwrap.printer



# --- Cleanup ---
clean-demo:
	@echo "Cleaning up Demo artifacts..."
	rm -f demo/data/*.json demo/output/*.html demo/output/*.pdf
	rm -rf demo/output/static

clean-clamour:
	@echo "Cleaning up Daily Clamour artifacts..."
	rm -f daily_clamour/data/*.json daily_clamour/output/*.html daily_clamour/output/*.pdf
	rm -rf daily_clamour/output/static

clean: clean-demo clean-clamour
	@echo "Cleaning up logs..."
	rm -rf fishwrap/logs/* fishwrap/fishwrap/logs/*
	@echo "Cleanup complete."

clean-all: clean
	@echo "Cleaning up virtual environment and Python bytecode..."
	rm -rf venv
	find . -depth -name "__pycache__" -exec rm -rf {} \;
	@echo "Full cleanup complete."
