from __future__ import annotations

from collections import defaultdict
from copy import deepcopy

from app.models import CustomerGroup, QueueRule, SeatingRecord, SimulationResult, Table


def validate_inputs(queue_rules: list[QueueRule], tables: list[Table], groups: list[CustomerGroup]) -> None:
    if not queue_rules:
        raise ValueError("At least one queue rule is required.")
    if not tables:
        raise ValueError("At least one table is required.")
    if not groups:
        raise ValueError("At least one customer group is required.")

    for queue_rule in queue_rules:
        if queue_rule.min_size <= 0:
            raise ValueError(f"Queue '{queue_rule.name}' has invalid min_size.")
        if queue_rule.max_size is not None and queue_rule.max_size < queue_rule.min_size:
            raise ValueError(f"Queue '{queue_rule.name}' has invalid max_size.")

    for table in tables:
        if table.capacity <= 0:
            raise ValueError(f"Table '{table.table_id}' must have positive capacity.")

    max_capacity = max(table.capacity for table in tables)
    for group in groups:
        if group.group_size <= 0 or group.dining_duration <= 0 or group.arrival_time < 0:
            raise ValueError(f"Group '{group.group_id}' contains invalid values.")
        if group.group_size > max_capacity:
            raise ValueError(
                f"Group '{group.group_id}' size {group.group_size} exceeds max table capacity {max_capacity}."
            )
        if not any(rule.matches(group.group_size) for rule in queue_rules):
            raise ValueError(f"No queue can serve group '{group.group_id}' size {group.group_size}.")


def assign_queue(group: CustomerGroup, queue_rules: list[QueueRule]) -> str:
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
) -> None:
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
            group.table_id = table.table_id
            table.occupied_by = group.group_id
            table.occupied_until = current_time + group.dining_duration
            table.occupied_minutes += group.dining_duration
            table.seated_groups += 1
            seating_records.append(
                SeatingRecord(
                    time=current_time,
                    table_id=table.table_id,
                    group_id=group.group_id,
                    queue_name=queue_name,
                    wait_time=current_time - group.arrival_time,
                    dining_duration=group.dining_duration,
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
    validate_inputs(queue_rules, tables, groups)
    if turnover_duration < 0:
        raise ValueError("Turnover duration cannot be negative.")
    tables = deepcopy(tables)
    groups = deepcopy(groups)
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

        _seat_waiting_groups(current_time, queue_names, waiting, active_tables, seating_records)

        if turnover_duration:
            for table in active_tables:
                if table.occupied_until is not None and table.occupied_by is not None:
                    table.occupied_until += turnover_duration
                    table.occupied_by = None

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
        + [record.time + record.dining_duration + turnover_duration for record in seating_records]
    )
    total_capacity_time = total_time * len(active_tables) if total_time else 0
    used_capacity_time = sum(table.occupied_minutes for table in active_tables)
    total_seat_minutes = total_time * sum(table.capacity for table in active_tables) if total_time else 0
    used_seat_minutes = sum(
        group.group_size * group.dining_duration for group in served_groups
    )

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
        max_queue_lengths={name: max_queue_lengths.get(name, 0) for name in queue_names},
        served_by_queue=served_by_queue,
        average_wait_by_queue=average_wait_by_queue,
        seating_records=seating_records,
        unserved_group_ids=[group.group_id for group in unserved_groups],
    )


def format_result(result: SimulationResult) -> str:
    lines = [
        f"Restaurant: {result.restaurant_name}",
        f"Scenario: {result.scenario_name}",
        f"Groups served: {result.groups_served}/{result.total_groups}",
        f"Groups unserved: {result.groups_unserved}",
        f"Average wait time: {result.average_wait_time:.2f} minutes",
        f"Max wait time: {result.max_wait_time} minutes",
        f"Table utilization (occupied tables): {result.table_utilization:.2f}%",
        f"Seat utilization (used seats): {result.seat_utilization:.2f}%",
        f"Service level (<=15 min): {result.service_level:.2f}%",
        f"Average wasted seats per seating: {result.average_table_size_gap:.2f}",
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
            f"from queue {record.queue_name} after waiting {record.wait_time} min"
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
