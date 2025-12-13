import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from fishwrap.db.models import Article

def test_db():
    print("[TEST] Connecting to newsroom.db...")
    # 1. Setup Connection
    engine = create_engine('sqlite:///newsroom.db')
    Session = sessionmaker(bind=engine)
    session = Session()

    # 2. Create Object
    print("[TEST] Creating dummy article...")
    new_article = Article(
        title="The Glass Box Test",
        link="https://fishwrap.org/test/1",
        source_url="https://fishwrap.org/rss",
        external_id="guid-123-abc",
        timestamp=1700000000.0,
        categories=["test", "engineering"],
        computed_score=9000.5,
        computed_breakdown={"boost": "high_test_value"}
    )

    # 3. Save (Commit)
    try:
        session.add(new_article)
        session.commit()
        print("[TEST] Article saved successfully.")
    except Exception as e:
        print(f"[FAIL] Error saving article: {e}")
        session.rollback()
        return

    # 4. Read Back
    print("[TEST] Querying article back...")
    retrieved = session.query(Article).filter_by(link="https://fishwrap.org/test/1").first()

    if retrieved:
        print(f"[PASS] Retrieved Article:")
        print(f"   - ID (UUID): {retrieved.id}")
        print(f"   - Title:     {retrieved.title}")
        print(f"   - JSON Data: {retrieved.computed_breakdown}")
        
        # Cleanup (Delete test data)
        print("[TEST] Cleaning up...")
        session.delete(retrieved)
        session.commit()
    else:
        print("[FAIL] Could not retrieve article.")

if __name__ == "__main__":
    test_db()