---
description: Analyze a Koinly crypto tax report PDF. Dispatches the koinly-analyzer subagent, writes a sidecar JSON next to the PDF, and prints a short summary.
argument-hint: <path-to-koinly-pdf>
---

# Analyze Koinly Tax Report

Your job is to extract the summary totals and end-of-year holdings from the Koinly tax report PDF at `$ARGUMENTS` using the `koinly-analyzer` subagent, then write the result as a sidecar JSON file and print a short human summary.

## Context

- The authoritative specification for this command lives at `docs/superpowers/specs/2026-04-10-analyze-koinly-design.md`. If anything below is unclear, defer to the spec.
- The `koinly-analyzer` subagent (in `.claude/agents/koinly-analyzer.md`) is the only component that reads the PDF. You do not read the PDF yourself — delegating to the subagent keeps the 25+ page report out of the main conversation context.
- Every NZD figure in the output must be traceable to a printed number on the source PDF. Neither you nor the subagent may infer, convert, or compute numbers — with the single exception of `income.gains_total`, which is defined as `capital_gains_net + other_gains_net` (both are printed NZD figures from the same document).

## Steps

### 1. Validate the input

- `$ARGUMENTS` should be a path to a PDF file. If it is empty, tell the user the command needs a path and stop.
- Use `Bash` with `ls -la "<path>"` to confirm the file exists. If it does not, report the missing path and stop — do not dispatch the subagent.
- Confirm the path ends in `.pdf` (case-insensitive). If not, report and stop.
- Resolve the path to an absolute form using `Bash` (`realpath` or equivalent) so the subagent receives an unambiguous path.

### 2. Dispatch the subagent

- Use the `Agent` tool with `subagent_type: "koinly-analyzer"`.
- Pass the absolute PDF path in the prompt. Example prompt body:
  > "Analyze this Koinly tax report and return the JSON result per your instructions. PDF path: `<absolute-path>`"
- The subagent returns a single JSON object. Do not add any additional instructions that would cause it to return prose.

### 3. Parse and validate the result

- The subagent's response must be parseable as JSON. If it is not, print the raw response, tell the user the analyzer returned malformed output, and stop. Do not write a sidecar.
- Verify the top-level keys match the schema in the spec: `status`, `confidence`, `report`, `income`, `expenses`, `end_of_year_balances`, `source_file`, `notes`. Also verify required nested keys: `income.capital_gains_net`, `income.other_gains_net`, `income.gains_total`, `income.income_summary_total`, `expenses.total`, `end_of_year_balances.total_cost`, `end_of_year_balances.total_value`, `end_of_year_balances.assets`. If any required key is missing, treat it as a malformed result (as above).

### 4. Write the sidecar JSON

- Compute the sidecar path: same directory as the input PDF, same stem, extension `.extracted.json`. For example, `expenses/INV003(Koinly Tax Report 2025).pdf` → `expenses/INV003(Koinly Tax Report 2025).extracted.json`.
- Use `Write` to save the JSON pretty-printed (2-space indentation) to the sidecar path. Overwrite if it already exists — stale sidecars are worse than fresh ones.

### 5. Print the human summary

Print a short summary to the chat. Use the file's basename (not the full path) on the first line. Use the exact path the user gave for `Saved:`. Values that could not be parsed show as `—`.

**High confidence:**

```
✓ <filename> — Koinly Tax Report (<tax_year>, <period_start> → <period_end>)
  Income:
    Capital gains net:    NZD <n>
    Other gains net:      NZD <n>
    Gains total:          NZD <n>    (computed)
    Income summary total: NZD <n>
  Expenses total:         NZD <n>
  End of year balances:
    Total cost:           NZD <n>
    Total value:          NZD <n>
    Holdings:             <count> assets
  Saved: <sidecar-path>
```

**Low confidence:**

```
⚠ <filename> — Koinly Tax Report (<tax_year or "period unclear">)
  Income:
    Capital gains net:    <NZD n or —>
    Other gains net:      <NZD n or —>
    Gains total:          <NZD n or —>
    Income summary total: <NZD n or —>
  Expenses total:         <NZD n or —>
  End of year balances:
    Total cost:           <NZD n or —>
    Total value:          <NZD n or —>
    Holdings:             <count or —> assets
  Issues:
    - <each note on its own line>
  Saved: <sidecar-path>
```

## Guardrails

- Do not read the PDF yourself. That is the subagent's job and keeps the main context clean.
- Do not compute, infer, or look up numeric values under any circumstances. The only permitted computation is the subagent's own `gains_total = capital_gains_net + other_gains_net`, and that happens inside the subagent.
- Do not silently swallow malformed subagent output. If the JSON is broken, surface the raw response so it can be diagnosed.
- Do not delete or modify the source PDF.
