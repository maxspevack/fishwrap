"""
fishwrap._config — engine-wide configuration, loaded from a Masthead.

Historical (v2): _config was a Python module exec'd from the user's
config.py at import time. The user wrote `EDITORIAL_POLICIES = [...]` and
similar globals in their config, and the engine read them off this module.

Current: the user's editorial state lives in `masthead.toml` + optional
`dossier.md` + optional `policies.jsonl`, all in an instance directory.
`FISHWRAP_CONFIG` now points at that directory (not a Python file). This
module loads the masthead at import time and exposes the values the
existing engine consumers (fetcher, enhancer, db, utils) read.

Consumers should READ from this module's globals. They should not modify
them. New code should prefer to take a `Masthead` instance as a parameter
rather than reading globals; this module is a compatibility shim for the
modules that pre-date that style.
"""
import os
import sys
from pathlib import Path

from fishwrap.masthead import Masthead


# ============ engine-internal defaults (not in the masthead) ============

# Article-content truncation for storage. Long-form articles get cropped
# here so a single feed item with megabytes of <content:encoded> doesn't
# blow up the database row.
MAX_ARTICLE_LENGTH = 15000

# Concurrency cap for the fetcher's ThreadPoolExecutor. Lower this if the
# configured feed set hits a small number of hosts (a high value becomes
# a thundering herd against one origin).
FETCH_WORKERS = 10

# Minimum seconds between requests to a single host when no explicit
# RATE_LIMITS entry applies in fishwrap/utils.py. Set to 0 to allow
# unthrottled concurrency for unlisted hosts; raise to apply a global
# floor across every host.
FETCH_DEFAULT_RATE_LIMIT_SECONDS = 0.0

# ============ engine-internal artifact paths (relative to cwd or output dir) ============

ARTICLES_DB_FILE = "articles_db.json"  # legacy
RUN_SHEET_FILE = "demo/output/run_sheet.json"
ENHANCED_ISSUE_FILE = "demo/output/enhanced_issue.json"
SECRETS_FILE = "secrets.json"
STATS_FILE = "demo/output/publication_stats.json"
LATEST_HTML_FILE = "demo/output/index.html"
LATEST_PDF_FILE = "demo/output/edition.pdf"


# ============ masthead-derived values (loaded from FISHWRAP_CONFIG dir) ============

MASTHEAD: Masthead | None = None
FEEDS: list[str] = []
TIMEZONE: str = "UTC"
USER_AGENT: str = "Fishwrap/1.0 (+https://github.com/maxspevack/fishwrap)"
EXPIRATION_HOURS: int = 24
DATABASE_URL: str = "sqlite:///demo/data/vanilla.db"
FOUNDING_DATE: str = "2024-01-01"
THEME: str = "demo/themes/basic"
SECTIONS: list[dict] = []
SOURCE_SECTIONS: dict[str, str] = {}


def _load_from_instance_dir(instance_dir: str | Path):
    """Load a Masthead from the given directory and populate this module's globals."""
    global MASTHEAD, FEEDS, TIMEZONE, USER_AGENT, EXPIRATION_HOURS
    global DATABASE_URL, FOUNDING_DATE, SECTIONS, SOURCE_SECTIONS

    MASTHEAD = Masthead.load(instance_dir)
    FEEDS = MASTHEAD.feeds
    TIMEZONE = MASTHEAD.timezone
    USER_AGENT = MASTHEAD.user_agent
    EXPIRATION_HOURS = MASTHEAD.expiration_hours
    FOUNDING_DATE = MASTHEAD.identity.get("founding_date", FOUNDING_DATE)
    SECTIONS = MASTHEAD.sections
    SOURCE_SECTIONS = MASTHEAD.source_sections

    # DATABASE_URL is engine-internal. Default to a per-instance file under demo/data/.
    db_path = Path("demo/data") / f"{Path(instance_dir).name}.db"
    DATABASE_URL = f"sqlite:///{db_path}"


# ============ load at import time if FISHWRAP_CONFIG is set ============

_config_path = os.environ.get("FISHWRAP_CONFIG")
if _config_path:
    p = Path(_config_path)
    if not p.exists():
        print(f"[CONFIG] Warning: FISHWRAP_CONFIG={_config_path} but path not found.")
    elif p.is_dir():
        # New shape: directory containing masthead.toml + dossier.md + policies.jsonl
        try:
            _load_from_instance_dir(p)
        except Exception as e:
            print(f"[CONFIG] Error loading masthead from {p}: {e}")
            sys.exit(1)
    elif p.is_file() and p.name == "masthead.toml":
        # Convenience: user pointed at the masthead file directly; load its parent.
        try:
            _load_from_instance_dir(p.parent)
        except Exception as e:
            print(f"[CONFIG] Error loading masthead from {p.parent}: {e}")
            sys.exit(1)
    else:
        print(f"[CONFIG] FISHWRAP_CONFIG={_config_path} is not a directory or a masthead.toml. "
              f"The v2 Python-config format is no longer supported. "
              f"Migrate to masthead.toml (see demo/ for an example).")
        sys.exit(1)
