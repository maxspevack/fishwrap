"""
fishwrap.enhancer — full text for the stories that made the paper.

Reads the newest runsheet, scrapes full text for each published story that
the database does not already hold, and stores it on the article row. Writes
nothing else: the runsheet is the editor's record and stays as written.
"""
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from newspaper import Article as NewsArticle
from tqdm import tqdm

from fishwrap import _config
from fishwrap import runsheet
from fishwrap import utils
from fishwrap.db import repository

MAX_WORKERS = 20


def enhance_article(link):
    """Scrape full text for one link. Returns (success, text)."""
    if not link:
        return False, None
    utils.rate_limit(utils.get_domain(link))
    try:
        na = NewsArticle(link)
        na.download()
        na.parse()
        text = na.text
        if len(text) > _config.MAX_ARTICLE_LENGTH:
            text = text[:_config.MAX_ARTICLE_LENGTH] + "... [Truncated]"
        return True, text
    except Exception as e:
        print(f"Error scraping {link}: {e}")
        return False, None


def run_enhancer():
    timer = utils.Stopwatch().start()
    path = runsheet.latest(Path(_config.OUTPUT_DIR))
    if path is None:
        raise SystemExit(f"[ENHANCER] no runsheet under {_config.OUTPUT_DIR}; run the editor first")
    _header, records = runsheet.read(path)
    published = [r["link"] for r in records if r["fate"]["published"]]
    print(f"\n[ENHANCER] Starting Parallel Enhancement... (Runsheet: {len(published)} published stories)")

    have = repository.get_content_by_links(published)
    to_fetch = [link for link in published if not have.get(link, {}).get("is_enhanced")]
    stats = {'hits': len(published) - len(to_fetch), 'fetches': 0, 'errors': 0}

    if to_fetch:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(enhance_article, link): link for link in to_fetch}
            with tqdm(total=len(to_fetch), desc="Enhancing", unit="article") as pbar:
                for future in as_completed(futures):
                    link = futures[future]
                    try:
                        ok, text = future.result()
                        if ok and repository.update_enhancement_by_link(link, text):
                            stats['fetches'] += 1
                        else:
                            stats['errors'] += 1
                    except Exception:
                        print(f"CRITICAL ERROR processing {link}:")
                        traceback.print_exc()
                        stats['errors'] += 1
                    pbar.update(1)

    print(f"\n[ENHANCER] Finished in {timer.stop():.2f}s. "
          f"Hits: {stats['hits']}, Fetches: {stats['fetches']}, Errors: {stats['errors']}")


if __name__ == "__main__":
    run_enhancer()
