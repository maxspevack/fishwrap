---
layout: default
title: Scaling the School
has_children: true
nav_order: 3
---

# 🐟 Scaling the School: Case Studies in High-Performance News

Subject: Brown Bag Lunch (BYO Fish & Chips) 🐟🍟

---

## 🎣 The Catch of the Day

Welcome, everyone. Thanks for skipping lunch to hear about how we stopped our production server from catching fire.

We started with a simple idea: Scrape the internet, filter out the trash, and print a daily newspaper. It worked beautifully when we were catching minnows. But recently, our database grew to over 1,000 articles. Suddenly, our "Editor" module went from taking seconds to taking... forever.

We were drowning in our own net. Here is the story of how we rebuilt the factory to handle the load.

## 🚀 The Results: Holy Mackerel!

We deployed the new pipeline to `dailyclamour.com`. The transformation is staggering.

| Metric | Before Optimization | After Optimization | Improvement |
| :--- | :--- | :--- | :--- |
| **Editor Runtime** | ~45 seconds | < 0.5 seconds | **~90x Faster** |
| **Pipeline I/O** | ~51 seconds | ~15 seconds | **~3.5x Faster** |
| **Complexity** | O(N²) | O(N) (Effective) | **Logarithmic** |
| **Zombie Outbreaks**| Frequent | 0 | **Safe** |
| **Engineer Mood** | 🤬 | 🍺 | **Significant** |

---

## 📚 The Case Studies

We didn't just tune the engine; we gutted it. We broke the problem down into three distinct engineering challenges.

### [Vol 1. The Hatchet & The Scalpel](./01_algorithms.html)
**Topic:** Algorithmic Complexity (CPU)
How we reduced our scoring loop from **O(N*K)** to **O(1)** and our deduplication from **O(N²)** to effectively **O(N)** using "Golden Records" and Jaccard Indices.

### [Vol 2. Breaking the Speed of Light](./02_concurrency.html)
**Topic:** Concurrency & Network I/O
How we stopped standing in line. We moved from sequential processing to **Parallel Threading**, but then accidentally DDoS'd Reddit and had to implement **Token Bucket Rate Limiting**.

### [Vol 3. The Zombie Defense](./03_consistency.html)
**Topic:** State Management & Consistency
How we stopped "Zombie Articles" from rising from the dead by decoupling **Retention** (Memory) from **Publication** (Freshness), and how we solved the "Memento" bug where we kept forgetting what we learned.

---

## 🎓 The Golden Rules

1.  **Don't compute at read-time what you can compute at write-time.**
2.  **Cheap checks first.** Always filter your data with a "hatchet" (sets) before you go in with a "scalpel" (AI/Fuzzy).
3.  **Memory != Display.** State is necessary for deduplication, even if you don't show it.
4.  **Network I/O is for the birds.** Parallelize it, but rate-limit it.
5.  **There's always a bigger fish.**

<img src="https://i.redd.it/iriscb26whx01.jpg" style="width: 100%; border-radius: 8px; margin-top: 20px;" alt="There's always a bigger fish">