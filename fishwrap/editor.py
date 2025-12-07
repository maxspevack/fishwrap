import json
from urllib.parse import urlparse # Still needed for urlparse in run_editor
import difflib
from fishwrap import _config
from fishwrap import scoring

# Removed clean_url function as it's no longer used in organize_and_cluster

def classify_article(article):
    title = article.get('title', '').lower()
    content = (article.get('content') or '').lower()[:500]
    cats = [c.lower() for c in article.get('categories', [])]
    source_url = article.get('source_url', '')
    
    # 1. Establish Default Section from Source
    default_section = None
    for source_key, section in _config.SOURCE_SECTIONS.items():
        if source_key in source_url:
            default_section = section
            break

    # 2. Keyword Scoring (Content Analysis)
    text_blob = f"{title} {' '.join(cats)} {content}"
    def score_keywords(keywords):
        return sum(1 for k in keywords if f" {k} " in f" {text_blob} ")

    scores = {k: score_keywords(v) for k, v in _config.KEYWORDS.items()}
    
    reason = "fallback"
    final_cat = 'culture' # Fallback
    
    # 3. Override Logic (Content beats Source if signal is strong)
    if scores['sports'] >= 3: 
        final_cat = 'sports'
        reason = "keyword_strong_match"
    elif scores['tech'] >= 3: 
        final_cat = 'tech'
        reason = "keyword_strong_match"
    elif scores['news'] >= 2: 
        final_cat = 'news'
        reason = "keyword_strong_match"
    elif scores['culture'] >= 3: 
        final_cat = 'culture'
        reason = "keyword_strong_match"
    
    # 4. Return Default if exists
    elif default_section:
        final_cat = default_section
        reason = "source_default"
    
    # 5. Fallback for unknown sources (Standard Logic)
    elif scores['news'] >= 1: 
        final_cat = 'news'
        reason = "keyword_weak_match"
    elif scores['sports'] >= 1: 
        final_cat = 'sports'
        reason = "keyword_weak_match"
    elif scores['tech'] >= 1: 
        final_cat = 'tech'
        reason = "keyword_weak_match"
    elif scores['culture'] >= 1: 
        final_cat = 'culture'
        reason = "keyword_weak_match"
    
    # Debug Info
    debug_info = {
        'scores': scores,
        'reason': reason,
        'default_section': default_section
    }
    
    return final_cat, debug_info

def organize_and_cluster(articles):
    """
    Performs GLOBAL fuzzy deduplication first, then buckets into sections.
    This ensures that if a story appears in multiple sections (e.g. News vs Culture),
    they merge into the highest-scoring version (likely News) and don't split votes.
    """
    # 1. Sort ALL articles by score descending
    articles.sort(key=lambda x: x.get('impact_score', 0), reverse=True)
    
    clusters = []
    
    # 2. Global Clustering Loop
    for candidate in articles:
        is_duplicate = False
        candidate_title = candidate.get('title', '').lower()
        
        for leader in clusters:
            leader_title = leader.get('title', '').lower()
            
            # Fuzzy Match
            similarity = difflib.SequenceMatcher(None, leader_title, candidate_title).ratio()
            
            if similarity > 0.70: # Threshold
                is_duplicate = True
                
                # Apply Boost (Use Configured Multiplier)
                multiplier = getattr(_config, 'FUZZY_BOOST_MULTIPLIER', 1)
                boost_unit = _config.BOOST_UNIT_VALUE * multiplier
                old_score = leader['impact_score']
                leader['impact_score'] += boost_unit
                
                # Update Breakdown for Transparency
                if 'score_breakdown' not in leader: leader['score_breakdown'] = {}
                leader['score_breakdown']['total_boosts'] = leader['score_breakdown'].get('total_boosts', 0) + multiplier
                leader['score_breakdown']['boost_score'] = leader['score_breakdown'].get('boost_score', 0) + boost_unit
                leader['score_breakdown']['final_score'] = leader['score_breakdown'].get('final_score', 0) + boost_unit
                
                if 'fuzzy_matches' not in leader['score_breakdown']:
                    leader['score_breakdown']['fuzzy_matches'] = []
                leader['score_breakdown']['fuzzy_matches'].append(candidate_title)
                
                # print(f"[EDITOR] Fuzzy Boost: Merging '{candidate.get('title')}' into '{leader.get('title')}' (Sim: {similarity:.2f}). Score: {old_score} -> {leader['impact_score']}")
                break # Stop checking other clusters, we found a home
        
        if not is_duplicate:
            clusters.append(candidate)
            
    # 3. Bucketize the Leaders
    final_buckets = {'news': [], 'sports': [], 'tech': [], 'culture': []}
    
    for article in clusters:
        cat = article.get('temp_section')
        # Skip logic is handled upstream by scoring penalties, but safe to check
        if not cat or cat.startswith('skip'): 
            continue
            
        if cat in final_buckets:
            final_buckets[cat].append(article)
        else:
            final_buckets['news'].append(article)
            
    return final_buckets

def run_editor():
    with open(_config.ARTICLES_DB_FILE, 'r') as f:
        raw_db = json.load(f)
        
    print(f"\n[EDITOR] Starting... (Candidates: {len(raw_db)})")
    
    # --- Phase 1: Classify & Score ---
    scored_articles = []
    section_candidates = {'news': 0, 'sports': 0, 'tech': 0, 'culture': 0}
    
    for aid, article in raw_db.items():
        cat, cls_debug = classify_article(article)
        article['temp_section'] = cat
        article['classification_debug'] = cls_debug # SAVE DEBUG INFO
        
        if cat.startswith('skip'):
            article['impact_score'] = 0
            article['score_breakdown'] = {}
        else:
            section_candidates[cat] += 1
            # ... (rest of scoring logic)
            
            score, breakdown = scoring.compute_score(article, section=cat)
            article['impact_score'] = score
            article['score_breakdown'] = breakdown
            scored_articles.append(article)

    # --- Phase 2: Organize & Cluster (The Black Box) ---
    buckets = organize_and_cluster(scored_articles)

    # --- Phase 3: Select & Save ---
    run_sheet = {} 
    total_selected = 0
    
    print("\n" + "="*60)
    print(f" EDITOR SUMMARY")
    print("="*60)
    print(f" {'Section':<10} | {'Candidates':<10} | {'Selected':<8} | {'Min Score':<10}")
    print("-" * 60)
    
    for cat, capacity in _config.EDITION_SIZE.items():
        items = buckets[cat]
        items.sort(key=lambda x: x.get('impact_score', 0), reverse=True)
        
        # Filter by Minimum Score
        min_score = _config.MIN_SECTION_SCORES.get(cat, 0)
        items = [i for i in items if i.get('impact_score', 0) >= min_score]
        
        selected = items[:capacity]
        run_sheet[cat] = selected
        total_selected += len(selected)
        
        print(f" {cat.capitalize():<10} | {section_candidates.get(cat, 0):<10} | {len(selected):<8} | {min_score:<10}")

    print("-" * 60)
    print(f" {'TOTAL':<10} | {len(raw_db):<10} | {total_selected:<8} |")
    print("=" * 60 + "\n")
        
    with open(_config.RUN_SHEET_FILE, 'w') as f:
        json.dump(run_sheet, f, indent=2)

if __name__ == "__main__":
    run_editor()
