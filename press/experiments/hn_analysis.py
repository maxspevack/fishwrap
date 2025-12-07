import requests
import time
from datetime import datetime, timedelta

def fetch_hn_stories(days=14, min_points=10):
    """
    Fetches stories from Algolia HN API from the last N days.
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    start_ts = int(start_date.timestamp())
    
    # Algolia API endpoint
    url = "http://hn.algolia.com/api/v1/search_by_date"
    
    all_hits = []
    page = 0
    
    print(f"Fetching HN stories from the last {days} days (>{min_points} points)...")
    
    while True:
        params = {
            'tags': 'story',
            'numericFilters': [
                f'created_at_i>{start_ts}',
                f'points>{min_points}'
            ],
            'hitsPerPage': 100,
            'page': page
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            hits = data.get('hits', [])
            
            if not hits:
                break
                
            all_hits.extend(hits)
            page += 1
            
            # Rate limit politeness
            time.sleep(0.1)
            
            # Safety break (e.g., max 1000 items)
            if len(all_hits) >= 1000:
                print("Hit limit of 1000 items, stopping.")
                break
                
        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            break
            
    return all_hits

def simulate_score(hits, score_weight=1.0, comment_weight=1.2):
    """
    Calculates a custom score for each hit.
    """
    scored = []
    for hit in hits:
        points = hit.get('points', 0)
        comments = hit.get('num_comments', 0)
        title = hit.get('title', 'No Title')
        
        # The Formula
        final_score = (points * score_weight) + (comments * comment_weight)
        
        scored.append({
            'title': title,
            'points': points,
            'comments': comments,
            'final_score': int(final_score)
        })
    
    # Sort by the new calculated score
    scored.sort(key=lambda x: x['final_score'], reverse=True)
    return scored

def print_table(scored_data, limit=25):
    print(f"\n{'RK':<3} | {'SCORE':<6} | {'PTS':<4} | {'CMT':<4} | {'TITLE'}")
    print("-" * 80)
    
    for i, item in enumerate(scored_data[:limit]):
        title = item['title'][:50] + "..." if len(item['title']) > 50 else item['title']
        print(f"{i+1:<3} | {item['final_score']:<6} | {item['points']:<4} | {item['comments']:<4} | {title}")

if __name__ == "__main__":
    # 1. Fetch Data
    hits = fetch_hn_stories(days=7, min_points=50) # Last 7 days, >50 points
    
    # 2. Define Experiments
    experiments = [
        {'name': "Baseline (1.0 / 1.0)", 'w_score': 1.0, 'w_cmt': 1.0},
        {'name': "Comment Heavy (1.0 / 2.0)", 'w_score': 1.0, 'w_cmt': 2.0},
        {'name': "Score Heavy (2.0 / 0.5)", 'w_score': 2.0, 'w_cmt': 0.5},
        {'name': "Balanced High (3.0 / 5.0)", 'w_score': 3.0, 'w_cmt': 5.0}, # Looking for Reddit equivalence
    ]
    
    # 3. Run Experiments
    for exp in experiments:
        print(f"\n\n=== {exp['name']} ===")
        results = simulate_score(hits, score_weight=exp['w_score'], comment_weight=exp['w_cmt'])
        print_table(results)
