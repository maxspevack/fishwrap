# Fishwrap 🐟📰

**Fishwrap** is a Python-based personalized newspaper engine. It aggregates content from RSS feeds, curates it into sections (e.g., News, Tech, Sports), enhances it with full text and metadata, and renders it into a clean, read-later HTML dashboard.

See a live example of Fishwrap in production at **[The Daily Clamour](https://dailyclamour.com)**.

## 🚀 Quick Start

Fishwrap comes with a "Vanilla" demo configuration that gets you running in minutes.

### 1. Setup
```bash
git clone https://github.com/maxspevack/fishwrap.git
cd fishwrap
make setup
```

### 2. Run the Demo
This will fetch a sample set of feeds (NYT, BBC, ESPN, The Verge, etc.) and generate a newspaper.
```bash
make run-vanilla
```

### 3. Read Your Paper
Open the generated file in your browser:
```
open demo/output/latest.html
```

## 🛠 Creating Your Own Publication

To create your own newspaper, use the `demo/` directory as a template.

1.  **Copy the Demo:**
    ```bash
    cp -r demo my_paper
    ```
2.  **Configure:**
    Edit `my_paper/config.py` to add your favorite RSS feeds and adjust editorial weights.
3.  **Run:**
    You can run it by pointing the engine to your config:
    ```bash
    export FISHWRAP_CONFIG=$(pwd)/my_paper/config.py
    python3 -m fishwrap.fetcher
    python3 -m fishwrap.editor
    # ... etc
    ```

## 🏗 Architecture

Fishwrap operates as a linear pipeline:

1.  **Fetcher:** Ingests raw RSS/JSON feeds and stores them in a local database.
2.  **Editor:** Curates the edition, selecting top stories based on "Impact Score" (Votes, Comments, Freshness).
3.  **Enhancer:** Scrapes full article text and metadata.
4.  **Printer:** Renders the final output using a customizable Theme engine.

## 📂 Repository Structure

*   **`fishwrap/`**: The core Python engine (stateless).
*   **`demo/`**: A reference implementation with a basic configuration and theme.
*   **`daily_clamour/`**: (Internal) The production configuration for *The Daily Clamour*.

## 📜 License
BSD 3-Clause.