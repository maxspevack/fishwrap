---
layout: default
title: Vol 2. Concurrency
parent: The Architect's Log
nav_order: 2
---

# Vol 2. The Parallel Press
## Concurrency & Network I/O

We fixed the CPU bottlenecks, but our I/O was stuck in the era of dial-up.

### The Single-Lane Highway (Sequential I/O)
Our **Fetcher** (downloading RSS feeds) and **Enhancer** (scraping full text) were running sequentially. One feed at a time. One article at a time.

If `nytimes.com` was slow, the entire pipeline paused to wait for it. It was like running a printing press where you wait for the ink to dry on page 1 before you even start looking for paper for page 2.

---

## Strategy D: The Speed of Light (Parallelism)
*aka "Why stand in line when you can open 10 doors?"*

**The Fix:** `concurrent.futures.ThreadPoolExecutor`.

We refactored the I/O-heavy loops to spawn **10 worker threads**. Now, we fetch 10 feeds at once. We scrape 10 articles at once. The network latency overlaps, and we crush the wait time.

**The Initial Results:**

| Component | Sequential (Before) | Parallel (After) | Improvement |
| :--- | :--- | :--- | :--- |
| **Fetcher** (26 feeds) | ~17.0s | ~2.5s | **6.8x Faster** |
| **Enhancer** (36 articles) | ~34.0s | ~4.3s | **7.9x Faster** |
| **Total I/O Time** | ~51.0s | ~6.8s | **7.5x Faster** |

We thought we were geniuses. But then we hit a wall.

---

## Strategy E: Traffic Control (Rate Limiting)
*aka "Don't DDoS Reddit"*

Our new parallel fetcher was *too* fast. We unleashed 10 concurrent threads against Reddit's API, and Reddit immediately slapped us with **HTTP 429: Too Many Requests**.

We had effectively DDoS'd our own data sources. The pipeline crashed. We were rude guests.

**The Fix:** Domain-Based Locks (`threading.Lock`).

We implemented a polite "Token Bucket" style rate limiter in our `utils.py`.
*   **Global Lock:** We track the last request time for each domain.
*   **The Wait:** If a thread wants to hit `reddit.com`, it grabs the "Reddit Lock." If the last request was < 2 seconds ago, it sleeps.
*   **Concurrency Preserved:** This only serializes requests to *the same domain*. We can still fetch from `nytimes.com`, `bbc.co.uk`, and `reddit.com` simultaneously. We just won't hit Reddit 10 times in 10ms.

**Result:** 0 Errors. The pipeline is slightly slower than the "unsafe" version (~15s total I/O), but it is **stable** and polite.

**Lesson:** With great power comes great responsibility. The Architect builds fast, but the Architect also builds safe.

[Back to The Architect's Log](./index.html)