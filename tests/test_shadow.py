"""python -m unittest discover tests"""
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from fetch_reference import credit_floor, select_games
from shadow import capped, devig, ref_probs, rules


def prop(over_won=0, au=0.5, over=1.9, under=2.0, model_under="", ref=""):
    return {"date_melb": "2026-11-05", "game": "A @ B", "player": "x", "over_won": over_won, "au_prob": au,
            "over_odds": over, "under_odds": under, "model_under": model_under, "ref_prob": ref}


class Rules(unittest.TestCase):
    def named(self, *a, **k):
        return dict(rules([prop(*a, **k)]))

    def test_devig(self):
        self.assertAlmostEqual(devig(2.0, 2.0), .5)

    def test_r1_threshold_uses_frozen_bias(self):
        # (0.5 + 0.0305) * 1.93 - 1 = 2.39%, in; at 1.92 it's 1.86%, out
        self.assertEqual(len(self.named(under=1.93)["R1 Under above bias-adjusted AU consensus"]), 1)
        self.assertEqual(len(self.named(under=1.92)["R1 Under above bias-adjusted AU consensus"]), 0)

    def test_r2_needs_model_agreement(self):
        self.assertEqual(len(self.named(model_under=.6)["R2 R1 and the model agrees"]), 1)
        self.assertEqual(len(self.named(model_under=.4)["R2 R1 and the model agrees"]), 0)
        self.assertEqual(len(self.named()["R2 R1 and the model agrees"]), 0)

    def test_s1_prices_each_side_from_reference(self):
        s1 = self.named(ref=.6, over=1.9, under=2.0)["S1 best AU price above reference price by 2%+"]
        self.assertEqual([round(b["ev"], 2) for b in s1], [.14])
        self.assertEqual(s1[0]["pnl"], -1.0)  # Over bet, Over lost

    def test_cap(self):
        mk = lambda game, player, ev: {"game": game, "player": player, "ev": ev}
        out = capped([mk("g", "a", .3), mk("g", "a", .2), mk("g", "b", .1), mk("g", "c", .05), mk("h", "a", .01)])
        self.assertEqual([(b["game"], b["player"]) for b in out], [("g", "a"), ("g", "b"), ("h", "a")])

    def test_only_exact_two_sided_lines_count(self):
        rows = [{"bookmaker": "novig", "line": "20.5", "side": s, "odds": "1.9"} for s in ("Over", "Under")]
        rows.append({"bookmaker": "fanduel", "line": "20.5", "side": "Over", "odds": "1.9"})
        rows += [{"bookmaker": "draftkings", "line": "21.5", "side": s, "odds": "1.9"} for s in ("Over", "Under")]
        self.assertEqual(set(ref_probs(rows, 20.5)), {"novig"})


class Reference(unittest.TestCase):
    now = datetime(2026, 11, 4, 19, 0, tzinfo=timezone.utc)  # 6am Melbourne

    def ev(self, hours):
        return {"commence_time": (self.now + timedelta(hours=hours)).isoformat()}

    def test_window_and_saved_slate(self):
        e = [self.ev(5), self.ev(20)]
        self.assertEqual(select_games(e, self.now, 12, set()), e[:1])
        self.assertEqual(select_games(e, self.now, 12, {"2026-11-05"}), [])

    def test_credit_floor_counts_days_to_the_first(self):
        self.assertEqual(credit_floor(self.now), 150 * 27)
        self.assertEqual(credit_floor(datetime(2026, 12, 31, tzinfo=timezone.utc)), 150)


if __name__ == "__main__":
    unittest.main()
