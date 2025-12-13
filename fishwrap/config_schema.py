from pydantic import BaseModel, Field, HttpUrl
from typing import List, Dict, Optional, Union, Any

class ScoringProfile(BaseModel):
    base_boosts: int
    score_weight: float
    comment_weight: float

class Policy(BaseModel):
    type: str
    boosts: int
    match: Optional[str] = None
    phrases: Optional[List[str]] = None
    domains: Optional[List[str]] = None

class Section(BaseModel):
    id: str
    title: str
    description: str

class VisualThresholds(BaseModel):
    lead: int
    feature: int

class FishwrapConfig(BaseModel):
    # --- 1. Feeds ---
    FEEDS: List[str]

    # --- 2. Paths (Optional, often environment specific) ---
    CONFIG_BASE_DIR: Optional[str] = None
    ARTICLES_DB_FILE: Optional[str] = None
    RUN_SHEET_FILE: Optional[str] = None
    ENHANCED_ISSUE_FILE: Optional[str] = None
    SECRETS_FILE: Optional[str] = None
    STATS_FILE: Optional[str] = None
    LATEST_HTML_FILE: Optional[str] = None
    LATEST_PDF_FILE: Optional[str] = None
    DATABASE_URL: Optional[str] = "sqlite:///newsroom.db"

    # --- 3. Pipeline Settings ---
    TIMEZONE: str = "UTC"
    FOUNDING_DATE: str = "2025-01-01"
    THEME: str = "themes/basic"
    MAX_ARTICLE_LENGTH: int = 10000
    EXPIRATION_HOURS: int = 24
    USER_AGENT: str = "Fishwrap/1.0"

    # --- 4. Editor Settings ---
    EDITION_SIZE: Dict[str, int]
    MIN_SECTION_SCORES: Dict[str, int]

    # --- 5. Source Affinity ---
    SOURCE_SECTIONS: Dict[str, str]

    # --- 6. Classification Keywords ---
    KEYWORDS: Dict[str, List[str]]

    # --- 6. Scoring Settings (Note: Duplicate section number in original config) ---
    BOOST_UNIT_VALUE: int = 100
    FUZZY_BOOST_MULTIPLIER: int = 1
    SCORING_PROFILES: Dict[str, ScoringProfile]

    # --- 7. Editorial Policies ---
    EDITORIAL_POLICIES: List[Policy]

    # --- 8. Printer Settings ---
    SECTIONS: List[Section]

    # --- 9. Visual Formatting ---
    VISUAL_THRESHOLDS: Dict[str, VisualThresholds]

    class Config:
        # Allow extra fields for backward compatibility or plugins
        extra = 'ignore' 
