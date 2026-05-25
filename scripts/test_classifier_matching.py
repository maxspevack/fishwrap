"""
Regression tests for issues #28 (case mismatch) and #29 (word-boundary punctuation).
Both bugs lived in the same line of editor.py (and a parallel line in scoring.py).
The unified fix uses re.search with \b boundaries and re.escape on a lowercased keyword.
"""
import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fishwrap import editor
from fishwrap import scoring
from fishwrap import _config


def _mk_article(title, source_url='http://example.com', content='', categories=None):
    return {
        'title': title,
        'content': content,
        'categories': categories or [],
        'source_url': source_url,
        'timestamp': time.time(),
    }


def _set_classifier_config(keywords):
    _config.SECTIONS = [
        {'id': k, 'title': k.title(), 'description': ''} for k in keywords.keys()
    ] + [{'id': 'fallback', 'title': 'Fallback', 'description': ''}]
    _config.KEYWORDS = keywords
    _config.SOURCE_SECTIONS = {}


def _expect_score(label, article, section, expected_score):
    _, debug = editor.classify_article(article)
    actual = debug['scores'].get(section, 0)
    if actual != expected_score:
        print(f"[FAIL] {label}: expected scores[{section!r}]={expected_score}, got {actual} "
              f"(full scores={debug['scores']})")
        sys.exit(1)
    print(f"[PASS] {label}")


def test_case_insensitive_keywords():
    """#28: keyword 'NCIS' (uppercase) must match lowercased article text."""
    print("\n[TEST] #28 case-insensitive keyword matching...")
    _set_classifier_config({'procedural': ['NCIS', 'Mark Harmon']})

    article = _mk_article('NCIS finale: Mark Harmon returns as Gibbs')
    _expect_score('NCIS + Mark Harmon both match', article, 'procedural', 2)


def test_punctuation_boundary_colon():
    """#29: keyword 'ncis' must match 'NCIS: Origins'."""
    print("\n[TEST] #29 colon boundary...")
    _set_classifier_config({'procedural': ['ncis']})

    article = _mk_article('NCIS: Origins season premiere review')
    _expect_score('ncis matches NCIS:', article, 'procedural', 1)


def test_punctuation_boundary_comma():
    """#29: keyword 'bridgerton' must match 'Bridgerton, Netflix renews'."""
    print("\n[TEST] #29 comma boundary...")
    _set_classifier_config({'drama': ['bridgerton']})

    article = _mk_article("'Bridgerton,' Netflix renews")
    _expect_score('bridgerton matches Bridgerton,', article, 'drama', 1)


def test_punctuation_boundary_period():
    """#29: keyword 'the pitt' must match 'The Pitt. Noah Wyle interview'."""
    print("\n[TEST] #29 period boundary...")
    _set_classifier_config({'procedural': ['the pitt']})

    article = _mk_article('The Pitt. Noah Wyle interview')
    _expect_score('the pitt matches The Pitt.', article, 'procedural', 1)


def test_apostrophe_keyword():
    """#29 caveat: apostrophe-bearing keywords like 'grey\\'s anatomy' must still match."""
    print("\n[TEST] #29 apostrophe in keyword...")
    _set_classifier_config({'drama': ["grey's anatomy"]})

    article = _mk_article("Grey's Anatomy returns this fall")
    _expect_score("grey's anatomy matches", article, 'drama', 1)


def test_embedded_substring_does_not_match():
    """#29 negative: 'ncis' must NOT match 'reconncissaance' or other embedded substrings."""
    print("\n[TEST] #29 embedded substring boundary preserved...")
    _set_classifier_config({'procedural': ['ncis']})

    # Synthetic embedded case — 'ncis' inside a larger token has no boundary.
    article = _mk_article('foobarncisbaz launches')
    _expect_score('ncis must NOT match foobarncisbaz', article, 'procedural', 0)


def test_acronym_expansion_does_not_match():
    """#29 issue example: 'ncis' keyword must NOT match an article that spells the agency out."""
    print("\n[TEST] #29 acronym not matched by expansion...")
    _set_classifier_config({'procedural': ['ncis']})

    article = _mk_article('Naval Criminal Investigative Service announces overhaul')
    _expect_score('ncis must NOT match expanded form', article, 'procedural', 0)


def test_full_classification_strong_match():
    """End-to-end: case + punctuation fix together produce a 'keyword_strong_match' classification."""
    print("\n[TEST] Strong-match end-to-end (>=3 keywords)...")
    _set_classifier_config({'procedural': ['NCIS', 'Mark Harmon', 'Gibbs']})

    article = _mk_article('NCIS: Mark Harmon returns as Gibbs in season finale')
    final_cat, debug = editor.classify_article(article)

    if final_cat != 'procedural':
        print(f"[FAIL] Expected final_cat='procedural', got {final_cat!r}")
        sys.exit(1)
    if debug['reason'] != 'keyword_strong_match':
        print(f"[FAIL] Expected reason='keyword_strong_match', got {debug['reason']!r}")
        sys.exit(1)
    if debug['scores']['procedural'] < 3:
        print(f"[FAIL] Expected procedural score >= 3, got {debug['scores']['procedural']}")
        sys.exit(1)
    print(f"[PASS] classified as procedural via keyword_strong_match "
          f"(score={debug['scores']['procedural']})")


def test_scoring_policy_punctuation_boundary():
    """#29 parallel fix in scoring.py: keyword_boost policy must trigger on 'NCIS:' too."""
    print("\n[TEST] #29 scoring.py keyword_boost punctuation boundary...")
    _config.SCORING_PROFILES = {
        'dynamic': {'base_boosts': 0, 'score_weight': 1.0, 'comment_weight': 1.0},
        'static': {'base_boosts': 0, 'score_weight': 0, 'comment_weight': 0},
    }
    _config.BOOST_UNIT_VALUE = 100
    _config.EDITORIAL_POLICIES = [
        {'type': 'keyword_boost', 'phrases': ['ncis'], 'boosts': 5},
    ]

    article = _mk_article('NCIS: Origins season premiere review')
    score, breakdown = scoring.compute_score(article)
    triggered = [p for p in breakdown['policies'] if p['type'] == 'keyword_boost']
    if not triggered:
        print(f"[FAIL] keyword_boost did not trigger on 'NCIS:'. breakdown={breakdown}")
        sys.exit(1)
    print(f"[PASS] keyword_boost fired on NCIS: (final_score={score})")


def test_scoring_policy_case_insensitive():
    """scoring.py was already case-insensitive (phrase.lower()) — sanity check it stays that way."""
    print("\n[TEST] scoring.py case-insensitive sanity...")
    _config.SCORING_PROFILES = {
        'dynamic': {'base_boosts': 0, 'score_weight': 1.0, 'comment_weight': 1.0},
        'static': {'base_boosts': 0, 'score_weight': 0, 'comment_weight': 0},
    }
    _config.BOOST_UNIT_VALUE = 100
    _config.EDITORIAL_POLICIES = [
        {'type': 'keyword_boost', 'phrases': ['Bridgerton'], 'boosts': 5},
    ]

    article = _mk_article('bridgerton season 4 trailer drops')
    score, breakdown = scoring.compute_score(article)
    triggered = [p for p in breakdown['policies'] if p['type'] == 'keyword_boost']
    if not triggered:
        print(f"[FAIL] Bridgerton policy did not trigger on lowercase title. breakdown={breakdown}")
        sys.exit(1)
    print(f"[PASS] case-insensitive scoring policy works")


if __name__ == "__main__":
    test_case_insensitive_keywords()
    test_punctuation_boundary_colon()
    test_punctuation_boundary_comma()
    test_punctuation_boundary_period()
    test_apostrophe_keyword()
    test_embedded_substring_does_not_match()
    test_acronym_expansion_does_not_match()
    test_full_classification_strong_match()
    test_scoring_policy_punctuation_boundary()
    test_scoring_policy_case_insensitive()
    print("\n[OK] All classifier matching tests passed.")
