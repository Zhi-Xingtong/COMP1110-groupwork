from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from app.models import CustomerGroup, QueueRule, SimulationResult, Table


def _read_json(path: str | Path) -> dict | list:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if file_path.stat().st_size == 0:
        raise ValueError(f"File is empty: {file_path}")

    try:
        with file_path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid JSON format in {file_path}: {error.msg}") from error


def load_restaurant_settings(path: str | Path) -> tuple[str, int, int, list[QueueRule], list[Table]]:
    """Load restaurant settings JSON into queue rules and table objects."""

    data = _read_json(path)
    if not isinstance(data, dict):
        raise ValueError("Restaurant settings JSON must be an object.")

    restaurant_name = str(data.get("restaurant_name", "Unnamed Restaurant")).strip()
    service_threshold = int(data.get("service_threshold", 15))
    turnover_duration = int(data.get("turnover_duration", 0))

    queues_raw = data.get("queues")
    tables_raw = data.get("tables")
    if not isinstance(queues_raw, list) or not queues_raw:
        raise ValueError("Restaurant settings must include a non-empty 'queues' list.")
    if not isinstance(tables_raw, list) or not tables_raw:
        raise ValueError("Restaurant settings must include a non-empty 'tables' list.")

    queue_rules: list[QueueRule] = []
    for item in queues_raw:
        if not isinstance(item, dict):
            raise ValueError("Each queue definition must be a JSON object.")
        queue_rules.append(
            QueueRule(
                name=str(item["name"]).strip(),
                min_size=int(item["min_size"]),
                max_size=(int(item["max_size"]) if item.get("max_size") is not None else None),
            )
        )

    tables: list[Table] = []
    for item in tables_raw:
        if not isinstance(item, dict):
            raise ValueError("Each table definition must be a JSON object.")
        tables.append(
            Table(
                table_id=str(item["table_id"]).strip(),
                capacity=int(item["capacity"]),
                reserved=bool(item.get("reserved", False)),
            )
        )

    return restaurant_name, service_threshold, turnover_duration, queue_rules, tables


def load_customer_groups(path: str | Path) -> tuple[str, list[CustomerGroup]]:
    """Load customer arrival JSON into customer group objects."""

    data = _read_json(path)
    if not isinstance(data, dict):
        raise ValueError("Customer arrival JSON must be an object.")

    scenario_name = str(data.get("scenario_name", "Unnamed Scenario")).strip()
    groups_raw = data.get("groups", [])
    if not isinstance(groups_raw, list):
        raise ValueError("'groups' must be a JSON list.")

    groups: list[CustomerGroup] = []
    for item in groups_raw:
        if not isinstance(item, dict):
            raise ValueError("Each group definition must be a JSON object.")
        groups.append(
            CustomerGroup(
                group_id=str(item["group_id"]).strip(),
                arrival_time=int(item["arrival_time"]),
                group_size=int(item["group_size"]),
                dining_duration=int(item["dining_duration"]),
            )
        )

    return scenario_name, groups


def save_simulation_result(path: str | Path, result: SimulationResult) -> Path:
    """Save simulation output metrics to a JSON file."""

    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    payload = asdict(result)
    with file_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2)
    return file_path
