# Fishwrap 🐟📰

**"The algorithm you can read. The feed that ends."**

**Fishwrap** is a "Glass-Box" daily briefing engine. It transforms the chaos of the internet (RSS feeds, Reddit threads, Hacker News) into finite, auditable **Artifacts**—beautiful, distraction-free HTML or PDF editions.

It is designed to be the "Anti-Feed" for the Diamond Age.

👀 **See it in action:**
*   [The Daily Clamour](https://dailyclamour.com) (Live Production Instance)
*   [The Zero Day](https://fishwrap.org/demo/cyber/) (Cybersecurity Demo)
*   [The Hallucination](https://fishwrap.org/demo/ai/) (AI Research Demo)

---

## 🗞️ Stop the Presses! (Quick Start)

Fishwrap ships with three reference "Verticals" to demonstrate its flexibility.

### 1. Hire the Staff
Clone the repo and install dependencies:
```bash
git clone https://github.com/maxspevack/fishwrap.git
cd fishwrap
make setup
```

### 2. Choose Your Vertical
Run the pipeline for the edition you want to print:

*   **The Vanilla Edition (General News):**
    ```bash
    make run-vanilla
    open demo/output/latest.html
    ```

*   **The Zero Day (Cybersecurity):**
    ```bash
    make run-cyber
    open demo/output/cyber_latest.html
    ```

*   **The Hallucination (AI Research):**
    ```bash
    make run-ai
    open demo/output/ai_latest.html
    ```

---

## 🧐 The Glass Box (How It Works)

Fishwrap is built on the philosophy of **Transparency** and **Auditability**.

*   **The Fetcher:** Scours your defined feeds (RSS, JSON).
*   **The Editor:** Dynamically buckets articles into Sections based on `config.py`. It applies your transparent **Editorial Policies** (Boosts/Penalties) to calculate an Impact Score.
*   **The Enhancer:** Scrapes full text so you don't have to click away.
*   **The Printer:** Generates a static HTML/PDF file.

Everything is driven by a simple Python configuration file. You are the Editor-in-Chief.

[**Read the Full Documentation**](https://fishwrap.org)

---

## 📂 Repository Structure

*   **`fishwrap/`**: The core stateless engine.
*   **`demo/`**: Reference configurations (`config.py`, `cyber_config.py`, `ai_config.py`) and themes.
*   **`docs/`**: The source for [fishwrap.org](https://fishwrap.org).

---

## 📜 License
BSD 3-Clause.
