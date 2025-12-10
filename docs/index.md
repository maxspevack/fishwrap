---
layout: default
title: The Manifesto
nav_order: 1
---

# Fishwrap 🐟

**The algorithm you can read. The feed that ends.**

> "One of the insights of the Victorian Revival was that it was not necessarily a good thing for everyone to read a completely different newspaper in the morning; so the higher one rose in the society, the more similar one's Times became to one's peers'."
>
> — **Neal Stephenson**, *The Diamond Age*

---

## The Manifesto: Aperture & Artifacts

We are drowning in infinite streams.

Social media, news aggregators, and "For You" pages are designed to be bottomless. They optimize for **engagement**, which usually means rage, anxiety, or addiction. They treat you like a pair of eyeballs to be monetized.

**Fishwrap is the "Anti-Feed."**

It is an open-source newspaper engine designed for the **Diamond Age** of information. It is built on three radical ideas:

### 1. Finiteness is a Status Symbol
In a world of cheap, infinite content, the ultimate luxury is **an ending**.
Like the bespoke *Times* delivered to the elite in Stephenson's Neo-Victorian future, a newspaper should be an **Artifact**—a discrete object with a beginning, a middle, and a last page. Fishwrap transforms the chaos of the web into a finite HTML or PDF edition that you can read, finish, and put away. The peasants scroll; the elite read.

### 2. The Fishbowl (Transparency)
If an algorithm decides what you read, you must be able to read the algorithm.
Most feeds are black boxes. Fishwrap is a **Fishbowl**. Our scoring logic is a clear, simple Python script (`scoring.py`) that you can audit, edit, and control. You decide if "AI Hype" gets a boost or a penalty. You are the Editor-in-Chief.

### 3. The Aperture of Time
We don't just aggregate; we condense.
In *Anathem*, the intellectuals (Avout) filtered information through time to separate signal from noise.
*   **The Feed (The Saecular World):** Screams about everything, instantly. We ignore this.
*   **The Paper (1-Day Aperture):** A 24-hour summary. Only what matters *today*.
*   **The Chronicle (1-Year Aperture):** (Coming Soon) A re-aggregation of the year's best stories. As in *Anathem*, "the only criterion for a news item... was that it still had to seem interesting."

---

## The Service: RSS Bankruptcy

Do you have 2,000 unread items in Feedly? Do you have a "Read Later" folder in Pocket that is effectively a graveyard?

**You are suffering from Information Hoarding.**

Fishwrap is your bankruptcy lawyer. We read the 2,000 items for you. We apply *your* rules to find the 15 that matter. We print them into a beautiful, distraction-free edition. We throw the rest in the trash.

### Who is this for?
*   **The Hacker:** Who wants to `git clone` their news consumption and write Python rules to banish "Individual-1" from their reality.
*   **The Specialist:** Who needs a high-signal "briefing" on **AI**, **Cybersecurity**, or **Pop Culture** without the SEO sludge.
*   **The Curator:** Who wants to publish a "Daily Digest" for their team or community.

---

## Get Started

Fishwrap is a Python application you run on your own machine.

1.  **Clone the Newsroom:**
    ```bash
    git clone https://github.com/maxspevack/fishwrap.git
    cd fishwrap
    ```

2.  **Run the Demo:**
    ```bash
    make setup
    make run-vanilla
    ```

3.  **Read:**
    Open `demo/output/latest.html` in your browser.

[View Source on GitHub](https://github.com/maxspevack/fishwrap){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 } [See the Live Demo](https://dailyclamour.com){: .btn .fs-5 .mb-4 .mb-md-0 }