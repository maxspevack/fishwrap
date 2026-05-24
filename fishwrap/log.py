"""Centralized logging for the fishwrap engine.

Level controlled by the FISHWRAP_LOG_LEVEL environment variable
(default INFO). Output goes to stderr so it composes with the
print()-based progress output that goes to stdout.
"""
import logging
import os
import sys

_LEVEL_NAMES = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


def _resolve_level() -> int:
    raw = os.environ.get("FISHWRAP_LOG_LEVEL", "INFO").upper()
    if raw not in _LEVEL_NAMES:
        raw = "INFO"
    return getattr(logging, raw)


def get_logger(name: str) -> logging.Logger:
    """Return a module-scoped logger configured against the engine root."""
    root = logging.getLogger("fishwrap")
    if not root.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        )
        root.addHandler(handler)
        root.setLevel(_resolve_level())
        root.propagate = False
    return logging.getLogger(name)
