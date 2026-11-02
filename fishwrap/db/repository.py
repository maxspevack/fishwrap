"""
fishwrap.db.repository — the newsroom database.

SQLite, one table (models.py), keyed by link. Bootstraps its own schema on
first use, so fresh checkouts and ephemeral container runs need no init step.
"""
import os
import time
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from fishwrap import _config
from fishwrap.db.models import Article, Base

_current_engine = None
_SessionLocal = None


def _get_database_url():
    """The DB URL from _config; relative SQLite paths resolve against CWD."""
    db_url = getattr(_config, 'DATABASE_URL', 'sqlite:///newsroom.db')
    if db_url.startswith('sqlite:///'):
        db_file = db_url.replace('sqlite:///', '')
        if not os.path.isabs(db_file):
            return f"sqlite:///{os.path.abspath(db_file)}"
    return db_url


def _initialize_engine():
    """Create (or re-create, if _config changed) the engine and session factory."""
    global _current_engine, _SessionLocal
    url = _get_database_url()
    if _current_engine is None or str(_current_engine.url) != url:
        _current_engine = create_engine(url)
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_current_engine)
        Base.metadata.create_all(_current_engine)


class SessionContext:
    def __enter__(self):
        _initialize_engine()
        self.db = _SessionLocal()
        return self.db

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()


# ============ writes ============

def upsert_article(article_data):
    """Insert or update by link. Returns 'new' or 'updated'.

    An update takes the newer timestamp, the latest title (feeds fix typos),
    and the latest metadata. It never touches full_content or is_enhanced.
    """
    with SessionContext() as db:
        existing = db.query(Article).filter(Article.link == article_data['link']).first()
        if not existing:
            db.add(Article(**article_data))
            db.commit()
            return "new"
        if (article_data.get('timestamp') or 0) > (existing.timestamp or 0):
            existing.timestamp = article_data['timestamp']
        if article_data.get('title'):
            existing.title = article_data['title']
        existing.categories = article_data.get('categories')
        existing.source_url = article_data.get('source_url')
        existing.comments_url = article_data.get('comments_url')
        db.commit()
        return "updated"


def update_enhancement_by_link(link, full_content, comments_full=None):
    """Store scraped full text for one article. Returns True if it existed."""
    with SessionContext() as db:
        article = db.query(Article).filter(Article.link == link).first()
        if not article:
            return False
        article.full_content = full_content
        article.comments_full = comments_full or []
        article.is_enhanced = True
        db.commit()
        return True


def prune_old_articles(hours=72):
    """Delete articles older than `hours`. Returns the number deleted."""
    cutoff = time.time() - (hours * 3600)
    with SessionContext() as db:
        n = db.query(Article).filter(Article.timestamp < cutoff).delete()
        db.commit()
        return n


# ============ reads ============

def get_max_timestamp():
    from sqlalchemy import func
    with SessionContext() as db:
        return db.query(func.max(Article.timestamp)).scalar()


def get_recent_articles(hours=24, anchor_ts=None):
    """Articles in the `hours` before `anchor_ts` (default: now), in the
    editor's total order: newest first, ties by link."""
    if anchor_ts is None:
        anchor_ts = time.time()
    cutoff = anchor_ts - (hours * 3600)
    with SessionContext() as db:
        rows = (db.query(Article)
                .filter(Article.timestamp >= cutoff)
                .order_by(Article.timestamp.desc(), Article.link.asc())
                .all())
        return [to_dict(a) for a in rows]


def get_total_count():
    with SessionContext() as db:
        return db.query(Article).count()


def get_article_by_link(link):
    with SessionContext() as db:
        a = db.query(Article).filter(Article.link == link).first()
        return to_dict(a) if a else None


def get_content_by_links(links):
    """{link: {'content', 'full_content', 'is_enhanced'}} for the given links."""
    links = list(links)
    if not links:
        return {}
    out = {}
    with SessionContext() as db:
        for i in range(0, len(links), 500):
            chunk = links[i:i + 500]
            for a in db.query(Article).filter(Article.link.in_(chunk)).all():
                out[a.link] = {"content": a.content, "full_content": a.full_content,
                               "is_enhanced": bool(a.is_enhanced)}
    return out


# ============ helper ============

def to_dict(model_instance):
    d = {}
    for c in model_instance.__table__.columns:
        value = getattr(model_instance, c.name)
        if isinstance(value, datetime):
            value = value.isoformat()
        d[c.name] = value
    return d
