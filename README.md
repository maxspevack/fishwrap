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

## 🏢 Tour the Newsroom (Architecture)

Step inside the bustling Fishwrap newsroom and meet our dedicated staff:

1.  **🕵️‍♀️ The Beat Reporter (Fetcher):** Our tireless scouts scour the digital streets (RSS feeds, social aggregators) for breaking stories. They're particularly adept at sniffing out discussions on Hacker News.
2.  **✏️ The News Desk Editor (Editor):** Here's where the magic happens. Our sharp-eyed editors classify incoming stories, debate their "Impact Score" (combining votes, comments, and freshness), and apply our strict `EDITORIAL_POLICIES` to decide what makes the front page.
3.  **🔬 The Investigative Unit (Enhancer):** No clickbait here! This team digs deep, fetching the full article text and vital metadata so our readers get the complete picture, not just a headline.
4.  **🖨 The Press Operator (Printer):** Finally, the presses roll! Our skilled operators take the curated, enhanced content and lay it out beautifully according to the chosen Theme (whether it's "Vintage Clamour" or our clean "Basic" style).

## 📂 Archives (Repository Structure)

*   **`fishwrap/`**: The stateless Python core. Contains the logic for the pipeline.
*   **`demo/`**: The "Vanilla" reference implementation. A clean slate for you to build on.
*   **`daily_clamour/`**: An example production instance (The Daily Clamour).

## 🔮 Contributing & Roadmap

We are actively improving Fishwrap. Current focus areas include:

*   **📊 Scoring Algorithms:** Experiment with normalizing "Impact Scores" across diverse sources (e.g., Reddit, Hacker News). The goal is to ensure a "big deal" article from one source is fairly compared to another by applying a "grade on a curve" per source. This will prevent sources with naturally higher engagement from always dominating the front page.
*   **📄 PDF Generation:** The PDF renderer is currently disabled. We plan to re-enable it with full support for the new Theming engine, allowing for "Print Editions" of your custom paper.
*   **📱 Advanced Mobile:** While the grid is responsive, we want to add features like collapsible sections and "List View" toggles for phone users.
*   **🎨 Theme Gallery:** We aim to create more reference themes (e.g., "Dark Mode Terminal", "Modern Magazine") to showcase the engine's flexibility.

---

## 🏷️ Version & Releases

*   **[Versioning Strategy (VERSIONING.md)](VERSIONING.md):** Understand how Fishwrap's version numbers (MAJOR.MINOR.PATCH) are determined.
*   **[Release Notes (RELEASE_NOTES.md)](RELEASE_NOTES.md):** See what's new in each release, from features to bug fixes.

---

## 📜 License
BSD 3-Clause.