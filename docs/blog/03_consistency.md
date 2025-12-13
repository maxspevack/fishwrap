---
layout: default
title: Vol 3. Consistency
parent: The Architect's Log
nav_order: 3
---

# Vol 3. The Unbroken Chain
## State Management & Consistency

Performance is useless if the data is wrong. As we scaled, we encountered "ghosts"—data that refused to die or refused to stay saved.

---

## Strategy C: The Memory Buffer (Logic)
*aka "The Walking Dead"*

We discovered a flaw in our freshness logic. We wanted to print only 24-hour-old news, so we deleted everything older than 24 hours from the database.

**The Bug:** If an article was 25 hours old, we deleted it. But if the RSS feed *still contained* that article, the Fetcher would see it, say "Hey, I don't know this ID!", and import it as a **New Item**.

We called these "Zombie Articles." They would rise from the dead, bypassing our "Old News" filters because they looked brand new (timestamp now).

**The Fix:** We decoupled **Retention** from **Publication**.
1.  **Retention (Memory):** The Database now keeps items for **48 hours**. This acts as a memory buffer. If the RSS feed re-submits a 25-hour-old item, we recognize the ID and ignore it.
2.  **Publication (Freshness):** The Editor now strictly filters for items `< 24 hours` old when building the page.

We store the past to understand the present, but we only print the present.

---

## Strategy F: Solving Memento (State Preservation)
*aka "Don't Forget What You Just Learned"*

We found a regression after implementing the parallel pipeline. The **Enhancer** would scrape text (expensive operation), save it to the DB, but then the **Fetcher** (running in the next hour's cycle) would overwrite that entry with raw RSS data, wiping out the scraped text.

We were basically Guy Pearce in *Memento*, re-scraping the same 80 articles every single hour. It was wasteful, slow, and expensive.

**The Fix:** Merge, don't overwrite.

We updated the `upsert` logic in the Fetcher to check for existing "expensive" fields (`full_content`, `is_enhanced`) and preserve them if they exist.

**Result:** **100% Cache Hit Rate** on subsequent runs. Zero wasted bandwidth. The chain remains unbroken.

[Back to The Architect's Log](./index.html)