import json
import urllib.request
import xml.etree.ElementTree as ET
import time
from datetime import datetime
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from fishwrap import _config
from fishwrap import utils
from fishwrap import editor
from fishwrap import scoring
from fishwrap.db import repository

NAMESPACES = {
    'atom': 'http://www.w3.org/2005/Atom',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'content': 'http://purl.org/rss/1.0/modules/content/',
    'media': 'http://search.yahoo.com/mrss/'
}

def get_scoring_profile_for_url(url):
    """Determines the appropriate scoring profile key for a given URL."""
    if 'hnrss.org' in url:
        return 'dynamic' # Treat HN as dynamic to use weights
    return 'static'

def fetch_reddit_json(url):
    """Fetches Reddit JSON and standardizes to match our article format."""
    articles = []
    try:
        data_str = utils.fetch_url(url)
        if not data_str:
            return []
            
        data = json.loads(data_str)
            
        children = data['data']['children']
        for child in children:
            post = child['data']
            
            permalink = post['permalink']
            link = f"https://www.reddit.com{permalink}"
            
            article = {
                'title': post['title'],
                'link': link,
                'source_url': url,
                'external_id': post['id'], # Map 'id' to 'external_id'
                'timestamp': post['created_utc'],
                'content': post.get('selftext', ''),
                'categories': [post.get('subreddit', 'reddit'), post.get('link_flair_text') or ''],
                'stats_comments': post['num_comments'],
                'stats_score': post['score'],
                # 'base_boosts': ... logic handled in process_feed loop
            }
            article['categories'] = [c for c in article['categories'] if c]
            articles.append(article)
    except Exception as e:
        pass 
        
    return articles

def process_feed(url, cutoff):
    """
    Fetches and parses a single feed (RSS/Atom/JSON).
    Returns a list of article dicts.
    """
    items = []
    try:
        if url.endswith('.json'):
            items = fetch_reddit_json(url)
        else:
            scoring_profile_key = get_scoring_profile_for_url(url)
            profile = _config.SCORING_PROFILES[scoring_profile_key]

            raw_data = utils.fetch_url(url)
            if raw_data:
                # Basic XML parsing
                try:
                    root = ET.fromstring(raw_data)
                except ET.ParseError:
                    return [] # Skip malformed XML

                is_atom = 'feed' in root.tag
                
                xml_items = root.findall(f"{{{NAMESPACES['atom']}}}entry") if is_atom else (root.find('channel').findall('item') if root.find('channel') is not None else [])
                
                for item in xml_items:
                    article = {}
                    # Title
                    if is_atom:
                        title_elem = item.find(f"{{{NAMESPACES['atom']}}}title")
                    else:
                        title_elem = item.find("title")
                    
                    article['title'] = title_elem.text if (title_elem is not None and title_elem.text) else "No Title"

                    # ID/Link
                    if is_atom:
                        id_elem = item.find(f"{{{NAMESPACES['atom']}}}id")
                        link_elem = item.find(f"{{{NAMESPACES['atom']}}}link")
                        ext_id = id_elem.text if (id_elem is not None and id_elem.text) else (link_elem.attrib.get('href') if link_elem is not None else article['title'])
                        link = link_elem.attrib.get('href') if link_elem is not None else ""
                    else:
                        guid = item.find("guid")
                        link_elem = item.find("link")
                        ext_id = guid.text if (guid is not None and guid.text) else (link_elem.text if (link_elem is not None and link_elem.text) else article['title'])
                        link = link_elem.text if link_elem is not None else ""

                        comments_elem = item.find("comments")
                        if comments_elem is not None:
                            article['comments_url'] = comments_elem.text
                    
                    article['external_id'] = ext_id
                    article['link'] = link
                    article['source_url'] = url
                    
                    # Date
                    if is_atom:
                        date_elem = item.find(f"{{{NAMESPACES['atom']}}}updated")
                        if date_elem is None: date_elem = item.find(f"{{{NAMESPACES['atom']}}}published")
                        date_text = date_elem.text if date_elem is not None else None
                    else:
                        date_elem = item.find("pubDate")
                        date_text = date_elem.text if date_elem is not None else None
                    
                    article['timestamp'] = utils.parse_date(date_text)
                    
                    # Filter old immediately to save memory
                    if article['timestamp'] < cutoff: continue

                    # Content
                    if is_atom:
                        content_elem = item.find(f"{{{NAMESPACES['atom']}}}content")
                        article['content'] = content_elem.text if (content_elem is not None and content_elem.text) else ""
                    else:
                        content_enc = item.find(f"{{{NAMESPACES['content']}}}encoded")
                        desc = item.find("description")
                        
                        content_val = ""
                        if content_enc is not None and content_enc.text:
                            content_val = content_enc.text
                        elif desc is not None and desc.text:
                            content_val = desc.text
                            
                        article['content'] = content_val
                    
                    article['base_boosts'] = profile['base_boosts']
                    article['stats_score'] = 0
                    article['stats_comments'] = 0

                    if 'hnrss.org' in url:
                        points_match = re.search(r'Points: (\d+)', (article.get('content') or ''))
                        comments_match = re.search(r'Comments: (\d+)', (article.get('content') or ''))
                        if points_match: article['stats_score'] = int(points_match.group(1))
                        if comments_match: article['stats_comments'] = int(comments_match.group(1))
                    
                    items.append(article)
    except Exception as e:
        return [] 
        
    return items

def update_database():
    initial_db_count = repository.get_total_count()
    
    # 2. Prune Old Articles (Retention Memory)
    # Using hardcoded 72h default or config driven
    cutoff_hours = _config.EXPIRATION_HOURS * 2 
    deleted_count = repository.prune_old_articles(hours=cutoff_hours)
    
    # 3. Fetch Feeds Concurrently
    urls = _config.FEEDS
    
    stats = {
        'feeds_processed': 0,
        'items_fetched': 0,
        'new_items': 0,
        'updated_items': 0
    }

    print(f"\n[FETCHER] Starting Parallel Fetch... (DB: {initial_db_count} -> Pruned: {deleted_count})")
    
    current_ts = time.time()
    cutoff_ts = current_ts - (cutoff_hours * 3600)

    # Use ThreadPoolExecutor for I/O bound tasks
    MAX_WORKERS = 10 
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit all tasks
        future_to_url = {executor.submit(process_feed, url, cutoff_ts): url for url in urls}
        
        # Process as they complete
        with tqdm(total=len(urls), desc="Fetching Feeds", unit="feed") as pbar:
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    items = future.result()
                    
                    stats['items_fetched'] += len(items)
                    stats['feeds_processed'] += 1
                    
                    for article in items:
                        if article['timestamp'] < cutoff_ts: continue
                        
                        # --- PRE-COMPUTE SCORING ---
                        if 'base_boosts' not in article:
                             article['base_boosts'] = 0

                        cat, cls_debug = editor.classify_article(article)
                        score, breakdown = scoring.compute_score(article, section=cat)
                        
                        article['computed_category'] = cat
                        article['computed_score'] = score
                        article['computed_breakdown'] = breakdown
                        article['computed_debug'] = cls_debug
                        
                        if 'base_boosts' in article: del article['base_boosts']
                        # ---------------------------

                        res = repository.upsert_article(article)
                        
                        if res == "new":
                            stats['new_items'] += 1
                        else:
                            stats['updated_items'] += 1
                            
                except Exception as e:
                    tqdm.write(f"[!] Exception fetching {url}: {e}")
                
                pbar.update(1)

    final_count = repository.get_total_count()

    # Summary Report
    print(f"\n[FETCHER] Processed {stats['feeds_processed']}/{len(urls)} feeds. {stats['new_items']} new, {stats['updated_items']} updated. DB Size: {final_count}.")

if __name__ == "__main__":
    update_database()