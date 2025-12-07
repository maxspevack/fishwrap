import urllib.request
import ssl
import re
import html
import email.utils
from datetime import datetime
from fishwrap import _config

# Shared SSL context for scraping (permissive)
_ssl_context = ssl.create_default_context()
_ssl_context.check_hostname = False
_ssl_context.verify_mode = ssl.CERT_NONE

def get_ssl_context():
    """Returns the shared permissive SSL context."""
    return _ssl_context

def fetch_url(url, headers=None, timeout=15):
    """
    Robust URL fetcher with default headers and timeout.
    Returns decoded UTF-8 string or None on failure.
    Properly encodes URLs to handle non-ASCII characters.
    """
    if not headers:
        headers = {'User-Agent': _config.USER_AGENT}
    
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
        with urllib.request.urlopen(req, context=_ssl_context, timeout=timeout) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
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
