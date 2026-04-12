---
description: Extract the total expense in NZD from a PDF invoice. Dispatches the expense-extractor subagent, writes a sidecar JSON next to the PDF, and prints a short summary.
argument-hint: <path-to-pdf>
---

# Extract Expense from Invoice

Your job is to extract the total expense in NZD from the PDF invoice at `$ARGUMENTS` using the `expense-extractor` subagent, then write the result as a sidecar JSON file and print a short human summary.

## Context

- The authoritative specification for this command lives at `docs/superpowers/specs/2026-04-09-extract-expense-design.md`. If anything below is unclear, defer to the spec.
- The `expense-extractor` subagent (in `.claude/agents/expense-extractor.md`) is the only component that reads the PDF. You do not read the PDF yourself — delegating to the subagent keeps the invoice content out of the main conversation context.
- Every NZD figure in the output must be traceable to a printed number on the source PDF. Neither you nor the subagent may perform currency conversion.

## Steps

### 1. Validate the input

- `$ARGUMENTS` should be a path to a PDF file. If it is empty, tell the user the command needs a path and stop.
- Use `Bash` with `ls -la "<path>"` to confirm the file exists. If it does not, report the missing path and stop — do not dispatch the subagent.
- Confirm the path ends in `.pdf` (case-insensitive). If not, report and stop.
- Resolve the path to an absolute form using `Bash` (`realpath` or equivalent) so the subagent receives an unambiguous path.

### 2. Dispatch the subagent

- Use the `Agent` tool with `subagent_type: "expense-extractor"`.
- Pass the absolute PDF path in the prompt. Example prompt body:
  > "Extract the expense from this invoice and return the JSON result per your instructions. PDF path: `<absolute-path>`"
- The subagent returns a single JSON object. Do not add any additional instructions that would cause it to return prose.

### 3. Parse and validate the result

- The subagent's response must be parseable as JSON. If it is not, print the raw response, tell the user the extractor returned malformed output, and stop. Do not write a sidecar.
- Verify the top-level keys match the schema in the spec: `status`, `confidence`, `nzd_amount`, `nzd_source`, `original`, `invoice`, `source_file`, `notes`. If any required key is missing, treat it as a malformed result (as above).

### 4. Write the sidecar JSON

- Compute the sidecar path: same directory as the input PDF, same stem, extension `.extracted.json`. For example, `expenses/INV001-Expenses.pdf` → `expenses/INV001-Expenses.extracted.json`.
- Use `Write` to save the JSON pretty-printed (2-space indentation) to the sidecar path. Overwrite if it already exists — stale sidecars are worse than fresh ones.

### 5. Print the human summary

Print a short summary to the chat. Format:

**High confidence:**

```
✓ <filename> — <vendor> (<date>)
  Expense: NZD <amount>  [high confidence, <nzd_source>]
  Original: <original.amount> <original.currency>
  Note: <first note, if any>
  Saved: <sidecar-path>
```

**Low confidence:**

```
⚠ <filename> — <vendor or "vendor unclear"> (<date or "date unclear">)
  Expense: <NZD amount or "not in NZD">  [low confidence]
  Original: <original.amount> <original.currency>
  Issues:
    - <each note on its own line>
  Saved: <sidecar-path>
```

Use the file's basename (not the full path) on the first line. Use the exact path the user gave for `Saved:`.

## Guardrails

- Do not read the PDF yourself. That is the subagent's job and keeps the main context clean.
- Do not compute or look up an exchange rate under any circumstances. If the subagent reports `nzd_source: "none"`, the human summary must say "not in NZD" and the user will handle it from their bank statement.
- Do not silently swallow malformed subagent output. If the JSON is broken, surface the raw response so it can be diagnosed.
- Do not delete or modify the source PDF.
