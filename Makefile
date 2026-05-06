SHELL := /bin/bash
.PHONY: setup update test build-core run-vanilla run-cyber run-ai run-showrunner clean-output clean-venv clean-all

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
	@$(PYTHON) scripts/test_validate_config.py
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

# --- Demo Targets (local development) ---
# Production demos refresh via .github/workflows/demos.yml against the
# published image, not from these targets. These targets are for local
# engine development only.
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

# --- Cleanup ---
clean-output:
	rm -rf demo/output/* fishwrap/logs/*

clean-venv:
	rm -rf venv
	find . -name "__pycache__" -type d -exec rm -rf {} +

clean-all: clean-output clean-venv
