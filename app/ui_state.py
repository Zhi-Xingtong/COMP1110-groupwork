from __future__ import annotations

from collections import deque
from copy import deepcopy
from dataclasses import dataclass

from app.models import CustomerGroup, QueueRule, Table
from app.simulator import assign_queue, validate_inputs


@dataclass
class UiSnapshot:
    current_time: int
    queue_lengths: dict[str, int]
    waiting_groups: int
    waiting_people: int
    average_waiting_time: float
    pending_arrivals: int
    next_arrival_time: int | None
    seated_groups: int
    active_tables: int
    current_table_utilization: float
    cumulative_table_utilization: float


class InteractiveQueueState:
    def __init__(self, queue_rules: list[QueueRule], tables: list[Table], turnover_duration: int = 0) -> None:
        validate_inputs(queue_rules, tables, [])
        if turnover_duration < 0:
            raise ValueError("Turnover duration cannot be negative.")

        self.queue_rules = deepcopy(queue_rules)
        self.tables = deepcopy([table for table in tables if not table.reserved])
        self.turnover_duration = turnover_duration
        self.current_time = 0
        self.waiting: dict[str, deque[CustomerGroup]] = {rule.name: deque() for rule in self.queue_rules}
        self.pending_arrivals: deque[CustomerGroup] = deque()
        self.completed_groups: list[CustomerGroup] = []
        self.log_messages: list[str] = []
        self.scenario_name: str | None = None
        self._scenario_blueprint: list[CustomerGroup] = []
        self._group_counter = 1

        if not self.tables:
            raise ValueError("At least one non-reserved table is required for the interactive UI.")

    def snapshot(self) -> UiSnapshot:
        waiting_groups = [group for queue in self.waiting.values() for group in queue]
        waiting_group_count = len(waiting_groups)
        waiting_people = sum(group.group_size for group in waiting_groups)
        average_waiting_time = (
            sum(self.current_time - group.arrival_time for group in waiting_groups) / waiting_group_count
            if waiting_groups
            else 0.0
        )
        active_tables = sum(1 for table in self.tables if not table.is_available)
        current_table_utilization = active_tables / len(self.tables) * 100 if self.tables else 0.0
        total_capacity_time = self.current_time * len(self.tables)
        cumulative_table_utilization = (
            sum(table.occupied_minutes for table in self.tables) / total_capacity_time * 100
            if total_capacity_time
            else 0.0
        )
        return UiSnapshot(
            current_time=self.current_time,
            queue_lengths={name: len(groups) for name, groups in self.waiting.items()},
            waiting_groups=waiting_group_count,
            waiting_people=waiting_people,
            average_waiting_time=average_waiting_time,
            pending_arrivals=len(self.pending_arrivals),
            next_arrival_time=(self.pending_arrivals[0].arrival_time if self.pending_arrivals else None),
            seated_groups=len(self.completed_groups),
            active_tables=active_tables,
            current_table_utilization=current_table_utilization,
            cumulative_table_utilization=cumulative_table_utilization,
        )

    def queue_fronts(self) -> dict[str, CustomerGroup | None]:
        return {
            queue_name: (queue[0] if queue else None)
            for queue_name, queue in self.waiting.items()
        }

    def preview_pending_arrivals(self, limit: int = 5) -> list[CustomerGroup]:
        if limit <= 0:
            return []
        return list(self.pending_arrivals)[:limit]

    def has_active_session(self) -> bool:
        return bool(
            self.pending_arrivals
            or any(queue for queue in self.waiting.values())
            or any(not table.is_available for table in self.tables)
        )

    def _queue_group(self, group: CustomerGroup) -> CustomerGroup:
        group.queue_name = assign_queue(group, self.queue_rules)
        self.waiting[group.queue_name].append(group)
        return group

    def _release_arrivals_up_to_current_time(self) -> list[CustomerGroup]:
        released: list[CustomerGroup] = []
        while self.pending_arrivals and self.pending_arrivals[0].arrival_time <= self.current_time:
            released.append(self._queue_group(self.pending_arrivals.popleft()))
        return released

    def _reset_runtime_state(self) -> list[CustomerGroup]:
        self.current_time = 0
        self.waiting = {rule.name: deque() for rule in self.queue_rules}
        self.pending_arrivals = deque(
            sorted(
                deepcopy(self._scenario_blueprint),
                key=lambda group: (group.arrival_time, group.group_id),
            )
        )
        self.completed_groups = []
        self.log_messages = []
        self._group_counter = 1
        for table in self.tables:
            table.occupied_until = None
            table.occupied_by = None
            table.occupied_minutes = 0
            table.seated_groups = 0
        return self._release_arrivals_up_to_current_time()

    def load_scenario(self, groups: list[CustomerGroup], scenario_name: str = "Custom Scenario") -> None:
        validate_inputs(self.queue_rules, self.tables, groups)
        self.scenario_name = scenario_name.strip() or "Custom Scenario"
        self._scenario_blueprint = sorted(
            deepcopy(groups),
            key=lambda group: (group.arrival_time, group.group_id),
        )
        released = self._reset_runtime_state()
        self.log_messages.append(
            f"Loaded scenario '{self.scenario_name}' with {len(self._scenario_blueprint)} groups"
        )
        if released:
            self.log_messages.append(
                f"t=0: released {len(released)} scenario groups into the live queues"
            )

    def add_group(self, group_size: int, dining_duration: int) -> CustomerGroup:
        if group_size <= 0 or dining_duration <= 0:
            raise ValueError("Group size and dining duration must be positive.")

        group = CustomerGroup(
            group_id=f"U{self._group_counter:03d}",
            arrival_time=self.current_time,
            group_size=group_size,
            dining_duration=dining_duration,
        )
        group.queue_name = assign_queue(group, self.queue_rules)
        max_capacity = max(table.capacity for table in self.tables)
        if group.group_size > max_capacity:
            raise ValueError(f"Group size {group.group_size} exceeds max table capacity {max_capacity}.")

        self.waiting[group.queue_name].append(group)
        self._group_counter += 1
        self.log_messages.append(
            f"t={self.current_time}: added group {group.group_id} (size {group.group_size}) to {group.queue_name}"
        )
        return group

    def remove_front(self, queue_name: str) -> CustomerGroup:
        queue = self.waiting.get(queue_name)
        if queue is None:
            raise ValueError(f"Unknown queue: {queue_name}")
        if not queue:
            raise ValueError(f"Queue '{queue_name}' is already empty.")

        group = queue.popleft()
        self.log_messages.append(f"t={self.current_time}: removed front group {group.group_id} from {queue_name}")
        return group

    def remove_front_batch(self, queue_name: str, count: int) -> list[CustomerGroup]:
        if count <= 0:
            raise ValueError("Removal count must be positive.")

        queue = self.waiting.get(queue_name)
        if queue is None:
            raise ValueError(f"Unknown queue: {queue_name}")
        if len(queue) < count:
            raise ValueError(
                f"Queue '{queue_name}' only has {len(queue)} group(s), so {count} cannot be removed."
            )

        removed_groups = [queue.popleft() for _ in range(count)]
        removed_ids = ", ".join(group.group_id for group in removed_groups)
        self.log_messages.append(
            f"t={self.current_time}: removed {count} front group(s) from {queue_name} ({removed_ids})"
        )
        return removed_groups

    def advance_time(self, minutes: int) -> None:
        if minutes <= 0:
            raise ValueError("Advance minutes must be positive.")

        self.current_time += minutes
        released_tables = []
        for table in self.tables:
            if table.occupied_until is not None and table.occupied_until <= self.current_time:
                released_tables.append(table.table_id)
                table.occupied_until = None
                table.occupied_by = None
        released_groups = self._release_arrivals_up_to_current_time()

        if released_tables:
            self.log_messages.append(
                f"t={self.current_time}: released tables {', '.join(sorted(released_tables))}"
            )
        if released_groups:
            self.log_messages.append(
                f"t={self.current_time}: {len(released_groups)} scheduled groups joined the queues"
            )
        if not released_tables and not released_groups:
            self.log_messages.append(f"t={self.current_time}: advanced time by {minutes} minutes")

    def seat_waiting_groups(self) -> list[tuple[str, str]]:
        seated_pairs: list[tuple[str, str]] = []
        while True:
            available_tables = sorted(
                [table for table in self.tables if table.is_available],
                key=lambda table: (table.capacity, table.table_id),
            )
            if not available_tables:
                break

            assigned_any = False
            for table in available_tables:
                candidates: list[tuple[CustomerGroup, str]] = []
                for queue_name, queue in self.waiting.items():
                    if queue and queue[0].group_size <= table.capacity:
                        candidates.append((queue[0], queue_name))

                if not candidates:
                    continue

                group, queue_name = min(
                    candidates,
                    key=lambda item: (item[0].arrival_time, item[0].group_size, item[0].group_id),
                )
                self.waiting[queue_name].popleft()
                group.seated_time = self.current_time
                group.departure_time = self.current_time + group.dining_duration + self.turnover_duration
                group.table_id = table.table_id
                table.occupied_by = group.group_id
                table.occupied_until = group.departure_time
                table.occupied_minutes += group.dining_duration + self.turnover_duration
                table.seated_groups += 1
                self.completed_groups.append(group)
                self.log_messages.append(
                    f"t={self.current_time}: seated {group.group_id} at {table.table_id} from {queue_name}"
                )
                seated_pairs.append((group.group_id, table.table_id))
                assigned_any = True

            if not assigned_any:
                break

        if not seated_pairs:
            self.log_messages.append(f"t={self.current_time}: no eligible groups could be seated")
        return seated_pairs

    def reset(self) -> None:
        released = self._reset_runtime_state()
        if self.scenario_name is not None:
            self.log_messages.append(f"Reset session and reloaded scenario '{self.scenario_name}'")
            if released:
                self.log_messages.append(
                    f"t=0: released {len(released)} scenario groups into the live queues"
                )
        else:
            self.log_messages.append("Reset session")
