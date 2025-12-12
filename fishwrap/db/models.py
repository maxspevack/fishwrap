from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, Float, Boolean
from sqlalchemy.orm import declarative_base
import uuid
from datetime import datetime

Base = declarative_base()

class Article(Base):
    __tablename__ = 'articles'
    
    # Architecture Standard: UUID Primary Keys
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Core Data
    title = Column(String, nullable=False)
    link = Column(String, nullable=False, unique=True) # Ensure link uniqueness
    source_url = Column(String)
    external_id = Column(String, index=True) # RSS GUID
    timestamp = Column(Float) # Epoch time
    
    # Content
    content = Column(Text)
    full_content = Column(Text)
    comments_url = Column(String)
    comments_full = Column(JSON) # List of strings
    
    # Metadata
    categories = Column(JSON) # List of strings from feed
    stats_score = Column(Integer, default=0)
    stats_comments = Column(Integer, default=0)
    
    # Processing Flags
    is_enhanced = Column(Boolean, default=False)
    
    # The Glass Box (Computed Metrics)
    computed_score = Column(Float, default=0.0)
    computed_category = Column(String)
    computed_breakdown = Column(JSON) # Detailed scoring log
    computed_debug = Column(JSON) # Drift/Classification debug info
    
    # System Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Article(title='{self.title[:30]}...', score={self.computed_score})>"
