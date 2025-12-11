import json
import urllib.request
from urllib.parse import urlparse
import os
import time
import html
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from newspaper import Article 
from fishwrap import _config
from fishwrap import utils
import xml.etree.ElementTree as ET

# Load Cookie
DEFECTOR_COOKIE = None
if os.path.exists(_config.SECRETS_FILE):
    try:
        with open(_config.SECRETS_FILE, 'r') as f:
            secrets = json.load(f)
            DEFECTOR_COOKIE = secrets.get('defector_cookie')
    except Exception:
        pass

# --- Helper Functions ---
def fetch_json(url):
    try:
        content = utils.fetch_url(url)
        if content:
            return json.loads(content)
    except Exception as e:
        # print(f"Error parsing JSON from {url}: {e}")
        pass
    return None

def extract_article_text_newspaper3k(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        return None

def fetch_hn_comments_api(item_id, limit=10):
    comments = []
    try:
        api_url = f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json"
        item_data = fetch_json(api_url)
        if not item_data or 'kids' not in item_data:
            return []
        # Sequential fetch within a thread is fine, or could parallelize this too?
        # For now, keep simple. 10 requests is fast enough if the main loop is parallel.
        for kid_id in item_data['kids'][:limit]:
            c_data = fetch_json(f"https://hacker-news.firebaseio.com/v0/item/{kid_id}.json")
            if c_data and 'text' in c_data and not c_data.get('deleted'):
                user = c_data.get('by', 'anon')
                text = html.unescape(c_data['text'])
                text = re.sub(r'<[^>]+>', '', text)
                comments.append(f"{user}: {text}")
    except Exception:
        pass
    return comments

def extract_hn_id(url):
    match = re.search(r'id=(\d+)', url)
    if match:
        return match.group(1)
    return None

def fetch_lwn_comments(article_url):
    comments = []
    try:
        match = re.search(r'Articles/(\d+)', article_url)
        if match:
            aid = match.group(1)
            rss_url = f"https://lwn.net/headlines/{aid}/"
            rss_content = utils.fetch_url(rss_url)
            if rss_content:
                try:
                    root = ET.fromstring(rss_content)
                    items = root.findall('./channel/item')
                    for item in items[:7]:
                        title = item.find('title').text or ''
                        desc = item.find('description').text or ''
                        clean_desc = re.sub(r'<[^>]+>', '', html.unescape(desc))[:300]
                        clean_desc = clean_desc.replace('\n', ' ').strip()
                        if clean_desc:
                            comments.append(f"{title}: {clean_desc}")
                except ET.ParseError:
                    pass
    except Exception:
        pass
    return comments

def parse_reddit_comments_json(json_data, limit=10):
    comments = []
    if not json_data or not isinstance(json_data, list) or len(json_data) < 2:
        return []
    try:
        for c in json_data[1]['data']['children']:
            if c['kind'] == 't1':
                data = c['data']
                if not data.get('distinguished') and not data.get('stickied') and data.get('body'):
                    comments.append(f"u/{data.get('author')}: {data.get('body')}")
                    if len(comments) >= limit:
                        break
    except Exception:
        pass
    return comments

def process_article(article, db_cache):
    """
    Enhances a single article.
    Returns (enhanced_article, was_cache_hit, has_error)
    """
    link = article.get('link', '')
    source_url = article.get('source_url', '')
    aid = str(article.get('id'))
    
    # Initialize defaults
    article['full_content'] = article.get('content') or ''
    article['comments_full'] = []
    
    was_cache_hit = False
    has_error = False

    if not link:
        return article, False, False # Skip, effectively processed

    # Check DB Cache
    cached_art = db_cache.get(aid)
    has_cached_content = cached_art and cached_art.get('full_content') and (len(cached_art['full_content']) > 20 or cached_art['full_content'].startswith("See discussion:"))
    has_cached_comments = cached_art and cached_art.get('comments_full') and len(cached_art['comments_full']) > 0
    
    domain = urlparse(link).netloc
    needs_fetch = True
    
    is_discussion_site = 'reddit.com' in domain or 'news.ycombinator' in domain or 'hnrss' in source_url
    if has_cached_content:
        if is_discussion_site:
            if has_cached_comments: needs_fetch = False
        else:
            needs_fetch = False
            
    if not needs_fetch:
        article['full_content'] = cached_art.get('full_content', article['full_content'])
        article['comments_full'] = cached_art.get('comments_full', [])
        return article, True, False

    # Perform Enhancement (Network I/O)
    try:
        # --- REDDIT ---
        if 'reddit.com' in domain:
            json_url = link.split('?')[0] + '.json'
            data = fetch_json(json_url)
            if data:
                article['comments_full'] = parse_reddit_comments_json(data)
                if "See discussion:" not in article['full_content'] and not article['full_content']:
                    article['full_content'] = f"See discussion: {link}"

        # --- HN / LWN ---
        elif 'hnrss' in source_url or 'news.ycombinator' in domain or 'lwn.net' in domain:
            if 'hnrss' in source_url or 'news.ycombinator' in domain:
                hn_id = extract_hn_id(link)
                if not hn_id:
                    m = re.search(r'item\?id=(\d+)', article['full_content'])
                    if m: hn_id = m.group(1)
                if hn_id:
                    article['comments_full'] = fetch_hn_comments_api(hn_id)
            
            if 'lwn.net' in domain:
                article['comments_full'] = fetch_lwn_comments(link)

            if 'news.ycombinator.com' not in domain:
                txt = extract_article_text_newspaper3k(link)
                if txt:
                    article['full_content'] = txt
            
            if 'lwn.net' in domain and (not article['full_content'] or article['full_content'].strip().startswith("Copyright")):
                    article['full_content'] = article.get('content') or "No content available."

        # --- DEFECTOR ---
        elif 'defector.com' in domain and DEFECTOR_COOKIE:
            headers = {'User-Agent': _config.USER_AGENT, 'Cookie': DEFECTOR_COOKIE}
            html_c = utils.fetch_url(link, headers=headers)
            if html_c:
                art = Article('')
                art.set_html(html_c)
                art.parse()
                article['full_content'] = art.text
            else:
                has_error = True

        # --- GENERIC ---
        else:
            txt = extract_article_text_newspaper3k(link)
            if txt and len(txt) > 100:
                article['full_content'] = txt
            elif not txt or len(txt) <= 100:
                has_error = True
                
    except Exception:
        has_error = True

    return article, False, has_error

def enhance_articles():
    if not os.path.exists(_config.RUN_SHEET_FILE):
        return
    
    with open(_config.RUN_SHEET_FILE, 'r') as f:
        run_sheet_raw = json.load(f)

    # Load master DB for persistence/caching
    db = {}
    if os.path.exists(_config.ARTICLES_DB_FILE):
        try:
            with open(_config.ARTICLES_DB_FILE, 'r') as f:
                db = json.load(f)
        except Exception:
            pass

    # Flatten run sheet for parallel processing
    # We keep track of sections via 'section' key injected into article dict
    all_articles = []
    for sid, arts in run_sheet_raw.items():
        for a in arts:
            a['section'] = sid
            all_articles.append(a)

    print(f"\n[ENHANCER] Starting Parallel Enhancement... (Run Sheet: {len(all_articles)} items)")
    
    stats = {'hits': 0, 'misses': 0, 'errors': 0}
    enhanced_results = {sid: [] for sid in run_sheet_raw.keys()}
    db_updated = False
    
    MAX_WORKERS = 10
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit tasks
        future_to_article = {executor.submit(process_article, article, db): article for article in all_articles}
        
        with tqdm(total=len(all_articles), desc="Enhancing", unit="article") as pbar:
            for future in as_completed(future_to_article):
                try:
                    enhanced_art, hit, error = future.result()
                    
                    if hit: stats['hits'] += 1
                    else: stats['misses'] += 1
                    if error: stats['errors'] += 1
                    
                    # Add to result bucket
                    sid = enhanced_art['section']
                    enhanced_results[sid].append(enhanced_art)
                    
                    # Update Master DB (if new data found)
                    if not hit and not error:
                        aid = str(enhanced_art.get('id'))
                        if aid in db:
                            db[aid]['full_content'] = enhanced_art.get('full_content')
                            db[aid]['comments_full'] = enhanced_art.get('comments_full')
                            db_updated = True
                            
                except Exception as e:
                    stats['errors'] += 1
                    tqdm.write(f"[!] Enhancer Exception: {e}")
                
                pbar.update(1)
        
    if db_updated:
        with open(_config.ARTICLES_DB_FILE, 'w') as f:
            json.dump(db, f, indent=2)

    with open(_config.ENHANCED_ISSUE_FILE, 'w') as f:
        json.dump(enhanced_results, f, indent=2)
        
    print("\n" + "="*40)
    print(f" ENHANCER SUMMARY")
    print("="*40)
    print(f" Total Articles: {len(all_articles)}")
    print(f" Cache Hits:     {stats['hits']}")
    print(f" Network Fetches:{stats['misses']}")
    print(f" Errors/Partial: {stats['errors']}")
    print("="*40 + "\n")

if __name__ == "__main__":
    enhance_articles()