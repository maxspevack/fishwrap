import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
import os
import re
from fishwrap import _config
from fishwrap import utils

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
    # Reddit is handled separately in fetch_reddit_json, but conceptually dynamic
    return 'static'

def fetch_reddit_json(url):
    """Fetches Reddit JSON and standardizes to match our article format."""
    #print(f"[FETCHER] Fetching Reddit JSON: {url}...")
    articles = []
    try:
        data_str = utils.fetch_url(url)
        if not data_str:
            return []
            
        data = json.loads(data_str)
            
        children = data['data']['children']
        for child in children:
            post = child['data']
            
            # Ensure absolute URL for links
            permalink = post['permalink']
            link = f"https://www.reddit.com{permalink}"
            
            article = {
                'id': post['id'],
                'title': post['title'],
                'link': link,
                'source_url': url,
                'timestamp': post['created_utc'],
                'content': post.get('selftext', ''), # Raw markdown/text
                'categories': [post.get('subreddit', 'reddit'), post.get('link_flair_text') or ''],
                'stats_comments': post['num_comments'],
                'stats_score': post['score'],
                'thumbnail': post.get('thumbnail', ''),
                # New scoring fields, initialized by Fetcher
                'base_boosts': _config.SCORING_PROFILES['dynamic']['base_boosts'],
                'boosts_count': 0
            }
            # Log initialization
            #print(f"[FETCHER] Init: '{article['title']}' -> Base Boosts: {article['base_boosts']}")
            
            # Clean up None in categories
            article['categories'] = [c for c in article['categories'] if c]
            
            articles.append(article)
    except Exception as e:
        print(f"Error fetching Reddit JSON {url}: {e}")
        
    return articles

def upsert_article(db, new_article):
    """
    Simple Upsert Logic.
    - If seen in DB -> Update stats (max) and timestamp (latest).
    - If new -> Insert.
    """
    aid = new_article['id']
    
    if aid in db:
        # Update Existing
        existing = db[aid]
        
        # Keep max stats (e.g. if Reddit score goes up)
        existing['stats_score'] = max(existing.get('stats_score', 0), new_article.get('stats_score', 0))
        existing['stats_comments'] = max(existing.get('stats_comments', 0), new_article.get('stats_comments', 0))
        
        # Update timestamp to latest seen (keeps it fresh in pruning window)
        if new_article['timestamp'] > existing['timestamp']:
            existing['timestamp'] = new_article['timestamp']
            
        # Backfill comments_url if missing in existing but present in new
        if 'comments_url' not in existing and 'comments_url' in new_article:
            existing['comments_url'] = new_article['comments_url']
            
        return "updated"
        
    else:
        # Insert New
        db[aid] = new_article
        return "new"


import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
import os
import re
from tqdm import tqdm
from fishwrap import _config
from fishwrap import utils

# ... (Keep imports and constants)

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
    
    # 2. Prune Old Articles
    current_time = datetime.now().timestamp()
    cutoff = current_time - (_config.EXPIRATION_HOURS * 3600)
    
    keys_to_delete = [aid for aid, article in db.items() if article['timestamp'] < cutoff]
    for k in keys_to_delete:
        del db[k]
        
    # 3. Fetch Feeds
    urls = _config.FEEDS
    
    stats = {
        'feeds_processed': 0,
        'items_fetched': 0,
        'new_items': 0,
        'updated_items': 0
    }

    print(f"\n[FETCHER] Starting... (DB: {initial_db_count} -> {len(db)} after pruning)")
    
    # Progress Bar for Feeds
    with tqdm(total=len(urls), desc="Fetching Feeds", unit="feed") as pbar:
        for url in urls:
            try:
                # Branch for JSON vs XML
                items = []
                if url.endswith('.json'):
                    items = fetch_reddit_json(url)
                else:
                    # Determine scoring profile for RSS/Atom feeds
                    scoring_profile_key = get_scoring_profile_for_url(url)
                    profile = _config.SCORING_PROFILES[scoring_profile_key]

                    raw_data = utils.fetch_url(url)
                    if raw_data:
                        root = ET.fromstring(raw_data)
                        is_atom = 'feed' in root.tag
                        
                        xml_items = root.findall(f"{{{NAMESPACES['atom']}}}entry") if is_atom else (root.find('channel').findall('item') if root.find('channel') is not None else [])
                        
                        for item in xml_items:
                            article = {}
                            # ... (Title extraction)
                            if is_atom:
                                title_elem = item.find(f"{{{NAMESPACES['atom']}}}title")
                            else:
                                title_elem = item.find("title")
                            article['title'] = title_elem.text if title_elem is not None else "No Title"

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

                                # Capture comments URL (standard RSS field, used by HN)
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
                            
                            # Filter old
                            if article['timestamp'] < cutoff: continue

                            # Content
                            if is_atom:
                                content_elem = item.find(f"{{{NAMESPACES['atom']}}}content")
                                article['content'] = content_elem.text if content_elem is not None else ""
                            else:
                                content_enc = item.find(f"{{{NAMESPACES['content']}}}encoded")
                                desc = item.find("description")
                                article['content'] = content_enc.text if content_enc is not None else (desc.text if desc is not None else "")
                            
                            # Init Stats
                            article['base_boosts'] = profile['base_boosts']
                            article['stats_score'] = 0
                            article['stats_comments'] = 0
                            article['boosts_count'] = 0

                            # HN Parsing
                            if 'hnrss.org' in url:
                                points_match = re.search(r'Points: (\d+)', (article.get('content') or ''))
                                comments_match = re.search(r'Comments: (\d+)', (article.get('content') or ''))
                                if points_match: article['stats_score'] = int(points_match.group(1))
                                if comments_match: article['stats_comments'] = int(comments_match.group(1))
                            
                            items.append(article)

                # Process Parsed Items
                stats['items_fetched'] += len(items)
                for article in items:
                    if article['timestamp'] < cutoff: continue
                    
                    # Upsert
                    res = upsert_article(db, article)
                    if res == "new":
                        stats['new_items'] += 1
                    else:
                        stats['updated_items'] += 1
                
                stats['feeds_processed'] += 1
                
            except Exception as e:
                tqdm.write(f"[!] Error processing {url}: {e}")
            
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
    print("="*40 + "\n")

if __name__ == "__main__":
    update_database()
