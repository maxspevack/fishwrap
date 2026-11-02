import sys
import os
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fishwrap import fetcher

class TestFetcherResilience(unittest.TestCase):
    
    @patch('fishwrap.utils.fetch_url')
    def test_process_feed_garbage(self, mock_fetch):
        print("[TEST] Verifying Fetcher Resilience (Garbage Input)...")
        
        # Scenario 1: Garbage XML
        mock_fetch.return_value = "<rss>Garbage<broken>"
        
        items = fetcher.process_feed('http://bad-feed.com', 0)
        
        if items == []:
            print("  [PASS] Handled Garbage XML (Empty list returned).")
        else:
            print(f"  [FAIL] Did not handle garbage XML: {items}")
            sys.exit(1)
            
    @patch('fishwrap.utils.fetch_url')
    def test_process_feed_none(self, mock_fetch):
        # Scenario 2: Network Failure (None)
        mock_fetch.return_value = None
        
        items = fetcher.process_feed('http://dead-feed.com', 0)
        
        if items == []:
            print("  [PASS] Handled Network Failure (Empty list returned).")
        else:
            print(f"  [FAIL] Did not handle None: {items}")
            sys.exit(1)


RSS_DOC = """<?xml version="1.0"?>
<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/">
  <channel><title>T</title>
    <item>
      <title>
            Alpha   story
      </title>
      <link>https://example.com/alpha</link>
      <guid>alpha-guid</guid>
      <comments>https://example.com/alpha#comments</comments>
      <pubDate>Mon, 02 Nov 2026 00:00:00 GMT</pubDate>
      <description>teaser</description>
      <content:encoded>&lt;p&gt;full body&lt;/p&gt;</content:encoded>
    </item>
    <item>
      <title>Too old</title>
      <link>https://example.com/old</link>
      <pubDate>Mon, 01 Jan 2001 00:00:00 GMT</pubDate>
    </item>
  </channel>
</rss>"""

ATOM_DOC = """<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>A</title>
  <entry>
    <title>Beta entry</title>
    <id>urn:beta</id>
    <link href="https://example.com/beta"/>
    <updated>2026-11-02T00:00:00Z</updated>
    <content>beta body</content>
  </entry>
</feed>"""


class TestParserModelContract(unittest.TestCase):
    """Every dict the parser emits must construct an Article. The fetcher
    once emitted a key the model had dropped (base_boosts), and every feed
    failed at insert time while the fetcher reported success per feed."""

    @patch('fishwrap.utils.fetch_url')
    def test_rss_items_construct_article(self, mock_fetch):
        from fishwrap.db.models import Article
        mock_fetch.return_value = RSS_DOC
        items = fetcher.process_feed('https://example.com/rss', cutoff=1_000_000_000)
        self.assertEqual([i['title'] for i in items], ['Alpha story'])
        a = items[0]
        self.assertEqual(a['link'], 'https://example.com/alpha')
        self.assertEqual(a['external_id'], 'alpha-guid')
        self.assertEqual(a['comments_url'], 'https://example.com/alpha#comments')
        self.assertEqual(a['content'], '<p>full body</p>')
        self.assertEqual(a['source_url'], 'https://example.com/rss')
        self.assertGreater(a['timestamp'], 1_000_000_000)
        Article(**a)  # raises TypeError on any key the model lacks

    @patch('fishwrap.utils.fetch_url')
    def test_atom_entries_construct_article(self, mock_fetch):
        from fishwrap.db.models import Article
        mock_fetch.return_value = ATOM_DOC
        items = fetcher.process_feed('https://example.com/atom', cutoff=1_000_000_000)
        self.assertEqual(len(items), 1)
        a = items[0]
        self.assertEqual(a['title'], 'Beta entry')
        self.assertEqual(a['link'], 'https://example.com/beta')
        self.assertEqual(a['external_id'], 'urn:beta')
        self.assertEqual(a['content'], 'beta body')
        Article(**a)


if __name__ == "__main__":
    unittest.main()
