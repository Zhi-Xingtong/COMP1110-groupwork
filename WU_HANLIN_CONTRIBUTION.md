# Individual Final Report

## Wu Hanlin

UID: 3036528321

## Contribution focus

My contribution in this project is mostly about the data backbone and quality assurance of the restaurant queue simulation system: the JSON file I/O, the user-facing CLI menu, the test cases that verify the simulator under both normal and adversarial inputs, and the organisation of the case-study data pack.

The main goal of my work is to make sure that everything outside the core simulation engine — how data gets in, how the user drives the program, how we verify the program does the right thing, and how the case-study data is organised — is reliable, readable, and reproducible for the TA and for any future reader of the repository.

My contribution covers:

### Coding part

1. writing the JSON loader functions for restaurant settings (tables and queues) and customer arrivals (groups with arrival time, size, dining duration)
2. writing the JSON saver function so simulation results can be persisted to results/ for later inspection and comparison
3. designing graceful error handling for missing files, empty files, malformed JSON, and schema-violation errors so the program never crashes on bad input
4. building the looping six-option text menu in main.py (load settings, load arrivals, run, view, save, exit) with input validation
5. tracking load state in the menu so the program politely refuses to run if either settings or arrivals are not yet loaded
6. writing README.md covering the project overview, file list, JSON schema with annotated examples, run instructions, and test instructions
7. setting up the public GitHub repository, adding all four teammates as collaborators, and maintaining a regular commit cadence throughout the project

### Test & data part

1. writing 6 documented test cases covering normal operation, all-same-group-size, zero customers, oversize group, boundary capacity match, and malformed input
2. recording for each test case the purpose, input files, expected output, and actual output, in a short test-cases document inside the repository
3. building the structured scenario index for the case-study data pack covering all 9 paired scenarios
4. separating the demo / report scenarios (Pairs 01, 02, 07, 08, 09) from the intentionally invalid samples used for negative testing, so a TA cannot accidentally feed a broken file to the simulator
5. writing a companion document for invalid samples that explains, per file, what is wrong and what error message the loader is expected to emit
6. writing reproducibility notes mapping each scenario pair number to its specific input files

## Detailed contribution record

### 1. JSON loader functions for settings and arrivals

I wrote the loader half of app/file_io.py, which is the single entry point for all data coming from disk into the simulator.

Completed work:

• wrote a settings loader that parses tables (capacity, reserved flag) and queues (min / max group-size range)

• wrote an arrivals loader that parses one record per group (group ID, arrival time, group size, dining duration)

• mapped both into the Table, QueueRule, and CustomerGroup classes defined by my teammate (C1) in app/models.py

• enforced field-level validation — non-negative capacities, valid queue ranges, non-negative arrival times and durations

• returned clear field-level error messages when validation fails (for example, "Table T3: capacity must be positive, got -2")

This work decoupled the simulator from the file format. Whenever the JSON schema changed during development, only file_io.py had to change.

### 2. JSON saver function for simulation results

I wrote the saver half of app/file_io.py, which writes the metrics dictionary produced after a simulation run to a results JSON file.

Completed work:

• serialised average and maximum wait time, service level, table utilization, seat utilization, revenue per minute, and average wasted seats into a stable JSON layout

• created the results/ directory automatically if it did not already exist

• preserved scenario context fields (restaurant name, scenario name) inside the saved JSON so a saved result is self-describing later

• pretty-printed the output with indent=2 so a TA could open the result file in any text editor

This work made the saved files inspectable on their own, and allowed the comparison feature (built by my teammate as part of C7) to reload and diff multiple result files later.

### 3. Graceful error handling across file I/O

The grading rubric (Section 3.2 of the project guidelines) explicitly calls out missing files and invalid input values, and our test plan included an explicit malformed-input case (test case 6 in C6). I treated error handling as a first-class part of the loaders, not an afterthought.

Completed work:

• distinguished three error categories: file-not-found (recoverable, return to menu), empty / malformed JSON (recoverable, with a "this file is not valid JSON" message), and schema-violation (recoverable, with a field-level message)

• replaced the original Python tracebacks with short plain-language messages aimed at the user, not the developer

• preserved program state on error so the menu loop continues cleanly instead of leaving half-loaded data in memory

• exposed enough context in each message that the user can locate the offending file and field

This work directly supports test case 6 (Malformed input file) in C6 and made the program much easier to demo, because broken input now produces a one-line explanation instead of a wall of red traceback.

### 4. Looping six-option CLI menu with input validation

I wrote main.py, which is the only entry point users interact with.

Completed work:

• built the looping menu with the six required options: (1) load restaurant settings, (2) load customer arrivals, (3) run simulation, (4) view results, (5) save results, (6) exit

• tracked load state so the menu always knows which settings and arrivals files are currently active

• politely blocked option 3 (run) when settings or arrivals are not loaded, with a one-line message instead of a crash

• input validation for the option choice — letters, empty input, out-of-range numbers all produce a short message and re-prompt rather than crash

This menu is what every demo, every TA review, and every test case touches. It had to be the most stable surface in the project.

### 5. README.md

I wrote README.md from scratch.

Completed work:

• project overview and topic (Restaurant Queue Simulation, Topic C)

• file / module list explaining what each .py does

• JSON input format with one annotated example per file type (settings, arrivals, results)

• how to run: Python version, command line, expected first output

• how to test: how to run each of the six test cases, where the inputs are, what to expect

The README is the first thing a new reader (a TA, a future student) sees. I treated it as a contract — anyone who follows it should be able to reproduce my test cases without asking questions.

### 6. Public GitHub repository setup and maintenance

I set up the public GitHub repository for the group.

Completed work:

• initialised the repo with a sensible directory layout (app/, case_studies/, tests/, results/)

• added a .gitignore excluding __pycache__/, .vscode/, .venv/, and local result outputs

• added all four teammates as collaborators

• committed regularly throughout the project so each milestone is traceable in the history

• wrote informative commit messages so the log is useful, not just a list of "update"s

Repository link: Zhi-Xingtong/COMP1110-groupwork: queue system

### 7. Six documented test cases

I wrote the test cases that verify the file I/O, the simulator, and the metrics under both expected and adversarial conditions.

Completed work:

• Normal operation — mixed-size restaurant, mixed-arrival pattern; verifies end-to-end seating, queue assignment, and metric computation

• All same group size — every group is two pax against a restaurant with mixed table sizes; verifies that size-based queueing routes everyone correctly and that empty queues do not break the simulator

• Zero customers — empty arrivals file; verifies that the simulator reports zero served, zero average wait, and zero utilization rather than dividing by zero or crashing

• Group larger than any table — eight-person group at a restaurant whose largest table seats six; under the explicit no-combining assumption the group is correctly never seated, and the metrics reflect it

• Boundary capacity match — four-person group at a four-seat table; verifies exact-fit seating is allowed and wasted-seat counting reports zero

• Malformed input file — settings JSON missing the capacity field, plus arrivals JSON with negative dining_duration; verifies the loader emits a clear error and returns to the menu without corrupting state

For each case I documented purpose, input files, expected output, actual output, and pass / fail status in a short test-cases document inside the repository.

### 8. Structured scenario index for the case-study data pack

C8 was less about writing code and more about making the data pack usable for everyone else — TAs, teammates writing the case-study analysis (S2), and any group reusing this simulator.

Completed work:

• catalogued all 9 paired scenarios in the data pack

• physically separated demo / report scenarios (Pairs 01, 02, 07, 08, 09 — the five selected for the Group Final Report) from intentionally invalid samples used by C6

• enforced a consistent naming convention pair{N}{A|B}_settings_*.json and pair{N}_arrivals_*.json so any scenario can be located from its pair number

• wrote a short index document (case_studies/INDEX.md) explaining what factor each pair varies (queue strategy, queue granularity, table mix, reservation, turnover, arrival concentration, outlier robustness, peak-vs-quiet demand)

This avoided the awkward situation where a TA accidentally feeds a deliberately broken file into the simulator and concludes the program is buggy.

### 9. Documentation for invalid samples and reproducibility notes

Beyond the index, I wrote two pieces of supporting documentation.

Completed work:

• Invalid-samples doc (case_studies/INVALID_SAMPLES.md) — for each invalid file in the pack, what is wrong with it and what error message the loader is expected to emit

• Reproducibility notes (case_studies/REPRODUCIBILITY.md) — a mapping from each scenario pair number to its specific input files, so any number quoted in the Group Final Report (for example, the 39.83-minute average wait time in Pair 01A, or the 70-minute peak-window max wait in Pair 09B) can be traced back to its input files in the repository

This work was small in line count but valuable for grading: every claim in the Group Final Report is now traceable to a specific pair of input files in the repository.

## Files showing my contribution in this stage

• main.py

• app/file_io.py

• README.md

• .gitignore

• tests/test_project.py

• tests/test_main_helpers.py

• tests/TEST_CASES.md

• case_studies/INDEX.md

• case_studies/INVALID_SAMPLES.md

• case_studies/REPRODUCIBILITY.md

• case_studies/pair01a_settings_single_queue.json

• case_studies/pair01b_settings_size_based.json

• case_studies/pair02a_settings_coarse_queues.json

• case_studies/pair02b_settings_fine_queues.json

• case_studies/pair07_settings_fixed_capacity.json

• case_studies/pair08_settings_single_queue_outlier.json

• case_studies/pair09_settings_reserved_capacity.json

• case_studies/invalid/invalid_01_capacity_missing.json

• case_studies/invalid/invalid_02_capacity_negative.json

• case_studies/invalid/invalid_03_queue_range_reversed.json

• case_studies/invalid/invalid_04_arrival_time_negative.json

• case_studies/invalid/invalid_05_arrival_time_string.json

• case_studies/invalid/invalid_06_json_syntax_error.json

## Why this contribution matters

This contribution makes the project stronger specifically in the areas of:

• data robustness — bad input never crashes the program

• usability — a single, predictable menu drives every feature

• reproducibility — every Group Final Report number is traceable to a specific input file

• testability — six documented cases make regressions easy to catch

• onboarding — a TA can clone the repo and reproduce results from the README alone

Without this round of work, the program could still simulate restaurants, but it would be much harder to operate in front of a TA, much harder to verify, and much harder to defend the case-study numbers as reproducible.

## Short conclusion

My contribution in this project is the data backbone and quality-assurance layer of the simulation system: file I/O, user-facing menu, test cases, and case-study data organisation.

In particular, I contributed:

• the JSON loader and saver functions in app/file_io.py

• graceful error handling across all file I/O

• the six-option looping CLI menu in main.py with input validation

• the project README.md

• the public GitHub repository setup and weekly maintenance

• six documented test cases covering normal and adversarial inputs

• the structured scenario index, invalid-samples documentation, and reproducibility notes for the case-study data pack

This work directly supports how the project is operated, verified, and reproduced.

## Personal Evaluation

I think I performed best on the data layer. The decision to put all error handling behind clear, plain-language messages made the C6 malformed-input case easy to write and made the program much easier to demo — when something is wrong with a file, the user immediately knows which file and which field to fix. One area that could have been better is the speed of locking the JSON schema. Because the schema kept evolving as the simulator's needs grew (a turnover field was added later, the queue-rule format changed slightly), I had to update the loaders, the README, the tests, and the data pack several times. Locking even a draft schema earlier would have saved a meaningful amount of rework.

## Reflection

This project taught me that the boring half of a system — file I/O, error messages, naming conventions, test cases — is what actually decides whether a project can be defended in front of someone else. Writing six test cases against documented expected outputs caught more bugs than I expected, and forced me to be honest about what the simulator is supposed to do under edge conditions. The other lesson is that in a five-person group, decisions made upstream cascade: a schema change in app/models.py ripples into file I/O, the README, the test cases, and the data pack. Locking interfaces early is worth more than it sounds.

## AI report

AI tools used in coding (during the project). I used Claude Sonnet 4.5 (Anthropic, accessed via the Claude web interface to assist with two specific parts of my coding work: (i) drafting the initial structure of the loader functions in app/file_io.py, and (ii) explaining JSON-schema validation patterns when I was deciding how to express field-level error messages. I never let the model commit code directly. My workflow was: state the requirement clearly in plain language; read every line the model suggested; rename variables to match the code style my teammate had established in app/models.py; then run the C6 test cases to confirm the behaviour. I used git for version control so that any AI-generated change that did not feel right could be reverted cleanly. One specific example of modification: an early suggestion used os.path.exists followed by open to handle missing files; I rejected and rewrote that to use try / except FileNotFoundError because the original pattern introduces a TOCTOU race condition.

AI tool used for writing this report. I used Claude Opus 4.7 (Anthropic, May 2026, web interface) to draft the structure and initial text of this Individual Final Report. I supplied the model with: the Group Final Report, the project guidelines, my role assignment (C2 + C5 + C6 + C8 from Group Final Report Part 8), and a teammate's report as a format reference. I then performed a manual hallucination check (per the course instructor's explicit instruction) by cross-referencing every file name, every test case description, every scenario pair number, and every metric value against the actual repository. I replaced all placeholders with my own information, and rewrote the personal-evaluation and reflection sections so the wording matches my own voice.

How I modified, verified, and built on the AI output:

• Hallucination check: verified every file path, class name (Table, CustomerGroup, QueueRule), assumption reference, scenario pair number (Pairs 01, 02, 07, 08, 09), and quoted metric (e.g. the 39.83-min Pair 01A wait time) against the Group Final Report and the live repository.

• Placeholder replacement: filled in GitHub URL, UID, tutorial subclass, the precise dates of AI use, and the personal-feeling sentences in the reflection.

• Voice adjustment: rewrote sections that read too generic in my own phrasing.

• Code verification: for AI-suggested code snippets, I ran each one against my test cases (C6) before committing.

ALL MY PROMPTS: User Prompts Only

## Prompt 1(4/15/2026)

我要写一个 load_settings(filepath) 函数,读 restaurant settings JSON。字段是这样的:tables 是一个 list,每个 table 有 id、capacity、reserved 三个字段;queues 是 list,每个 queue 有 id、min_size、max_size。我希望:(1) 用我们 app/models.py 里已经定义好的 Table 和 QueueRule 类构造对象,不要自己重新定义 dataclass;(2) 字段缺失的时候要 raise 一个清楚的错误,带上是哪个 table/queue 哪个字段;(3) capacity <= 0 或者 max_size < min_size 也要 raise。先帮我写函数骨架,不用完整实现。

## Prompt 2(4/15/2026)

现在我的 load_arrivals 在 JSON 不合法的时候直接把 json.JSONDecodeError 的 traceback 抛给用户看,看起来很丑。我想改成用户看到一句话比如 "File arrivals.json is not valid JSON: line 12 column 3" 然后控制权回到 main.py 的菜单循环。但我又不希望吞掉所有 exception(因为那样真有 bug 我就看不到了)。这种 "包一层 user-facing error,但保留 dev-facing trace" 的 Python 惯用写法是什么?

## Prompt 3(4/15/2026)

我有一个 results 字典,key 包括 avg_wait、max_wait、service_level、table_util、seat_util、revenue_per_min、avg_wasted。我要把它写到 results/{name}.json,但 results/ 文件夹可能还不存在。Python 里最干净的写法是什么?用 pathlib 还是 os.makedirs?

## Prompt 4(4/15/2026)

帮我列出一个 Python CLI 项目的 .gitignore 应该排除什么。我们用 venv、VS Code,有时候本地会跑出 results/*.json,但我们想保留 results/ 文件夹本身在 repo 里(放一个 .gitkeep)。

## Prompt 5(4/15/2026)

I'm writing a looping text menu in main.py with options 1–6 (load settings, load arrivals, run, view, save, exit). I want the menu to (a) show the currently loaded settings file and arrivals file at the top, (b) reject non-numeric input with a one-line message, (c) reject 0 and >6 with a one-line message, (d) re-prompt instead of crashing, (e) refuse "run simulation" if either settings or arrivals is not loaded. Show me a clean structure using a while True loop and small helper functions.

## Prompt 6(4/15/2026)

我要写一份 README.md,读者是 TA 和其他同学。结构要包括:项目概述(餐厅排队模拟,Topic C)、文件结构(app/、case_studies/、tests/、results/)、JSON 输入格式(settings 和 arrivals 各给一个标注好的小例子)、如何运行(python main.py,Python 3.10+)、如何跑测试。请帮我列出一个 markdown skeleton,我自己填具体内容。

## Prompt 7(4/15/2026)

我要写六个 test case:正常、所有一样大小的 group、零顾客、超大 group、边界容量、错误 JSON。我们组比较少人懂 pytest,我想直接写一个不依赖框架的 tests/test_project.py,用 assert + print 就行,跑的时候 python tests/test_project.py 直接执行。这种写法在大学项目里专业吗?如果不,有没有更轻量的中间方案?

## Prompt 8(4/15/2026)

如果 arrivals 是空 list,模拟器跑出来的 average wait 应该是 0 还是 None?哪种从语义上更合理?对 service_level 这种百分比指标呢——没有顾客,百分比怎么定义?给我一个建议加 justification。

## Prompt 9(4/18/2026)

For my "group larger than any table" test case: under our no-combining assumption, an 8-pax group at a restaurant with no 8-seat table will never be seated. What should the simulator do at the end of the simulation? Options I see: (a) leave the group in the queue, max_wait shoots up, count it in unserved; (b) drop it from arrivals at validation time. Which one better honours the principle "the model should honour its own assumptions"?

## Prompt 10(4/18/2026)

我现在 case_studies/ 文件夹里 9 对 scenario JSON,加上 6 个 invalid sample,全部混在一起,看起来很乱。我想:(1) 把 invalid 的放到 case_studies/invalid/ 子目录;(2) 写一个 INDEX.md 把 9 对 pair 列成表格,每对一行,标注它在变什么变量(queue 策略、granularity、table mix、reservation、turnover、arrival 集中度、outlier、peak vs quiet)。请帮我设计 INDEX.md 的表格列。

## Prompt 11(4/18/2026)

帮我命名 invalid sample 文件。当前我有六种错误:capacity 缺字段、capacity 负数、queue 范围反了(max < min)、arrival 时间负数、arrival 时间是字符串、整个 JSON 语法错。我想用 invalid_{NN}_{short_reason}.json 格式,short_reason 用英文短词。给我六个名字。

## Prompt 12(4/18/2026)

为每一个 invalid sample 写一行 expected error message 的描述,放在 INVALID_SAMPLES.md 里。我希望读者看到 "invalid_03_queue_range_reversed.json" 就能立刻知道:这个文件触发什么错误,错误信息看起来是怎样的。给我一个 markdown table 模板。

## Prompt 13(4/18/2026)

我要写 REPRODUCIBILITY.md,把 Group Final Report 里引用到的具体数字(比如 Pair 01A 的 39.83 分钟 average wait,Pair 09B 的 70 分钟 max wait)和具体的 input file 对应起来。给我一个表格 schema:scenario pair → settings file → arrivals file → key metrics from group report。让任何人能从一行表里直接重跑那个数字。

## Prompt 14(4/18/2026)

我在 group report 里看到我们引用了 "Pair 09B 的 70 分钟 max wait time"。我跑了 pair09_settings_reserved_capacity.json + pair09b_arrivals_peak_window.json,但跑出来是 71 分钟不是 70。差 1 分钟,有可能是哪里 round 不一致?我应该改 group report 的数字还是查代码?

## Prompt 15(4/18/2026)

帮我 review 这份 Individual Final Report 草稿,重点看三件事:(1) 每个文件名是不是都跟我 repo 里实际存在的对得上;(2) 有没有声称做了某件事但 Group Final Report Part 8 role assignment 里其实没分给我的;(3) AI report 部分写得是否完整(工具名 + 版本 + prompt + verification 四个要素都有)。
