# Fishwrap 🐟📰

**"Fishwrap"** is the internal codename for the engine behind **The Daily Clamour**, a fully automated, personalized newspaper generator.

It aggregates content from RSS feeds, Reddit, and Hacker News, curates it into sections (News, Tech, Culture, Sports), enhances it with full text and top comments, and publishes it as a clean, read-later HTML dashboard and PDF edition.

## 🚀 Quick Start

### 1. Setup Environment
```bash
make setup
source venv/bin/activate
```

### 2. Run the Press
To run the full pipeline (Fetch -> Edit -> Enhance -> Print):
```bash
make run-fishwrap
```

### 3. Output
The generated editions are saved to the project root:
*   `fishwrap/latest.html` (Interactive Bento Grid)
*   `fishwrap/latest.pdf` (Print Edition)

## 🏗 Project Structure

*   **`fishwrap/`**: The core Python package containing the logic pipeline.
    *   [Read the Package Documentation](fishwrap/README.md)
*   **`venv/`**: Python virtual environment.
*   **`articles_db.json`**: The persistent master database of all fetched articles.
*   **`auto_publish.sh`**: Helper script for `launchd` automation.

## ⚙️ Automation

The system is designed to run automatically via `launchd` using the provided `auto_publish.sh` script.

## 📜 License
Private personal project.
