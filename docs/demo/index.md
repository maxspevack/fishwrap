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

## 🧪 Reference Demo

The reference demo shows what the engine produces with a minimal config and the `basic` theme. It is the starting point for building your own paper.

| Edition | Description | Link |
| :--- | :--- | :--- |
| **The Vanilla** | A general mix of RSS feeds. The engine's baseline capability. | [**Read Vanilla**](vanilla/) |

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
```bash
make run-vanilla
# output is at demo/output/index.html
```
