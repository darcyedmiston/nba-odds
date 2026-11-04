"""python -m unittest discover tests"""
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from model import best_option, main_lines
from picks import settle_row, stakes
from plan_day import build_plan, decide


def row(book, line, side, odds):
    return {"bookmaker": book, "line": line, "side": side, "odds": odds}


def ev(*hours_from, base=datetime(2026, 11, 4, 19, 0, tzinfo=timezone.utc)):
    return [{"commence_time": (base + timedelta(hours=h)).isoformat()} for h in hours_from], base


class Ladder(unittest.TestCase):
    rows = [row("betright", 29.5, "Over", 1.15), row("betright", 34.5, "Over", 1.46),
            row("betright", 39.5, "Over", 2.15),
            row("sportsbet", 38.5, "Over", 1.9), row("sportsbet", 38.5, "Under", 1.9),
            row("unibet", 37.5, "Over", 1.85), row("unibet", 37.5, "Under", 1.95)]

    def test_over_only_rung_is_not_a_main_line(self):
        self.assertEqual(set(main_lines(self.rows)), {"sportsbet", "unibet"})

    def test_under_survives(self):
        under = best_option(main_lines(self.rows), "Under", "pra")
        self.assertEqual((under["line"], under["book"]), (38.5, "sportsbet"))

    def test_most_balanced_line_is_used(self):
        rows = [row("neds", 20.5, "Over", 1.5), row("neds", 20.5, "Under", 2.5),
                row("neds", 22.5, "Over", 1.9), row("neds", 22.5, "Under", 1.9)]
        self.assertEqual(main_lines(rows)["neds"]["line"], 22.5)


class Plan(unittest.TestCase):
    def test_times_build_back_from_first_tip(self):
        e, now = ev(5.0, 7.0)  # 6am Melb now; tips 11am and 1pm
        p = build_plan(e, now)
        self.assertEqual((p["first_tip_melb"], p["last_tip_melb"]), ("11:00", "13:00"))
        self.assertEqual((p["refresh_melb"], p["pretip_melb"], p["games"]), ("09:30", "10:00", 2))

    def test_normal_day_waits_then_pulls(self):
        e, now = ev(5.0)
        wait, pull, closing, again = decide(build_plan(e, now), now)
        self.assertEqual((round(wait), pull, closing, again), (210, True, True, False))

    def test_early_game_skips_refresh_but_starts_closing(self):
        e, now = ev(1.75)  # tip 15 min after the refresh would be near now
        self.assertEqual(decide(build_plan(e, now), now), (0, False, True, False))

    def test_far_off_slate_restarts_the_wait(self):
        e, now = ev(23.0)
        self.assertEqual(decide(build_plan(e, now), now), (340, False, False, True))

    def test_next_day_games_stay_out_of_the_slate(self):
        e, now = ev(5.0, 29.0)
        self.assertEqual(build_plan(e, now)["games"], 1)

    def test_no_games(self):
        now = datetime(2026, 11, 4, tzinfo=timezone.utc)
        self.assertIsNone(build_plan([], now))
        self.assertEqual(decide(None, now), (0, False, False, False))


class Settle(unittest.TestCase):
    def row(self, **kw):
        base = {"player_key": "a b", "stat": "pts", "side": "Over", "line": "10.5", "odds": "1.90",
                "actual": "", "margin": "", "result": "", "pnl_flat10": ""}
        return {**base, **kw}

    final = {"status": "Final", "minutes": "30", "pts": "12"}

    def test_win(self):
        r = self.row()
        settle_row(r, {"a b": self.final})
        self.assertEqual((r["actual"], r["result"], r["pnl_flat10"], r["margin"]), ("12", "Win", "9.00", "+1.5"))

    def test_under_loses_when_stat_is_over(self):
        r = self.row(side="Under")
        settle_row(r, {"a b": self.final})
        self.assertEqual((r["result"], r["pnl_flat10"]), ("Loss", "-10.00"))

    def test_hand_result_is_kept(self):
        r = self.row(actual="9", result="Win")
        settle_row(r, {"a b": self.final})
        self.assertEqual((r["actual"], r["result"]), ("9", "Win"))

    def test_absent_player_voids_only_when_games_are_final(self):
        r = self.row()
        settle_row(r, {"c d": {"status": "In Progress"}})
        self.assertEqual(r["result"], "")
        settle_row(r, {"c d": self.final})
        self.assertEqual(r["result"], "Void")

    def test_stakes_follow_tier_and_cap(self):
        r = stakes({"date_melb": "2026-11-05", "tier": "Diff 4", "placed": "Paper"})
        self.assertEqual((r["model_stake"], r["rec_stake"]), (15, 10))
        r = stakes({"date_melb": "2026-11-07", "tier": "Diff 4", "placed": "Paper"})
        self.assertEqual(r["rec_stake"], 15)
        r = stakes({"date_melb": "2026-11-07", "tier": "Watchlist", "placed": "No"})
        self.assertEqual((r["rec_stake"], r["actual_stake"]), (0, ""))


if __name__ == "__main__":
    unittest.main()
