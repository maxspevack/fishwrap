.PHONY: setup update run-press generate-pdf publish-resume clean

VENV_PATH := $(CURDIR)/venv
PYTHON := $(VENV_PATH)/bin/python3
PIP := $(VENV_PATH)/bin/pip

# --- Setup & Environment ---
setup:
	@echo "Setting up Python virtual environment and installing dependencies..."
	@brew install python3 cairo pango gdk-pixbuf libffi # Essential for WeasyPrint/Python native libs
	@python3 -m venv $(VENV_PATH)
	@$(PIP) install --upgrade pip
	@$(PIP) install -r requirements.txt
	@echo "Setup complete. To activate the venv, run 'source venv/bin/activate'."

update:
	@echo "Updating Python dependencies..."
	@$(PIP) install --upgrade -r requirements.txt

# --- Gemini Gazette (Newspaper) ---
run-press:
	@echo "Running the Gemini Gazette pipeline..."
	@$(PYTHON) -m press.fetcher
	@$(PYTHON) -m press.editor
	@$(PYTHON) -m press.enhancer
	@$(PYTHON) -m press.printer

# --- spevack.org (Resume Site) ---
generate-pdf:
	@echo "Generating resume.pdf from spevack-org/index.md..."
	@$(PYTHON) -c "import markdown, weasyprint, requests; \
	html_content = markdown.markdown(open('spevack-org/index.md').read()); \
	css_url = 'https://draculatheme.com/assets/css/style.css'; \
	css_content = requests.get(css_url).text; \
	full_html = f'''<!DOCTYPE html><html><head><style>{css_content}</style><style>body {{ padding: 50px; background-color: #282a36; color: #f8f8f2; }}</style></head><body>{html_content}</body></html>'''; \
	weasyprint.HTML(string=full_html).write_pdf('spevack-org/resume.pdf'); \
	print('resume.pdf generated in spevack-org/')"

publish-resume: generate-pdf
	@echo "Publishing spevack.org (pushing changes to GitHub)..."
	cd spevack-org && git add . && git commit -m "chore: Update website and resume PDF" && git push

# --- Cleanup ---
clean:
	@echo "Cleaning up build artifacts..."
	rm -rf press/logs/*.log press/logs/*.err press/articles_db.json press/run_sheet.json press/enhanced_issue.json
	rm -f press/latest.html press/latest.pdf
	rm -f spevack-org/resume.pdf
	@echo "Cleanup complete."
