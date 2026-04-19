# Zhao Zihao Contribution Statement

## Identity

Member name: Zhao Zihao

## Contribution focus

My contribution in this stage of the project is the **demo-oriented refinement and coding improvement** of the restaurant queue simulation system.  
The main goal of my work was not to redesign the whole simulation model from scratch, but to turn the existing project into a clearer, more convincing, and more presentation-ready program for final demonstration and practical use.

The work I completed in this stage focuses on:

- improving command-line interaction and usability
- making the program easier to operate in a live demo
- improving the readability of simulation outputs
- making comparison mode more useful for strategy evaluation
- refining case-study settings so comparisons are fairer and more defensible
- adding more meaningful business-style evaluation metrics

## Main contribution summary

I led and completed a substantial round of final-stage refinement work on the Python CLI application.  
This work was aimed at making the project easier to demonstrate, easier to interpret, and more aligned with how queue strategies and seating configurations should be compared in practice.

My contribution in this phase includes:

1. redesigning the CLI workflow so users can select settings and arrival scenarios from discovered files instead of typing raw paths every time
2. adding a persistent status area to the main menu so the currently loaded setting and arrival scenario are always visible
3. simplifying the displayed names of settings and scenarios so the menu is cleaner and more suitable for demo use
4. creating a proper comparison mode that compares multiple restaurant settings against one fixed customer-arrival scenario
5. improving comparison output with side-by-side tables and visual highlighting for best and tied-best values
6. improving result presentation by converting the seating timeline into a structured table instead of a long text log
7. simplifying result saving so the user can enter only a simple filename and save directly into the `results/` folder
8. normalizing the case-study settings so the main strategy and seating-layout comparisons use a fairer total seat count of 20
9. adding an economic-style metric, **revenue per minute**, based on a fixed per-customer spending assumption
10. adding a `Group 15` startup ASCII banner so the CLI opens with a clearer group identity during demo

## Detailed contribution record

### 1. CLI menu and file-selection redesign

I improved the command-line user experience of `main.py`.

Completed work:

- added automatic discovery of available restaurant settings JSON files
- added automatic discovery of available customer arrival JSON files
- changed the old path-only workflow into a numbered selection workflow
- kept manual path entry as a fallback for new files
- removed `sample_data/` entries from the main menu list so the live demo focuses on the formal case-study files
- simplified file labels in the menu into human-readable names such as `coarse queue`, `few large tables`, `peak hour`, and `uniform large`

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

- comparison mode now asks the user to choose one customer-arrival scenario directly inside comparison mode
- the user can then select multiple restaurant settings in one step
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

### 7. Strategy and seating-layout comparison fairness

I adjusted the case-study settings so the total seat count is more consistent and the comparisons are more defensible.

Completed work:

- normalized the three queue-strategy settings to the same total seating capacity:
  - `2 + 2 + 2 + 4 + 4 + 6 = 20`
- kept `few large tables` at:
  - `4 + 4 + 6 + 6 = 20`
- changed `many small tables` to:
  - `2 + 2 + 2 + 2 + 2 + 2 + 4 + 4 = 20`

This improves fairness by reducing distortion caused by different total seat counts.

### 8. Business-oriented metric improvement

I added a more meaningful performance metric based on a simple economic assumption.

Completed work:

- assumed a fixed spending amount per customer
- implemented **revenue per minute**
- added this metric to:
  - single-run analysis output
  - comparison tables

This helps the project move from a purely operational evaluation toward a more practical efficiency interpretation.

### 9. Demo identity and startup presentation

I also improved the first impression of the CLI by adding a startup banner.

Completed work:

- added a `Group 15` ASCII banner shown when the program starts
- kept the banner lightweight so it improves demo identity without disrupting the menu workflow

This gives the program a cleaner and more recognizable opening for live presentation.

## Files showing my contribution in this stage

- `main.py`
- `app\simulator.py`
- `app\models.py`
- `case_studies\settings_coarse_queue.json`
- `case_studies\settings_single_queue.json`
- `case_studies\settings_size_based.json`
- `case_studies\settings_many_small_tables.json`
- `case_studies\settings_few_large_tables.json`
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
- fairer 20-seat case-study settings
- the new revenue-per-minute metric
- the `Group 15` startup banner
- the associated testing and integration work

This work directly improves how the project is operated, demonstrated, and evaluated.
