---
layout: default
title: Demos
nav_order: 2
---

# The Fleet 🔱

See the Fishwrap engine in action.

## 🌟 Live Production

**[The Daily Clamour](https://dailyclamour.com)**
*The Flagship Edition.* A general-purpose news, sports, tech, and culture newspaper.

It demonstrates the full power of the "Glass-Box" engine:
*   **Finite:** Updates exactly **once per day** at 04:00 AM Pacific. No infinite scroll, no "breaking news" anxiety.
*   **Branded:** Custom aesthetics and a recognizable masthead.
*   **Automated:** Runs entirely on a strict schedule. The feed that ends.

---

## 🧪 Reference Demo

A reference demo ships in the source tree at `demo/`. It is the template for building your own paper — a `masthead.toml`, a `dossier.md`, and a `policies.jsonl` that the engine reads to produce an edition.

**[The Vanilla](/demo/vanilla/)** is that demo, rebuilt every day from the engine's `main` branch. It is the integration environment: what you see there is the engine's HEAD, not a release. The Daily Clamour above runs a pinned release and moves only when one is cut.

---

## ⚡ Run It Yourself

Want to print your own edition? It takes less than a minute to spin up a newsroom.

### 1. Hire the staff

```bash
git clone https://github.com/maxspevack/fishwrap.git
cd fishwrap
make setup
```

### 2. Print an edition

```bash
make run-vanilla
# Renders to demo/output/edition-reader.html
```

Then open `demo/output/edition-reader.html` in your browser.
</content>
</invoke>