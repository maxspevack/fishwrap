SHELL := /bin/bash
.PHONY: setup update test build-core run-vanilla clean-output clean-venv clean-all

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
	@$(PYTHON) scripts/test_logging_wiring.py
	@$(PYTHON) scripts/test_xml_safety.py
	@$(PYTHON) scripts/test_schema_integrity.py
	@$(PYTHON) scripts/test_scoring_determinism.py
	@$(PYTHON) scripts/test_templates.py
	@$(PYTHON) scripts/test_validate_config.py
	@$(PYTHON) scripts/test_classifier_matching.py
	@$(PYTHON) scripts/test_fw_db_config.py
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

# --- Demo Target (local development) ---
# Production demos refresh via .github/workflows/demos.yml against the
# published image, not from this target. This target is for local
# engine development only.
run-vanilla:
	@echo "--- Building Vanilla Demo ---"
	@$(MAKE) build-core CONFIG=demo/config.py

# --- Cleanup ---
clean-output:
	rm -rf demo/output/* logs/*

clean-venv:
	rm -rf venv
	find . -name "__pycache__" -type d -exec rm -rf {} +

clean-all: clean-output clean-venv
