"""
fishwrap.db.models — the newsroom schema.

One table. The article corpus for the current window, keyed by link. The
edition's decision record is the runsheet (fishwrap.runsheet), not a table:
the three audit tables that used to live here were written on every build
and never read back.
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, String, Float, Text, JSON, Boolean, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Article(Base):
    __tablename__ = 'articles'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Core data
    title = Column(String, nullable=False)
    link = Column(String, nullable=False, unique=True)  # the key everything else uses
    source_url = Column(String)
    external_id = Column(String, index=True)  # RSS GUID
    timestamp = Column(Float, index=True)  # epoch seconds

    # Content
    content = Column(Text)
    full_content = Column(Text)
    comments_url = Column(String)
    comments_full = Column(JSON)

    # Metadata
    categories = Column(JSON)

    # Processing flags
    is_enhanced = Column(Boolean, default=False)

    # System timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Article(title='{self.title[:30]}...', link={self.link})>"
