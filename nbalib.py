"""Shared helpers for the NBA edge model (ESPN access, names, dates)."""
import json
import re
import time
import unicodedata
import urllib.request
from datetime import date, datetime, timedelta, timezone

ESPN = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba"
UA = {"User-Agent": "nba-odds edge model (github.com/darcyedmiston/nba-odds)"}
MELB = timezone(timedelta(hours=11))  # AEDT; switch to +10 in April

# Odds API market key -> gamelog column
MARKETS = {
    "player_points": "pts",
    "player_rebounds": "reb",
    "player_assists": "ast",
    "player_threes": "threes",
    "player_points_rebounds_assists": "pra",
}


def get_json(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(2 * (i + 1))


def norm_name(name):
    """'Luka Dončić' / 'Jabari Smith Jr.' / "De'Aaron Fox" -> 'luka doncic' / 'jabari smith' / 'deaaron fox'."""
    s = unicodedata.normalize("NFKD", name or "").encode("ascii", "ignore").decode()
    s = s.lower().replace(".", "").replace("'", "").replace("-", " ")
    s = re.sub(r"\b(jr|sr|ii|iii|iv|v)\b", "", s)
    return re.sub(r"\s+", " ", s).strip()


def season_of(d):
    """US game date -> season label, e.g. 2026-01-05 -> '2025-26'."""
    y = d.year if d.month >= 8 else d.year - 1
    return f"{y}-{str(y + 1)[2:]}"


def prev_season(season):
    y = int(season[:4]) - 1
    return f"{y}-{str(y + 1)[2:]}"


def melb_to_us(d_melb):
    """A Melbourne slate date maps to the previous US (ET) date."""
    return d_melb - timedelta(days=1)


def today_melb():
    return datetime.now(MELB).date()


def parse_date(s):
    return date.fromisoformat(s)


def team_key(name):
    """Full team name -> lowercase nickname key ('Los Angeles Lakers' -> 'lakers',
    'Portland Trail Blazers' -> 'trail blazers')."""
    n = norm_name(name)
    for two in ("trail blazers",):
        if n.endswith(two):
            return two
    return n.split(" ")[-1]
