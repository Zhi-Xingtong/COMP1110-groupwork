# Paired Case Study Data Pack

This folder contains 9 paired scenarios for the restaurant queue simulation.

Each pair follows the same design rule:

- both variations use the same customer arrival file
- only one factor changes between variation A and variation B
- all files use the JSON format required by the program
- the pair is intended to reveal a clear operational trade-off

## Pair 01: Number of Queues / Queue Strategy

Arrival file:

- `pair01_arrivals_mixed_peak.json`

Variations:

- `pair01a_settings_single_queue.json`
- `pair01b_settings_size_based.json`

Changed factor:

- single FCFS queue vs size-based queues

Purpose:

- shows how a single queue can block small groups behind larger groups
- shows how size-based queues can reduce waiting for eligible small groups

## Pair 02: Queue Granularity

Arrival file:

- `pair02_arrivals_granularity_test.json`

Variations:

- `pair02a_settings_coarse_queues.json`
- `pair02b_settings_fine_queues.json`

Changed factor:

- coarse queues (`1-4`, `5-6`) vs fine queues (`1-2`, `3-4`, `5-6`)

Purpose:

- shows the trade-off between simpler queue management and more precise group-size matching

## Pair 03: Table Size Distribution for Small Parties

Arrival file:

- `pair03_arrivals_small_party_rush.json`

Variations:

- `pair03a_settings_many_small_tables.json`
- `pair03b_settings_few_large_tables.json`

Changed factor:

- many small tables vs fewer large tables

Purpose:

- shows that small-party demand benefits from more small tables
- shows that large tables can create seat waste when most customers are groups of 1-2

## Pair 04: Table Mix for Family Groups

Arrival file:

- `pair04_arrivals_family_groups.json`

Variations:

- `pair04a_settings_balanced_table_mix.json`
- `pair04b_settings_family_table_mix.json`

Changed factor:

- balanced table mix vs more 4-person tables

Purpose:

- shows that a family-oriented table mix improves performance when many groups have 3-4 people

## Pair 05: Reserved Capacity

Arrival file:

- `pair05_arrivals_reservation_pressure.json`

Variations:

- `pair05a_settings_no_reserved_tables.json`
- `pair05b_settings_one_reserved_table.json`

Changed factor:

- no reserved tables vs one table withheld from walk-in seating

Purpose:

- approximates the opportunity cost of reservation or VIP capacity
- shows how reducing walk-in capacity increases waiting time

## Pair 06: Turnover Duration

Arrival file:

- `pair06_arrivals_turnover_test.json`

Variations:

- `pair06a_settings_short_turnover.json`
- `pair06b_settings_long_turnover.json`

Changed factor:

- short cleaning/turnover time vs long cleaning/turnover time

Purpose:

- shows how table reset time affects waiting time, service level, and throughput

## Pair 07: Burst vs Trickle Arrivals

Setting file:

- `pair07_settings_fixed_capacity.json`

Variations:

- `pair07a_arrivals_burst_peak.json`
- `pair07b_arrivals_trickle_flow.json`

Changed factor:

- concentrated arrivals in a short peak window vs the same total demand spread over a longer period

Purpose:

- shows how a fixed restaurant layout reacts to changes in arrival concentration
- highlights the difference between designing for average demand and designing for peak demand

## Pair 08: Outlier Disruption

Setting file:

- `pair08_settings_single_queue_outlier.json`

Variations:

- `pair08a_arrivals_standard_flow.json`
- `pair08b_arrivals_outlier_group.json`

Changed factor:

- standard group mix vs the same flow with one 8-person outlier group

Purpose:

- shows how a single large outlier can block a single FCFS queue
- exposes the operational cost of the no-table-combining assumption

## Pair 09: Reservation Timing Mismatch

Setting file:

- `pair09_settings_reserved_capacity.json`

Variations:

- `pair09a_arrivals_quiet_window.json`
- `pair09b_arrivals_peak_window.json`

Changed factor:

- a reserved-table policy under quiet demand vs the same policy under peak demand

Purpose:

- shows that withholding one table is much less costly in a quiet window than in a peak window
- supports discussion of why reservation policies become riskier during busy periods

## Recommended Demo Pairs

For a short live demo, we recommend:

- Pair 01 for queue strategy
- Pair 03 for table-size distribution
- Pair 05 for reserved capacity

For final report analysis, Pairs 01-06 remain the formal restaurant-setting comparisons, while Pairs 07-09 work well as demand-side sensitivity or stress-test extensions.
