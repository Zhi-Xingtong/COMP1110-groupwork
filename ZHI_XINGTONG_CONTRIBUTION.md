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
- adding paired case-study data that varies exactly one factor per pair
- extending the paired data pack with demand-side stress and sensitivity scenarios
- refining the main README so the final project can be tested and understood by professors and TAs

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

I contributed to the paired case-study data in two different ways.

For `Pair 01` to `Pair 06`, I supported the construction and alignment of the formal paired-scenario pack with the simulation engine and project requirements.

These files are designed to match the project requirement that each pair varies exactly one factor while using the same customer arrival pattern:

- Pair 01 compares single queue and size-based queues.
- Pair 02 compares coarse queues and fine-grained queues.
- Pair 03 compares many small tables and fewer large tables.
- Pair 04 compares balanced table mix and family-oriented table mix.
- Pair 05 compares no reserved tables and one reserved table.
- Pair 06 compares short turnover time and long turnover time.

For `Pair 07` to `Pair 09`, I designed and implemented the demand-side extension scenarios as part of my contribution. These pairs keep the restaurant setting fixed while changing customer-side conditions:

- Pair 07 compares burst arrivals and trickle arrivals.
- Pair 08 compares a standard flow and a flow containing one large outlier group.
- Pair 09 compares quiet-window and peak-window demand under the same reserved-capacity setting.

The paired scenarios cover:

- queue strategy
- queue granularity
- table size distribution
- table mix for family groups
- reserved capacity
- turnover duration
- arrival concentration
- outlier disruption
- reservation timing mismatch under different demand states

The paired scenarios are controlled so the comparison within each pair is fair and easy to explain.

In particular, `Pair 07-09` extend the original setting-side comparison pack by exposing demand sensitivity, outlier disruption, and reservation timing effects that are not captured as directly by `Pair 01-06`.

## README refinement

I also helped refine the main `README.md` for final submission.

This makes the repository easier for external readers to evaluate without needing extra explanation from group members.

## Files that clearly show my contribution

- `app/models.py`
- `app/simulator.py`
- `case_studies/pair01_arrivals_mixed_peak.json`
- `case_studies/pair01a_settings_single_queue.json`
- `case_studies/pair01b_settings_size_based.json`
- `case_studies/pair02_arrivals_granularity_test.json`
- `case_studies/pair02a_settings_coarse_queues.json`
- `case_studies/pair02b_settings_fine_queues.json`
- `case_studies/pair03_arrivals_small_party_rush.json`
- `case_studies/pair03a_settings_many_small_tables.json`
- `case_studies/pair03b_settings_few_large_tables.json`
- `case_studies/pair04_arrivals_family_groups.json`
- `case_studies/pair04a_settings_balanced_table_mix.json`
- `case_studies/pair04b_settings_family_table_mix.json`
- `case_studies/pair05_arrivals_reservation_pressure.json`
- `case_studies/pair05a_settings_no_reserved_tables.json`
- `case_studies/pair05b_settings_one_reserved_table.json`
- `case_studies/pair06_arrivals_turnover_test.json`
- `case_studies/pair06a_settings_short_turnover.json`
- `case_studies/pair06b_settings_long_turnover.json`
- `case_studies/pair07_settings_fixed_capacity.json`
- `case_studies/pair07a_arrivals_burst_peak.json`
- `case_studies/pair07b_arrivals_trickle_flow.json`
- `case_studies/pair08_settings_single_queue_outlier.json`
- `case_studies/pair08a_arrivals_standard_flow.json`
- `case_studies/pair08b_arrivals_outlier_group.json`
- `case_studies/pair09_settings_reserved_capacity.json`
- `case_studies/pair09a_arrivals_quiet_window.json`
- `case_studies/pair09b_arrivals_peak_window.json`
- `README.md`
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
- paired case-study data supports clearer final case-study comparisons
- the final README helps professors and TAs understand, run, and test the project

Together, these parts make it possible for the whole project to produce meaningful, repeatable, and explainable simulation results.
