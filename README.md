# COMP1110 Topic C Restaurant Queue Simulation

This project simulates restaurant queue strategies using a text-based Python program. It models customer arrivals, queue assignment, seating decisions, table turnover, and performance metrics so the group can compare different queue-management strategies under controlled scenarios.

## Project overview

The system focuses on a size-based queue model with these main assumptions:

- no table sharing
- no table combining
- strict FCFS within each queue
- no walk-aways
- fixed dining duration
- optional fixed turnover time
- optional reserved tables excluded from walk-in seating

The simulation is event-driven. Instead of moving minute by minute, the clock jumps to the next arrival or the next table becoming available.

## File list

- `main.py`
  text menu for loading files, running the simulation, viewing results, and saving results
- `app/models.py`
  shared data structures for queues, groups, tables, seating records, and simulation results
- `app/simulator.py`
  core simulation engine, validation, metrics computation, and formatted console output
- `app/file_io.py`
  JSON loading and saving functions for restaurant settings, customer arrivals, and results
- `sample_data/restaurant_settings.json`
  example restaurant configuration
- `sample_data/customer_arrivals.json`
  example scenario input
- `case_studies/`
  richer scenario data pack for comparison, demo, and report writing
- `tests/test_project.py`
  automated test cases for core project requirements
- `WU_HANLIN_CONTRIBUTION.md`
  clear record of Wu Hanlin's coding contribution

## JSON format

### Restaurant settings JSON

```json
{
  "restaurant_name": "Group 15 Demo Restaurant",
  "service_threshold": 15,
  "turnover_duration": 5,
  "queues": [
    { "name": "Queue A (1-2)", "min_size": 1, "max_size": 2 },
    { "name": "Queue B (3-4)", "min_size": 3, "max_size": 4 },
    { "name": "Queue C (5+)", "min_size": 5, "max_size": null }
  ],
  "tables": [
    { "table_id": "T1", "capacity": 2, "reserved": false },
    { "table_id": "T2", "capacity": 4, "reserved": false }
  ]
}
```

### Customer arrivals JSON

```json
{
  "scenario_name": "Mixed Lunch Rush",
  "groups": [
    { "group_id": "G1", "arrival_time": 0, "group_size": 2, "dining_duration": 30 },
    { "group_id": "G2", "arrival_time": 2, "group_size": 4, "dining_duration": 45 }
  ]
}
```

### Results JSON

After running the simulation, the program can save a results JSON containing summary metrics and the seating timeline, including:

- average and maximum wait time
- groups served and unserved
- queue performance
- table utilization
- seat utilization
- service level
- seating records

## How to run

1. Open a terminal in the project folder.
2. Run:

```bash
python main.py
```

3. Choose menu options:
   - load restaurant settings
   - load customer arrivals
   - run simulation
   - view results
   - save results

You can use the sample files in `sample_data/` for a quick demo.

If you need more data for presentation or analysis, use the files in `case_studies/`.

## Data pack for report and demo

The `case_studies/` folder now contains:

- 5 restaurant setting files
- 4 arrival scenario files
- 20 customer groups in each case-study arrival file
- suggested pairings for comparing queue strategies and table layouts

This makes the codebase more useful for final demo, report writing, and contribution evidence.

## How to test

Run:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

The automated tests cover:

- normal operation
- all same group size
- zero customers
- group larger than any table
- boundary capacity match
- invalid input file
- JSON load/save integration
- case-study dataset loading and simulation runs

## Contribution note

According to the project plan, Wu Hanlin is responsible for:

- `C2` File I/O
- `C5` Text menu, README, GitHub support materials
- `C6` Test cases

That work is implemented in this version and documented in `WU_HANLIN_CONTRIBUTION.md`.
