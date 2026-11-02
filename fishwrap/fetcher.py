"""
fishwrap.fetcher — intake.

Fetches every feed in the masthead concurrently, parses RSS/Atom, and upserts
each item into the newsroom database keyed by link. Nothing is classified or
ranked here: the editor recomputes everything from the masthead on every
build. The fetcher persists the raw article and nothing else.

Vote-ranked sources (Reddit JSON, Hacker News via hnrss) were removed on
2026-11-01 along with their score/comment plumbing. Votes are not an ordering
input; coverage across sources is.
"""
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import defusedxml.ElementTree as ET
from tqdm import tqdm

from fishwrap import _config
from fishwrap import utils
from fishwrap.db import repository
from fishwrap.log import get_logger

log = get_logger(__name__)

NAMESPACES = {
    'atom': 'http://www.w3.org/2005/Atom',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'content': 'http://purl.org/rss/1.0/modules/content/',
    'media': 'http://search.yahoo.com/mrss/'
}


def _text(elem):
    return elem.text if (elem is not None and elem.text) else None


def _title(elem):
    """Feed titles arrive with embedded newlines and indentation; collapse them."""
    t = _text(elem)
    return " ".join(t.split()) if t else None


def parse_feed(raw_data, url, cutoff):
    """Parse one RSS or Atom document into article dicts.

    Every dict carries exactly the keys the Article model accepts
    (scripts/test_fetcher_resilience.py holds that contract). Items older
    than `cutoff` (epoch seconds) are dropped here to save memory.
    """
    root = ET.fromstring(raw_data)
    is_atom = 'feed' in root.tag
    atom = NAMESPACES['atom']

    if is_atom:
        xml_items = root.findall(f"{{{atom}}}entry")
    else:
        channel = root.find('channel')
        xml_items = channel.findall('item') if channel is not None else []

    items = []
    for item in xml_items:
        article = {}
        if is_atom:
            article['title'] = _title(item.find(f"{{{atom}}}title")) or "No Title"
            link_elem = item.find(f"{{{atom}}}link")
            link = link_elem.attrib.get('href') if link_elem is not None else ""
            article['external_id'] = _text(item.find(f"{{{atom}}}id")) or link or article['title']
            date_text = _text(item.find(f"{{{atom}}}updated")) or _text(item.find(f"{{{atom}}}published"))
            content_val = _text(item.find(f"{{{atom}}}content")) or ""
        else:
            article['title'] = _title(item.find("title")) or "No Title"
            link = _text(item.find("link")) or ""
            article['external_id'] = _text(item.find("guid")) or link or article['title']
            comments_url = _text(item.find("comments"))
            if comments_url:
                article['comments_url'] = comments_url
            date_text = _text(item.find("pubDate"))
            content_val = (_text(item.find(f"{{{NAMESPACES['content']}}}encoded"))
                           or _text(item.find("description")) or "")

        article['link'] = link
        article['source_url'] = url
        article['timestamp'] = utils.parse_date(date_text)
        if article['timestamp'] < cutoff:
            continue
        article['content'] = content_val
        items.append(article)
    return items


def process_feed(url, cutoff):
    """Fetch and parse a single feed. Returns a list of article dicts; an
    unreachable or unparseable feed returns [] and is logged, never raised."""
    try:
        raw_data = utils.fetch_url(url, timeout=30)
        if not raw_data:
            return []
        return parse_feed(raw_data, url, cutoff)
    except ET.ParseError as e:
        log.warning("xml parse failed for %s: %s", url, e)
        return []
    except Exception:
        log.exception("unexpected error parsing feed %s", url)
        return []


def update_database():
    timer = utils.Stopwatch().start()
    initial_db_count = repository.get_total_count()

    # Retention: keep twice the edition window so yesterday's leaders are
    # still in the DB for dedup's 48 h window.
    cutoff_hours = _config.EXPIRATION_HOURS * 2
    deleted_count = repository.prune_old_articles(hours=cutoff_hours)

    urls = _config.FEEDS
    stats = {'feeds_processed': 0, 'items_fetched': 0, 'new_items': 0, 'updated_items': 0}

    print(f"\n[FETCHER] Starting Parallel Fetch... (DB: {initial_db_count} -> Pruned: {deleted_count})")

    cutoff_ts = time.time() - (cutoff_hours * 3600)
    max_workers = getattr(_config, 'FETCH_WORKERS', 10)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(process_feed, url, cutoff_ts): url for url in urls}
        with tqdm(total=len(urls), desc="Fetching Feeds", unit="feed") as pbar:
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    items = future.result()
                    stats['items_fetched'] += len(items)
                    stats['feeds_processed'] += 1
                    for article in items:
                        if repository.upsert_article(article) == "new":
                            stats['new_items'] += 1
                        else:
                            stats['updated_items'] += 1
                except Exception as e:
                    tqdm.write(f"[!] Exception fetching {url}: {e}")
                pbar.update(1)

    final_count = repository.get_total_count()
    duration = timer.stop()
    print(f"\n[FETCHER] Processed {stats['feeds_processed']}/{len(urls)} feeds in {duration:.2f}s. "
          f"{stats['new_items']} new, {stats['updated_items']} updated. DB Size: {final_count}.")


if __name__ == "__main__":
    update_database()
