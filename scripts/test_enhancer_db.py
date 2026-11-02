"""
Enhancer persistence: full text stored by link, flagged enhanced, read back.

Run: python3 scripts/test_enhancer_db.py
Or:  make test
"""
import os
import sys
import time
import unittest
import uuid

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# A throwaway instance so this never touches the demo DB: the masthead loader
# derives sqlite:///demo/data/<dirname>.db from the instance directory name.
os.environ['FISHWRAP_CONFIG'] = 'demo/test_config'

from fishwrap.db import repository  # noqa: E402


class EnhancerPersistenceTests(unittest.TestCase):

    def test_update_by_link_round_trip(self):
        link = f"http://test.example/{uuid.uuid4()}"
        repository.upsert_article({'title': 'Enhancer Test', 'link': link,
                                   'source_url': 'http://test.example/feed', 'timestamp': time.time()})
        self.assertTrue(repository.update_enhancement_by_link(link, "full text", ["c1"]))
        fetched = repository.get_article_by_link(link)
        self.assertEqual(fetched['full_content'], "full text")
        self.assertEqual(fetched['comments_full'], ["c1"])
        self.assertTrue(fetched['is_enhanced'])
        by_links = repository.get_content_by_links([link, "http://nope.example/x"])
        self.assertEqual(set(by_links), {link})
        self.assertTrue(by_links[link]['is_enhanced'])

    def test_unknown_link_is_false(self):
        self.assertFalse(repository.update_enhancement_by_link("http://nope.example/y", "x"))


if __name__ == "__main__":
    unittest.main()
