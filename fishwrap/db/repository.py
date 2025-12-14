from datetime import datetime, timedelta
import time
from sqlalchemy import create_engine, select, delete, func
from sqlalchemy.orm import sessionmaker
from fishwrap.db.models import Article, Run, RunArticle, AuditLog
from fishwrap import _config
import os

# --- Database Setup ---
_current_engine = None
_SessionLocal = None

def _get_database_url():
    """Determines the database URL from _config or falls back to default.
    Resolves relative SQLite paths to absolute based on CWD.
    """
    db_url = getattr(_config, 'DATABASE_URL', 'sqlite:///newsroom.db')
    
    # Resolve relative paths for sqlite dbs to make them absolute
    if db_url.startswith('sqlite:///'):
        db_file = db_url.replace('sqlite:///', '')
        if not os.path.isabs(db_file):
            # This makes sqlite dbs relative to the current working directory
            # of the process that loads _config.
            return f"sqlite:///{os.path.abspath(db_file)}"
    return db_url

def _initialize_engine():
    """Initializes or re-initializes the SQLAlchemy engine and session factory."""
    global _current_engine, _SessionLocal
    current_config_url = _get_database_url()

    # Only re-initialize if the URL has changed or not yet initialized
    if _current_engine is None or str(_current_engine.url) != current_config_url:
        _current_engine = create_engine(current_config_url)
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_current_engine)
        # print(f"[DB] Initialized engine for: {_current_engine.url}") # Debugging

# --- Context Manager ---
class SessionContext:
    def __enter__(self):
        _initialize_engine() # Ensure engine is initialized/re-initialized based on current _config
        self.db = _SessionLocal()
        return self.db
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()

# --- Repository Functions ---

def save_run(run_data, articles_list):
    """
    Saves a Run and its associated RunArticles.
    run_data: dict of Run fields (including stats_*, source_dominance, perf_metrics).
    articles_list: list of dicts {'article_id': ..., 'rank': ..., 'score': ..., 'section': ...}
    """
    with SessionContext() as db:
        # Create Run
        new_run = Run(**run_data)
        db.add(new_run)
        db.flush() # Flush to get the ID (though UUID is pre-generated, good practice)
        
        # Create RunArticles
        for item in articles_list:
            ra = RunArticle(
                run_id=new_run.id,
                article_id=item['article_id'],
                final_score=item.get('score'),
                rank=item.get('rank'),
                section=item.get('section')
            )
            db.add(ra)
            
        db.commit()
        return new_run.id

def save_audit_logs(run_id, audit_list):
    """
    Bulk inserts audit logs for a run.
    audit_list: list of dicts matching AuditLog schema.
    """
    if not audit_list: return
    
    with SessionContext() as db:
        # We can use bulk_insert_mappings for speed if needed, but objects are fine for SQLite scale
        logs = []
        for item in audit_list:
            log = AuditLog(
                run_id=run_id,
                article_id=item['article_id'],
                original_section=item.get('original_section'),
                final_section=item.get('final_section'),
                base_score=item.get('base_score'),
                modifier_score=item.get('modifier_score'),
                final_score=item.get('final_score'),
                decision=item.get('decision'),
                trace=item.get('trace')
            )
            logs.append(log)
        
        db.add_all(logs)
        db.commit()

def upsert_article(article_data):
    """
    Insert or Update an article based on 'link' uniqueness.
    Preserves critical fields like 'is_enhanced' and merges stats.
    Returns: 'new' or 'updated'
    """
    with SessionContext() as db:
        # Check for existence by LINK (our unique key)
        # We use strict link matching.
        existing = db.query(Article).filter(Article.link == article_data['link']).first()
        
        if not existing:
            # Create New
            new_article = Article(**article_data)
            db.add(new_article)
            db.commit()
            return "new"
        else:
            # Update Existing (Merge Logic)
            
            # 1. Update timestamp only if newer? 
            # Actually, usually we want the latest timestamp seen in the feed
            # But let's respect the logic: if the feed says it's newer, update it.
            if article_data.get('timestamp', 0) > existing.timestamp:
                existing.timestamp = article_data['timestamp']
            
            # 2. Merge Stats (Max Strategy)
            existing.stats_score = max(existing.stats_score, article_data.get('stats_score', 0))
            existing.stats_comments = max(existing.stats_comments, article_data.get('stats_comments', 0))
            
            # 3. Update Content/Title if provided (feeds might update typos)
            if article_data.get('title'):
                existing.title = article_data['title']
            
            # 4. Computed Fields (Always overwrite with latest classification)
            existing.computed_score = article_data.get('computed_score', 0.0)
            existing.computed_category = article_data.get('computed_category')
            existing.computed_breakdown = article_data.get('computed_breakdown')
            existing.computed_debug = article_data.get('computed_debug')
            
            # 5. Metadata
            existing.categories = article_data.get('categories')
            existing.source_url = article_data.get('source_url')
            existing.comments_url = article_data.get('comments_url')
            
            # NOTE: We specifically DO NOT overwrite 'full_content' or 'is_enhanced' 
            # if they exist on the DB object, unless the incoming data explicitly has them 
            # (which usually it doesn't from the Fetcher).
            
            db.commit()
            return "updated"

def get_recent_articles(hours=24):
    """
    Fetch articles for the Editor within the time window.
    Returns a list of Article objects (which behave like dicts if needed).
    """
    cutoff = time.time() - (hours * 3600)
    
    with SessionContext() as db:
        articles = db.query(Article).filter(Article.timestamp >= cutoff).all()
        # Detach from session so they can be used after session closes
        # The easiest way is to expunge, but for read-only usage in Editor, 
        # creating a list of dicts might be safer for existing code compatibility.
        # Let's return dicts to minimize refactoring friction in Editor.
        return [to_dict(a) for a in articles]

def prune_old_articles(hours=72):
    """
    Janitor: Delete articles older than X hours.
    """
    cutoff = time.time() - (hours * 3600)
    with SessionContext() as db:
        result = db.query(Article).filter(Article.timestamp < cutoff).delete()
        db.commit()
        return result

def get_total_count():
    with SessionContext() as db:
        return db.query(Article).count()

def get_source_dominance():
    """
    Returns list of (domain, count) tuples for Glass Box reporting.
    """
    with SessionContext() as db:
        # This requires some Python-side processing since source_url is a full URL string
        # SQL processing of strings is messy across different DBs.
        # For 'newsroom.db' scale (thousands), fetching specific cols is fine.
        results = db.query(Article.source_url).all()
        
        counts = {}
        for row in results:
            url = row[0]
            if not url: continue
            try:
                domain = url.split('/')[2]
                counts[domain] = counts.get(domain, 0) + 1
            except:
                pass
                
        return sorted(counts.items(), key=lambda x: x[1], reverse=True)[:5]

def get_total_runs():
    """Returns the total number of recorded runs."""
    with SessionContext() as db:
        return db.query(Run).count()

def get_last_run():
    """Returns the last recorded run object."""
    with SessionContext() as db:
        return db.query(Run).order_by(Run.timestamp.desc()).first()

def get_recent_runs(limit=10):
    """Returns a list of recent Run objects."""
    with SessionContext() as db:
        runs = db.query(Run).order_by(Run.timestamp.desc()).limit(limit).all()
        # Detach/convert to dicts to persist after session close
        return [to_dict(r) for r in runs]

def get_article_by_id(article_id):
    """Fetches a single article by ID (UUID)."""
    # Note: Fetcher uses RSS GUID as 'external_id' but our internal ID is UUID.
    # The Run Sheet stores the UUID as 'id'.
    with SessionContext() as db:
        article = db.query(Article).filter(Article.id == article_id).first()
        if article:
            return to_dict(article)
        return None

def update_enhancement(article_id, full_content, comments_full):
    """Updates an article with enhanced content."""
    with SessionContext() as db:
        article = db.query(Article).filter(Article.id == article_id).first()
        if article:
            article.full_content = full_content
            article.comments_full = comments_full
            article.is_enhanced = True
            db.commit()
            return True
        return False

# --- Helper ---
def to_dict(model_instance):
    """Converts SQLAlchemy model to dict, handling datetimes."""
    d = {}
    for c in model_instance.__table__.columns:
        value = getattr(model_instance, c.name)
        if isinstance(value, datetime):
            value = value.isoformat()
        d[c.name] = value
    return d