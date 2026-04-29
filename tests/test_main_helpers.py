from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.models import SeatingRecord, SimulationResult
from main import (
    _build_comparison_pairs,
    _discover_input_files,
    _format_comparison_table,
    _format_queue_ranges,
    _group_banner,
    _resolve_result_save_path,
    _visible_choice_paths,
)


class MainHelperTests(unittest.TestCase):
    def test_discover_input_files_classifies_settings_and_arrivals_only(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "settings.json").write_text(
                json.dumps(
                    {
                        "restaurant_name": "Demo",
                        "queues": [{"name": "Small", "min_size": 1, "max_size": 2}],
                        "tables": [{"table_id": "T1", "capacity": 2, "reserved": False}],
                    }
                ),
                encoding="utf-8",
            )
            (root / "arrivals.json").write_text(
                json.dumps(
                    {
                        "scenario_name": "Lunch",
                        "groups": [
                            {"group_id": "G1", "arrival_time": 0, "group_size": 2, "dining_duration": 20}
                        ],
                    }
                ),
                encoding="utf-8",
            )
            (root / "result.json").write_text(
                json.dumps({"restaurant_name": "Demo", "groups_served": 1}),
                encoding="utf-8",
            )

            with patch("main._repo_root", return_value=root):
                settings_paths, arrival_paths = _discover_input_files()

        self.assertEqual([path.name for path in settings_paths], ["settings.json"])
        self.assertEqual([path.name for path in arrival_paths], ["arrivals.json"])

    def test_format_queue_ranges_handles_open_ended_rule(self) -> None:
        from app.models import QueueRule

        queue_ranges = _format_queue_ranges([QueueRule("Small", 1, 2), QueueRule("Large", 5, None)])

        self.assertEqual(queue_ranges, "Small:1-2, Large:5+")

    def test_visible_choice_paths_hides_sample_data_entries(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            case_path = root / "case_studies" / "settings_case.json"
            sample_path = root / "sample_data" / "restaurant_settings.json"
            case_path.parent.mkdir(parents=True, exist_ok=True)
            sample_path.parent.mkdir(parents=True, exist_ok=True)
            case_path.write_text("{}", encoding="utf-8")
            sample_path.write_text("{}", encoding="utf-8")

            with patch("main._repo_root", return_value=root):
                visible_paths = _visible_choice_paths([case_path, sample_path])

        self.assertEqual(visible_paths, [case_path])

    def test_group_banner_contains_group_15(self) -> None:
        banner = _group_banner()

        self.assertIn("____ ____", banner)
        self.assertIn("| |___ \\", banner)
        self.assertIn("| |___) |", banner)

    def test_resolve_result_save_path_uses_results_folder_for_bare_name(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            with patch("main._repo_root", return_value=root):
                resolved_path = _resolve_result_save_path("demo_run")

        self.assertEqual(resolved_path, root / "results" / "demo_run.json")

    def test_resolve_result_save_path_keeps_relative_path(self) -> None:
        resolved_path = _resolve_result_save_path(r"exports\demo.json")

        self.assertEqual(resolved_path, Path(r"exports\demo.json"))

    def test_build_comparison_pairs_supports_setting_and_arrival_variations(self) -> None:
        settings_paths = [
            Path("case_studies/pair01a_settings_single_queue.json"),
            Path("case_studies/pair01b_settings_size_based.json"),
            Path("case_studies/pair07_settings_fixed_capacity.json"),
        ]
        arrival_paths = [
            Path("case_studies/pair01_arrivals_mixed_peak.json"),
            Path("case_studies/pair07a_arrivals_burst_peak.json"),
            Path("case_studies/pair07b_arrivals_trickle_flow.json"),
        ]

        comparison_pairs = _build_comparison_pairs(settings_paths, arrival_paths)

        self.assertEqual(comparison_pairs["pair01"]["mode"], "settings")
        self.assertEqual(len(comparison_pairs["pair01"]["settings"]), 2)
        self.assertEqual(len(comparison_pairs["pair01"]["arrivals"]), 1)
        self.assertEqual(comparison_pairs["pair07"]["mode"], "arrivals")
        self.assertEqual(len(comparison_pairs["pair07"]["settings"]), 1)
        self.assertEqual(len(comparison_pairs["pair07"]["arrivals"]), 2)

    def test_format_comparison_table_includes_metric_rows(self) -> None:
        result = SimulationResult(
            restaurant_name="Demo Restaurant",
            scenario_name="Lunch",
            total_groups=5,
            groups_served=4,
            groups_unserved=1,
            average_wait_time=11.5,
            max_wait_time=46,
            table_utilization=54.35,
            seat_utilization=49.59,
            service_level=75.0,
            spend_per_customer=50.0,
            revenue_per_minute=4.25,
            average_table_size_gap=0.5,
            reserved_tables=1,
            walk_in_tables=3,
            service_threshold=15,
            turnover_duration=5,
            max_queue_lengths={"Small": 1},
            served_by_queue={"Small": 4},
            average_wait_by_queue={"Small": 11.5},
            seating_records=[
                SeatingRecord(
                    time=0,
                    departure_time=35,
                    table_id="T1",
                    group_id="G1",
                    queue_name="Small",
                    wait_time=0,
                    dining_duration=30,
                    wasted_seats=0,
                )
            ],
            unserved_group_ids=["G5"],
        )
        better_result = SimulationResult(
            restaurant_name="Better Restaurant",
            scenario_name="Lunch",
            total_groups=5,
            groups_served=5,
            groups_unserved=0,
            average_wait_time=8.5,
            max_wait_time=20,
            table_utilization=60.0,
            seat_utilization=55.0,
            service_level=90.0,
            spend_per_customer=50.0,
            revenue_per_minute=5.75,
            average_table_size_gap=0.2,
            reserved_tables=0,
            walk_in_tables=3,
            service_threshold=15,
            turnover_duration=5,
            max_queue_lengths={"Small": 1},
            served_by_queue={"Small": 5},
            average_wait_by_queue={"Small": 8.5},
            seating_records=[
                SeatingRecord(
                    time=0,
                    departure_time=25,
                    table_id="T1",
                    group_id="G1",
                    queue_name="Small",
                    wait_time=0,
                    dining_duration=20,
                    wasted_seats=0,
                )
            ],
            unserved_group_ids=[],
        )

        table = _format_comparison_table([("settings_a", result), ("settings_b", better_result)])

        self.assertIn("Metric", table)
        self.assertIn("Avg wait (min)", table)
        self.assertIn("settings_a", table)
        self.assertIn("54.35", table)
        self.assertIn("Groups unserved", table)
        self.assertIn("8.50 *", table)
        self.assertIn("5/5 *", table)
        self.assertIn("Revenue / min", table)

    def test_format_comparison_table_hides_unserved_row_when_all_zero(self) -> None:
        result = SimulationResult(
            restaurant_name="Demo Restaurant",
            scenario_name="Lunch",
            total_groups=5,
            groups_served=5,
            groups_unserved=0,
            average_wait_time=11.5,
            max_wait_time=46,
            table_utilization=54.35,
            seat_utilization=49.59,
            service_level=75.0,
            spend_per_customer=50.0,
            revenue_per_minute=4.25,
            average_table_size_gap=0.5,
            reserved_tables=1,
            walk_in_tables=3,
            service_threshold=15,
            turnover_duration=5,
            max_queue_lengths={"Small": 1},
            served_by_queue={"Small": 5},
            average_wait_by_queue={"Small": 11.5},
            seating_records=[],
            unserved_group_ids=[],
        )

        table = _format_comparison_table([("settings_a", result), ("settings_b", result)])

        self.assertNotIn("Groups unserved", table)

    def test_format_comparison_table_keeps_nonzero_unserved_values_visible(self) -> None:
        result = SimulationResult(
            restaurant_name="Small Tables",
            scenario_name="Lunch",
            total_groups=5,
            groups_served=2,
            groups_unserved=3,
            average_wait_time=11.5,
            max_wait_time=46,
            table_utilization=54.35,
            seat_utilization=49.59,
            service_level=75.0,
            spend_per_customer=50.0,
            revenue_per_minute=2.15,
            average_table_size_gap=0.5,
            reserved_tables=1,
            walk_in_tables=3,
            service_threshold=15,
            turnover_duration=5,
            max_queue_lengths={"Small": 1},
            served_by_queue={"Small": 2},
            average_wait_by_queue={"Small": 11.5},
            seating_records=[],
            unserved_group_ids=["G3", "G4", "G5"],
        )
        better_result = SimulationResult(
            restaurant_name="Better Restaurant",
            scenario_name="Lunch",
            total_groups=5,
            groups_served=5,
            groups_unserved=0,
            average_wait_time=8.5,
            max_wait_time=20,
            table_utilization=60.0,
            seat_utilization=55.0,
            service_level=90.0,
            spend_per_customer=50.0,
            revenue_per_minute=5.75,
            average_table_size_gap=0.2,
            reserved_tables=0,
            walk_in_tables=3,
            service_threshold=15,
            turnover_duration=5,
            max_queue_lengths={"Small": 1},
            served_by_queue={"Small": 5},
            average_wait_by_queue={"Small": 8.5},
            seating_records=[],
            unserved_group_ids=[],
        )

        table = _format_comparison_table([("small_tables", result), ("better", better_result)])

        self.assertIn("Groups unserved", table)
        self.assertIn("3", table)


if __name__ == "__main__":
    unittest.main()
