import urllib.request
import ssl
import re
import html
import email.utils
import time
import threading
import urllib.parse
from datetime import datetime
from fishwrap import _config

# Shared SSL context for scraping (permissive)
_ssl_context = ssl.create_default_context()
_ssl_context.check_hostname = False
_ssl_context.verify_mode = ssl.CERT_NONE

# Rate Limiting State
_rate_limit_lock = threading.Lock()
_last_request_time = {}
_domain_locks = {}

# Config: Minimum seconds between requests to specific domains
RATE_LIMITS = {
    'reddit.com': 2.0,
    'www.reddit.com': 2.0,
    'old.reddit.com': 2.0,
    'hacker-news.firebaseio.com': 0.5, # HN is usually faster/permissive
}

def get_domain(url):
    """Returns the netloc (domain) from a URL string."""
    try:
        parsed = urllib.parse.urlparse(url)
        return parsed.netloc
    except:
        return ""

def get_ssl_context():
    """Returns the shared permissive SSL context."""
    return _ssl_context

def _get_domain_lock(domain):
    """Returns a threading.Lock for a specific domain."""
    with _rate_limit_lock:
        if domain not in _domain_locks:
            _domain_locks[domain] = threading.Lock()
        return _domain_locks[domain]

def rate_limit(domain):
    """
    Enforces rate limits for a given domain.
    """
    limit_delay = 0
    target_domain = None
    
    # Check parent domain for reddit (e.g. old.reddit.com -> reddit.com) matches
    # Simple check for now: exact match or contains
    for d, delay in RATE_LIMITS.items():
        if d in domain:
            limit_delay = delay
            target_domain = d
            break
            
    if limit_delay > 0:
        # Acquire lock for this domain to serialize requests
        lock = _get_domain_lock(target_domain)
        with lock:
            last_time = _last_request_time.get(target_domain, 0)
            now = time.time()
            elapsed = now - last_time
            
            if elapsed < limit_delay:
                sleep_time = limit_delay - elapsed
                # print(f"[RATE LIMIT] Sleeping {sleep_time:.2f}s for {domain}")
                time.sleep(sleep_time)
            
            _last_request_time[target_domain] = time.time()

def fetch_url(url, headers=None, timeout=15, max_size=5 * 1024 * 1024):
    """
    Robust URL fetcher with default headers, timeout, DOMAIN RATE LIMITING,
    and size/time enforcement via chunked reads.
    Returns decoded UTF-8 string or None on failure.
    """
    if not headers:
        headers = {'User-Agent': _config.USER_AGENT}
    
    # 1. Rate Limiting Logic
    parsed = urllib.parse.urlparse(url)
    domain = parsed.netloc
    rate_limit(domain)

    # 2. Fetch Logic
    try:
        # Parse the URL to encode its path and query components correctly
        parsed_url = urllib.parse.urlparse(url)
        # Encode only the path and query, not scheme or netloc
        # safe characters for path are '/' and for query are '&='
        encoded_path = urllib.parse.quote(parsed_url.path, safe='/%')
        encoded_query = urllib.parse.quote(parsed_url.query, safe='&?=')
        
        # Reconstruct the URL with encoded parts
        encoded_url = urllib.parse.urlunparse((
            parsed_url.scheme,
            parsed_url.netloc,
            encoded_path,
            parsed_url.params, # params is already encoded by urlparse
            encoded_query,
            parsed_url.fragment # fragment is not sent to server
        ))

        req = urllib.request.Request(encoded_url, headers=headers)
        
        # Start Clock
        start_time = time.time()
        
        with urllib.request.urlopen(req, context=_ssl_context, timeout=timeout) as response:
            content = b""
            while True:
                # Check Time
                if time.time() - start_time > timeout:
                    # print(f"Timeout fetching {url}")
                    return None
                
                chunk = response.read(1024 * 64) # 64KB chunks
                if not chunk:
                    break
                    
                content += chunk
                
                # Check Size
                if len(content) > max_size:
                    # print(f"Oversize fetching {url}")
                    return None
            
            return content.decode('utf-8')

    except Exception as e:
        # print(f"Error fetching {url}: {e}")
        return None

def clean_html(raw_html):
    """Strips all HTML tags."""
    if not raw_html:
        return ""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext.strip()

def strip_all_html_and_links(text):
    """
    More aggressive cleaner that handles images, links, and escapes.
    Replaces links with [Link].
    """
    if not text:
        return ""
    
    # Remove img tags
    text = re.sub(r'<img[^>]*>', '', text, flags=re.IGNORECASE)
    # Remove a tags, keep content
    text = re.sub(r'<a[^>]*>(.*?)</a>', r'\1', text, flags=re.DOTALL | re.IGNORECASE)
    # Remove all other tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Unescape HTML entities - Double pass to catch nested escapes
    text = html.unescape(text)
    text = html.unescape(text)
    
    # Replace raw URLs with [Link]
    url_pattern = r'(https?://\S+|www\.\S+)'
    text = re.sub(url_pattern, '[Link]', text, flags=re.IGNORECASE)
    
    return text

def parse_date(date_str):
    """Attempts to parse RSS/Atom date strings into a timestamp. Returns 0.0 on failure."""
    if not date_str:
        return 0.0
    try:
        # Try RFC 822 (standard RSS)
        parsed = email.utils.parsedate_to_datetime(date_str)
        return parsed.timestamp()
    except Exception:
        try:
            # Try ISO 8601 (Atom)
            # Python 3.7+ fromisoformat handles some, but simplistic replacement for Z helps
            if date_str.endswith('Z'):
                date_str = date_str[:-1] + '+00:00'
            return datetime.fromisoformat(date_str).timestamp()
        except Exception:
            return 0.0

def smart_truncate(text, max_length):
    """Truncates text at a sentence boundary near the limit."""
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    
    truncated = text[:max_length]
    # Try to find the last sentence ending
    last_period = max(truncated.rfind('.'), truncated.rfind('?'), truncated.rfind('!'))
    
    if last_period > max_length * 0.8:
        return truncated[:last_period + 1] + " [...]"
    return truncated + " [...]"

class Stopwatch:
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    def start(self):
        self.start_time = time.time()
        return self
        
    def stop(self):
        self.end_time = time.time()
        return self.duration
        
    @property
    def duration(self):
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0