<div align="center">
  <img src="docs/static/images/fishwrap_logo.svg" alt="Fishwrap" width="400">
  <br>
  <b>The algorithm you can read. The feed that ends.</b>
</div>

<br>

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
    open demo/output/index.html
    ```

*   **The Zero Day (Cybersecurity):**
    ```bash
    make run-cyber
    open demo/output/cyber_index.html
    ```

*   **The Hallucination (AI Research):**
    ```bash
    make run-ai
    open demo/output/ai_index.html
    ```

---

## 🧐 The Glass Box (How It Works)

Fishwrap is built on the philosophy of **Transparency** and **Auditability**.

*   **The Fetcher:** Scours your defined feeds (RSS, JSON) using **Concurrent I/O** (10x faster than sequential).
*   **The Editor:** Dynamically buckets articles into Sections based on `config.py`. It applies your transparent **Editorial Policies** (Boosts/Penalties) to calculate an Impact Score.
*   **The Enhancer:** Scrapes full text so you don't have to click away, utilizing intelligent caching and **Rate Limiting** to be a good citizen.
*   **The Printer:** Generates a static HTML/PDF file.

Everything is driven by a simple Python configuration file. You are the Editor-in-Chief.

[**Read the Full Documentation**](https://fishwrap.org)

---

## 🧰 Database Management (`fw-db`)

Fishwrap uses a local SQLite database ("The Newsroom") to track articles and runs. You can manage this using the `fw-db` utility.

**Note:** You must provide the configuration file *before* the command so the tool knows which database to target.

```bash
# Check status (Article count, DB size)
python3 scripts/fw-db.py --config demo/config.py status

# List recent editions (Runs)
python3 scripts/fw-db.py --config demo/config.py runs
```

---

## 📚 Engineering Blog

We document our journey in building a high-performance news engine.

*   [**Scaling the School**](https://fishwrap.org/engineering/): A 3-part case study on how we gutted O(N²) logic, parallelized the pipeline, and fixed "Zombie" data bugs.

---

## 📂 Repository Structure

*   **`fishwrap/`**: The core stateless engine.
*   **`demo/`**: Reference configurations (`config.py`, `cyber_config.py`, `ai_config.py`) and themes.
*   **`docs/`**: The source for [fishwrap.org](https://fishwrap.org).

---

## 🤝 Join the Newsroom

We are actively developing Fishwrap to be the engine of the "Anti-Feed" movement.

*   [**Roadmap (2026):**](ROADMAP.md) See our plan for Observability, The Chronicle, and the PDF Engine.
*   [**Contributing:**](CONTRIBUTING.md) How to add feeds, fix bugs, and tune the algorithm.
*   [**Release Notes:**](docs/RELEASE_NOTES.md) History of changes.

---

## 📜 License
Apache License 2.0.
