# Vol 1. The Hatchet & The Scalpel
## Optimizing Algorithmic Complexity

When we profiled our "Editor", we found two rotting carcasses eating our CPU cycles.

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

## Strategy A: The Golden Record (Architecture)
*aka "Score Once, Read Many"*

We moved the heavy lifting from the **Editor** (read-time) to the **Fetcher** (write-time).

Now, when a fresh fish is hauled onto the boat (ingested), we immediately:
1.  **Classify it** (Is it Sports? Tech?).
2.  **Score it** (Is it important?).
3.  **Tag it** (Write `_computed_score` to the JSON).

The database became our "Golden Record." The Editor stopped being a judge and started being a bouncer—it just looks at the tag on the fish's ear.

**Result:** The scoring loop vanished. **O(N*K) → O(1) lookup.**

---

## Strategy B: The Hatchet (Algorithm)
*aka "Don't compare a Salmon to a Boot"*

We still needed to deduplicate (cluster), but we needed to stop comparing everything to everything. We applied two filters:

### 1. The Time Window ⏳
News gets stale. A story about a server outage today is not a duplicate of a server outage from 1999.
We added a hard **48-hour window**. If the fish are from different eras, we don't compare them.

### 2. The Jaccard Pre-Filter 🪓
This was the *piece de resistance*. `difflib` is accurate but slow. Python `sets` are stupid but fast.

Before running the expensive DNA test (`difflib`), we now do a "Jaccard Index" check (Set Intersection). (Full disclosure: We didn't learn this in school. Google told us this is what you use when strings are "kinda" the same.)

We break the titles into sets of words.

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

[Back to Engineering Hub](./index.html)
