import json
from urllib.parse import urlparse
import difflib
from datetime import datetime
from fishwrap import _config
from fishwrap import scoring
from fishwrap import auditor
from fishwrap.db import repository

def classify_article(article):
    """
    Classifies an article into a section based on Source or Content keywords.
    Dynamically uses keys from _config.KEYWORDS and _config.SECTIONS.
    """
    title = article.get('title', '').lower()
    content = (article.get('content') or '').lower()[:500]
    cats = [c.lower() for c in article.get('categories', []) if c]
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

    # Calculate scores for ALL defined keyword categories
    scores = {k: score_keywords(v) for k, v in _config.KEYWORDS.items()}
    
    reason = "fallback"
    # Default fallback is the LAST section defined in config (usually 'culture' or 'general')
    final_cat = _config.SECTIONS[-1]['id'] 
    
    # 3. Override Logic (Content beats Source if signal is strong)
    match_found = False
    
    # Check for Strong Matches (>= 3)
    for section in _config.SECTIONS:
        sid = section['id']
        if scores.get(sid, 0) >= 3:
            final_cat = sid
            reason = "keyword_strong_match"
            match_found = True
            break # First strong match wins
            
    if not match_found:
        # 4. Return Default (Source) if exists
        if default_section:
            final_cat = default_section
            reason = "source_default"
        else:
            # 5. Check for Weak Matches (>= 1)
            for section in _config.SECTIONS:
                sid = section['id']
                if scores.get(sid, 0) >= 1:
                    final_cat = sid
                    reason = "keyword_weak_match"
                    break

    # Debug Info
    debug_info = {
        'scores': scores,
        'reason': reason,
        'default_section': default_section
    }
    
    return final_cat, debug_info

def organize_and_cluster(articles):
    """
    Performs GLOBAL fuzzy deduplication using Time-Windowed Blocking.
    Only compares articles published within a 48-hour window of each other.
    """
    # 1. Sort ALL articles by score descending
    articles.sort(key=lambda x: x.get('impact_score', 0), reverse=True)
    
    clusters = []
    
    # 48 hours in seconds
    WINDOW_SECONDS = 48 * 3600
    
    # Pre-tokenize all titles once to avoid re-splitting in loop
    token_cache = {}
    for a in articles:
        words = set(w for w in a.get('title', '').lower().split() if len(w) > 3)
        token_cache[id(a)] = words

    # 2. Global Clustering Loop
    for candidate in articles:
        is_duplicate = False
        candidate_title = candidate.get('title', '').lower()
        candidate_ts = candidate.get('timestamp', 0)
        candidate_words = token_cache[id(candidate)]
        
        for leader in clusters:
            # OPTIMIZATION 1: Time Window Check
            leader_ts = leader.get('timestamp', 0)
            if abs(candidate_ts - leader_ts) > WINDOW_SECONDS:
                continue
            
            # OPTIMIZATION 2: Jaccard Pre-Filter
            leader_words = token_cache[id(leader)]
            if candidate_words.isdisjoint(leader_words):
                continue

            leader_title = leader.get('title', '').lower()
            
            # Fuzzy Match (Expensive)
            similarity = difflib.SequenceMatcher(None, leader_title, candidate_title).ratio()
            
            if similarity > 0.70: # Threshold
                is_duplicate = True
                
                # Apply Boost (Use Configured Multiplier)
                multiplier = getattr(_config, 'FUZZY_BOOST_MULTIPLIER', 1)
                boost_unit = _config.BOOST_UNIT_VALUE * multiplier
                
                leader['impact_score'] += boost_unit
                
                # Update Breakdown for Transparency
                if 'score_breakdown' not in leader: leader['score_breakdown'] = {}
                leader['score_breakdown']['total_boosts'] = leader['score_breakdown'].get('total_boosts', 0) + multiplier
                leader['score_breakdown']['boost_score'] = leader['score_breakdown'].get('boost_score', 0) + boost_unit
                leader['score_breakdown']['final_score'] = leader['score_breakdown'].get('final_score', 0) + boost_unit
                
                if 'fuzzy_matches' not in leader['score_breakdown']:
                    leader['score_breakdown']['fuzzy_matches'] = []
                leader['score_breakdown']['fuzzy_matches'].append(candidate_title)
                
                break 
        
        if not is_duplicate:
            clusters.append(candidate)
            
    # 3. Bucketize the Leaders (Dynamic)
    final_buckets = {section['id']: [] for section in _config.SECTIONS}
    default_bucket_key = _config.SECTIONS[0]['id']
    
    for article in clusters:
        cat = article.get('temp_section')
        if not cat or cat.startswith('skip'): 
            continue
            
        if cat in final_buckets:
            final_buckets[cat].append(article)
        else:
            final_buckets[default_bucket_key].append(article)
            
    return final_buckets

def run_editor():
    # --- Phase 1: Load Scored Articles (Lightweight) ---
    print(f"\n[EDITOR] Starting... (Fetching recent articles from DB)")
    
    # DB Load
    raw_candidates = repository.get_recent_articles(hours=_config.EXPIRATION_HOURS)
    print(f"[EDITOR] Loaded {len(raw_candidates)} candidates.")

    scored_articles = []
    
    # Dynamic Candidate Counter
    section_candidates = {section['id']: 0 for section in _config.SECTIONS}
    drift_count = 0
    drift_examples = []
    
    for article in raw_candidates:
        # DB articles already have computed_score etc.
        # We need to map DB fields to the format Editor logic expects if naming differs.
        # Models: computed_score -> Editor: impact_score
        
        cat = article.get('computed_category')
        score = article.get('computed_score')
        breakdown = article.get('computed_breakdown')
        cls_debug = article.get('computed_debug')

        # Fallback if DB data is missing (shouldn't happen with new logic, but safe)
        if not cat:
            cat, cls_debug = classify_article(article)
            score, breakdown = scoring.compute_score(article, section=cat)
        
        # Drift Tracking
        debug_info = cls_debug or {}
        default_sec = debug_info.get('default_section')
        if default_sec and cat != default_sec:
            drift_count += 1
            if len(drift_examples) < 3:
                drift_examples.append(f"'{article.get('title')[:30]}...' ({default_sec} -> {cat})")
        
        # Populate fields expected by template/logic
        article['temp_section'] = cat
        article['impact_score'] = score
        article['score_breakdown'] = breakdown
        article['classification_debug'] = debug_info
        
        if cat and cat.startswith('skip'):
            continue
            
        if cat in section_candidates:
            section_candidates[cat] += 1
            
        scored_articles.append(article)

    # --- Phase 2: Organize & Cluster (Windowed) ---
    buckets = organize_and_cluster(scored_articles)

    # --- Phase 3: Select & Save ---
    run_sheet = {}
    total_selected = 0
    cut_line_report = {} # Store top 3 misses per section
    section_diversity = {} # Store source breakdown per section
    
    # Iterate through Configured Sections to maintain order
    current_time_ts = datetime.now().timestamp()
    print_cutoff = current_time_ts - (_config.EXPIRATION_HOURS * 3600)

    for section_def in _config.SECTIONS:
        cat = section_def['id']
        capacity = _config.EDITION_SIZE.get(cat, 5) # Default capacity if missing
        
        items = buckets.get(cat, [])
        
        # Filter 1: Freshness (Strict Print Window)
        items = [i for i in items if i.get('timestamp', 0) >= print_cutoff]

        items.sort(key=lambda x: x.get('impact_score', 0), reverse=True)
        
        # Filter 2: Minimum Score
        min_score = _config.MIN_SECTION_SCORES.get(cat, 0)
        qualified_items = [i for i in items if i.get('impact_score', 0) >= min_score]
        
        selected = qualified_items[:capacity]
        run_sheet[cat] = selected
        total_selected += len(selected)
        
        # Calculate Diversity for this section
        source_counts = {}
        for item in selected:
            try:
                # simple domain parse
                domain = item.get('source_url', '').split('/')[2]
            except:
                domain = 'unknown'
            source_counts[domain] = source_counts.get(domain, 0) + 1
        
        # Convert to list of (domain, count) sorted by count
        sorted_sources = sorted(source_counts.items(), key=lambda x: x[1], reverse=True)
        section_diversity[cat] = sorted_sources
        
        # Capture Cut-Line (The best of the rest)
        missed = items[len(selected):]
        cut_line_report[cat] = missed[:3]

    # Summary Report (High-level only, details in Auditor report)
    print(f"\n[EDITOR] Selected {total_selected} articles ({drift_count} reclassified).")
    
    with open(_config.RUN_SHEET_FILE, 'w') as f:
        json.dump(run_sheet, f, indent=2)
    
    # The Auditor will now persist and generate the detailed report
    total_db_count = repository.get_total_count()
    auditor.audit_run(run_sheet, raw_candidates, {
        'input_count': total_db_count,
        'cut_line': cut_line_report
    })

if __name__ == "__main__":
    run_editor()
