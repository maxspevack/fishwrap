"""
Schema integrity: Base.metadata.create_all against a fresh SQLite file
produces exactly the one table the engine uses, with every declared column.

Run: python3 scripts/test_schema_integrity.py
Or:  make test
"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine, inspect  # noqa: E402
from fishwrap.db.models import Base  # noqa: E402

EXPECTED_COLUMNS = {
    'articles': {
        'id', 'title', 'link', 'source_url', 'external_id', 'timestamp',
        'content', 'comments_url', 'categories', 'created_at', 'updated_at',
    },
}


class SchemaTests(unittest.TestCase):

    def test_create_all_matches_models(self):
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        try:
            engine = create_engine(f'sqlite:///{db_path}')
            Base.metadata.create_all(engine)
            insp = inspect(engine)
            self.assertEqual(set(insp.get_table_names()), set(EXPECTED_COLUMNS))
            for table, cols in EXPECTED_COLUMNS.items():
                self.assertEqual({c['name'] for c in insp.get_columns(table)}, cols)
            self.assertEqual(insp.get_foreign_keys('articles'), [])
        finally:
            os.unlink(db_path)


if __name__ == "__main__":
    unittest.main()
