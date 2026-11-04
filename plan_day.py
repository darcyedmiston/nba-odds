"""Work out the day's timetable from the first tip-off (free Odds API call).

    python plan_day.py          # write odds/schedule.json for the scans to read
    python plan_day.py --wait   # used by refresh.yml: sleep until the refresh time

Tip-offs on a Melbourne morning range from about 7:30am to noon, so fixed clock
times are either late or stale. The timetable is built backwards from the first game:
    first tip - 90 min   full-slate odds refresh and re-score
    first tip - 60 min   pre-tip review (the scheduled scan moves itself here)
    each tip -  5 min    closing lines (closing.yml)
"""
import argparse
import json
import os
import time
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

API = "https://api.the-odds-api.com/v4/sports/basketball_nba"
MELB = ZoneInfo("Australia/Melbourne")
REFRESH_LEAD_MIN = 90
PRETIP_LEAD_MIN = 60
MIN_GAP_MIN = 45     # skip the refresh if the morning pull is about this fresh anyway
MAX_WAIT_MIN = 340   # GitHub jobs stop at 6 hours; longer waits restart the job


def parse_tip(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def build_plan(events, now):
    """Timetable for the next Melbourne slate with an untipped game, or None."""
    tips = sorted(t for t in (parse_tip(e["commence_time"]) for e in events)
                  if now < t <= now + timedelta(hours=36))
    if not tips:
        return None
    day = tips[0].astimezone(MELB).date()
    slate = [t for t in tips if t.astimezone(MELB).date() == day]
    first, last = slate[0], slate[-1]
    refresh = first - timedelta(minutes=REFRESH_LEAD_MIN)
    pretip = first - timedelta(minutes=PRETIP_LEAD_MIN)
    return {
        "date_melb": day.isoformat(), "games": len(slate),
        "first_tip_melb": first.astimezone(MELB).strftime("%H:%M"),
        "last_tip_melb": last.astimezone(MELB).strftime("%H:%M"),
        "refresh_melb": refresh.astimezone(MELB).strftime("%H:%M"),
        "pretip_melb": pretip.astimezone(MELB).strftime("%H:%M"),
        "first_tip_utc": first.isoformat(), "refresh_utc": refresh.isoformat(),
        "closing_auto": True,
    }


def decide(plan, now):
    """What refresh.yml should do: (wait_minutes, pull, closing, again)."""
    if plan is None:
        return 0, False, False, False
    wait = (datetime.fromisoformat(plan["refresh_utc"]) - now).total_seconds() / 60
    if wait > MAX_WAIT_MIN:          # too far off for one job: wait, then restart
        return MAX_WAIT_MIN, False, False, True
    if wait < MIN_GAP_MIN:           # early game: the morning pull is already fresh
        return 0, False, True, False
    return wait, True, True, False


def get_events():
    url = f"{API}/events?apiKey={os.environ['ODDS_API_KEY']}"
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.load(r)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wait", action="store_true")
    args = ap.parse_args()
    now = datetime.now(timezone.utc)
    plan = build_plan(get_events(), now)
    if not args.wait:
        out = Path("odds/schedule.json")
        out.write_text(json.dumps(plan or {"games": 0, "closing_auto": False}, indent=1) + "\n")
        print(plan or "no games")
        return
    wait, pull, closing, again = decide(plan, now)
    print(f"plan: {plan}\nwait {wait:.0f} min, pull={pull}, closing={closing}, again={again}", flush=True)
    time.sleep(max(wait, 0) * 60)
    with open(os.environ["GITHUB_OUTPUT"], "a") as f:
        f.write(f"pull={str(pull).lower()}\nclosing={str(closing).lower()}\nagain={str(again).lower()}\n")


if __name__ == "__main__":
    main()
