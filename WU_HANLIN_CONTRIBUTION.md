# Wu Hanlin Contribution Statement

## Identity

Member name: Wu Hanlin

According to the group task allocation, my assigned coding responsibilities were:

- `C2` File I/O
- `C5` Text menu, README, and GitHub support materials
- `C6` Test cases
- `C8` Scenario data quality and reproducibility support

## Contribution focus

My contribution focused on the **program support layer** around the simulation engine.

I did not mainly work on the core simulation algorithm, data model, or metric formulas. Those parts belong to the engine layer. My role was to make the project usable, testable, and understandable as a complete submitted program.

The main purpose of my work was to connect the core simulation with practical project use:

- users can load restaurant settings and customer arrivals from JSON files
- users can run the program through a text menu instead of calling functions manually
- users can save simulation results for later checking and report writing
- the repository has clear instructions and example data
- the implementation is supported by repeatable automated tests
- scenario files are organised and documented so report results can be reproduced

This contribution is different from later demo refinements. My work established the basic file workflow, menu workflow, documentation base, sample data, and testing coverage needed for the project to run reliably.

## C2: File I/O

Implemented mainly in `app/file_io.py`.

For this part, I created the file input and output functions used by the rest of the program.

My work included:

- implementing JSON reading for restaurant setting files
- implementing JSON reading for customer arrival files
- converting JSON data into the project model objects used by the simulator
- supporting optional fields such as turnover duration and reserved tables
- saving simulation results back into a JSON file
- adding error handling for missing files, empty files, invalid JSON, and incorrect top-level JSON structures

This part is important because it separates external data files from the simulation code. It means the project can run many different scenarios without changing Python code each time.

For my individual report, this part can be explained as the bridge between user-provided data and the internal simulation model.

## C5: Text menu, README, and project support materials

Implemented mainly in `main.py`, `README.md`, `sample_data/`, and part of `case_studies/`.

For the text interface, I contributed the basic command-line workflow that lets a user operate the project directly.

My work included:

- building the menu structure for loading settings, loading arrivals, running the simulation, viewing results, saving results, and exiting
- connecting menu options with the file I/O functions and the simulation engine
- checking whether required inputs had been loaded before running the simulation
- displaying clear messages when files or inputs were invalid
- supporting result export through the menu

For the documentation and support files, I helped make the repository easier to understand and assess.

My work included:

- writing the README structure for project overview, file structure, running instructions, input format, output metrics, and test instructions
- preparing sample JSON files for quick testing
- adding supporting case-study files that can be used for demonstration and report discussion
- keeping file names and folder structure understandable for future use

This C5 work provides the basic user-facing layer of the project. Later refinements to the demo interface, comparison display, status area, and presentation polish are separate from my main contribution.

## C6: Test cases

Implemented mainly in `tests/test_project.py`.

For this part, I wrote and extended tests to check that the project works across normal, boundary, and error cases.

My work included tests for:

- normal simulation operation
- multiple groups with the same group size
- zero-customer input
- a group that is larger than any available table
- capacity boundary matching, such as a group of 2 using a 2-seat table
- invalid JSON input
- loading restaurant settings and arrivals from JSON files
- saving simulation results as JSON
- running case-study data through the simulation

The purpose of these tests is not only to check one output value. They also show that the file I/O layer, simulator call, and result-saving workflow can work together as an end-to-end program.

For my individual report, this part can be explained as verification work: I tested both the expected workflow and the failure cases that a user may encounter.

## C8: Scenario data quality and reproducibility support

Implemented mainly in `case_studies/SCENARIO_INDEX.md`, `case_studies/README.md`, and `case_studies/invalid_samples/`.

This part does not change the original simulation logic or the CLI workflow. It supports the project by making the data pack easier to inspect, reproduce, and explain.

My work included:

- organising the case-study files so each pair has a clear fixed input and changed factor
- documenting which scenario files belong together
- separating normal demo/report scenarios from intentionally invalid robustness examples
- adding report-oriented notes so the same scenario pairs can be reused consistently in the final report
- supporting validation discussion through invalid examples such as capacity mismatch and missing queue-rule coverage

This C8 work is different from Zhao Zihao's `C7` work. C7 improves the user interface, navigation, display tables, comparison highlighting, and result-saving experience. C8 focuses on data quality, scenario traceability, and reproducibility, without changing how the program runs.

## Contribution boundary with teammates

To avoid overlap, my contribution should be understood within these boundaries:

- I was responsible for `C2`, so I can discuss JSON loading, JSON saving, file validation, and how external data enters or leaves the program.
- I was responsible for `C5`, so I can discuss the basic menu workflow, README instructions, sample data, and project support materials.
- I was responsible for `C6`, so I can discuss the automated tests and how they verify important scenarios.
- I was responsible for `C8`, so I can discuss data-pack organisation, scenario indexing, invalid sample documentation, and reproducibility support.
- I should not claim the main data model, event-driven simulation algorithm, seating logic, or metric formulas as my own core work.
- I should not claim the later final-stage CLI polish, comparison-table redesign, persistent status display, revenue-per-minute feature, or demo banner as my main work.

This boundary keeps my contribution clear and avoids repeating the work described by other group members.

## Files that show my contribution

The files most directly related to my contribution are:

- `app/file_io.py`
- `main.py`
- `README.md`
- `sample_data/restaurant_settings.json`
- `sample_data/customer_arrivals.json`
- `case_studies/SCENARIO_INDEX.md`
- `case_studies/README.md`
- `case_studies/invalid_samples/README.md`
- `tests/test_project.py`
- `WU_HANLIN_CONTRIBUTION.md`

Supporting files that also connect to my work:

- `case_studies/README.md`
- `case_studies/*.json`

The case-study files should be described carefully in my report. I can mention that I helped provide data support for testing, demonstration, and report discussion, but I should avoid claiming all scenario design decisions if they overlap with teammates' contribution statements.

## Individual report notes

For the individual report, my contribution can be organised in this order:

1. Explain the problem my part solved: the simulator needed external data loading, user operation, output saving, documentation, and tests.
2. Explain `C2`: how JSON settings and arrivals are loaded, validated, converted, and saved.
3. Explain `C5`: how the command-line menu and README made the project usable by tutors and group members.
4. Explain `C6`: how tests covered normal operation, edge cases, error handling, and integration between files and simulation.
5. Explain `C8`: how the case-study data pack was organised and documented for reproducible report use.
6. Explain my boundary: I supported the complete program around the engine, while the core simulation algorithm and later demo polish were handled separately.

## Short conclusion

My contribution made the project complete from a practical user and submission perspective.

Through `C2`, `C5`, `C6`, and `C8`, I helped turn the simulation engine into a runnable, documented, data-driven, reproducible, and testable program. This work supports the rest of the group by making the system easier to operate, verify, demonstrate, and explain in the final report.
