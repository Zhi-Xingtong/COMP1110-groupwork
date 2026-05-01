# Invalid Case Study Samples

This folder contains intentionally incompatible JSON examples for documentation, debugging, and viva discussion.

These files are not meant for normal comparison runs. They are designed to fail validation for clear reasons.

## Sample pair 1: table capacity mismatch

- `settings_max_capacity_4.json`
  all walk-in tables have capacity `4` or less
- `arrivals_contains_size_6.json`
  includes a group of size `6`

Expected result:
running this pair should fail because at least one group is larger than every walk-in table.

## Sample pair 2: queue-rule gap

- `settings_missing_size_3_queue.json`
  queue rules allow `1-2` and `4-6`, but not `3`
- `arrivals_size_3_only.json`
  includes a group of size `3`

Expected result:
running this pair should fail because no queue rule matches size `3`.

Use these files when you want to show that the project validates bad inputs instead of silently producing misleading results.
