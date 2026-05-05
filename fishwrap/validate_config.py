"""
fishwrap.validate_config — config schema doctor.

Catches the schema-level errors that cause runtime crashes 4 minutes
into a fetch: missing required keys, wrong top-level types, malformed
nested structures.

Does NOT validate semantics: URLs are not probed, timezones are not
checked against IANA, file paths are not required to exist on disk.
Those concerns are the runtime engine's. The job here is "fail in
100 ms with a clear message" instead of "fail in 4 minutes with a
KeyError stack trace."

Invocation:
    python -m fishwrap.validate_config <path-to-config.py>

Exit codes:
    0  config is valid
    1  config is invalid (one or more errors on stderr, prefixed `error:`)
    2  usage error (bad args, file not found, parse failure)

This module is the source of truth for the config schema. The
human-readable reference document (docs/CONFIG_SCHEMA.md) is produced
in a separate issue (D2-fw); if the two ever disagree, this code wins.
"""

from __future__ import annotations

import os
import sys
from typing import Any, Callable, Optional


# --- Type checkers ----------------------------------------------------
# Each returns None if the value passes, or a descriptive error string.

def _is_str(v: Any) -> Optional[str]:
    return None if isinstance(v, str) else f"must be a string, got {type(v).__name__}"


def _is_number(v: Any) -> Optional[str]:
    # bool is a subclass of int — exclude it explicitly.
    if isinstance(v, bool):
        return f"must be a number, got bool"
    if isinstance(v, (int, float)):
        return None
    return f"must be a number, got {type(v).__name__}"


def _is_dict(v: Any) -> Optional[str]:
    return None if isinstance(v, dict) else f"must be a dict, got {type(v).__name__}"


def _is_list(v: Any) -> Optional[str]:
    return None if isinstance(v, list) else f"must be a list, got {type(v).__name__}"


def _is_nonempty_list_of_str(v: Any) -> Optional[str]:
    if not isinstance(v, list):
        return f"must be a list, got {type(v).__name__}"
    if not v:
        return "must be non-empty"
    for i, item in enumerate(v):
        if not isinstance(item, str):
            return f"item [{i}] must be a string, got {type(item).__name__}"
    return None


def _is_nonempty_list(v: Any) -> Optional[str]:
    if not isinstance(v, list):
        return f"must be a list, got {type(v).__name__}"
    if not v:
        return "must be non-empty"
    return None


# --- Schema -----------------------------------------------------------

# Required keys: consumer MUST define these — no engine default produces
# meaningful output without them. FEEDS=[] = nothing to fetch; SECTIONS=[] =
# no buckets to produce. Everything else in fishwrap/_config.py has a
# usable default and is therefore treated as optional below.
REQUIRED_KEYS: dict[str, Callable[[Any], Optional[str]]] = {
    "FEEDS": _is_nonempty_list_of_str,
    "SECTIONS": _is_nonempty_list,
}

# Optional keys: validated only if present in the consumer's config.
# Absence falls back to whatever fishwrap/_config.py declares as default.
OPTIONAL_KEYS: dict[str, Callable[[Any], Optional[str]]] = {
    # Structural / nested
    "KEYWORDS": _is_dict,
    "EDITORIAL_POLICIES": _is_list,
    "SCORING_PROFILES": _is_dict,
    "EDITION_SIZE": _is_dict,
    "MIN_SECTION_SCORES": _is_dict,
    "SOURCE_SECTIONS": _is_dict,
    "VISUAL_THRESHOLDS": _is_dict,
    # Path / string keys
    "DATABASE_URL": _is_str,
    "LATEST_HTML_FILE": _is_str,
    "LATEST_PDF_FILE": _is_str,
    "RUN_SHEET_FILE": _is_str,
    "ENHANCED_ISSUE_FILE": _is_str,
    "STATS_FILE": _is_str,
    "SECRETS_FILE": _is_str,
    "ARTICLES_DB_FILE": _is_str,
    "USER_AGENT": _is_str,
    "FOUNDING_DATE": _is_str,
    "TIMEZONE": _is_str,
    "THEME": _is_str,
    # Numeric
    "BOOST_UNIT_VALUE": _is_number,
    "FUZZY_BOOST_MULTIPLIER": _is_number,
    "EXPIRATION_HOURS": _is_number,
    "MAX_ARTICLE_LENGTH": _is_number,
}


def validate_config_namespace(ns: dict) -> list[str]:
    """Validate a loaded config namespace dict.

    Returns a list of human-readable error strings (empty list = valid).
    Collects all errors rather than failing on the first — fixing a
    typo-ridden config in one pass is more useful than fixing one at
    a time.
    """
    errors: list[str] = []

    for key, checker in REQUIRED_KEYS.items():
        if key not in ns:
            errors.append(f"{key} is missing — required")
            continue
        msg = checker(ns[key])
        if msg:
            errors.append(f"{key}: {msg}")

    for key, checker in OPTIONAL_KEYS.items():
        if key in ns:
            msg = checker(ns[key])
            if msg:
                errors.append(f"{key}: {msg}")

    # Nested shape checks for the structures most likely to be wrong.

    sections = ns.get("SECTIONS")
    if isinstance(sections, list):
        for i, section in enumerate(sections):
            if not isinstance(section, dict):
                errors.append(f"SECTIONS[{i}] must be a dict, got {type(section).__name__}")
                continue
            for required_field in ("id", "title"):
                if required_field not in section:
                    errors.append(f"SECTIONS[{i}] is missing required field '{required_field}'")
                elif not isinstance(section[required_field], str):
                    errors.append(
                        f"SECTIONS[{i}].{required_field} must be a string, "
                        f"got {type(section[required_field]).__name__}"
                    )

    policies = ns.get("EDITORIAL_POLICIES")
    if isinstance(policies, list):
        for i, p in enumerate(policies):
            if not isinstance(p, dict):
                errors.append(f"EDITORIAL_POLICIES[{i}] must be a dict, got {type(p).__name__}")
                continue
            if "type" not in p:
                errors.append(f"EDITORIAL_POLICIES[{i}] is missing required field 'type'")
            elif not isinstance(p["type"], str):
                errors.append(
                    f"EDITORIAL_POLICIES[{i}].type must be a string, "
                    f"got {type(p['type']).__name__}"
                )
            if "boosts" in p:
                msg = _is_number(p["boosts"])
                if msg:
                    errors.append(f"EDITORIAL_POLICIES[{i}].boosts {msg}")

    profiles = ns.get("SCORING_PROFILES")
    if isinstance(profiles, dict):
        for required_profile in ("dynamic", "static"):
            if required_profile not in profiles:
                errors.append(f"SCORING_PROFILES is missing required key '{required_profile}'")
            elif not isinstance(profiles[required_profile], dict):
                errors.append(
                    f"SCORING_PROFILES.{required_profile} must be a dict, "
                    f"got {type(profiles[required_profile]).__name__}"
                )

    return errors


def load_config_namespace(config_path: str) -> dict:
    """Load a config.py via exec — matches the engine's loader (fishwrap/_config.py).

    Returns the post-exec globals with __dunder__ keys filtered out.
    Raises whatever exception exec() raises if the config is unparseable.
    """
    config_globals: dict = {"__file__": config_path}
    with open(config_path, "r") as f:
        exec(f.read(), config_globals)
    return {k: v for k, v in config_globals.items() if not k.startswith("__")}


def main(argv: Optional[list[str]] = None) -> int:
    args = sys.argv[1:] if argv is None else argv

    if len(args) != 1:
        print(
            "usage: python -m fishwrap.validate_config <path-to-config.py>",
            file=sys.stderr,
        )
        return 2

    config_path = args[0]

    if not os.path.isfile(config_path):
        print(f"error: config file not found: {config_path}", file=sys.stderr)
        return 2

    try:
        ns = load_config_namespace(config_path)
    except Exception as e:
        print(f"error: could not parse config: {type(e).__name__}: {e}", file=sys.stderr)
        return 2

    errors = validate_config_namespace(ns)
    if errors:
        for err in errors:
            print(f"error: {err}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
