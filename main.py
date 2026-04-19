from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Callable

from app.file_io import load_customer_groups, load_restaurant_settings, save_simulation_result
from app.models import CustomerGroup, QueueRule, SimulationResult, Table
from app.simulator import format_result, run_simulation

BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
DIM = "\033[90m"
RESET = "\033[0m"


def _prompt_path(prompt: str) -> str:
    return input(prompt).strip().strip('"')


def _repo_root() -> Path:
    return Path(__file__).resolve().parent


def _relative_display_path(path: Path) -> str:
    try:
        return str(path.relative_to(_repo_root()))
    except ValueError:
        return str(path)


def _safe_read_json(path: Path) -> dict | None:
    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _supports_color() -> bool:
    return sys.stdout.isatty()


def _blue(text: str) -> str:
    return f"{BLUE}{text}{RESET}" if _supports_color() else text


def _dim(text: str) -> str:
    return f"{DIM}{text}{RESET}" if _supports_color() else text


def _red(text: str) -> str:
    return f"{RED}{text}{RESET}" if _supports_color() else text


def _yellow(text: str) -> str:
    return f"{YELLOW}{text}{RESET}" if _supports_color() else text


def _green(text: str) -> str:
    return f"{GREEN}{text}{RESET}" if _supports_color() else text


def _group_banner() -> str:
    banner = "\n".join(
        [
            "  ____ ____   ___  _   _ ____    _ ____  ",
            " / ___|  _ \\ / _ \\| | | |  _ \\  / | ___| ",
            "| |  _| |_) | | | | | | | |_) | | |___ \\ ",
            "| |_| |  _ <| |_| | |_| |  __/  | |___) |",
            " \\____|_| \\_\\\\___/ \\___/|_|     |_|____/ ",
        ]
    )
    if not _supports_color():
        return banner

    styled_lines = [
        _blue("  ____ ____   ___  _   _ ____    _ ____  "),
        _blue(" / ___|  _ \\ / _ \\| | | |  _ \\  / | ___| "),
        _blue("| |  _| |_) | | | | | | | |_) | | |___ \\ "),
        _blue("| |_| |  _ <| |_| | |_| |  __/  | |___) |"),
        _blue(" \\____|_| \\_\\\\___/ \\___/|_|     |_|____/ "),
    ]
    return "\n".join(styled_lines)


def _discover_input_files() -> tuple[list[Path], list[Path]]:
    settings_paths: list[Path] = []
    arrivals_paths: list[Path] = []

    for path in sorted(_repo_root().rglob("*.json"), key=lambda item: str(item.relative_to(_repo_root()))):
        data = _safe_read_json(path)
        if data is None:
            continue
        if isinstance(data.get("queues"), list) and isinstance(data.get("tables"), list):
            settings_paths.append(path)
        elif "groups" in data and isinstance(data.get("groups"), list):
            arrivals_paths.append(path)

    return settings_paths, arrivals_paths


def _visible_choice_paths(paths: list[Path]) -> list[Path]:
    visible_paths: list[Path] = []
    for path in paths:
        try:
            relative_path = path.relative_to(_repo_root())
        except ValueError:
            visible_paths.append(path)
            continue
        if relative_path.parts and relative_path.parts[0] == "sample_data":
            continue
        visible_paths.append(path)
    return visible_paths


def _resolve_result_save_path(raw_input: str) -> Path:
    candidate = Path(raw_input.strip().strip('"'))
    if not str(candidate):
        raise ValueError("Please enter a result file name or path.")

    if candidate.is_absolute():
        return candidate

    if len(candidate.parts) == 1:
        file_name = candidate.name
        if not Path(file_name).suffix:
            file_name = f"{file_name}.json"
        return _repo_root() / "results" / file_name

    return candidate


def _friendly_name(path: str | Path, prefix: str) -> str:
    stem = Path(path).stem
    if stem.startswith(prefix):
        stem = stem[len(prefix) :]
    return stem.replace("_", " ").strip() or Path(path).stem.replace("_", " ")


def _setting_name(path: str | Path) -> str:
    return _friendly_name(path, "settings_")


def _arrival_name(path: str | Path) -> str:
    return _friendly_name(path, "arrivals_")


def _setting_counts(queue_rules: list[QueueRule], tables: list[Table]) -> tuple[int, int, int]:
    return len(queue_rules), len(tables), sum(1 for table in tables if table.reserved)


def _format_queue_ranges(queue_rules: list[QueueRule]) -> str:
    return ", ".join(
        (
            f"{rule.name}:{rule.min_size}-{rule.max_size}"
            if rule.max_size is not None
            else f"{rule.name}:{rule.min_size}+"
        )
        for rule in queue_rules
    )


def _format_table_summary(tables: list[Table]) -> str:
    return ", ".join(
        f"{table.table_id}({table.capacity}{', reserved' if table.reserved else ''})" for table in tables
    )


def _describe_setting_option(path: Path) -> str:
    return _setting_name(path)


def _describe_arrival_option(path: Path) -> str:
    return _arrival_name(path)


def _print_discovered_options(title: str, paths: list[Path], describe_path: Callable[[Path], str]) -> None:
    print(_blue(title))
    if not paths:
        print("  No discovered files found.")
    else:
        for index, path in enumerate(paths, start=1):
            name = describe_path(path)
            print(f"  {index}. {_blue(name)}")
            print(f"     {_blue('-' * len(name))}")
    print(_dim("  Type a number to choose a listed file, or enter a custom path."))


def _prompt_discovered_path(
    title: str, paths: list[Path], describe_path: Callable[[Path], str], manual_prompt: str
) -> str:
    _print_discovered_options(title, paths, describe_path)
    while True:
        choice = _prompt_path(manual_prompt)
        if not choice:
            print("Please enter a number or a file path.")
            continue
        if choice.isdigit():
            index = int(choice)
            if 1 <= index <= len(paths):
                return str(paths[index - 1])
            print(f"Invalid selection. Choose a number from 1 to {len(paths)}.")
            continue
        return choice


def _prompt_multiple_paths(paths: list[Path]) -> list[str]:
    _print_discovered_options("Available restaurant settings:", paths, _describe_setting_option)
    while True:
        raw_value = _prompt_path(
            "Choose setting numbers separated by commas, or enter custom paths separated by commas: "
        )
        entries = [entry.strip().strip('"') for entry in raw_value.split(",") if entry.strip()]
        if not entries:
            print("Please choose at least two settings.")
            continue

        resolved_paths: list[str] = []
        invalid_selection = False
        for entry in entries:
            if entry.isdigit():
                index = int(entry)
                if not 1 <= index <= len(paths):
                    print(f"Invalid selection '{entry}'.")
                    invalid_selection = True
                    break
                resolved_paths.append(str(paths[index - 1]))
            else:
                resolved_paths.append(entry)

        if invalid_selection:
            continue

        unique_paths = list(dict.fromkeys(resolved_paths))
        if len(unique_paths) < 2:
            print("Please choose at least two different settings for comparison.")
            continue
        return unique_paths


def _print_status_block(
    current_setting_path: str | None,
    current_arrivals_path: str | None,
    queue_rules: list[QueueRule],
    tables: list[Table],
    groups: list[CustomerGroup],
) -> None:
    print("\nRestaurant Queue Simulation")
    print(_blue("---------------------------"))
    if current_setting_path is None:
        print("Current setting not set")
        print("Queues: -")
        print("Tables: -")
        print("Reserved: -")
    else:
        queues_count, tables_count, reserved_count = _setting_counts(queue_rules, tables)
        print(f"Current setting: {_blue(_setting_name(current_setting_path))}")
        print(f"Queues: {queues_count}")
        print(f"Tables: {tables_count}")
        print(f"Reserved: {reserved_count}")

    if current_arrivals_path is None:
        print("Current arrivals not set")
    else:
        print(f"Current arrivals: {_blue(_arrival_name(current_arrivals_path))} | groups: {len(groups)}")


def _format_comparison_table(results_by_setting: list[tuple[str, SimulationResult]]) -> str:
    headers = ["Metric"] + [label for label, _ in results_by_setting]
    row_specs: list[tuple[str, list[str], list[float] | None, str | None]] = [
        ("Restaurant", [result.restaurant_name for _, result in results_by_setting], None, None),
        (
            "Groups served",
            [f"{result.groups_served}/{result.total_groups}" for _, result in results_by_setting],
            [result.groups_served for _, result in results_by_setting],
            "max",
        ),
        (
            "Avg wait (min)",
            [f"{result.average_wait_time:.2f}" for _, result in results_by_setting],
            [result.average_wait_time for _, result in results_by_setting],
            "min",
        ),
        (
            "Max wait (min)",
            [str(result.max_wait_time) for _, result in results_by_setting],
            [result.max_wait_time for _, result in results_by_setting],
            "min",
        ),
        (
            "Service level (%)",
            [f"{result.service_level:.2f}" for _, result in results_by_setting],
            [result.service_level for _, result in results_by_setting],
            "max",
        ),
        (
            "Table util (%)",
            [f"{result.table_utilization:.2f}" for _, result in results_by_setting],
            [result.table_utilization for _, result in results_by_setting],
            "max",
        ),
        (
            "Seat util (%)",
            [f"{result.seat_utilization:.2f}" for _, result in results_by_setting],
            [result.seat_utilization for _, result in results_by_setting],
            "max",
        ),
        (
            "Revenue / min",
            [f"{result.revenue_per_minute:.2f}" for _, result in results_by_setting],
            [result.revenue_per_minute for _, result in results_by_setting],
            "max",
        ),
        (
            "Avg wasted seats",
            [f"{result.average_table_size_gap:.2f}" for _, result in results_by_setting],
            [result.average_table_size_gap for _, result in results_by_setting],
            "min",
        ),
        ("Walk-in tables", [str(result.walk_in_tables) for _, result in results_by_setting], None, None),
        ("Reserved tables", [str(result.reserved_tables) for _, result in results_by_setting], None, None),
    ]
    if any(result.groups_unserved > 0 for _, result in results_by_setting):
        row_specs.insert(
            2,
            (
                "Groups unserved",
                [str(result.groups_unserved) for _, result in results_by_setting],
                [result.groups_unserved for _, result in results_by_setting],
                None,
            ),
        )
    rows: list[list[tuple[str, str]]] = []
    for label, display_values, raw_values, ranking in row_specs:
        highlighted_cells: list[tuple[str, str]] = [(label, "plain")]
        best_value: float | None = None
        if raw_values is not None and ranking is not None:
            best_value = max(raw_values) if ranking == "max" else min(raw_values)
        for display_value, raw_value in zip(
            display_values,
            raw_values if raw_values is not None else [None] * len(display_values),
        ):
            if label == "Groups unserved" and raw_value is not None and raw_value > 0:
                highlighted_cells.append((display_value, "danger"))
                continue
            is_best = best_value is not None and raw_value == best_value
            cell_text = f"{display_value} *" if is_best else display_value
            if not is_best:
                highlighted_cells.append((cell_text, "plain"))
                continue
            best_count = 0 if raw_values is None or best_value is None else sum(1 for value in raw_values if value == best_value)
            highlighted_cells.append((cell_text, "best-unique" if best_count == 1 else "best-tie"))
        rows.append(highlighted_cells)

    header_cells: list[tuple[str, str]] = [(header, "plain") for header in headers]
    table_rows = [header_cells] + rows
    column_widths = [
        max(len(row[column_index][0]) for row in table_rows) for column_index in range(len(headers))
    ]

    def format_row(row: list[tuple[str, str]]) -> str:
        rendered_cells: list[str] = []
        for column_index, (cell_text, style) in enumerate(row):
            padded_text = cell_text.ljust(column_widths[column_index])
            if style == "danger":
                rendered_cells.append(_red(padded_text))
            elif style == "best-unique":
                rendered_cells.append(_green(padded_text))
            elif style == "best-tie":
                rendered_cells.append(_yellow(padded_text))
            else:
                rendered_cells.append(padded_text)
        return " | ".join(rendered_cells)

    separator = "-+-".join("-" * width for width in column_widths)
    return "\n".join([format_row(header_cells), separator] + [format_row(row) for row in rows])


def main() -> None:
    current_setting_path: str | None = None
    current_arrivals_path: str | None = None
    restaurant_name = ""
    scenario_name = ""
    service_threshold = 15
    turnover_duration = 0
    queue_rules: list[QueueRule] = []
    tables: list[Table] = []
    groups: list[CustomerGroup] = []
    result: SimulationResult | None = None

    print(_group_banner())
    while True:
        _print_status_block(current_setting_path, current_arrivals_path, queue_rules, tables, groups)
        print("1. Load restaurant settings")
        print("2. Load customer arrivals")
        print("3. Run simulation")
        print("4. View results")
        print("5. Save results")
        print("6. Compare settings")
        print("7. Exit")

        choice = input("Choose an option (1-7): ").strip()
        try:
            if choice == "1":
                settings_paths, _ = _discover_input_files()
                settings_paths = _visible_choice_paths(settings_paths)
                path = _prompt_discovered_path(
                    "Available restaurant settings:",
                    settings_paths,
                    _describe_setting_option,
                    "Choose a setting number or enter a custom path: ",
                )
                restaurant_name, service_threshold, turnover_duration, queue_rules, tables = load_restaurant_settings(path)
                current_setting_path = path
                result = None
                print(f"Loaded setting: {_blue(_setting_name(path))}")
            elif choice == "2":
                _, arrival_paths = _discover_input_files()
                arrival_paths = _visible_choice_paths(arrival_paths)
                path = _prompt_discovered_path(
                    "Available customer arrival scenarios:",
                    arrival_paths,
                    _describe_arrival_option,
                    "Choose an arrival number or enter a custom path: ",
                )
                scenario_name, groups = load_customer_groups(path)
                current_arrivals_path = path
                result = None
                print(f"Loaded arrivals: {_blue(_arrival_name(path))}")
            elif choice == "3":
                if not queue_rules or not tables:
                    print("Please load restaurant settings first.")
                    continue
                if not scenario_name:
                    print("Please load customer arrivals first.")
                    continue
                result = run_simulation(
                    restaurant_name=restaurant_name,
                    scenario_name=scenario_name,
                    queue_rules=queue_rules,
                    tables=tables,
                    groups=groups,
                    service_threshold=service_threshold,
                    turnover_duration=turnover_duration,
                )
                print("Simulation completed.")
            elif choice == "4":
                if result is None:
                    print("No result available. Run the simulation first.")
                    continue
                print()
                print(format_result(result))
            elif choice == "5":
                if result is None:
                    print("No result available. Run the simulation first.")
                    continue
                raw_path = _prompt_path(
                    "Result file name or path (name only saves to results\\<name>.json): "
                )
                save_path = _resolve_result_save_path(raw_path)
                saved_path = save_simulation_result(save_path, result)
                print(f"Results saved to {saved_path}.")
            elif choice == "6":
                settings_paths, arrival_paths = _discover_input_files()
                settings_paths = _visible_choice_paths(settings_paths)
                arrival_paths = _visible_choice_paths(arrival_paths)
                comparison_arrival_path = _prompt_discovered_path(
                    "Available customer arrival scenarios:",
                    arrival_paths,
                    _describe_arrival_option,
                    "Choose an arrival number or enter a custom path for comparison: ",
                )
                comparison_scenario_name, comparison_groups = load_customer_groups(comparison_arrival_path)
                comparison_paths = _prompt_multiple_paths(settings_paths)
                comparison_results: list[tuple[str, SimulationResult]] = []
                comparison_failures: list[tuple[str, str]] = []
                for comparison_path in comparison_paths:
                    setting_label = _setting_name(comparison_path)
                    try:
                        (
                            comparison_restaurant_name,
                            comparison_service_threshold,
                            comparison_turnover_duration,
                            comparison_queue_rules,
                            comparison_tables,
                        ) = load_restaurant_settings(comparison_path)
                        comparison_result = run_simulation(
                            restaurant_name=comparison_restaurant_name,
                            scenario_name=comparison_scenario_name,
                            queue_rules=comparison_queue_rules,
                            tables=comparison_tables,
                            groups=comparison_groups,
                            service_threshold=comparison_service_threshold,
                            turnover_duration=comparison_turnover_duration,
                            allow_unserviceable_groups=True,
                        )
                    except (FileNotFoundError, ValueError, KeyError, TypeError) as error:
                        comparison_failures.append((setting_label, str(error)))
                        continue
                    comparison_results.append((setting_label, comparison_result))

                print()
                print(f"Comparison for scenario '{comparison_scenario_name}':")
                if comparison_results:
                    print(_format_comparison_table(comparison_results))
                else:
                    print("No comparable settings succeeded.")
                if comparison_failures:
                    print()
                    print("Skipped settings:")
                    for setting_label, error_message in comparison_failures:
                        print(f"  - {setting_label}: {error_message}")
            elif choice == "7":
                print("Exiting program.")
                return
            else:
                print("Invalid option. Please choose a number from 1 to 7.")
        except (FileNotFoundError, ValueError, KeyError, TypeError) as error:
            print(f"Error: {error}")


if __name__ == "__main__":
    main()
