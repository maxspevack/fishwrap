import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from fishwrap import _config
from fishwrap import utils
from fishwrap import editor
from fishwrap import scoring

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
                'id': post['id'],
                'title': post['title'],
                'link': link,
                'source_url': url,
                'timestamp': post['created_utc'],
                'content': post.get('selftext', ''),
                'categories': [post.get('subreddit', 'reddit'), post.get('link_flair_text') or ''],
                'stats_comments': post['num_comments'],
                'stats_score': post['score'],
                'thumbnail': post.get('thumbnail', ''),
                'base_boosts': _config.SCORING_PROFILES['dynamic']['base_boosts'],
                'boosts_count': 0
            }
            article['categories'] = [c for c in article['categories'] if c]
            articles.append(article)
    except Exception as e:
        # Return empty list on failure, let caller handle logging if needed
        # but for concurrent execution, maybe return exception? 
        # For now, just print to stderr or tqdm.write
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
                        article['id'] = id_elem.text if (id_elem is not None and id_elem.text) else (link_elem.attrib.get('href') if link_elem is not None else article['title'])
                        article['link'] = link_elem.attrib.get('href') if link_elem is not None else ""
                    else:
                        guid = item.find("guid")
                        link = item.find("link")
                        article['id'] = guid.text if (guid is not None and guid.text) else (link.text if (link is not None and link.text) else article['title'])
                        article['link'] = link.text if link is not None else ""

                        comments_elem = item.find("comments")
                        if comments_elem is not None:
                            article['comments_url'] = comments_elem.text
                    
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
                    article['boosts_count'] = 0

                    if 'hnrss.org' in url:
                        points_match = re.search(r'Points: (\d+)', (article.get('content') or ''))
                        comments_match = re.search(r'Comments: (\d+)', (article.get('content') or ''))
                        if points_match: article['stats_score'] = int(points_match.group(1))
                        if comments_match: article['stats_comments'] = int(comments_match.group(1))
                    
                    items.append(article)
    except Exception as e:
        # We catch here to ensure one bad feed doesn't crash the thread
        # In a real app we might log this better
        return [] 
        
    return items

def upsert_article(db, new_article):
    """
    Upsert Logic with Pre-Computed Scoring.
    """
    aid = new_article['id']
    res = "new"
    
    if aid in db:
        existing = db[aid]
        res = "updated"
        
        # Merge Persistent Data
        new_article['stats_score'] = max(existing.get('stats_score', 0), new_article.get('stats_score', 0))
        new_article['stats_comments'] = max(existing.get('stats_comments', 0), new_article.get('stats_comments', 0))
        
        if existing['timestamp'] > new_article['timestamp']:
             new_article['timestamp'] = existing['timestamp']
             
        if 'comments_url' in existing and 'comments_url' not in new_article:
             new_article['comments_url'] = existing['comments_url']

        # Preserver Enhancer Artifacts
        if 'full_content' in existing: new_article['full_content'] = existing['full_content']
        if 'comments_full' in existing: new_article['comments_full'] = existing['comments_full']
        if 'is_enhanced' in existing: new_article['is_enhanced'] = existing['is_enhanced']
             
    # --- PRE-COMPUTE SCORING ---
    cat, cls_debug = editor.classify_article(new_article)
    score, breakdown = scoring.compute_score(new_article, section=cat)
    
    new_article['_computed_category'] = cat
    new_article['_computed_score'] = score
    new_article['_computed_breakdown'] = breakdown
    new_article['_computed_debug'] = cls_debug
    # ---------------------------

    db[aid] = new_article
    return res

def update_database():
    # 1. Load existing DB
    if os.path.exists(_config.ARTICLES_DB_FILE):
        try:
            with open(_config.ARTICLES_DB_FILE, 'r') as f:
                db = json.load(f)
        except json.JSONDecodeError:
            db = {}
    else:
        db = {}
    
    initial_db_count = len(db)
    
    # 2. Prune Old Articles (Retention Memory)
    current_time = datetime.now().timestamp()
    cutoff = current_time - (_config.EXPIRATION_HOURS * 3600 * 2)
    
    keys_to_delete = [aid for aid, article in db.items() if article['timestamp'] < cutoff]
    for k in keys_to_delete:
        del db[k]
        
    # 3. Fetch Feeds Concurrently
    urls = _config.FEEDS
    
    stats = {
        'feeds_processed': 0,
        'items_fetched': 0,
        'new_items': 0,
        'updated_items': 0
    }

    print(f"\n[FETCHER] Starting Parallel Fetch... (DB: {initial_db_count} -> {len(db)} after pruning)")
    
    # Use ThreadPoolExecutor for I/O bound tasks
    MAX_WORKERS = 10 
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit all tasks
        future_to_url = {executor.submit(process_feed, url, cutoff): url for url in urls}
        
        # Process as they complete
        with tqdm(total=len(urls), desc="Fetching Feeds", unit="feed") as pbar:
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    items = future.result()
                    
                    stats['items_fetched'] += len(items)
                    stats['feeds_processed'] += 1
                    
                    # Upsert must happen in main thread or be locked (main thread is easiest here)
                    for article in items:
                        if article['timestamp'] < cutoff: continue
                        
                        res = upsert_article(db, article)
                        if res == "new":
                            stats['new_items'] += 1
                        else:
                            stats['updated_items'] += 1
                            
                except Exception as e:
                    tqdm.write(f"[!] Exception fetching {url}: {e}")
                
                pbar.update(1)

    # 4. Save
    with open(_config.ARTICLES_DB_FILE, 'w') as f:
        json.dump(db, f, indent=2)

    # 5. Summary Report
    print("\n" + "="*40)
    print(f" FETCHER SUMMARY")
    print("="*40)
    print(f" Feeds Processed:   {stats['feeds_processed']}/{len(urls)}")
    print(f" Total Items Seen:  {stats['items_fetched']}")
    print(f" New Items Added:   {stats['new_items']}")
    print(f" Existing Updated:  {stats['updated_items']}")
    print(f" Database Size:     {len(db)}")
    
    # 6. Source Dominance Report
    # Calculate simple histogram from the current DB or just the new items?
    # The user request implies "Source Dominance" which usually means "Who is flooding the DB?"
    # So we should look at the *entire* DB to see the current state of the pool.
    
    source_counts = {}
    for article in db.values():
        # simple parse of domain from source_url
        try:
            domain = article.get('source_url', '').split('/')[2]
        except:
            domain = 'unknown'
        source_counts[domain] = source_counts.get(domain, 0) + 1
        
    sorted_sources = sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    print("-" * 40)
    print(" Source Dominance (Top 5 in DB)")
    print("-" * 40)
    for domain, count in sorted_sources:
        print(f" {count:<4} : {domain}")
    print("="*40 + "\n")

if __name__ == "__main__":
    update_database()