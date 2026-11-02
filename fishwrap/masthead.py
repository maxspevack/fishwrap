"""
fishwrap.masthead — the loader for masthead.toml + dossier.md + policies.jsonl.

The masthead is the new shape of the per-instance configuration. It replaces
the v2 Python config.py (with EDITORIAL_POLICIES, BOOST_UNIT_VALUE, etc.) with
a two-file user-facing data model:

  masthead.toml  — engine constants, sections, feeds, source-section routing
  dossier.md     — the editor's voice (prose); read by the LLM editor in
                   paid mode; visible to the human in any mode

A third file, policies.jsonl, is an append-only event log of signed editorial
policies (source_ban, title_pattern_ban, topic_ban, source_whitelist,
section_lead_preference). It is consumed by the engine alongside the masthead.
The policies file will be folded into the masthead's structured vocabulary in
a future release; for now it is the operative store for those primitives.

Public surface:
  Masthead.load(instance_dir)            -> Masthead
  Masthead.feeds                         -> list[str]
  Masthead.sections                      -> list[dict]
  Masthead.source_sections               -> dict[str, str]
  Masthead.policies                      -> list[dict]  (active, after strikes)
  Masthead.dossier_text                  -> str
  Masthead.dossier_lines                 -> list[str]   (1-indexed)
  Masthead.section_by_id(sid)            -> dict | None
"""
from __future__ import annotations

import json
import tomllib
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Masthead:
    """Loaded state of one instance's editorial configuration."""

    instance_dir: Path
    raw: dict = field(default_factory=dict)
    policies: list[dict] = field(default_factory=list)
    dossier_text: str = ""
    dossier_lines: list[str] = field(default_factory=list)

    # ---- properties that mirror the TOML shape ----

    @property
    def identity(self) -> dict:
        return self.raw.get("identity", {})

    @property
    def engine(self) -> dict:
        return self.raw.get("engine", {})

    @property
    def sections(self) -> list[dict]:
        return self.raw.get("section", [])

    @property
    def feeds(self) -> list[str]:
        return self.raw.get("feeds", {}).get("urls", [])

    @property
    def source_sections(self) -> dict[str, str]:
        return self.raw.get("source_sections", {})

    @property
    def name(self) -> str:
        return self.identity.get("name", "Untitled")

    @property
    def timezone(self) -> str:
        return self.identity.get("timezone", "UTC")

    @property
    def user_agent(self) -> str:
        return self.identity.get("user_agent", "Fishwrap/1.0")

    @property
    def expiration_hours(self) -> int:
        return int(self.engine.get("expiration_hours", 24))

    # ---- methods ----

    def section_by_id(self, sid: str) -> dict | None:
        for s in self.sections:
            if s.get("id") == sid:
                return s
        return None

    def keywords_for(self, section_id: str) -> list[str]:
        s = self.section_by_id(section_id)
        return list(s.get("keywords") or []) if s else []

    # ---- loader ----

    @classmethod
    def load(cls, instance_dir: str | Path) -> "Masthead":
        d = Path(instance_dir)
        toml_path = d / "masthead.toml"
        if not toml_path.exists():
            raise FileNotFoundError(f"masthead.toml not found in {d}")
        raw = tomllib.loads(toml_path.read_text())

        # Validate the minimum the engine requires.
        errs = validate(raw)
        if errs:
            raise ValueError(f"masthead.toml at {d} is invalid:\n" + "\n".join(f"  - {e}" for e in errs))

        # Active policies = apply create/strike events in order.
        pol_path = d / "policies.jsonl"
        policies: list[dict] = []
        if pol_path.exists() and pol_path.read_text().strip():
            active: dict[str, dict] = {}
            for line in pol_path.read_text().splitlines():
                if not line.strip():
                    continue
                ev = json.loads(line)
                if ev.get("event") == "create":
                    active[ev["policy_id"]] = ev
                elif ev.get("event") == "strike":
                    active.pop(ev["policy_id"], None)
            policies = list(active.values())

        dossier_path = d / "dossier.md"
        dossier_text = ""
        dossier_lines: list[str] = []
        if dossier_path.exists():
            dossier_text = dossier_path.read_text()
            dossier_lines = dossier_text.splitlines()

        return cls(
            instance_dir=d,
            raw=raw,
            policies=policies,
            dossier_text=dossier_text,
            dossier_lines=dossier_lines,
        )


# ============ validation ============

REQUIRED_TOP_KEYS = {"identity", "engine", "section", "feeds"}
REQUIRED_IDENTITY_KEYS = {"name", "timezone"}
REQUIRED_ENGINE_KEYS = {"expiration_hours"}
REQUIRED_SECTION_KEYS = {"id", "title", "edition_size", "lead_count", "feature_count", "max_per_source"}


def validate(raw: dict) -> list[str]:
    """Return a list of human-readable errors. Empty list means valid."""
    errs: list[str] = []

    missing_top = REQUIRED_TOP_KEYS - set(raw.keys())
    if missing_top:
        errs.append(f"missing top-level table(s): {sorted(missing_top)}")
        return errs  # don't continue — the structural shape is wrong

    if not isinstance(raw["identity"], dict):
        errs.append("identity: must be a table")
    else:
        missing_id = REQUIRED_IDENTITY_KEYS - set(raw["identity"].keys())
        if missing_id:
            errs.append(f"identity: missing key(s) {sorted(missing_id)}")

    if not isinstance(raw["engine"], dict):
        errs.append("engine: must be a table")
    else:
        missing_eng = REQUIRED_ENGINE_KEYS - set(raw["engine"].keys())
        if missing_eng:
            errs.append(f"engine: missing key(s) {sorted(missing_eng)}")

    if not isinstance(raw["section"], list) or not raw["section"]:
        errs.append("section: must be a non-empty array of [[section]] tables")
    else:
        section_ids: set[str] = set()
        for i, s in enumerate(raw["section"]):
            if not isinstance(s, dict):
                errs.append(f"section[{i}]: must be a table")
                continue
            missing_sec = REQUIRED_SECTION_KEYS - set(s.keys())
            if missing_sec:
                errs.append(f"section[{i}] (id={s.get('id','?')}): missing key(s) {sorted(missing_sec)}")
            sid = s.get("id")
            if isinstance(sid, str):
                if sid in section_ids:
                    errs.append(f"section[{i}]: duplicate id {sid!r}")
                section_ids.add(sid)

    # Routing targets must be declared sections; a typo here would otherwise
    # route a whole source into a section the printer never renders.
    ss = raw.get("source_sections", {})
    if ss and not isinstance(ss, dict):
        errs.append("source_sections: must be a table of domain = section_id")
    elif ss and isinstance(raw["section"], list):
        declared = {s.get("id") for s in raw["section"] if isinstance(s, dict)}
        for dom, sid in ss.items():
            if sid not in declared:
                errs.append(f"source_sections: {dom!r} routes to undeclared section {sid!r}")

    feeds = raw.get("feeds", {})
    if not isinstance(feeds, dict) or not isinstance(feeds.get("urls"), list) or not feeds["urls"]:
        errs.append("feeds.urls: must be a non-empty array of strings")
    else:
        for i, u in enumerate(feeds["urls"]):
            if not isinstance(u, str) or not u.strip():
                errs.append(f"feeds.urls[{i}]: must be a non-empty string")

    return errs
