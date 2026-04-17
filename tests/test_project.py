from __future__ import annotations

import json
import shutil
import unittest
from pathlib import Path

from app.file_io import load_customer_groups, load_restaurant_settings, save_simulation_result
from app.models import CustomerGroup, QueueRule, Table
from app.simulator import run_simulation


class ProjectTests(unittest.TestCase):
    def setUp(self) -> None:
        self.test_output_dir = Path("tests") / "_tmp_outputs"
        self.test_output_dir.mkdir(parents=True, exist_ok=True)
        self.queue_rules = [
            QueueRule("Small", 1, 2),
            QueueRule("Medium", 3, 4),
            QueueRule("Large", 5, None),
        ]
        self.tables = [
            Table("T1", 2),
            Table("T2", 4),
            Table("T3", 6, reserved=True),
        ]

    def tearDown(self) -> None:
        if self.test_output_dir.exists():
            shutil.rmtree(self.test_output_dir)

    def test_normal_operation(self) -> None:
        groups = [
            CustomerGroup("G1", 0, 2, 30),
            CustomerGroup("G2", 0, 4, 25),
            CustomerGroup("G3", 5, 1, 20),
        ]
        result = run_simulation("Demo", "Normal", self.queue_rules, self.tables, groups)
        self.assertEqual(result.groups_served, 3)
        self.assertEqual(result.groups_unserved, 0)
        self.assertEqual(result.max_wait_time, 20)

    def test_all_same_group_size(self) -> None:
        groups = [
            CustomerGroup("G1", 0, 2, 10),
            CustomerGroup("G2", 1, 2, 10),
            CustomerGroup("G3", 2, 2, 10),
        ]
        result = run_simulation("Demo", "Same Size", self.queue_rules, self.tables, groups)
        self.assertEqual(result.groups_served, 3)
        self.assertEqual(result.served_by_queue["Small"], 3)

    def test_zero_customers(self) -> None:
        result = run_simulation("Demo", "Empty", self.queue_rules, self.tables, [])
        self.assertEqual(result.total_groups, 0)
        self.assertEqual(result.groups_served, 0)
        self.assertEqual(result.service_level, 0.0)

    def test_group_larger_than_any_table(self) -> None:
        groups = [CustomerGroup("TooBig", 0, 8, 30)]
        with self.assertRaises(ValueError):
            run_simulation("Demo", "Too Big", self.queue_rules, self.tables, groups)

    def test_boundary_capacity_match(self) -> None:
        groups = [
            CustomerGroup("G1", 0, 2, 10),
            CustomerGroup("G2", 0, 4, 10),
        ]
        result = run_simulation("Demo", "Boundary", self.queue_rules, self.tables, groups)
        seated_tables = {record.group_id: record.table_id for record in result.seating_records}
        self.assertEqual(seated_tables["G1"], "T1")
        self.assertEqual(seated_tables["G2"], "T2")

    def test_error_input_file(self) -> None:
        invalid_path = self.test_output_dir / "invalid.json"
        invalid_path.write_text("{ bad json", encoding="utf-8")
        with self.assertRaises(ValueError):
            load_customer_groups(invalid_path)

    def test_load_and_save_json_files(self) -> None:
        settings_path = self.test_output_dir / "settings.json"
        arrivals_path = self.test_output_dir / "arrivals.json"
        results_path = self.test_output_dir / "results.json"

        settings_path.write_text(
            json.dumps(
                {
                    "restaurant_name": "Loaded Demo",
                    "service_threshold": 12,
                    "turnover_duration": 5,
                    "queues": [
                        {"name": "Small", "min_size": 1, "max_size": 2},
                        {"name": "Medium", "min_size": 3, "max_size": 4},
                    ],
                    "tables": [
                        {"table_id": "T1", "capacity": 2, "reserved": False},
                        {"table_id": "T2", "capacity": 4, "reserved": False},
                    ],
                }
            ),
            encoding="utf-8",
        )
        arrivals_path.write_text(
            json.dumps(
                {
                    "scenario_name": "Loaded Scenario",
                    "groups": [
                        {"group_id": "G1", "arrival_time": 0, "group_size": 2, "dining_duration": 20},
                        {"group_id": "G2", "arrival_time": 5, "group_size": 4, "dining_duration": 20},
                    ],
                }
            ),
            encoding="utf-8",
        )

        restaurant_name, service_threshold, turnover_duration, queue_rules, tables = load_restaurant_settings(
            settings_path
        )
        scenario_name, groups = load_customer_groups(arrivals_path)
        result = run_simulation(
            restaurant_name,
            scenario_name,
            queue_rules,
            tables,
            groups,
            service_threshold=service_threshold,
            turnover_duration=turnover_duration,
        )
        save_simulation_result(results_path, result)

        payload = json.loads(results_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["restaurant_name"], "Loaded Demo")
        self.assertEqual(payload["scenario_name"], "Loaded Scenario")
        self.assertEqual(payload["groups_served"], 2)

    def test_case_study_files_load_and_run(self) -> None:
        valid_pairs = [
            ("case_studies/settings_single_queue.json", "case_studies/arrivals_peak_hour.json"),
            ("case_studies/settings_size_based.json", "case_studies/arrivals_peak_hour.json"),
            ("case_studies/settings_coarse_queue.json", "case_studies/arrivals_peak_hour.json"),
            ("case_studies/settings_size_based.json", "case_studies/arrivals_low_traffic.json"),
            ("case_studies/settings_many_small_tables.json", "case_studies/arrivals_uniform_small.json"),
            ("case_studies/settings_few_large_tables.json", "case_studies/arrivals_uniform_large.json"),
        ]

        for settings_path, arrivals_path in valid_pairs:
            restaurant_name, service_threshold, turnover_duration, queue_rules, tables = load_restaurant_settings(
                settings_path
            )
            self.assertTrue(restaurant_name)
            self.assertGreater(len(queue_rules), 0)
            self.assertGreater(len(tables), 0)
            scenario_name, groups = load_customer_groups(arrivals_path)
            result = run_simulation(
                restaurant_name,
                scenario_name,
                queue_rules,
                tables,
                groups,
                service_threshold=service_threshold,
                turnover_duration=turnover_duration,
            )
            self.assertEqual(result.total_groups, 20)
            self.assertGreaterEqual(result.groups_served, 0)
            self.assertGreaterEqual(len(result.seating_records), 0)


if __name__ == "__main__":
    unittest.main()
