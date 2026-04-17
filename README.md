# COMP1110 Topic C: C1 + C3 + C4 Handover Notes

This README only explains the parts currently implemented for `C1`, `C3`, and `C4`, so other group members can quickly understand the existing code and continue with `C2`, `C5`, and `C6`.

## What is already implemented

### C1: Data model

File: `app/models.py`

This file defines the main entities used by the simulation:

- `QueueRule`: a queue size rule such as `1-2`, `3-4`, `5+`
- `CustomerGroup`: one arriving customer group
- `Table`: one restaurant table
- `SeatingRecord`: one successful seating event
- `SimulationResult`: all output metrics after one run

These classes are the shared data layer for the whole program.

### C3: Core simulation engine

File: `app/simulator.py`

This file contains the simulation logic.

Current method:

- Customer groups are processed in arrival-time order.
- Each group is assigned to the first queue whose size range matches the group size.
- The simulation is event-driven, not minute-by-minute.
- The clock jumps to the next event:
  either the next customer arrival or the next table becoming free.
- When tables are available, the program checks the front group of each queue.
- For each table, it seats the earliest-arriving eligible group among those queue fronts.
- No table sharing or table combining is allowed.
- Groups never leave the queue once they arrive.

This matches the main assumptions from the research:

- strict FCFS within each queue
- no walk-aways
- fixed dining duration
- optional fixed turnover/cleaning time
- optional reserved tables excluded from walk-in seating

### C4: Metrics computation

Main file: `app/simulator.py`

After each run, the program computes:

- average wait time
- maximum wait time
- groups served / groups unserved
- maximum queue length per queue
- table utilization
- seat utilization
- service level (`% seated within X minutes`)
- average wasted seats per seating
- queue-level served counts and average wait times

It also builds a readable seating timeline so case studies are easier to explain.

## Files and responsibilities

- `app/models.py`
  C1 data structures
- `app/simulator.py`
  C3 simulation logic and C4 metrics

## How the simulation currently works

Input expected by the engine:

- restaurant settings
  queues + tables
- arrival scenario
  groups with arrival time, size, and dining duration

High-level flow:

1. Load restaurant settings and arrival groups.
2. Validate the data.
3. Sort groups by arrival time.
4. Run the event loop.
5. Record each seating decision.
6. Compute summary metrics.
7. Format the result into a readable report.
