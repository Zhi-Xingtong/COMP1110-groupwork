# Individual Final Report 

## Zhao Zihao

## Contribution focus

My contribution in this project is mostly about the demo-oriented refinement and coding GUI improvement of the restaurant queue simulation system.

The main goal of my work is to optimize the user experience of this simulation model, making it more user-friendly and clearer for our final demostration.

My contribution in this phase includes:

### Coding part

1. redesigning the CLI workflow so users can select settings and arrival scenarios from discovered files instead of typing raw paths every time
2. adding a persistent status area to the main menu so the currently loaded setting and arrival scenario are always visible
3. simplifying the displayed names of settings and scenarios so the menu is cleaner and more suitable for demo use
4. creating a proper paired comparison mode that supports both setting-based and arrival-based pair comparisons
5. improving comparison output with side-by-side tables and visual highlighting for best and tied-best values
6. improving result presentation by converting the seating timeline into a structured table instead of a long text log
7. simplifying result saving so the user can enter only a simple filename and save directly into the `results/` folder
8. adding an economic-style metric, **revenue per minute**, based on a fixed per-customer spending assumption

### Demo part:

1. I have documented the complete workflow of my program to assist the TA in understanding its operation. This documentation covers the entire process: from cloning the repository and selecting specific strategy and scenario configurations to utilizing the comparison function. Additionally, I have included a dataset to demonstrate how the program processes data and generates results.

## Detailed contribution record

### 1. CLI menu and file-selection redesign

I improved the command-line user experience of `main.py`.

Completed work:

- added automatic discovery of available restaurant settings JSON files
- added automatic discovery of available customer arrival JSON files
- changed the old path-only workflow into a numbered selection workflow
- kept manual path entry as a fallback for new files
- removed `sample_data/` entries from the main menu list so the live demo focuses on the formal case-study files
- simplified file labels in the menu into human-readable names such as `pair01a single queue`, `pair01b size based`, and `pair06 turnover test`

This change makes the program much easier to operate in front of a tutor or class audience.

### 2. Persistent status display in the main interface

I added a persistent status area to the top of the CLI main page.

Completed work:

- when nothing is loaded, the program shows:
  - `Current setting not set`
  - `Current arrivals not set`
- after loading a setting, the interface shows:
  - current setting name
  - number of queues
  - number of tables
  - number of reserved tables
- after loading arrivals, the interface shows:
  - current arrival scenario name
  - number of groups

This makes the current simulation state visible at all times and reduces demo confusion.

### 3. Comparison mode redesign

I significantly improved the comparison workflow.

Originally, comparison depended on loading arrivals first in a separate step.  
I redesigned it into a self-contained demo workflow.

Completed work:

- comparison mode now lets the user choose one predefined pair directly
- for setting-side pairs, the program compares the two matching restaurant settings under one fixed arrival scenario
- for arrival-side pairs, the program compares the two matching arrival variations under one fixed restaurant setting
- the program outputs a side-by-side comparison table in the CLI
- invalid or unsuitable settings no longer break the whole comparison flow

This makes comparison mode much more practical for live strategy demonstration.

### 4. Comparison table readability and highlighting

I redesigned comparison output to make the table easier to interpret.

Completed work:

- introduced aligned CLI comparison tables
- added ranking markers for best values
- used different visual meanings for comparison highlighting:
  - unique best value
  - tied best value
  - clearly bad outcome (such as nonzero unserved groups)
- kept identical metrics visible instead of hiding them, so the table remains complete and academically defensible

This work improved the clarity of strategy comparison without changing the core simulation model.

### 5. Result-page readability improvements

I improved the output of a single simulation run.

Completed work:

- converted the old text-style seating timeline into a proper table with aligned columns
- reorganized the summary into a cleaner `label : value` format
- made important numerical results more visually prominent
- improved the layout of queue-length and queue-performance output

This makes it much easier to explain the meaning of a result during a demo.

### 6. Save-results workflow simplification

I simplified the result-saving experience.

Completed work:

- if the user enters only a simple name such as `demo_output`, the program now automatically saves to:
  - `results\demo_output.json`
- full manual paths are still supported if needed

This is a small but important usability improvement for live demonstration.


This improves fairness by reducing distortion caused by different total seat counts.

### 7. Business-oriented metric improvement

I added a more meaningful performance metric based on a simple economic assumption.

Completed work:

- assumed a fixed spending amount per customer
- implemented **revenue per minute**
- added this metric to:
  - single-run analysis output
  - comparison tables

This helps the project move from a purely operational evaluation toward a more practical efficiency interpretation.

### 8. Demo identity and startup presentation

I also improved the first impression of the CLI by adding a startup banner.

Completed work:

- added a `Group 15` ASCII banner shown when the program starts
- kept the banner lightweight so it improves demo identity without disrupting the menu workflow

This gives the program a cleaner and more recognizable opening for live presentation.

## Files showing my contribution in this stage

- `main.py`
- `app\simulator.py`
- `app\models.py`
- `case_studies\pair01a_settings_single_queue.json`
- `case_studies\pair01b_settings_size_based.json`
- `case_studies\pair02a_settings_coarse_queues.json`
- `case_studies\pair02b_settings_fine_queues.json`
- `case_studies\pair03a_settings_many_small_tables.json`
- `case_studies\pair03b_settings_few_large_tables.json`
- `case_studies\pair04a_settings_balanced_table_mix.json`
- `case_studies\pair04b_settings_family_table_mix.json`
- `case_studies\pair05a_settings_no_reserved_tables.json`
- `case_studies\pair05b_settings_one_reserved_table.json`
- `case_studies\pair06a_settings_short_turnover.json`
- `case_studies\pair06b_settings_long_turnover.json`
- `case_studies\pair07_settings_fixed_capacity.json`
- `case_studies\pair08_settings_single_queue_outlier.json`
- `case_studies\pair09_settings_reserved_capacity.json`
- `case_studies\pair07a_arrivals_burst_peak.json`
- `case_studies\pair07b_arrivals_trickle_flow.json`
- `case_studies\pair08a_arrivals_standard_flow.json`
- `case_studies\pair08b_arrivals_outlier_group.json`
- `case_studies\pair09a_arrivals_quiet_window.json`
- `case_studies\pair09b_arrivals_peak_window.json`
- `tests\test_project.py`
- `tests\test_main_helpers.py`
- `README.md`
- `ZHAO_ZIHAO_CONTRIBUTION.md`

## Why this contribution matters

This contribution makes the project stronger specifically in the areas of:

- demo quality
- usability
- interpretability of results
- fairness of comparison design
- practical value of the evaluation metrics

Without this round of work, the program could still run, but it would be much harder to demonstrate clearly, much harder to compare strategies convincingly, and less polished as a final presentation tool.

## Short conclusion

My contribution in this phase is the **final-stage refinement of the simulation system for demo, comparison, and usability**.

In particular, I contributed:

- the improved CLI interaction flow
- the persistent menu status display
- the redesigned comparison mode
- clearer result presentation
- the new revenue-per-minute metric
- the `Group 15` startup banner
- the associated testing and integration work

This work directly improves how the project is operated, demonstrated, and evaluated.



## AI report:

I used github copilot cli (GPT 5.4) to help me code and improve our program. I'm using it to write unit test and system test to verify its correctness, let it write a PRD before coding, and use opus 4.6 to doublecheck its correctness. I also use git to perform version control part so that I can cancel unwanted or problematic ai coding.



I also use ai to help me make subtitle which has time stamp so that i dont need to type it into my computer by myself.
