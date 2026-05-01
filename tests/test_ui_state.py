from __future__ import annotations

import unittest

from app.models import CustomerGroup, QueueRule, Table
from app.ui_state import InteractiveQueueState


class InteractiveQueueStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.queue_rules = [
            QueueRule("Small", 1, 2),
            QueueRule("Medium", 3, 4),
        ]
        self.tables = [
            Table("T1", 2),
            Table("T2", 4),
            Table("T3", 4, reserved=True),
        ]
        self.state = InteractiveQueueState(self.queue_rules, self.tables, turnover_duration=5)

    def test_snapshot_counts_waiting_groups_and_people(self) -> None:
        self.state.add_group(2, 20)
        self.state.add_group(3, 25)

        snapshot = self.state.snapshot()

        self.assertEqual(snapshot.waiting_groups, 2)
        self.assertEqual(snapshot.waiting_people, 5)
        self.assertEqual(snapshot.queue_lengths["Small"], 1)
        self.assertEqual(snapshot.queue_lengths["Medium"], 1)

    def test_remove_front_batch_is_atomic_when_queue_is_too_short(self) -> None:
        self.state.add_group(2, 20)

        with self.assertRaises(ValueError):
            self.state.remove_front_batch("Small", 2)

        self.assertEqual(len(self.state.waiting["Small"]), 1)
        self.assertEqual(self.state.waiting["Small"][0].group_id, "U001")

    def test_preview_pending_arrivals_returns_only_future_groups(self) -> None:
        groups = [
            CustomerGroup("G1", 0, 2, 20),
            CustomerGroup("G2", 5, 2, 20),
            CustomerGroup("G3", 10, 4, 25),
            CustomerGroup("G4", 15, 2, 15),
        ]

        self.state.load_scenario(groups, scenario_name="Preview")

        preview = self.state.preview_pending_arrivals(limit=2)

        self.assertEqual([group.group_id for group in preview], ["G2", "G3"])
        self.assertEqual(len(self.state.waiting["Small"]), 1)
        self.assertEqual(self.state.waiting["Small"][0].group_id, "G1")

    def test_has_active_session_tracks_waiting_busy_and_finished_states(self) -> None:
        self.assertFalse(self.state.has_active_session())

        self.state.add_group(2, 10)
        self.assertTrue(self.state.has_active_session())

        self.state.seat_waiting_groups()
        self.assertTrue(self.state.has_active_session())

        self.state.advance_time(15)
        self.assertFalse(self.state.has_active_session())


if __name__ == "__main__":
    unittest.main()
