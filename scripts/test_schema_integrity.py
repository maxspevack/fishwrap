"""
Schema integrity test for fishwrap.

The runtime bootstraps its schema via SQLAlchemy's Base.metadata.create_all
(see fishwrap/db/repository.py:_initialize_engine). This test verifies that
calling create_all against a fresh SQLite database produces a schema that:
  1. contains every table declared in fishwrap.db.models
  2. contains every column declared on those models
  3. has the foreign-key relationships declared on Run/RunArticle/AuditLog

Self-contained: creates and tears down its own tempfile DB. No dependency on
demo/data/ or any pre-existing artifact.
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine, inspect
from fishwrap.db.models import Base


EXPECTED_TABLES = {'articles', 'runs', 'run_articles', 'audit_logs'}

EXPECTED_COLUMNS = {
    'articles': {
        'id', 'title', 'link', 'source_url', 'external_id', 'timestamp',
        'content', 'full_content', 'comments_url', 'comments_full',
        'categories', 'is_enhanced', 'created_at', 'updated_at',
    },
    'runs': {
        'id', 'timestamp', 'run_type',
        'stats_input', 'stats_pool', 'stats_qualified', 'stats_selected',
        'source_dominance', 'cut_line_report', 'perf_metrics',
    },
    'run_articles': {
        'id', 'run_id', 'article_id', 'final_score', 'rank', 'section',
    },
    'audit_logs': {
        'id', 'run_id', 'article_id', 'original_section', 'final_section',
        'base_score', 'modifier_score', 'final_score', 'decision', 'trace',
    },
}

EXPECTED_FOREIGN_KEYS = {
    'run_articles': {('run_id', 'runs', 'id'), ('article_id', 'articles', 'id')},
    'audit_logs':   {('run_id', 'runs', 'id'), ('article_id', 'articles', 'id')},
}


def test_schema_integrity():
    print("[TEST] Verifying schema integrity (Base.metadata.create_all)...")

    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    try:
        engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(engine)
        inspector = inspect(engine)

        # 1. Tables
        actual_tables = set(inspector.get_table_names())
        missing_tables = EXPECTED_TABLES - actual_tables
        extra_tables = actual_tables - EXPECTED_TABLES
        if missing_tables:
            print(f"[FAIL] missing tables: {sorted(missing_tables)}")
            sys.exit(1)
        if extra_tables:
            print(f"[FAIL] unexpected tables created: {sorted(extra_tables)}")
            sys.exit(1)
        print(f"  [OK] tables match: {sorted(EXPECTED_TABLES)}")

        # 2. Columns
        for table, expected_cols in EXPECTED_COLUMNS.items():
            actual_cols = {c['name'] for c in inspector.get_columns(table)}
            missing_cols = expected_cols - actual_cols
            if missing_cols:
                print(f"[FAIL] {table}: missing columns {sorted(missing_cols)}")
                sys.exit(1)
        print(f"  [OK] columns match for all {len(EXPECTED_COLUMNS)} tables")

        # 3. Foreign keys
        for table, expected_fks in EXPECTED_FOREIGN_KEYS.items():
            actual_fks = set()
            for fk in inspector.get_foreign_keys(table):
                # Each fk: {'constrained_columns': [...], 'referred_table': '...', 'referred_columns': [...]}
                for col, ref_col in zip(fk['constrained_columns'], fk['referred_columns']):
                    actual_fks.add((col, fk['referred_table'], ref_col))
            missing_fks = expected_fks - actual_fks
            if missing_fks:
                print(f"[FAIL] {table}: missing foreign keys {sorted(missing_fks)}")
                sys.exit(1)
        print(f"  [OK] foreign keys match for {len(EXPECTED_FOREIGN_KEYS)} link tables")

        print("[PASS] Schema integrity verified.")
    finally:
        os.unlink(db_path)


if __name__ == "__main__":
    test_schema_integrity()
