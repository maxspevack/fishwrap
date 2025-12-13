import re
# Refactor: Use Pydantic Config Loader
from fishwrap.config_loader import Config as _config

def compute_score(article, section='general'):
    """
    Calculates the Impact Score for an article based on:
    1. Raw Stats (Upvotes/Comments)
    2. Editorial Policies (Boosts/Penalties)
    
    Returns: (final_score, breakdown_dict)
    """
    
    # --- 1. Base Score (Stats) ---
    # Determine scoring profile
    # Currently hardcoded logic in fetcher determines 'dynamic' vs 'static'
    # but we need to know WHICH profile to use here.
    # Ideally, article metadata should hint at source type, or we infer from URL again.
    # For now, let's assume 'static' unless we see heavy stats.
    
    profile_key = 'static'
    if article.get('stats_score', 0) > 0 or article.get('stats_comments', 0) > 0:
        profile_key = 'dynamic'
        
    profile = _config.SCORING_PROFILES[profile_key]
    
    # Calculate Base
    # Pydantic: Access attributes via dot notation
    score_val = article.get('stats_score', 0) * profile.score_weight
    comment_val = article.get('stats_comments', 0) * profile.comment_weight
    
    # Base Boosts (e.g. for static RSS feeds that need a baseline)
    # Fetcher might have set this, or we use profile default
    base_boosts_units = article.get('base_boosts', profile.base_boosts)
    base_boost_score = base_boosts_units * _config.BOOST_UNIT_VALUE
    
    base_score = score_val + comment_val + base_boost_score
    
    # --- 2. Editorial Policies (Boosts/Penalties) ---
    policy_score = 0
    breakdown = {
        'base_score': int(base_score),
        'policies': []
    }
    
    # Check all policies
    # Pydantic: Iterate list of Policy models
    for policy in _config.EDITORIAL_POLICIES:
        triggered = False
        
        # Keyword Boost/Penalty
        if policy.type in ('keyword_boost', 'keyword_penalty'):
            # Check Title
            text_blob = (article.get('title') or '') + " " + (article.get('content') or '')
            text_blob = text_blob.lower()
            
            for phrase in (policy.phrases or []):
                if f" {phrase.lower()} " in f" {text_blob} ": # Simple word boundary check
                    triggered = True
                    break # Trigger once per policy
        
        # Source/Domain Boost/Penalty
        elif policy.type in ('source_boost', 'domain_penalty'):
            source_url = article.get('source_url', '')
            match_target = policy.match or ""
            
            # Check explicit match or domain list
            if match_target and match_target in source_url:
                triggered = True
            
            if not triggered and policy.domains:
                for d in policy.domains:
                    if d in source_url:
                        triggered = True
                        break
                        
        # Content/Author Boost
        elif policy.type == 'content_boost':
             text_blob = (article.get('content') or '')
             for phrase in (policy.phrases or []):
                if phrase.lower() in text_blob.lower():
                    triggered = True
                    break

        if triggered:
            # Calculate impact
            impact = policy.boosts * _config.BOOST_UNIT_VALUE
            policy_score += impact
            breakdown['policies'].append({
                'type': policy.type,
                'boosts': policy.boosts,
                'score': impact
            })

    final_score = base_score + policy_score
    
    # Safety Floor
    if final_score < 0: final_score = 0
    
    breakdown['final_score'] = int(final_score)
    
    return int(final_score), breakdown