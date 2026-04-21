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
3. Select `size based`.
4. Choose `Load customer arrivals`.
5. Select `demo full showcase`.
6. Choose `Run simulation`.
7. Choose `View results`.

For a strategy-comparison demo:

1. Run `python main.py`.
2. Choose `Compare settings`.
3. Select one arrival scenario, such as `demo full showcase` or `demo turnover pressure`.
4. Select multiple settings, such as `single queue`, `coarse queue`, and `size based`.
5. Read the comparison table.

Recommended comparison pairs:

- `single queue` vs `size based`
  We use this pair to show the benefit of size-based queue assignment.
- `coarse queue` vs `size based`
  We use this pair to show the effect of queue granularity.
- `many small tables` vs `few large tables`
  We use this pair to show how table layout affects different demand patterns.

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

Our `case_studies/` folder contains restaurant settings and arrival scenarios for final analysis.

Our restaurant setting files:

- `settings_single_queue.json`
- `settings_size_based.json`
- `settings_coarse_queue.json`
- `settings_many_small_tables.json`
- `settings_few_large_tables.json`

Original arrival scenarios:

- `arrivals_peak_hour.json`
- `arrivals_low_traffic.json`
- `arrivals_uniform_small.json`
- `arrivals_uniform_large.json`

Demo-friendly arrival scenarios:

- `arrivals_demo_balanced_steady.json`
- `arrivals_demo_quiet_afternoon.json`
- `arrivals_demo_small_party_cafe.json`
- `arrivals_demo_family_dinner.json`
- `arrivals_demo_two_waves.json`
- `arrivals_demo_queue_blocking.json`
- `arrivals_demo_turnover_pressure.json`
- `arrivals_demo_full_showcase.json`

We designed the demo-friendly files to show our algorithm working across different situations while avoiding unrealistic failure cases.

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
