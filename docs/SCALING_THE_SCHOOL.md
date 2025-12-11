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

We identified rotting carcasses in our codebase.

### 1. The "Groundhog Day" Scoring (O(N*K))
Every time the Editor ran, it pulled *every* article from the database history and re-scored it. It scanned every title against hundreds of keywords (`K`) to determine if it was "News," "Tech," or "Garbage."

Imagine judging a fish contest, but every day you force the judges to re-evaluate the fish from last Tuesday, measuring them again with a magnifying glass. It was redundant, CPU-intensive, and scaled linearly with the number of keywords.

### 2. The Cluster Bomb (O(N²))
This was the real killer. To prevent duplicate stories (e.g., five different outlets reporting "AI is taking our jobs"), we used a **Fuzzy Deduplication** algorithm.

We compared every candidate article against every selected article using `difflib` (Levenshtein distance).

```python
# The Horror
for candidate in huge_list_of_fish:
    for leader in existing_clusters:
        # This is a heavy math operation!
        if difflib.ratio(candidate.title, leader.title) > 0.7:
            mark_as_duplicate()
```

With 1,000 items, that’s potentially **1,000,000** complex string comparisons. We were effectively trying to DNA-test every fish in the ocean against every other fish to see if they were siblings.

---

## 🛠️ The Fix: The Industrial Revolution

We realized we couldn't just tune the engine; we had to rebuild the factory. We implemented three major strategies.

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
News gets stale. A story about a server outage today is not a duplicate of a server outage from 1999.
We added a hard **48-hour window**. If the fish are from different eras, we don't compare them.

#### 2. The Jaccard Pre-Filter 🪓
This was the *piece de resistance*. `difflib` is accurate but slow. Python `sets` are stupid but fast.

Before running the expensive DNA test (`difflib`), we now do a "Jaccard Index" check (Set Intersection). We break the titles into sets of words.

*   **Article A:** "Gemini" "Launches" "New" "Rocket"
*   **Article B:** "Local" "Man" "Eats" "Pie"

**Intersection:** 0 words.

If the sets are disjoint, we **SKIP** the expensive check. We only run `difflib` if the titles share actual DNA (words).

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

**The Bug:** If an article was 25 hours old, we deleted it. But if the RSS feed *still contained* that article, the Fetcher would see it, say "Hey, I don't know this ID!", and import it as a **New Item**. We called these "Zombie Articles." They would rise from the dead, bypassing our "Old News" filters because they looked brand new.

**The Fix:** We decoupled **Retention** from **Publication**.
1.  **Retention (Memory):** The Database now keeps items for **48 hours**. This acts as a memory buffer. If the RSS feed re-submits a 25-hour-old item, we recognize the ID and ignore it.
2.  **Publication (Freshness):** The Editor now strictly filters for items `< 24 hours` old when building the page.

We store the past to understand the present, but we only print the present.

---

## 🚀 The Results: Holy Mackerel!

We deployed the new pipeline to `dailyclamour.com`.

| Metric | Before | After | Improvement |
| :--- | :--- | :--- | :--- |
| **Editor Runtime** | ~45 seconds | < 0.5 seconds | **~90x Faster** |
| **Complexity** | O(N²) | O(N) (Effective) | **Logarithmic** |
| **Zombie Outbreaks**| Frequent | 0 | **Safe** |
| **Engineer Mood** | 🤬 | 🍺 | **Significant** |

We went from a system that choked on 1,000 items to one that can easily handle 10,000+ without breaking a sweat.

## 🎓 The Lesson

1.  **Don't compute at read-time what you can compute at write-time.**
2.  **Cheap checks first.** Always filter your data with a "hatchet" (sets/integers) before you go in with a "scalpel" (fuzzy logic/AI).
3.  **Memory != Display.** Just because you don't show it to the user doesn't mean you shouldn't remember it. State is necessary for deduplication.
4.  **There's always a bigger fish.**
    ![There's always a bigger fish](https://i.redd.it/iriscb26whx01.jpg)
    (But now our code is fast enough to catch it).

Thanks for listening. Get back to work.

— Max