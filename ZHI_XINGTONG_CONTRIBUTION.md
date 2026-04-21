# Zhi Xingtong Contribution Statement

## Identity

Member name: Zhi Xingtong

According to the project plan table, I am responsible for:

- `C1` Data model
- `C3` Core simulation engine
- `C4` Metrics computation

## Contribution summary

My contribution is the core computational part of the restaurant queue simulation project.

The main goal of my work was to turn the restaurant queue problem into clear Python data structures and a working simulation engine. Other parts of the project, such as file loading, the text menu, and testing, can then call this core engine without needing to know the internal simulation details.

My work focuses on:

- defining the core entities used by the simulation
- implementing the event-driven queue simulation logic
- applying the project assumptions consistently
- computing the key performance metrics required for evaluation
- producing clear simulation results for case-study comparison
- adding demo-friendly arrival data that shows the algorithm working well across different situations

## Problem statement for my coding contribution

The restaurant queue problem needs more than simple input and output. The program must be able to model how groups arrive, join queues, wait for suitable tables, get seated, and leave after dining.

The practical problems I solved are:

- how to represent customer groups, tables, queues, seating records, and final results in code
- how to assign each arriving group to the correct queue based on group size
- how to advance simulation time efficiently from event to event instead of looping minute by minute
- how to seat eligible waiting groups while respecting table capacity and FCFS queue assumptions
- how to support project assumptions such as no table sharing, no table combining, fixed dining duration, fixed turnover time, and optional reserved tables
- how to compute wait-time, utilization, service-level, and queue-performance metrics after the simulation ends

## Code I completed

### C1: Data model

Implemented in `app/models.py`.

Completed work:

- defined `QueueRule` to describe which group sizes each queue accepts
- defined `CustomerGroup` to store arrival time, group size, dining duration, assigned queue, seating time, departure time, and table assignment
- defined `Table` to store table capacity, reservation status, current occupancy, and accumulated occupied time
- defined `SeatingRecord` to record each seating event for the final timeline
- defined `SimulationResult` to collect all metrics and output records from one simulation run

This data model provides a stable interface for the rest of the project.

### C3: Core simulation engine

Implemented in `app/simulator.py`.

Completed work:

- implemented input validation for queues, tables, and customer groups
- implemented queue assignment based on group size
- implemented an event-driven simulation loop
- processed customer arrivals in chronological order
- released tables when their occupied period ends
- seated suitable waiting groups when tables become available
- enforced no table sharing and no table combining
- supported fixed turnover or cleaning time after dining
- supported reserved tables by excluding them from the walk-in seating pool
- tracked seating time, departure time, table assignment, and unserved groups

The simulation uses event-based time advancement. Instead of checking every minute, it jumps directly to the next arrival or next table-freeing event. This makes the logic clearer and more efficient for our project scale.

### C4: Metrics computation

Implemented in `app/simulator.py`.

Completed work:

- calculated average wait time
- calculated maximum wait time
- counted groups served and unserved
- calculated maximum queue length per queue
- calculated table utilization
- calculated seat utilization
- calculated service level, meaning the percentage of groups seated within the threshold time
- calculated average wasted seats per seating
- calculated queue-level served counts and average wait times
- included revenue per minute as an additional practical evaluation metric
- generated a formatted result summary and seating timeline for interpretation

These metrics allow the group to compare queue strategies and table layouts using concrete numerical evidence.

## Case-study data support

I also added additional demo-friendly arrival scenarios in `case_studies/`.

These files are designed to show the simulation working well across a wider range of situations without creating misleading failure cases:

- `case_studies/arrivals_demo_balanced_steady.json`
- `case_studies/arrivals_demo_quiet_afternoon.json`
- `case_studies/arrivals_demo_small_party_cafe.json`
- `case_studies/arrivals_demo_family_dinner.json`
- `case_studies/arrivals_demo_two_waves.json`
- `case_studies/arrivals_demo_queue_blocking.json`
- `case_studies/arrivals_demo_turnover_pressure.json`
- `case_studies/arrivals_demo_full_showcase.json`

These scenarios cover:

- quiet low-traffic operation
- balanced steady arrivals
- small-party cafe rush
- family dinner groups
- two separate arrival waves
- single-queue blocking behavior
- turnover-pressure situations
- a mixed showcase scenario for final demo use

The new demo scenarios are controlled so they can be served by the existing restaurant settings and can better demonstrate that the algorithm works.

## Files that clearly show my contribution

- `app/models.py`
- `app/simulator.py`
- `case_studies/arrivals_demo_balanced_steady.json`
- `case_studies/arrivals_demo_quiet_afternoon.json`
- `case_studies/arrivals_demo_small_party_cafe.json`
- `case_studies/arrivals_demo_family_dinner.json`
- `case_studies/arrivals_demo_two_waves.json`
- `case_studies/arrivals_demo_queue_blocking.json`
- `case_studies/arrivals_demo_turnover_pressure.json`
- `case_studies/arrivals_demo_full_showcase.json`
- `ZHI_XINGTONG_CONTRIBUTION.md`

## How my part connects with teammates' work

My part provides the core engine layer of the program.

Other teammates' components depend on this core layer as follows:

- file I/O loads JSON data and converts it into the model objects I defined
- the text menu calls `run_simulation(...)` from `app/simulator.py`
- saved result files use the `SimulationResult` structure
- tests check that the simulation engine and metrics behave correctly
- case studies use the metrics from my engine to compare different restaurant strategies

This separation means the menu and file-loading code can change without rewriting the simulation algorithm.

## Short summary

My contribution provides the main computational foundation of the project:

- `C1` defines the data structures
- `C3` runs the restaurant queue simulation
- `C4` computes the evaluation metrics
- additional demo data supports clearer final case-study comparisons

Together, these parts make it possible for the whole project to produce meaningful, repeatable, and explainable simulation results.
