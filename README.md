# Fishwrap 🐟📰

**"Yesterday's News, Tomorrow's Wrapper."**

**Fishwrap** is a bespoke, automated newspaper engine for the digital age. It takes the chaos of the internet (RSS feeds, Reddit threads, Hacker News), applies editorial judgment (your rules), enhances it with full-text content, and prints a beautiful, distraction-free HTML edition.

It's not just an aggregator; it's a **publication platform** for an audience of one.

👀 **See it in action:** [The Daily Clamour](https://dailyclamour.com) (Running live on Fishwrap).

---

## 🗞️ Stop the Presses! (Quick Start)

Want to see what Fishwrap can do? We ship with a **Vanilla Demo** edition that aggregates top tech, news, and sports stories right out of the box.

### 1. Hire the Staff
Clone the repo and install dependencies:
```bash
git clone https://github.com/maxspevack/fishwrap.git
cd fishwrap
make setup
```

### 2. Print the Late Edition
Run the full pipeline (Fetch -> Edit -> Enhance -> Print) using the demo configuration:
```bash
make run-vanilla
```

### 3. Read All About It
Open your fresh-off-the-press newspaper:
```bash
open demo/output/latest.html
```

---

## 🧐 From the Editor's Desk (Documentation)

Ready to start your own publication? We have dedicated guides for that.

*   **[The Starter Kit (demo/README.md)](demo/README.md):** 
    *   *Read this first!* How to copy the demo, add your own feeds, change the logo, and publish your own paper.
    
*   **[The Engine Room (fishwrap/README.md)](fishwrap/README.md):** 
    *   *For Engineers.* Deep dive into the pipeline, the `load_template` system, and how to write custom renderers.

---

## 🏗 How the Sausage is Made (Architecture)

Fishwrap operates as a linear, four-stage assembly line:

1.  **🕵️‍♀️ The Fetcher:** Scours the web (RSS/JSON). Smartly handles Hacker News to prioritize discussion over links.
2.  **✏️ The Editor:** The brains of the operation. Scores stories based on "Impact" (Votes + Comments + Freshness) and your custom `EDITORIAL_POLICIES`. Curates the "Front Page".
3.  **🔬 The Enhancer:** The heavy lifter. Scrapes full article text, bylines, and metadata so you never have to click a clickbait link again.
4.  **🖨 The Printer:** The artist. Takes the enhanced content and renders it into a Theme (like our "Vintage" or "Basic" styles).

## 📂 Archives (Repository Structure)

*   **`fishwrap/`**: The stateless Python core. Contains the logic for the pipeline.
*   **`demo/`**: The "Vanilla" reference implementation. A clean slate for you to build on.
*   **`daily_clamour/`**: An example production instance (The Daily Clamour).

## 🔮 Contributing & Roadmap

We are actively improving Fishwrap. Current focus areas include:

*   **📄 PDF Generation:** The PDF renderer is currently disabled. We plan to re-enable it with full support for the new Theming engine, allowing for "Print Editions" of your custom paper.
*   **📱 Advanced Mobile:** While the grid is responsive, we want to add features like collapsible sections and "List View" toggles for phone users.
*   **🎨 Theme Gallery:** We aim to create more reference themes (e.g., "Dark Mode Terminal", "Modern Magazine") to showcase the engine's flexibility.

## 📜 License
BSD 3-Clause.