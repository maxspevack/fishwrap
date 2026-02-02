SHELL := /bin/bash
.PHONY: setup update test build-core run-vanilla run-cyber run-ai publish ship clean-output clean-venv run-clamour

# Paths
VENV := venv
PYTHON := $(VENV)/bin/python3
PIP := $(VENV)/bin/pip

# Environment Variables
# Suppress SyntaxWarnings (from legacy libs like newspaper3k)
export PYTHONWARNINGS := ignore::SyntaxWarning

# --- Environment ---
setup:
	@./scripts/install_venv.sh

update:
	@$(PIP) install --upgrade -r requirements.txt

# --- Testing ---
test:
	@echo "--- Running Unit Tests ---"
	@$(PYTHON) scripts/test_editor_logic.py
	@$(PYTHON) scripts/test_enhancer_db.py
	@$(PYTHON) scripts/test_fetcher_resilience.py
	@$(PYTHON) scripts/test_schema_integrity.py
	@$(PYTHON) scripts/test_scoring_determinism.py
	@$(PYTHON) scripts/test_templates.py
	@# test_fw_db.sh is a shell script, run it if it exists and is executable
	@if [ -x scripts/test_fw_db.sh ]; then ./scripts/test_fw_db.sh; fi
	@echo "✅ All Tests Passed."

# --- Atomic Build Unit ---
# Usage: make build-core CONFIG=demo/config.py
build-core:
	@if [ -z "$(CONFIG)" ]; then echo "Error: CONFIG argument required"; exit 1; fi
	@export FISHWRAP_CONFIG=$(CURDIR)/$(CONFIG) && \
	$(PYTHON) -m fishwrap.fetcher && \
	$(PYTHON) -m fishwrap.editor && \
	$(PYTHON) -m fishwrap.enhancer && \
	$(PYTHON) -m fishwrap.printer

# --- Demo Targets ---
run-vanilla:
	@echo "--- Building Vanilla Demo ---"
	@$(MAKE) build-core CONFIG=demo/config.py

run-cyber:
	@echo "--- Building Cyber Demo ---"
	@$(MAKE) build-core CONFIG=demo/cyber_config.py

run-ai:
	@echo "--- Building AI Demo ---"
	@$(MAKE) build-core CONFIG=demo/ai_config.py

run-showrunner:
	@echo "--- Building ShowRunner Demo ---"
	@$(MAKE) build-core CONFIG=demo/showrunner_config.py

# --- Production Target (Daily Clamour Hook) ---# Kept for backward compatibility with dailyclamour.com/deploy.sh logic
# But ideally, DC should use its own Makefile that calls into this if needed
run-clamour:
	@echo "Running The Daily Clamour (Legacy Hook)..."
	@if [ -z "$(FISHWRAP_CONFIG)" ]; then echo "Error: FISHWRAP_CONFIG env var required for run-clamour"; exit 1; fi
	@$(PYTHON) -m fishwrap.fetcher && \
	$(PYTHON) -m fishwrap.editor && \
	$(PYTHON) -m fishwrap.enhancer && \
	$(PYTHON) -m fishwrap.printer

# --- Publishing ---
publish:
	@./publish_demo.sh vanilla
	@./publish_demo.sh cyber
	@./publish_demo.sh ai
	@./publish_demo.sh showrunner

# --- The "One Button" ---

ship: setup test run-vanilla run-cyber run-ai run-showrunner publish

	@echo "✅ Ship Complete. Verify in docs/ and commit."

# --- Cleanup ---
clean-output:
	rm -rf demo/output/* fishwrap/logs/*

clean-venv:
	rm -rf venv
	find . -name "__pycache__" -type d -exec rm -rf {} +

clean-all: clean-output clean-venv
