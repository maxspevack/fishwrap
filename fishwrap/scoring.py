from fishwrap import _config

def identify_scoring_profile(article):
    """
    Determines if the article uses 'dynamic' (social) or 'static' (RSS) scoring.
    """
    url = article.get('source_url', '').lower()
    link = article.get('link', '').lower()
    
    if 'reddit.com' in url or 'reddit.com' in link:
        return 'dynamic'
    
    if 'hnrss.org' in url or 'news.ycombinator.com' in link:
        return 'dynamic'
        
    return 'static'

def compute_score(article, section='news'):
    """
    Main entry point. Returns (final_score, breakdown_dict).
    Calculates the score using:
    1. Stats Score (Raw metrics * Weights)
    2. Boost Score (Total Boosts * Unit Value)
    """
    profile_key = identify_scoring_profile(article)
    profile = _config.SCORING_PROFILES.get(profile_key, _config.SCORING_PROFILES['static'])
    
    # 1. Calculate Stats Score (The "Raw" Performance)
    stats_score = article.get('stats_score', 0)
    stats_comments = article.get('stats_comments', 0)
    
    score_weight = profile['score_weight']
    comment_weight = profile['comment_weight']
    
    stats_part = (stats_score * score_weight) + (stats_comments * comment_weight)
    
    # 2. Calculate Boosts (The "Editorial" Influence)
    # A. Base Boosts (From Profile)
    base_boosts = article.get('base_boosts', profile['base_boosts'])
    
    # B. Policy Boosts (From Config)
    policy_boosts = 0
    policy_hits = []
    
    title_lower = article.get('title', '').lower()
    link_lower = article.get('link', '').lower()
    source_lower = article.get('source_url', '').lower()
    content_lower = (article.get('content') or '').lower()
    
    for policy in _config.EDITORIAL_POLICIES:
        ptype = policy['type']
        pval = policy['boosts']
        
        if ptype == 'source_boost':
            target = policy['match'].lower()
            if target in link_lower or target in source_lower:
                policy_boosts += pval
                policy_hits.append((f"{ptype}: {target}", pval))
                
        elif ptype == 'keyword_penalty' or ptype == 'keyword_boost':
            for phrase in policy['phrases']:
                if phrase.lower() in title_lower:
                    policy_boosts += pval
                    policy_hits.append((f"{ptype}: {phrase}", pval))
        
        elif ptype == 'content_boost':
            for phrase in policy['phrases']:
                if phrase.lower() in content_lower:
                    policy_boosts += pval
                    policy_hits.append((f"{ptype}: {phrase}", pval))
                    
        elif ptype == 'domain_penalty':
            for domain in policy['domains']:
                if domain.lower() in link_lower:
                    policy_boosts += pval
                    policy_hits.append((f"{ptype}: {domain}", pval))

    # 3. Add Fetcher/Fuzzy Boosts
    fetcher_boosts = article.get('boosts_count', 0)
    
    # D. Total Boost Score
    total_boosts = base_boosts + policy_boosts + fetcher_boosts
    boost_unit = _config.BOOST_UNIT_VALUE
    boost_score = total_boosts * boost_unit
    
    final_score = int(stats_part + boost_score)
    
    breakdown = {
        'profile': profile_key,
        'section': section,
        'stats_part': int(stats_part),
        'stats_score': stats_score,
        'stats_comments': stats_comments,
        'base_boosts': base_boosts,
        'policy_boosts': policy_boosts,
        'policy_hits': policy_hits,
        'fetcher_boosts': fetcher_boosts,
        'total_boosts': total_boosts,
        'boost_unit': boost_unit,
        'boost_score': boost_score,
        'final_score': final_score
    }
    
    return final_score, breakdown
