#!/usr/bin/env python3
"""
Dispatch the day's demo build when it is due and has not been built.

GitHub starts scheduled workflows hours late, and the lag drifts (a median of
7.5 hours in 2026-11), so one daily cron cannot hold a time of day. tick.yml
runs this every hour instead. Each run asks one question: is it past DUE in the
masthead's timezone, and has an edition been built since? The ticks are late
too, but one lands every hour, so the build starts within about an hour of DUE
whatever the lag is. A failed build is retried on a later tick.

The decision is decide(), a pure function of the clock and the build
workflow's recent runs:

  wait      it is not yet DUE today
  done      a run created since DUE succeeded
  running   a run created since DUE is queued or in progress
  give-up   --max-attempts runs since DUE and none succeeded (exits 1)
  dispatch  otherwise

Usage (tick.yml):
  python3 scripts/demo_tick.py --workflow demo.yml \\
      --timezone America/Los_Angeles --due 05:00
"""
import argparse
import json
import subprocess
import sys
import time as time_module
from datetime import datetime, time, timezone
from zoneinfo import ZoneInfo


def _utc(iso: str) -> datetime:
    d = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def due_instant(now: datetime, tz: str, due: time) -> datetime:
    """Today's DUE, where 'today' and DUE are read in tz. Returned in UTC."""
    zone = ZoneInfo(tz)
    today = now.astimezone(zone).date()
    return datetime.combine(today, due, tzinfo=zone).astimezone(timezone.utc)


def decide(now: datetime, runs: list[dict], *, tz: str, due: time, max_attempts: int) -> str:
    """runs: the build workflow's recent runs, each with createdAt, status, conclusion."""
    start = due_instant(now, tz, due)
    if now < start:
        return "wait"
    since = [r for r in runs if _utc(r["createdAt"]) >= start]
    if any(r["status"] == "completed" and r["conclusion"] == "success" for r in since):
        return "done"
    if any(r["status"] != "completed" for r in since):
        return "running"
    if len(since) >= max_attempts:
        return "give-up"
    return "dispatch"


def recent_runs(workflow: str) -> list[dict]:
    out = subprocess.run(
        ["gh", "run", "list", "--workflow", workflow, "--limit", "40",
         "--json", "createdAt,status,conclusion"],
        check=True, stdout=subprocess.PIPE, text=True,
    ).stdout
    return json.loads(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--workflow", required=True, help="the build workflow's file name")
    ap.add_argument("--timezone", required=True, help="the masthead's timezone")
    ap.add_argument("--due", required=True, help="HH:MM in that timezone")
    ap.add_argument("--max-attempts", type=int, default=3)
    ap.add_argument("--ref", default="main")
    ap.add_argument("--now", default="", help="pretend it is this UTC instant (ISO 8601); for testing")
    ap.add_argument("--dry-run", action="store_true", help="print the decision; dispatch nothing")
    a = ap.parse_args(argv)

    now = _utc(a.now) if a.now else datetime.now(timezone.utc)
    due = time.fromisoformat(a.due)
    action = decide(now, recent_runs(a.workflow), tz=a.timezone, due=due, max_attempts=a.max_attempts)
    print(f"[TICK] now {now:%Y-%m-%dT%H:%MZ}, due {due_instant(now, a.timezone, due):%Y-%m-%dT%H:%MZ}: {action}")

    if action == "give-up":
        # A dispatched build runs as github-actions[bot], so its failure
        # notifies nobody. The tick is the scheduled run, so it goes red.
        print(f"::error::{a.workflow} has failed {a.max_attempts} times since it came due; not dispatching again today")
        return 1
    if action == "dispatch" and not a.dry_run:
        subprocess.run(["gh", "workflow", "run", a.workflow, "--ref", a.ref], check=True)
        print(f"[TICK] dispatched {a.workflow} on {a.ref}")
        # Late ticks can arrive together. They run one at a time (tick.yml's
        # concurrency group), so hold the slot until the new run is listed and
        # the next tick sees it as running.
        time_module.sleep(20)
    return 0


if __name__ == "__main__":
    sys.exit(main())
