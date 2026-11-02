SHELL := /bin/bash
.PHONY: setup update test build-core run-vanilla demo demo-html demo-open clean-output clean-venv clean-all

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
	@$(PYTHON) scripts/test_masthead.py
	@$(PYTHON) scripts/test_classify.py
	@$(PYTHON) scripts/test_pipeline.py
	@$(PYTHON) scripts/test_morgue.py
	@$(PYTHON) scripts/test_demo_instance.py
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

# --- Demo Targets (local development) ---
# `make run-vanilla` runs the full pipeline (fetch → editor → enhancer →
# printer). Use this against the live web; pulls feeds, slow.
#
# `make demo-html` skips the fetcher and the enhancer — it runs editor +
# printer against whatever is already in demo/data/demo.db. Use this when
# you just want to re-render the HTML from a snapshot. Fast.
#
# `make demo` is the convenience target — runs demo-html and opens the
# reader edition in the default browser.

run-vanilla:
	@echo "--- Building Vanilla Demo (full pipeline; pulls feeds) ---"
	@$(MAKE) build-core INSTANCE=demo

demo-html:
	@echo "--- Rendering the demo against demo/data/demo.db (no fetch) ---"
	@if [ ! -f demo/data/demo.db ]; then \
	  echo "[ERROR] demo/data/demo.db does not exist."; \
	  echo "[HINT]  Either run 'make run-vanilla' to fetch live, or copy a"; \
	  echo "        snapshot DB to that path (e.g., from a prior production run)."; \
	  exit 1; \
	fi
	@export FISHWRAP_CONFIG=$(CURDIR)/demo && \
	$(PYTHON) -m fishwrap.editor && \
	$(PYTHON) -m fishwrap.printer
	@echo ""
	@echo "✅ Demo rendered. Open:"
	@echo "    open $(CURDIR)/demo/output/edition-reader.html"

demo: demo-html
	@open $(CURDIR)/demo/output/edition-reader.html 2>/dev/null || true

# --- Cleanup ---
clean-output:
	rm -rf demo/output/* logs/*

clean-venv:
	rm -rf venv
	find . -name "__pycache__" -type d -exec rm -rf {} +

clean-all: clean-output clean-venv
