from __future__ import annotations

from collections import defaultdict
from copy import deepcopy

from app.models import CustomerGroup, QueueRule, SeatingRecord, SimulationResult, Table


def validate_inputs(queue_rules: list[QueueRule], tables: list[Table], groups: list[CustomerGroup]) -> None:
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
        if group.group_size > max_capacity:
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
) -> SimulationResult:
    """Run the restaurant queue simulation and return summarized metrics."""

    validate_inputs(queue_rules, tables, groups)
    if service_threshold < 0:
        raise ValueError("Service threshold cannot be negative.")
    if turnover_duration < 0:
        raise ValueError("Turnover duration cannot be negative.")

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

    average_wait = sum(wait_times) / len(wait_times) if wait_times else 0.0
    service_level = (
        sum(1 for wait in wait_times if wait <= service_threshold) / len(served_groups) * 100
        if served_groups
        else 0.0
    )
    utilization = (used_capacity_time / total_capacity_time * 100) if total_capacity_time else 0.0
    seat_utilization = (used_seat_minutes / total_seat_minutes * 100) if total_seat_minutes else 0.0
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

    lines = [
        f"Restaurant: {result.restaurant_name}",
        f"Scenario: {result.scenario_name}",
        f"Groups served: {result.groups_served}/{result.total_groups}",
        f"Groups unserved: {result.groups_unserved}",
        f"Average wait time: {result.average_wait_time:.2f} minutes",
        f"Max wait time: {result.max_wait_time} minutes",
        f"Table utilization (unavailable tables): {result.table_utilization:.2f}%",
        f"Seat utilization (used seats): {result.seat_utilization:.2f}%",
        f"Service level (<={result.service_threshold} min): {result.service_level:.2f}%",
        f"Average wasted seats per seating: {result.average_table_size_gap:.2f}",
        f"Turnover duration: {result.turnover_duration} minutes",
        f"Walk-in tables used: {result.walk_in_tables}",
        f"Reserved tables withheld: {result.reserved_tables}",
        "Max queue lengths:",
    ]
    lines.extend(
        f"  - {queue_name}: {queue_length}"
        for queue_name, queue_length in result.max_queue_lengths.items()
    )
    lines.append("Seating timeline:")
    if result.seating_records:
        lines.extend(
            "  - "
            f"t={record.time}: group {record.group_id} seated at {record.table_id} "
            f"from queue {record.queue_name} after waiting {record.wait_time} min; "
            f"departure at t={record.departure_time}; wasted seats={record.wasted_seats}"
            for record in result.seating_records
        )
    else:
        lines.append("  - No groups were seated.")

    if result.unserved_group_ids:
        lines.append("Unserved groups: " + ", ".join(result.unserved_group_ids))
    lines.append("Queue performance:")
    lines.extend(
        "  - "
        f"{queue_name}: served {result.served_by_queue[queue_name]}, "
        f"avg wait {result.average_wait_by_queue[queue_name]:.2f} min"
        for queue_name in result.max_queue_lengths
    )
    return "\n".join(lines)
