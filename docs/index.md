---
layout: default
title: Home
nav_order: 1
---

# Fishwrap 🐟📰

**"Yesterday's News, Tomorrow's Wrapper."**

Fishwrap is a bespoke, automated newspaper engine for the digital age. It transforms the chaos of the internet into a calm, curated, and distraction-free daily briefing.

[Get Started on GitHub](https://github.com/maxspevack/fishwrap){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 } [View Demo](https://dailyclamour.com){: .btn .fs-5 .mb-4 .mb-md-0 }

---

## Why Fishwrap?

### 🕵️‍♀️ Your Private Newsroom
Stop doom-scrolling. Fishwrap acts as your personal editorial staff. It fetches content from your favorite RSS feeds, Reddit communities, and Hacker News discussions, applying *your* specific rules to decide what matters.

### 🚫 No Clickbait, Just Content
The built-in **Enhancer** scrapes the full text of every article. You get a clean, unified reading experience without ads, pop-ups, or paywall snippets. Read the story, not the wrapper.

### 📊 Smart Scoring
Fishwrap doesn't just list headlines. It calculates an **Impact Score** for every item based on votes, comments, and freshness. You define the formula. Want to prioritize heated discussions on Hacker News? You can.

---

## Quick Start

Fishwrap is a Python application you run on your own machine or server.

1.  **Clone the Repo:**
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

---

## Documentation

*   [**Versioning Strategy**](VERSIONING.md): How we manage releases.
*   [**Release Notes**](RELEASE_NOTES.md): What's new in the latest version.
*   [**Architecture Deep Dive**](https://github.com/maxspevack/fishwrap/blob/main/fishwrap/README.md): Understanding the Fetch/Edit/Enhance/Print pipeline.

---

## About

Fishwrap is an open-source project created by [Max Spevack](https://spevack.org). It is licensed under the BSD 3-Clause License.
