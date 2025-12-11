# 🐟 Scaling the School: How We Gutted O(N²) Logic to Print the News Faster

**To:** The Engineering Team
**From:** Max
**Subject:** Brown Bag Lunch (BYO Fish & Chips)

---

## 🎣 The Catch of the Day

Welcome, everyone. Thanks for skipping lunch to hear about how we stopped our production server from catching fire.

For those of you new to the **Fishwrap** project (our "Glass-Box" newspaper engine), here is the elevator pitch: We scrape the ocean of the internet (RSS, Reddit, APIs), we filter out the trash (ads, clickbait), and we wrap the good stuff into a finite, daily edition.

It worked beautifully when we were catching minnows. But recently, our database grew to over 1,000 articles. Suddenly, our "Editor" module—the brain that selects the front page—went from taking seconds to taking... well, let's just say you could go catch a real fish in the time it took to compile the `latest.html`.

We were drowning in our own net. Here is the story of how we fixed it.

---

## 📉 The Smell: "Groundhog Day" & The Cluster Bomb

We identified three rotting carcasses in our codebase.

### 1. The "Groundhog Day" Scoring (O(N*K))
Every time the Editor ran, it pulled *every* article from the database history and re-scored it. It scanned every title against hundreds of keywords (`K`) to determine if it was "News," "Tech," or "Garbage." It was redundant, CPU-intensive, and scaled linearly with the number of keywords.

### 2. The Cluster Bomb (O(N²))
This was the real killer. To prevent duplicate stories, we used a **Fuzzy Deduplication** algorithm that compared every candidate article against every selected article using `difflib`. With 1,000 items, that’s potentially **1,000,000** complex string comparisons.

### 3. The Checkout Line (Sequential I/O)
Our Fetcher and Enhancer were running sequentially. We downloaded one RSS feed, waited, then downloaded the next. If one site was slow, the whole pipeline froze. It was like checking out groceries with only one cashier open.

---

## 🛠️ The Fix: The Industrial Revolution

We realized we couldn't just tune the engine; we had to rebuild the factory. We implemented six major strategies.

### Strategy A: The Golden Record (Architecture)
*aka "Score Once, Read Many"*

We moved the heavy lifting from the **Editor** (read-time) to the **Fetcher** (write-time).

Now, when a fresh fish is hauled onto the boat (ingested), we immediately:
1.  **Classify it** (Is it Sports? Tech?).
2.  **Score it** (Is it important?).
3.  **Tag it** (Write `_computed_score` to the JSON).

The database became our "Golden Record." The Editor stopped being a judge and started being a bouncer—it just looks at the tag on the fish's ear.

**Result:** The scoring loop vanished. **O(N*K) → O(1) lookup.**

### Strategy B: The Hatchet (Algorithm)
*aka "Don't compare a Salmon to a Boot"*

We still needed to deduplicate (cluster), but we needed to stop comparing everything to everything. We applied two filters:

#### 1. The Time Window ⏳
News gets stale. We added a hard **48-hour window**. If the fish are from different eras, we don't compare them.

#### 2. The Jaccard Pre-Filter 🪓
This was the *piece de resistance*. `difflib` is accurate but slow. Python `sets` are stupid but fast.

Before running the expensive DNA test (`difflib`), we now do a "Jaccard Index" check (Set Intersection). (Full disclosure: We didn't learn this in school. Google told us this is what you use when strings are "kinda" the same.)

```python
# The Optimization
candidate_words = token_cache[id(candidate)]
leader_words = token_cache[id(leader)]

# Set intersection is written in C. It is BLAZING fast.
if candidate_words.isdisjoint(leader_words):
    continue 

# Only run this if they share words
run_expensive_difflib()
```

**Result:** We eliminated ~95% of the expensive comparisons.

### Strategy C: The Memory Buffer (Logic)
*aka "Zombie Defense"*

We discovered a flaw in our freshness logic. We wanted to print only 24-hour-old news, so we deleted everything older than 24 hours from the database.

**The Bug:** If an article was 25 hours old, we deleted it. But if the RSS feed *still contained* that article, the Fetcher would see it, say "Hey, I don't know this ID!", and import it as a **New Item**. We called these "Zombie Articles."

**The Fix:** We decoupled **Retention** from **Publication**.
1.  **Retention (Memory):** The Database now keeps items for **48 hours**. This acts as a memory buffer.
2.  **Publication (Freshness):** The Editor now strictly filters for items `< 24 hours` old when building the page.

We store the past to understand the present, but we only print the present.

### Strategy D: The Speed of Light (Parallelism)
*aka "Why stand in line when you can open 10 doors?"*

We fixed the CPU bottlenecks (Editor), but our I/O was stuck in the 90s.

**The Fix:** `concurrent.futures.ThreadPoolExecutor`.
We refactored the I/O-heavy loops to spawn **10 worker threads**. Now, we fetch 10 feeds at once. We scrape 10 articles at once. The network latency overlaps, and we crush the wait time.

**The Initial Result:** Total I/O time dropped from ~51s to ~7s. **7.5x Faster.**

### Strategy E: Traffic Control (Rate Limiting)
*aka "Don't DDoS Reddit"*

Our new parallel fetcher was *too* fast. We unleashed 10 concurrent threads against Reddit's API, and Reddit immediately slapped us with **HTTP 429: Too Many Requests**.

**The Fix:** Domain-Based Locks (`threading.Lock`).
We implemented a polite "Token Bucket" style rate limiter. We serialize requests to the *same domain* (wait 2s between Reddit calls) while keeping different domains parallel. We are fast, but polite.

### Strategy F: Solving Memento (State Preservation)
*aka "Don't Forget What You Just Learned"*

We found a regression: The **Enhancer** would scrape text (expensive), save it to the DB, but then the **Fetcher** (in the next run) would overwrite that entry with raw RSS data, wiping out the scraped text. We were re-scraping the same 80 articles every hour.

**The Fix:** Merge, don't overwrite.
The Fetcher now respects existing fields (`full_content`, `is_enhanced`) when updating an article.
**Result:** **100% Cache Hit Rate** on subsequent runs. Zero wasted bandwidth.

---

## 🚀 The Results: Holy Mackerel!

We deployed the new pipeline to `dailyclamour.com`. The total transformation is staggering.

| Metric | Before Optimization | After Optimization | Improvement |
| :--- | :--- | :--- | :--- |
| **Editor Runtime** | ~45 seconds | < 0.5 seconds | **~90x Faster** |
| **Pipeline I/O** | ~51 seconds | ~15 seconds | **~3.5x Faster** |
| **Complexity** | O(N²) | O(N) (Effective) | **Logarithmic** |
| **Zombie Outbreaks**| Frequent | 0 | **Safe** |
| **Cache Hit Rate** | 0% (Buggy) | 100% | **Optimal** |
| **Engineer Mood** | 🤬 | 🍺 | **Significant** |

We went from a system that choked on 1,000 items to one that can easily handle 10,000+ without breaking a sweat.

## 🎓 The Lesson

1.  **Don't compute at read-time what you can compute at write-time.**
2.  **Cheap checks first.** Always filter your data with a "hatchet" (sets/integers) before you go in with a "scalpel" (fuzzy logic/AI).
3.  **Memory != Display.** Just because you don't show it to the user doesn't mean you shouldn't remember it. State is necessary for deduplication.
4.  **Network I/O is for the birds.** Never block the main thread on the internet. Parallelize it.
5.  **With great power comes great responsibility.** If you parallelize, you must rate-limit. Be a good citizen.
6.  **Persist your wins.** Make sure your write-path doesn't overwrite your expensive read-path data.
7.  **There's always a bigger fish.**

<img src="https://i.redd.it/iriscb26whx01.jpg" style="width: 100%; border-radius: 8px; margin-top: 20px;" alt="There's always a bigger fish">
