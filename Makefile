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
#
# Engine-shape tests (classify / dedup / select / morgue / etc.) belong
# to the new pipeline and are added in the next commit. The tests run
# here cover engine-agnostic concerns: the database schema, the fetcher,
# the logger, the XML safety layer, the enhancer.
test:
	@echo "--- Running Unit Tests ---"
	@$(PYTHON) scripts/test_enhancer_db.py
	@$(PYTHON) scripts/test_fetcher_resilience.py
	@$(PYTHON) scripts/test_logging_wiring.py
	@$(PYTHON) scripts/test_xml_safety.py
	@$(PYTHON) scripts/test_schema_integrity.py
	@$(PYTHON) scripts/test_fw_db_config.py
	@# test_fw_db.sh is a shell script, run it if it exists and is executable
	@if [ -x scripts/test_fw_db.sh ]; then ./scripts/test_fw_db.sh; fi
	@echo "✅ All Tests Passed."

# --- Atomic Build Unit ---
# Usage: make build-core INSTANCE=demo
# INSTANCE is an instance directory containing masthead.toml + dossier.md
# (+ optional policies.jsonl). The old CONFIG=demo/config.py form is gone;
# the user's editorial state is no longer a Python file.
build-core:
	@if [ -z "$(INSTANCE)" ]; then echo "Error: INSTANCE argument required"; exit 1; fi
	@export FISHWRAP_CONFIG=$(CURDIR)/$(INSTANCE) && \
	$(PYTHON) -m fishwrap.fetcher && \
	$(PYTHON) -m fishwrap.editor && \
	$(PYTHON) -m fishwrap.enhancer && \
	$(PYTHON) -m fishwrap.printer

# --- Demo Target (local development) ---
# The published image is not refreshed by this target; demos.yml workflow
# handles that against a pinned image. This target is for local engine
# development only.
run-vanilla:
	@echo "--- Building Vanilla Demo ---"
	@$(MAKE) build-core INSTANCE=demo

# --- Cleanup ---
clean-output:
	rm -rf demo/output/* logs/*

clean-venv:
	rm -rf venv
	find . -name "__pycache__" -type d -exec rm -rf {} +

clean-all: clean-output clean-venv
