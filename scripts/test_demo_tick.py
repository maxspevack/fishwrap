"""
Tests for scripts/demo_tick.py: the hourly tick dispatches the day's build
once it is due, never twice for one edition, and stops after repeated failures.

Run: python3 scripts/test_demo_tick.py
Or:  make test
"""
import os
import sys
import unittest
from datetime import datetime, time, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import demo_tick as dt  # noqa: E402

TZ = "America/Los_Angeles"
DUE = time(5, 0)


def at(iso: str) -> datetime:
    return datetime.fromisoformat(iso).replace(tzinfo=timezone.utc)


def run(created: str, status: str = "completed", conclusion: str | None = "success") -> dict:
    return {"createdAt": created + "Z", "status": status, "conclusion": conclusion}


def decide(now: str, runs: list[dict], max_attempts: int = 3) -> str:
    return dt.decide(at(now), runs, tz=TZ, due=DUE, max_attempts=max_attempts)


class DueInstantTests(unittest.TestCase):
    def test_due_follows_the_timezone_across_dst(self):
        # 05:00 Pacific is 13:00 UTC in winter and 12:00 UTC in summer.
        self.assertEqual(dt.due_instant(at("2026-11-28T20:00:00"), TZ, DUE), at("2026-11-28T13:00:00"))
        self.assertEqual(dt.due_instant(at("2026-07-04T20:00:00"), TZ, DUE), at("2026-07-04T12:00:00"))

    def test_today_is_the_local_date_not_the_utc_date(self):
        # 03:00 UTC on the 29th is still the 28th in Los Angeles.
        self.assertEqual(dt.due_instant(at("2026-11-29T03:00:00"), TZ, DUE), at("2026-11-28T13:00:00"))


class DecideTests(unittest.TestCase):
    def test_waits_before_due(self):
        self.assertEqual(decide("2026-11-28T12:59:00", []), "wait")

    def test_waits_after_local_midnight_even_though_yesterday_built(self):
        # 08:30 UTC is 00:30 Pacific: a new day, not yet due.
        self.assertEqual(decide("2026-11-28T08:30:00", [run("2026-11-27T13:20:00")]), "wait")

    def test_dispatches_once_due_with_nothing_built(self):
        self.assertEqual(decide("2026-11-28T13:00:00", []), "dispatch")

    def test_a_build_from_before_due_does_not_count(self):
        # A push at 01:00 Pacific built an edition; the daily one is still owed.
        self.assertEqual(decide("2026-11-28T13:30:00", [run("2026-11-28T09:00:00")]), "dispatch")

    def test_done_after_a_success_since_due(self):
        self.assertEqual(decide("2026-11-28T15:00:00", [run("2026-11-28T13:25:00")]), "done")

    def test_a_late_evening_tick_is_still_done(self):
        # 03:00 UTC on the 29th is 19:00 Pacific on the 28th.
        self.assertEqual(decide("2026-11-29T03:00:00", [run("2026-11-28T13:25:00")]), "done")

    def test_running_while_a_build_is_queued_or_in_progress(self):
        for status in ("queued", "in_progress"):
            self.assertEqual(decide("2026-11-28T13:40:00", [run("2026-11-28T13:25:00", status, None)]), "running")

    def test_a_failed_build_is_retried(self):
        failed = [run("2026-11-28T13:25:00", conclusion="failure")]
        self.assertEqual(decide("2026-11-28T14:30:00", failed), "dispatch")

    def test_gives_up_after_max_attempts(self):
        failed = [run(f"2026-11-28T{h}:25:00", conclusion="failure") for h in (13, 14, 15)]
        self.assertEqual(decide("2026-11-28T16:30:00", failed), "give-up")
        self.assertEqual(decide("2026-11-28T16:30:00", failed, max_attempts=4), "dispatch")

    def test_a_success_after_failures_is_done(self):
        runs = [run("2026-11-28T13:25:00", conclusion="failure"), run("2026-11-28T14:25:00")]
        self.assertEqual(decide("2026-11-28T15:30:00", runs), "done")

    def test_a_run_created_exactly_at_due_counts(self):
        self.assertEqual(decide("2026-11-28T13:30:00", [run("2026-11-28T13:00:00")]), "done")

    def test_cancelled_and_skipped_runs_count_as_attempts(self):
        runs = [run("2026-11-28T13:25:00", conclusion=c) for c in ("cancelled", "skipped", "failure")]
        self.assertEqual(decide("2026-11-28T16:30:00", runs), "give-up")

    def test_a_run_still_going_from_before_due_does_not_block(self):
        # Only runs created since DUE are this edition's.
        self.assertEqual(decide("2026-11-28T13:05:00", [run("2026-11-28T12:58:00", "in_progress", None)]), "dispatch")


class MainTests(unittest.TestCase):
    """main() with gh stubbed out: what gets dispatched, and the exit status."""

    def _main(self, runs, *extra):
        calls = []
        real_runs, real_run, real_sleep = dt.recent_runs, dt.subprocess.run, dt.time_module.sleep
        dt.recent_runs = lambda workflow: runs
        dt.subprocess.run = lambda cmd, **kw: calls.append(cmd)
        dt.time_module.sleep = lambda s: calls.append(["sleep", s])
        try:
            code = dt.main(["--workflow", "demo.yml", "--timezone", TZ, "--due", "05:00", *extra])
        finally:
            dt.recent_runs, dt.subprocess.run, dt.time_module.sleep = real_runs, real_run, real_sleep
        return code, calls

    def test_dispatch_runs_the_workflow_then_holds(self):
        code, calls = self._main([], "--now", "2026-11-28T13:30:00Z")
        self.assertEqual(code, 0)
        self.assertEqual(calls[0], ["gh", "workflow", "run", "demo.yml", "--ref", "main"])
        self.assertEqual(calls[1][0], "sleep")

    def test_dry_run_dispatches_nothing(self):
        code, calls = self._main([], "--now", "2026-11-28T13:30:00Z", "--dry-run")
        self.assertEqual((code, calls), (0, []))

    def test_done_and_wait_dispatch_nothing(self):
        self.assertEqual(self._main([run("2026-11-28T13:25:00")], "--now", "2026-11-28T15:00:00Z"), (0, []))
        self.assertEqual(self._main([], "--now", "2026-11-28T12:00:00Z"), (0, []))

    def test_give_up_exits_1_and_dispatches_nothing(self):
        failed = [run(f"2026-11-28T{h}:25:00", conclusion="failure") for h in (13, 14, 15)]
        self.assertEqual(self._main(failed, "--now", "2026-11-28T16:30:00Z"), (1, []))

    def test_now_without_an_offset_is_utc(self):
        self.assertEqual(self._main([], "--now", "2026-11-28T12:00:00"), (0, []))

    def test_a_gh_failure_is_not_swallowed(self):
        real = dt.recent_runs
        def boom(workflow):
            raise dt.subprocess.CalledProcessError(1, ["gh"])
        dt.recent_runs = boom
        try:
            with self.assertRaises(dt.subprocess.CalledProcessError):
                dt.main(["--workflow", "demo.yml", "--timezone", TZ, "--due", "05:00"])
        finally:
            dt.recent_runs = real


class WorkflowTests(unittest.TestCase):
    def test_tick_uses_the_demo_mastheads_timezone(self):
        import re
        import tomllib
        root = os.path.dirname(HERE)
        with open(os.path.join(root, "demo", "masthead.toml"), "rb") as f:
            masthead_tz = tomllib.load(f)["identity"]["timezone"]
        with open(os.path.join(root, ".github", "workflows", "tick.yml"), encoding="utf-8") as f:
            tick_tz = re.search(r"--timezone (\S+)", f.read()).group(1)
        self.assertEqual(tick_tz, masthead_tz)


if __name__ == "__main__":
    unittest.main()
