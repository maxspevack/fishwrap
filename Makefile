SHELL := /bin/bash
.PHONY: setup update test build-core run-vanilla demo demo-html demo-open replay show policy clean-output clean-venv clean-all

# Paths
VENV := venv
PYTHON := $(VENV)/bin/python3
PIP := $(VENV)/bin/pip

# --- Environment ---
setup:
	@./scripts/install_venv.sh

update:
	@$(PIP) install --upgrade -r requirements.txt

# --- Testing ---
test:
	@echo "--- Running Unit Tests ---"
	@$(PYTHON) scripts/test_fetcher_resilience.py
	@$(PYTHON) scripts/test_logging_wiring.py
	@$(PYTHON) scripts/test_xml_safety.py
	@$(PYTHON) scripts/test_schema_integrity.py
	@$(PYTHON) scripts/test_masthead.py
	@$(PYTHON) scripts/test_classify.py
	@$(PYTHON) scripts/test_pipeline.py
	@$(PYTHON) scripts/test_runsheet.py
	@$(PYTHON) scripts/test_replay.py
	@$(PYTHON) scripts/test_show_policy.py
	@$(PYTHON) scripts/test_morgue.py
	@$(PYTHON) scripts/test_demo_instance.py
	@$(PYTHON) scripts/test_printer_output.py
	@$(PYTHON) scripts/test_demo_archive.py
	@echo "✅ All Tests Passed."

# --- The Publisher's loop ---
# make show [DATE=YYYY-MM-DD] [CUTS=N]   the edition as text (newest local, or the archive)
# make policy ARGS='ban-source example.com --because "..."'
#   verbs: ban-source, ban-title, ban-topic, print-all, prefer-lead, strike, list
# then: make replay DATE=... to see what moved; commit; the next build applies it.
show:
	@rs="$(RUNSHEET)"; \
	if [ -z "$$rs" ] && [ -n "$(DATE)" ]; then \
	  if [ -f demo/output/$(DATE)/runsheet.jsonl.gz ]; then rs=demo/output/$(DATE)/runsheet.jsonl.gz; \
	  else mkdir -p demo/output/archive && git fetch -q origin state && \
	       git show origin/state:demo/vanilla/$(DATE)/runsheet.jsonl.gz > demo/output/archive/$(DATE).runsheet.jsonl.gz && \
	       rs=demo/output/archive/$(DATE).runsheet.jsonl.gz; fi; \
	fi; \
	FISHWRAP_CONFIG=$(CURDIR)/demo $(PYTHON) -m fishwrap.show $$rs $(if $(CUTS),--cuts $(CUTS),)

policy:
	@FISHWRAP_CONFIG=$(CURDIR)/demo $(PYTHON) -m fishwrap.policy $(ARGS)

# --- Replay ---
# Re-run an archived edition's candidates under the masthead as it is now
# and print what moved. Nothing is fetched or written.
#   make replay DATE=2026-11-01        local demo/output/<DATE>/, else the archive
#   make replay RUNSHEET=path/to/runsheet.jsonl.gz
replay:
	@rs="$(RUNSHEET)"; \
	if [ -z "$$rs" ] && [ -n "$(DATE)" ]; then \
	  if [ -f demo/output/$(DATE)/runsheet.jsonl.gz ]; then rs=demo/output/$(DATE)/runsheet.jsonl.gz; \
	  else mkdir -p demo/output/archive && git fetch -q origin state && \
	       git show origin/state:demo/vanilla/$(DATE)/runsheet.jsonl.gz > demo/output/archive/$(DATE).runsheet.jsonl.gz && \
	       rs=demo/output/archive/$(DATE).runsheet.jsonl.gz; fi; \
	fi; \
	if [ -z "$$rs" ]; then echo "usage: make replay DATE=YYYY-MM-DD | RUNSHEET=path"; exit 2; fi; \
	FISHWRAP_CONFIG=$(CURDIR)/demo $(PYTHON) -m fishwrap.replay "$$rs"

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
	$(PYTHON) -m fishwrap.printer

# --- Demo Targets (local development) ---
# `make run-vanilla` runs the full pipeline (fetch → editor → printer).
# Use this against the live web; pulls feeds, ~40 s.
#
# `make demo-html` skips the fetcher — it runs editor + printer against
# whatever is already in demo/data/demo.db. Fast.
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
	@echo "    open $(CURDIR)/demo/output/index.html   (redirects to today's edition)"

demo: demo-html
	@xdg-open $(CURDIR)/demo/output/index.html 2>/dev/null || open $(CURDIR)/demo/output/index.html 2>/dev/null || true

# --- Cleanup ---
clean-output:
	rm -rf demo/output/* logs/*

clean-venv:
	rm -rf venv
	find . -name "__pycache__" -type d -exec rm -rf {} +

clean-all: clean-output clean-venv
