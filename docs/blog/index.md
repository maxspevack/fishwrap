---
layout: default
title: The Architect's Log
has_children: true
nav_order: 3
---

# 📐 The Architect's Log
## Case Studies in Building the Anti-Feed

**Subject:** Engineering the "Glass Box" 📦

---

## 🏗️ The Blueprint

Welcome to the engine room. This is where we document the construction of **Fishwrap**, the open-source briefing engine behind [The Daily Clamour](https://dailyclamour.com).

We started with a simple ambition: Scrape the internet, filter out the trash, and print a finite newspaper. It sounded easy. Then we hit reality. Our database grew, our CPU caught fire, and we accidentally DDoS'd Reddit.

These are the field notes from our journey to build a high-performance, transparent news engine in Python.

## 🚀 Performance Benchmarks (v1.0)

We didn't just tune the engine; we rebuilt the factory floor.

| Metric | Before Optimization | After Optimization | Improvement |
| :--- | :--- | :--- | :--- |
| **Editor Runtime** | ~45 seconds | < 0.5 seconds | **~90x Faster** |
| **Pipeline I/O** | ~51 seconds | ~15 seconds | **~3.5x Faster** |
| **Complexity** | O(N²) | O(N) (Effective) | **Logarithmic** |
| **Zombie Outbreaks**| Frequent | 0 | **Safe** |

---

## 📚 The Chronicles

We break down the engineering challenges into distinct volumes.

### [Vol 1. Folding Chaos (Algorithms)](./01_algorithms.html)
**Topic:** Complexity & Deduplication
How we stopped comparing every fish to every other fish. We reduced our scoring loop from **O(N*K)** to **O(1)** and implemented a "Jaccard Hatchet" to pre-filter duplicates before applying the fuzzy logic scalpel.

### [Vol 2. The Parallel Press (Concurrency)](./02_concurrency.html)
**Topic:** Threading & Rate Limiting
How we stopped standing in line. We moved from sequential processing to **Parallel Threading**, but then flew too close to the sun and had to implement **Token Bucket Rate Limiting** to be polite citizens of the web.

### [Vol 3. The Unbroken Chain (Consistency)](./03_consistency.html)
**Topic:** State Management & "Zombies"
How we stopped "Zombie Articles" from rising from the dead by decoupling **Memory** (Retention) from **Freshness** (Publication), ensuring the engine remembers the past without re-printing it.

### [Vol 4. The Glass Box (Observability)](./04_glass_box.html)
**Topic:** Trust & Metrics
How we built **The Auditor**, a forensic module that generates a receipt for every editorial decision. We explore the "Anti-Feed Protection" metric and the philosophy of algorithmic transparency.

### [Vol 5. The Release (DevOps)](./05_release_engineering.html)
**Topic:** Stability & Build Systems
How we solved the "Split Brain" problem between our Engine and Product. We discuss **Calendar Versioning**, **Automated Release Runbooks**, and the architecture of "Forward Compatibility."

---

## 🎓 The Golden Rules of the Newsroom

1.  **Don't compute at read-time what you can compute at write-time.**
2.  **Cheap checks first.** Use a hatchet (sets) before you use a scalpel (Levenshtein).
3.  **Memory != Display.** Store history to understand the present, but only print the new.
4.  **Network I/O is for the birds.** Parallelize it, but rate-limit it.
5.  **There's always a bigger fish.**

<img src="https://i.redd.it/iriscb26whx01.jpg" style="width: 100%; border-radius: 8px; margin-top: 20px; border: 1px solid #ccc;" alt="There's always a bigger fish">
