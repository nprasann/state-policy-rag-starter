---
name: safe-refactoring
description: Use when restructuring code while preserving behavior.
---

## When to Use
Use this skill when the task involves:
- Cleaning up code
- Extracting services/interfaces
- Renaming files/classes/functions
- Reducing duplication
- Improving layering
- Separating concerns
- Preparing code for future features

## Goal
Improve maintainability without changing behavior unless explicitly requested.

## Refactoring Workflow
1. Inspect the relevant files.
2. Identify current behavior.
3. State the refactor plan before editing.
4. Make the smallest safe change.
5. Avoid unrelated formatting churn.
6. Run or describe validation.
7. Summarize behavior-preserving changes.

## Rules
- Do not rewrite entire modules unless necessary.
- Do not introduce new dependencies unless justified.
- Do not change public APIs unless requested.
- Do not remove existing functionality.
- Do not mix refactoring with new features unless explicitly asked.
- Preserve configuration names and environment variable names unless asked to change them.
- Keep commits/PRs focused.

## Good Refactor Targets
- Duplicate logic
- Large functions
- Mixed API/business/data-access logic
- Hardcoded configuration
- Poorly named functions
- Missing interfaces around external dependencies
- Weak error handling

## Avoid
- Cosmetic-only changes across many files
- Renaming without value
- Premature abstraction
- Framework rewrites
- Large folder restructuring without tests

## Validation
Use the best available validation:
- Existing test suite
- Targeted unit tests
- Integration smoke test
- Local run command
- Manual API call
- Static analysis/linting

If tests do not exist, recommend the smallest useful test before or after refactor.

## Output Expectations
When completing a refactor, report:
- What behavior was preserved
- What structure changed
- Files modified
- Tests/checks run
- Risks or follow-up work
