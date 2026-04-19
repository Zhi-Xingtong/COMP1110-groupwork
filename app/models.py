from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class QueueRule:
    """A party-size rule that determines which queue a group joins."""

    name: str
    min_size: int
    max_size: Optional[int]

    def matches(self, group_size: int) -> bool:
        upper_ok = self.max_size is None or group_size <= self.max_size
        return self.min_size <= group_size and upper_ok


@dataclass
class CustomerGroup:
    """One arriving customer group in the simulation."""

    group_id: str
    arrival_time: int
    group_size: int
    dining_duration: int
    queue_name: Optional[str] = None
    seated_time: Optional[int] = None
    departure_time: Optional[int] = None
    table_id: Optional[str] = None

    @property
    def wait_time(self) -> Optional[int]:
        if self.seated_time is None:
            return None
        return self.seated_time - self.arrival_time


@dataclass
class Table:
    """One restaurant table and its current simulation state."""

    table_id: str
    capacity: int
    reserved: bool = False
    occupied_until: Optional[int] = None
    occupied_by: Optional[str] = None
    occupied_minutes: int = 0
    seated_groups: int = 0

    @property
    def is_available(self) -> bool:
        return self.occupied_until is None


@dataclass
class SeatingRecord:
    """A successful seating event captured in the result timeline."""

    time: int
    departure_time: int
    table_id: str
    group_id: str
    queue_name: str
    wait_time: int
    dining_duration: int
    wasted_seats: int


@dataclass
class SimulationResult:
    """All user-facing metrics produced after one simulation run."""

    restaurant_name: str
    scenario_name: str
    total_groups: int
    groups_served: int
    groups_unserved: int
    average_wait_time: float
    max_wait_time: int
    table_utilization: float
    seat_utilization: float
    service_level: float
    spend_per_customer: float
    revenue_per_minute: float
    average_table_size_gap: float
    reserved_tables: int
    walk_in_tables: int
    service_threshold: int
    turnover_duration: int
    max_queue_lengths: dict[str, int]
    served_by_queue: dict[str, int]
    average_wait_by_queue: dict[str, float]
    seating_records: list[SeatingRecord] = field(default_factory=list)
    unserved_group_ids: list[str] = field(default_factory=list)
