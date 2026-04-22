# COMP1110 Topic C: Restaurant Queue Simulation

We built a text-based Python simulation for **Topic C: Restaurant Queue Simulation**. Our program models how customer groups arrive, join queues, wait for suitable tables, and get seated. We then report performance metrics so different queue strategies and table layouts can be compared with the same customer-arrival scenario.

## Project Scope

We focus on a simplified restaurant operation model.

We model:

- customer groups with arrival time, group size, and dining duration
- restaurant tables with fixed capacities
- one or more queues based on group-size ranges
- first-come-first-served processing within each queue
- table turnover or cleaning time
- reserved tables that can be excluded from walk-in seating
- performance metrics for case-study comparison

## Main Assumptions

- Each group must be seated at one table that has enough capacity.
- A table can serve only one group at a time.
- Groups do not share tables with strangers.
- Tables cannot be combined.
- Groups wait until they are seated.
- Dining duration and turnover duration are fixed input values.
- Our simulation clock jumps between events, such as arrivals and table departures.
- We use static input files and text-based interaction rather than live restaurant data or a graphical interface.

## File Structure

- `main.py`
  Our main text-menu program. Use this file to run the project.
- `app/models.py`
  Our data classes for queue rules, customer groups, tables, seating records, and simulation results.
- `app/simulator.py`
  Our core simulation engine, validation, seating logic, metric calculation, and formatted result output.
- `app/file_io.py`
  Our JSON loading and saving functions for restaurant settings, customer arrivals, and simulation results.
- `sample_data/`
  Small example files for quick testing.
- `case_studies/`
  Larger scenario data pack for final demo, report analysis, and strategy comparison.
- `tests/`
  Automated unit tests.
- `*_CONTRIBUTION.md`
  Our individual contribution records.

## How to Run

Open a terminal in the project folder and run:

```bash
python main.py
```

Our menu provides these main actions:

- load restaurant settings
- load customer arrivals
- run simulation
- view results
- save results as JSON
- compare multiple restaurant settings with one arrival scenario
- exit

## Recommended Quick Demo

For a simple single-run demo:

1. Run `python main.py`.
2. Choose `Load restaurant settings`.
3. Select `pair01b size based`.
4. Choose `Load customer arrivals`.
5. Select `pair01 mixed peak`.
6. Choose `Run simulation`.
7. Choose `View results`.

For a strategy-comparison demo:

1. Run `python main.py`.
2. Choose `Compare settings`.
3. Select one paired arrival scenario, such as `pair01 mixed peak` or `pair06 turnover test`.
4. Select the two matching settings for that pair, such as `pair01a single queue` and `pair01b size based`.
5. Read the comparison table.

Recommended comparison pairs:

- `pair01a single queue` vs `pair01b size based`
  We use this pair to show the benefit of size-based queue assignment.
- `pair02a coarse queues` vs `pair02b fine queues`
  We use this pair to show the effect of queue granularity.
- `pair03a many small tables` vs `pair03b few large tables`
  We use this pair to show how table layout affects small-party demand.

## Input File Formats

### Restaurant Settings JSON

Our restaurant setting files define the queue strategy, service threshold, turnover time, and table layout.

Example:

```json
{
  "restaurant_name": "Example Restaurant",
  "service_threshold": 15,
  "turnover_duration": 5,
  "queues": [
    { "name": "Queue A (1-2)", "min_size": 1, "max_size": 2 },
    { "name": "Queue B (3-4)", "min_size": 3, "max_size": 4 },
    { "name": "Queue C (5+)", "min_size": 5, "max_size": 6 }
  ],
  "tables": [
    { "table_id": "T1", "capacity": 2, "reserved": false },
    { "table_id": "T2", "capacity": 4, "reserved": false },
    { "table_id": "T3", "capacity": 6, "reserved": false }
  ]
}
```

Notes:

- `service_threshold` is used to calculate service level.
- `turnover_duration` is the cleaning or reset time after dining.
- `reserved: true` means the table is not used for walk-in seating.
- `max_size: null` can be used for an open-ended queue range.

### Customer Arrivals JSON

Our arrival files define one customer-arrival scenario.

Example:

```json
{
  "scenario_name": "Mixed Lunch Rush",
  "groups": [
    { "group_id": "G1", "arrival_time": 0, "group_size": 2, "dining_duration": 30 },
    { "group_id": "G2", "arrival_time": 2, "group_size": 4, "dining_duration": 45 }
  ]
}
```

Notes:

- Time is measured in minutes from the start of the simulation.
- `arrival_time` is when the group joins the system.
- `dining_duration` does not include turnover time.

## Output Metrics

After a simulation run, our program reports:

- groups served and unserved
- average wait time
- maximum wait time
- maximum queue length per queue
- table utilization
- seat utilization
- service level
- average wasted seats per seating
- queue-level average wait time
- revenue per minute based on a fixed spending assumption
- seating timeline

We can also save results as JSON from the menu.

## Case Study Data

Our `case_studies/` folder contains 6 paired scenarios for final analysis. In each pair, both variations use the same customer arrival pattern and change exactly one factor.

Our restaurant setting files:

- `pair01a_settings_single_queue.json`
- `pair01b_settings_size_based.json`
- `pair02a_settings_coarse_queues.json`
- `pair02b_settings_fine_queues.json`
- `pair03a_settings_many_small_tables.json`
- `pair03b_settings_few_large_tables.json`
- `pair04a_settings_balanced_table_mix.json`
- `pair04b_settings_family_table_mix.json`
- `pair05a_settings_no_reserved_tables.json`
- `pair05b_settings_one_reserved_table.json`
- `pair06a_settings_short_turnover.json`
- `pair06b_settings_long_turnover.json`

Our paired arrival files:

- `pair01_arrivals_mixed_peak.json`
- `pair02_arrivals_granularity_test.json`
- `pair03_arrivals_small_party_rush.json`
- `pair04_arrivals_family_groups.json`
- `pair05_arrivals_reservation_pressure.json`
- `pair06_arrivals_turnover_test.json`

We designed these paired files to match the project requirement: each pair varies exactly one factor while keeping the customer arrival pattern fixed.

Pair summary:

- Pair 01: single queue vs size-based queues
- Pair 02: coarse queues vs fine queues
- Pair 03: many small tables vs few large tables
- Pair 04: balanced table mix vs family-oriented table mix
- Pair 05: no reserved tables vs one reserved table
- Pair 06: short turnover time vs long turnover time

## How to Test

Run all automated tests with:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

Our tests cover:

- normal simulation operation
- same-size groups
- zero-customer input
- group too large for any table
- capacity boundary cases
- revenue metric calculation
- formatted result output
- invalid JSON input handling
- JSON load/save integration
- case-study file loading and simulation
- helper functions used by the text menu

## Contribution Files

We provide individual contribution records in:

- `WU_HANLIN_CONTRIBUTION.md`
- `ZHAO_ZIHAO_CONTRIBUTION.md`
- `ZHI_XINGTONG_CONTRIBUTION.md`

These files explain our coding contributions and the files most closely related to each member's work.
