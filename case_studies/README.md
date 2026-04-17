# Case Study Data Pack

This folder provides richer input data for scenario comparison and demo use.

## Included settings files

- `settings_single_queue.json`
  baseline single FCFS queue
- `settings_size_based.json`
  fine-grained size-based queue design
- `settings_coarse_queue.json`
  coarse queue grouping (`1-4` and `5+`)
- `settings_many_small_tables.json`
  more small tables
- `settings_few_large_tables.json`
  fewer but larger tables

## Included arrival files

- `arrivals_peak_hour.json`
  20 mixed groups during a heavy rush
- `arrivals_low_traffic.json`
  20 mixed groups with larger arrival gaps
- `arrivals_uniform_small.json`
  20 small groups
- `arrivals_uniform_large.json`
  20 large groups

## Suggested pairings

1. `settings_single_queue.json` vs `settings_size_based.json`
   Use the same `arrivals_peak_hour.json` to compare fairness and utilization.
2. `settings_coarse_queue.json` vs `settings_size_based.json`
   Use the same `arrivals_peak_hour.json` to compare coarse vs fine queue granularity.
3. `settings_many_small_tables.json` vs `settings_few_large_tables.json`
   Use the same `arrivals_peak_hour.json` or `arrivals_uniform_large.json` to compare table layouts.
4. `arrivals_low_traffic.json` vs `arrivals_peak_hour.json`
   Use the same `settings_size_based.json` to compare low traffic and peak hour demand.

These files were added to make the codebase easier to demonstrate, test, and discuss in the final submission.
