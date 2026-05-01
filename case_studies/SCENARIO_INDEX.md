# Scenario Data Index and Reproducibility Notes

This document supports `C8: Scenario data quality and reproducibility support`.

It does not change the simulation logic. Its purpose is to make the case-study data easier to audit, reuse, and reference in the final report or viva discussion.

## Normal paired scenarios

| Pair | Comparison type | Fixed input | Changed factor | Main use |
| --- | --- | --- | --- | --- |
| Pair 01 | Restaurant setting | `pair01_arrivals_mixed_peak.json` | single queue vs size-based queues | queue strategy comparison |
| Pair 02 | Restaurant setting | `pair02_arrivals_granularity_test.json` | coarse queues vs fine queues | queue granularity comparison |
| Pair 03 | Restaurant setting | `pair03_arrivals_small_party_rush.json` | many small tables vs few large tables | table layout comparison |
| Pair 04 | Restaurant setting | `pair04_arrivals_family_groups.json` | balanced mix vs family-oriented mix | family-group layout comparison |
| Pair 05 | Restaurant setting | `pair05_arrivals_reservation_pressure.json` | no reserved table vs one reserved table | reserved capacity comparison |
| Pair 06 | Restaurant setting | `pair06_arrivals_turnover_test.json` | short turnover vs long turnover | turnover-time comparison |
| Pair 07 | Arrival scenario | `pair07_settings_fixed_capacity.json` | burst arrivals vs trickle arrivals | demand concentration check |
| Pair 08 | Arrival scenario | `pair08_settings_single_queue_outlier.json` | standard flow vs one large outlier group | outlier disruption check |
| Pair 09 | Arrival scenario | `pair09_settings_reserved_capacity.json` | quiet window vs peak window | reservation timing sensitivity |

## Data quality rules

The case-study files are organised so that each normal pair has a clear comparison target:

- restaurant-setting pairs keep the arrival file fixed and change one restaurant-side factor
- arrival-scenario pairs keep the restaurant setting fixed and change one customer-demand factor
- file names include the pair number and the role of the file
- normal case-study files are intended to load successfully through the JSON input workflow

These rules make the results easier to reproduce because the report can point to a specific pair and explain exactly what changed.

## Invalid sample pack

The `invalid_samples/` folder is separate from the normal paired scenarios.

It contains intentionally incompatible examples for checking robustness and explaining validation behaviour:

- `settings_max_capacity_4.json` with `arrivals_contains_size_6.json`
- `settings_missing_size_3_queue.json` with `arrivals_size_3_only.json`

These files should not be used for normal comparison results. They are useful for showing that the project can reject unsuitable input instead of silently producing misleading output.

## Report use

For the individual report, this C8 work can be described as data governance and reproducibility support:

- organising scenario files so each pair has a clear purpose
- documenting which variable changes in each pair
- separating valid demo/report data from invalid robustness examples
- making the data pack easier for tutors and group members to inspect
