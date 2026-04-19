from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
import sys

from app.models import CustomerGroup, QueueRule, SeatingRecord, SimulationResult, Table

BLUE = "\033[94m"
CYAN = "\033[96m"
RED = "\033[91m"
RESET = "\033[0m"
DEFAULT_SPEND_PER_CUSTOMER = 50.0


def _supports_color() -> bool:
    return sys.stdout.isatty()


def _blue(text: str) -> str:
    return f"{BLUE}{text}{RESET}" if _supports_color() else text


def _cyan(text: str) -> str:
    return f"{CYAN}{text}{RESET}" if _supports_color() else text


def _red(text: str) -> str:
    return f"{RED}{text}{RESET}" if _supports_color() else text


def validate_inputs(
    queue_rules: list[QueueRule],
    tables: list[Table],
    groups: list[CustomerGroup],
    allow_unserviceable_groups: bool = False,
) -> None:
    """Validate queue rules, tables, and group records before simulation."""

    if not queue_rules:
        raise ValueError("At least one queue rule is required.")
    if not tables:
        raise ValueError("At least one table is required.")

    seen_queue_names: set[str] = set()
    for queue_rule in queue_rules:
        if not queue_rule.name:
            raise ValueError("Queue names cannot be empty.")
        if queue_rule.name in seen_queue_names:
            raise ValueError(f"Duplicate queue name '{queue_rule.name}'.")
        seen_queue_names.add(queue_rule.name)
        if queue_rule.min_size <= 0:
            raise ValueError(f"Queue '{queue_rule.name}' has invalid min_size.")
        if queue_rule.max_size is not None and queue_rule.max_size < queue_rule.min_size:
            raise ValueError(f"Queue '{queue_rule.name}' has invalid max_size.")

    seen_table_ids: set[str] = set()
    for table in tables:
        if not table.table_id:
            raise ValueError("Table IDs cannot be empty.")
        if table.table_id in seen_table_ids:
            raise ValueError(f"Duplicate table ID '{table.table_id}'.")
        seen_table_ids.add(table.table_id)
        if table.capacity <= 0:
            raise ValueError(f"Table '{table.table_id}' must have positive capacity.")

    if not groups:
        return

    max_capacity = max(table.capacity for table in tables)
    seen_group_ids: set[str] = set()
    for group in groups:
        if not group.group_id:
            raise ValueError("Group IDs cannot be empty.")
        if group.group_id in seen_group_ids:
            raise ValueError(f"Duplicate group ID '{group.group_id}'.")
        seen_group_ids.add(group.group_id)
        if group.group_size <= 0 or group.dining_duration <= 0 or group.arrival_time < 0:
            raise ValueError(f"Group '{group.group_id}' contains invalid values.")
        if group.group_size > max_capacity and not allow_unserviceable_groups:
            raise ValueError(
                f"Group '{group.group_id}' size {group.group_size} exceeds max table capacity {max_capacity}."
            )
        if not any(rule.matches(group.group_size) for rule in queue_rules):
            raise ValueError(f"No queue can serve group '{group.group_id}' size {group.group_size}.")


def assign_queue(group: CustomerGroup, queue_rules: list[QueueRule]) -> str:
    """Return the first queue rule that matches the group size."""

    for rule in queue_rules:
        if rule.matches(group.group_size):
            return rule.name
    raise ValueError(f"No matching queue for group size {group.group_size}.")


def _seat_waiting_groups(
    current_time: int,
    queue_names: list[str],
    waiting: dict[str, list[CustomerGroup]],
    tables: list[Table],
    seating_records: list[SeatingRecord],
    turnover_duration: int,
) -> None:
    """Seat eligible front-of-queue groups on currently available tables."""

    while True:
        available_tables = sorted(
            [table for table in tables if table.is_available],
            key=lambda table: (table.capacity, table.table_id),
        )
        if not available_tables:
            return

        assigned_any = False
        for table in available_tables:
            candidates: list[tuple[CustomerGroup, str]] = []
            for queue_name in queue_names:
                queue = waiting[queue_name]
                if queue and queue[0].group_size <= table.capacity:
                    candidates.append((queue[0], queue_name))

            if not candidates:
                continue

            group, queue_name = min(
                candidates,
                key=lambda item: (item[0].arrival_time, item[0].group_size, item[0].group_id),
            )
            waiting[queue_name].pop(0)
            group.seated_time = current_time
            group.departure_time = current_time + group.dining_duration + turnover_duration
            group.table_id = table.table_id
            table.occupied_by = group.group_id
            table.occupied_until = group.departure_time
            table.occupied_minutes += group.dining_duration + turnover_duration
            table.seated_groups += 1
            seating_records.append(
                SeatingRecord(
                    time=current_time,
                    departure_time=group.departure_time,
                    table_id=table.table_id,
                    group_id=group.group_id,
                    queue_name=queue_name,
                    wait_time=current_time - group.arrival_time,
                    dining_duration=group.dining_duration,
                    wasted_seats=table.capacity - group.group_size,
                )
            )
            assigned_any = True

        if not assigned_any:
            return


def run_simulation(
    restaurant_name: str,
    scenario_name: str,
    queue_rules: list[QueueRule],
    tables: list[Table],
    groups: list[CustomerGroup],
    service_threshold: int = 15,
    turnover_duration: int = 0,
    allow_unserviceable_groups: bool = False,
    spend_per_customer: float = DEFAULT_SPEND_PER_CUSTOMER,
) -> SimulationResult:
    """Run the restaurant queue simulation and return summarized metrics."""

    validate_inputs(queue_rules, tables, groups, allow_unserviceable_groups=allow_unserviceable_groups)
    if service_threshold < 0:
        raise ValueError("Service threshold cannot be negative.")
    if turnover_duration < 0:
        raise ValueError("Turnover duration cannot be negative.")
    if spend_per_customer < 0:
        raise ValueError("Spend per customer cannot be negative.")

    tables = deepcopy(tables)
    groups = sorted(deepcopy(groups), key=lambda group: (group.arrival_time, group.group_id))
    queue_names = [rule.name for rule in queue_rules]
    active_tables = [table for table in tables if not table.reserved]
    if not active_tables:
        raise ValueError("At least one non-reserved table is required for walk-in simulation.")

    waiting: dict[str, list[CustomerGroup]] = {name: [] for name in queue_names}
    max_queue_lengths: dict[str, int] = defaultdict(int)
    seating_records: list[SeatingRecord] = []

    arrival_index = 0
    while arrival_index < len(groups) or any(not table.is_available for table in active_tables) or any(waiting.values()):
        next_arrival = groups[arrival_index].arrival_time if arrival_index < len(groups) else None
        next_departure_candidates = [
            table.occupied_until for table in active_tables if table.occupied_until is not None
        ]
        next_departure = min(next_departure_candidates) if next_departure_candidates else None

        current_time_candidates = [value for value in (next_arrival, next_departure) if value is not None]
        if not current_time_candidates:
            break
        current_time = min(current_time_candidates)

        for table in active_tables:
            if table.occupied_until is not None and table.occupied_until <= current_time:
                table.occupied_until = None
                table.occupied_by = None

        while arrival_index < len(groups) and groups[arrival_index].arrival_time == current_time:
            group = groups[arrival_index]
            queue_name = assign_queue(group, queue_rules)
            group.queue_name = queue_name
            waiting[queue_name].append(group)
            max_queue_lengths[queue_name] = max(max_queue_lengths[queue_name], len(waiting[queue_name]))
            arrival_index += 1

        _seat_waiting_groups(
            current_time=current_time,
            queue_names=queue_names,
            waiting=waiting,
            tables=active_tables,
            seating_records=seating_records,
            turnover_duration=turnover_duration,
        )

    served_groups = [group for group in groups if group.seated_time is not None]
    unserved_groups = [group for group in groups if group.seated_time is None]
    wait_times = [group.wait_time for group in served_groups if group.wait_time is not None]
    served_by_queue: dict[str, int] = {name: 0 for name in queue_names}
    waits_by_queue: dict[str, list[int]] = {name: [] for name in queue_names}
    size_gaps: list[int] = []
    table_map = {table.table_id: table for table in active_tables}
    for group in served_groups:
        if group.queue_name is not None and group.wait_time is not None:
            served_by_queue[group.queue_name] += 1
            waits_by_queue[group.queue_name].append(group.wait_time)
        if group.table_id is not None:
            size_gaps.append(table_map[group.table_id].capacity - group.group_size)

    total_time = max(
        [0]
        + [group.arrival_time for group in groups]
        + [record.departure_time for record in seating_records]
    )
    total_capacity_time = total_time * len(active_tables) if total_time else 0
    used_capacity_time = sum(table.occupied_minutes for table in active_tables)
    total_seat_minutes = total_time * sum(table.capacity for table in active_tables) if total_time else 0
    used_seat_minutes = sum(group.group_size * group.dining_duration for group in served_groups)
    served_customers = sum(group.group_size for group in served_groups)
    total_revenue = served_customers * spend_per_customer

    average_wait = sum(wait_times) / len(wait_times) if wait_times else 0.0
    service_level = (
        sum(1 for wait in wait_times if wait <= service_threshold) / len(served_groups) * 100
        if served_groups
        else 0.0
    )
    utilization = (used_capacity_time / total_capacity_time * 100) if total_capacity_time else 0.0
    seat_utilization = (used_seat_minutes / total_seat_minutes * 100) if total_seat_minutes else 0.0
    revenue_per_minute = (total_revenue / total_time) if total_time else 0.0
    average_wait_by_queue = {
        name: (sum(values) / len(values) if values else 0.0)
        for name, values in waits_by_queue.items()
    }

    return SimulationResult(
        restaurant_name=restaurant_name,
        scenario_name=scenario_name,
        total_groups=len(groups),
        groups_served=len(served_groups),
        groups_unserved=len(unserved_groups),
        average_wait_time=average_wait,
        max_wait_time=max(wait_times) if wait_times else 0,
        table_utilization=utilization,
        seat_utilization=seat_utilization,
        service_level=service_level,
        spend_per_customer=spend_per_customer,
        revenue_per_minute=revenue_per_minute,
        average_table_size_gap=(sum(size_gaps) / len(size_gaps) if size_gaps else 0.0),
        reserved_tables=sum(1 for table in tables if table.reserved),
        walk_in_tables=len(active_tables),
        service_threshold=service_threshold,
        turnover_duration=turnover_duration,
        max_queue_lengths={name: max_queue_lengths.get(name, 0) for name in queue_names},
        served_by_queue=served_by_queue,
        average_wait_by_queue=average_wait_by_queue,
        seating_records=seating_records,
        unserved_group_ids=[group.group_id for group in unserved_groups],
    )


def format_result(result: SimulationResult) -> str:
    """Build a readable multi-line report for console output."""

    def format_plain_table(headers: list[str], rows: list[list[str]]) -> list[str]:
        table_rows = [headers] + rows
        column_widths = [
            max(len(str(row[column_index])) for row in table_rows) for column_index in range(len(headers))
        ]

        def format_row(row: list[str]) -> str:
            return " | ".join(
                str(cell).ljust(column_widths[column_index]) for column_index, cell in enumerate(row)
            )

        separator = "-+-".join("-" * width for width in column_widths)
        return [format_row(headers), separator] + [format_row(row) for row in rows]

    def format_summary_lines(items: list[tuple[str, str, str]]) -> list[str]:
        label_width = max(len(label) for label, _, _ in items)
        rendered_lines: list[str] = []
        for label, value, style in items:
            if style == "number":
                rendered_value = _cyan(value)
            elif style == "warning":
                rendered_value = _red(value)
            else:
                rendered_value = value
            rendered_lines.append(f"{label.ljust(label_width)} : {rendered_value}")
        return rendered_lines

    summary_items = [
        ("Restaurant", result.restaurant_name, "plain"),
        ("Scenario", result.scenario_name, "plain"),
        ("Groups served", f"{result.groups_served}/{result.total_groups}", "number"),
        (
            "Groups unserved",
            str(result.groups_unserved),
            "warning" if result.groups_unserved > 0 else "number",
        ),
        ("Average wait time", f"{result.average_wait_time:.2f} minutes", "number"),
        ("Max wait time", f"{result.max_wait_time} minutes", "number"),
        ("Table utilization", f"{result.table_utilization:.2f}%", "number"),
        ("Seat utilization", f"{result.seat_utilization:.2f}%", "number"),
        ("Service level", f"{result.service_level:.2f}% (<= {result.service_threshold} min)", "number"),
        ("Revenue per minute", f"{result.revenue_per_minute:.2f} @ {result.spend_per_customer:.0f}/customer", "number"),
        ("Average wasted seats", f"{result.average_table_size_gap:.2f}", "number"),
        ("Turnover duration", f"{result.turnover_duration} minutes", "number"),
        ("Walk-in tables used", str(result.walk_in_tables), "number"),
        ("Reserved tables", str(result.reserved_tables), "number"),
    ]

    lines = [_blue("Summary"), _blue("-------"), *format_summary_lines(summary_items), _blue("Max queue lengths:")]
    lines.extend(
        f"  - {queue_name.ljust(max(len(name) for name in result.max_queue_lengths))} : {_cyan(str(queue_length))}"
        for queue_name, queue_length in result.max_queue_lengths.items()
    )
    lines.append(_blue("Seating timeline:"))
    if result.seating_records:
        lines.extend(
            format_plain_table(
                ["Time", "Group", "Table", "Queue", "Wait", "Depart", "Wasted"],
                [
                    [
                        str(record.time),
                        record.group_id,
                        record.table_id,
                        record.queue_name,
                        str(record.wait_time),
                        str(record.departure_time),
                        str(record.wasted_seats),
                    ]
                    for record in result.seating_records
                ],
            )
        )
    else:
        lines.append("No groups were seated.")

    if result.unserved_group_ids:
        lines.append("Unserved groups: " + _red(", ".join(result.unserved_group_ids)))
    lines.append(_blue("Queue performance:"))
    lines.extend(
        "  - "
        f"{queue_name}: served {_cyan(str(result.served_by_queue[queue_name]))}, "
        f"avg wait {_cyan(f'{result.average_wait_by_queue[queue_name]:.2f} min')}"
        for queue_name in result.max_queue_lengths
    )
    return "\n".join(lines)
