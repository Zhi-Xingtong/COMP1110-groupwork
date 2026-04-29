# Wu Hanlin Contribution Statement

## Identity

Member name: Wu Hanlin

According to the project plan table, Wu Hanlin is responsible for:

- `C2` File I/O
- `C5` Text menu, README, GitHub support materials
- `C6` Test cases

## Contribution summary

My contribution is not the low-level simulation algorithm itself. My role is to turn the project into a complete, runnable, testable, and presentable program.

The main parts of my contribution are:

- completing the input and output file workflow
- building the text menu for direct use
- writing the README and example data
- adding richer case-study data for demo and report use
- writing and extending the automated test cases

## Problem statement for my coding contribution

My part of the project is to make the simulation usable as a complete program instead of only a partial engine file.

The practical problems I solved are:

- how to load restaurant settings and customer arrivals from JSON files safely
- how to save simulation results into a reusable JSON output
- how to let users operate the project through a clear text menu
- how to explain the project structure and JSON format in a README
- how to provide enough data for demo and report use
- how to prove the program works through systematic test cases

## Code I completed

### C2: File I/O

Implemented in `app/file_io.py`.

Completed work:

- load restaurant settings JSON
- load customer arrival JSON
- save simulation results JSON
- handle input errors such as missing file, empty file, and invalid JSON format

### C5: Text menu and project documentation

Implemented in `main.py`, `README.md`, and project data files.

Completed work:

- built a looping text menu
- added options to load settings, load arrivals, run simulation, view results, save results, compare paired scenarios, and exit
- wrote a complete README with project overview, file list, JSON examples, run instructions, and test instructions
- added sample JSON files for quick demonstration
- added a richer `case_studies/` data pack to support scenario comparison and report writing

### C6: Test cases

Implemented in `tests/test_project.py`.

Completed work:

- normal operation test
- all same group size test
- zero customers test
- group larger than any table test
- boundary capacity match test
- invalid input file test
- end-to-end JSON load/save integration test
- case-study dataset loading and simulation test

## Files that clearly show my contribution

- `app/file_io.py`
- `main.py`
- `README.md`
- `sample_data/restaurant_settings.json`
- `sample_data/customer_arrivals.json`
- `case_studies/README.md`
- `case_studies/pair01a_settings_single_queue.json`
- `case_studies/pair01b_settings_size_based.json`
- `case_studies/pair02a_settings_coarse_queues.json`
- `case_studies/pair02b_settings_fine_queues.json`
- `case_studies/pair03a_settings_many_small_tables.json`
- `case_studies/pair03b_settings_few_large_tables.json`
- `case_studies/pair04a_settings_balanced_table_mix.json`
- `case_studies/pair04b_settings_family_table_mix.json`
- `case_studies/pair05a_settings_no_reserved_tables.json`
- `case_studies/pair05b_settings_one_reserved_table.json`
- `case_studies/pair06a_settings_short_turnover.json`
- `case_studies/pair06b_settings_long_turnover.json`
- `case_studies/pair07_settings_fixed_capacity.json`
- `case_studies/pair08_settings_single_queue_outlier.json`
- `case_studies/pair09_settings_reserved_capacity.json`
- `case_studies/pair01_arrivals_mixed_peak.json`
- `case_studies/pair02_arrivals_granularity_test.json`
- `case_studies/pair03_arrivals_small_party_rush.json`
- `case_studies/pair04_arrivals_family_groups.json`
- `case_studies/pair05_arrivals_reservation_pressure.json`
- `case_studies/pair06_arrivals_turnover_test.json`
- `case_studies/pair07a_arrivals_burst_peak.json`
- `case_studies/pair07b_arrivals_trickle_flow.json`
- `case_studies/pair08a_arrivals_standard_flow.json`
- `case_studies/pair08b_arrivals_outlier_group.json`
- `case_studies/pair09a_arrivals_quiet_window.json`
- `case_studies/pair09b_arrivals_peak_window.json`
- `tests/test_project.py`
- `WU_HANLIN_CONTRIBUTION.md`

## Short summary

My contribution makes the project complete from a user perspective:

- input can be loaded from files
- the simulation can be run from a menu
- output can be viewed and saved
- the project can be understood from the README
- there is enough data to support demo and case-study discussion
- the implementation is supported by repeatable tests
