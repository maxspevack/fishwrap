import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from newspaper import Article as NewsArticle
from fishwrap.db import repository
from fishwrap import _config
from fishwrap import utils

def enhance_article(article_data):
    """
    Scrapes full text for a single article dict.
    Returns: (success, full_text, comments_list)
    """
    url = article_data.get('link')
    if not url: return False, None, None
    
    # Rate Limit
    domain = utils.get_domain(url)
    utils.rate_limit(domain)
    
    try:
        # Use newspaper3k
        na = NewsArticle(url)
        na.download()
        na.parse()
        
        text = na.text
        
        # Simple Length Check
        if len(text) > _config.MAX_ARTICLE_LENGTH:
            text = text[:_config.MAX_ARTICLE_LENGTH] + "... [Truncated]"
            
        return True, text, [] # Comments scraping is future work
        
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return False, None, None

def run_enhancer():
    """
    Reads the Run Sheet (selected articles), checks DB for cached content,
    and scrapes missing content concurrently.
    """
    timer = utils.Stopwatch().start()
    
    # 1. Load Run Sheet
    with open(_config.RUN_SHEET_FILE, 'r') as f:
        run_sheet = json.load(f)
        
    # Flatten
    all_articles = []
    for section in run_sheet.values():
        all_articles.extend(section)
        
    print(f"\n[ENHANCER] Starting Parallel Enhancement... (Run Sheet: {len(all_articles)} items)")
    
    # 2. Check Cache vs Network
    to_fetch = []
    
    for art in all_articles:
        db_art = repository.get_article_by_id(art.get('id'))
        if db_art and db_art.get('is_enhanced'):
            # Cache Hit
            art['full_content'] = db_art.get('full_content')
            pass
        else:
            to_fetch.append(art)
            
    stats = {
        'hits': len(all_articles) - len(to_fetch),
        'fetches': 0,
        'errors': 0
    }
    
    # 3. Fetch Missing
    if to_fetch:
        MAX_WORKERS = 20
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_art = {executor.submit(enhance_article, art): art for art in to_fetch}
            
            with tqdm(total=len(to_fetch), desc="Enhancing", unit="article") as pbar:
                for future in as_completed(future_to_art):
                    art = future_to_art[future]
                    try:
                        success, text, comments = future.result()
                        if success:
                            # Update DB
                            repository.update_enhancement(art.get('id'), text, comments)
                            # Update In-Memory Object for JSON dump
                            art['full_content'] = text
                            stats['fetches'] += 1
                        else:
                            stats['errors'] += 1
                    except:
                        stats['errors'] += 1
                    pbar.update(1)
    
    # 4. Save Updated Run Sheet (Now with Text)
    with open(_config.RUN_SHEET_FILE, 'w') as f:
        json.dump(run_sheet, f, indent=2)
        
    duration = timer.stop()
    print(f"\n[ENHANCER] Finished in {duration:.2f}s. Hits: {stats['hits']}, Fetches: {stats['fetches']}, Errors: {stats['errors']}")

if __name__ == "__main__":
    run_enhancer()