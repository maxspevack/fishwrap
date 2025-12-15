---
layout: default
title: Demos
nav_order: 2
---

# The Fleet 🔱

See the Fishwrap engine in action.

## 🌟 Live Production

**[The Daily Clamour](https://dailyclamour.com)**  
*The Flagship Edition.* A general-purpose news, sports, tech, and culture newspaper running on the `vintage` theme.

It demonstrates the full power of the "Glass-Box" engine:
*   **Finite:** Updates exactly **once per day** at 04:00 AM Pacific. No infinite scroll, no "breaking news" anxiety.
*   **Branded:** Features custom "Vintage Clamour" aesthetics and Scoop-the-Pearl.
*   **Automated:** Runs entirely on a strict schedule. The feed that ends.

---

## 🧪 Reference Demos

These three "Reference Verticals" demonstrate how the same engine can be tuned for completely different audiences just by changing `config.py`.

| Edition | Vertical | Description | Link |
| :--- | :--- | :--- | :--- |
| **The Vanilla** | General News | A standard mix of RSS feeds (NYT, BBC, The Verge). Shows the baseline capability. | [**Read Vanilla**](vanilla/) |
| **The Zero Day** | Cybersecurity | Prioritizes CVEs and exploits. Filters out vendor marketing fluff. | [**Read Zero Day**](cyber/) |
| **The Hallucination** | AI Research | Separates Arxiv papers and Github repos from the "AGI is coming" opinion pieces. | [**Read AI**](ai/) |

---

## ⚡ Run It Yourself

Want to print your own edition? It takes less than a minute to spin up a newsroom.

### 1. Hire the Staff
```bash
git clone https://github.com/maxspevack/fishwrap.git
cd fishwrap
make setup
```

### 2. Print an Edition
Run the pipeline for the vertical you want to generate:

**The Vanilla (General News):**
```bash
make run-vanilla
# output is at demo/output/index.html
```

**The Zero Day (Cybersecurity):**
```bash
make run-cyber
# output is at demo/output/cyber_index.html
```

**The Hallucination (AI Research):**
```bash
make run-ai
# output is at demo/output/ai_index.html
```
