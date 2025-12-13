from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, Float, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
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
    timestamp = Column(Float, index=True) # Epoch time
    
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

class Run(Base):
    """
    Represents a single execution of the pipeline (an 'Edition').
    Acts as the permanent log for the Auditor.
    """
    __tablename__ = 'runs'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Type: 'daily', 'weekly', 'manual'
    run_type = Column(String, default='daily')
    
    # Funnel Metrics (The Glass Box Stats)
    stats_input = Column(Integer, default=0)   # Total items seen/fetched
    stats_pool = Column(Integer, default=0)    # Candidates considered (freshness)
    stats_qualified = Column(Integer, default=0) # Above min score
    stats_selected = Column(Integer, default=0) # Final cut
    
    # Snapshots
    source_dominance = Column(JSON) # Snapshot of input sources
    cut_line_report = Column(JSON)  # Snapshot of near-misses
    perf_metrics = Column(JSON)     # Performance telemetry (timings)
    
    # Relationships
    articles = relationship("RunArticle", back_populates="run", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="run", cascade="all, delete-orphan")

class RunArticle(Base):
    """
    Link table: Which articles appeared in which Run?
    Allows us to reconstruct history (The Almanac).
    Only contains SELECTED articles.
    """
    __tablename__ = 'run_articles'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id = Column(String, ForeignKey('runs.id'))
    article_id = Column(String, ForeignKey('articles.id'))
    
    # Context specific to this run (Score might change over time, rank is specific to this edition)
    final_score = Column(Float)
    rank = Column(Integer)
    section = Column(String)
    
    run = relationship("Run", back_populates="articles")
    article = relationship("Article")

class AuditLog(Base):
    """
    The 'Black Box Recorder'.
    Stores the decision trace for EVERY article processed in a run, 
    including rejected ones. This drives the 'Fishmonger' Tuning UI.
    """
    __tablename__ = 'audit_logs'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id = Column(String, ForeignKey('runs.id'))
    article_id = Column(String, ForeignKey('articles.id'))
    
    # Classification Trace
    original_section = Column(String) # From Source Affinity
    final_section = Column(String)    # From Keyword Classifier
    
    # Scoring Trace
    base_score = Column(Float)
    modifier_score = Column(Float)
    final_score = Column(Float)
    
    # The Verdict
    decision = Column(String) # SELECTED, REJECTED, BURIED (Penalty)
    
    # Detailed Trace (JSON)
    # { 'boosts': ['AI', 'GitHub'], 'penalties': [], 'drift_reason': 'Keyword match' }
    trace = Column(JSON)
    
    run = relationship("Run", back_populates="audit_logs")
    article = relationship("Article")
