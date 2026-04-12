---
description: Fill an IR10 Financial Statements Summary from a folder of expense PDFs. Runs the full pipeline inline at the top level so it can dispatch leaf subagents.
argument-hint: <expenses-folder> [--template <path-to-excel>]
---

# Fill IR10 from Expense PDFs

You orchestrate the full IR10 pipeline from the top level of the session. Subagents cannot dispatch other subagents, so this command must not be delegated — do the work yourself. You dispatch four leaf subagents: `expense-extractor`, `koinly-analyzer`, `tax-form-expert`, `ir10-reviewer`.

## Guardrails

- Do NOT read PDFs yourself — only the extraction subagents do that.
- Do NOT read `IR10_CONTEXT.md` or `IR10_TEMPLATE_STRUCTURE.md` yourself except for what's strictly needed to verify things; pass the paths to subagents.
- Do NOT invent NZD amounts — only relay values from extractors or user overrides.
- Do NOT proceed to Stage 2 if Stage 1 has unresolved issues.

---

## PRE-FLIGHT

### P.1 — Parse `$ARGUMENTS`

Split on `--template`. Left side = expenses folder (required). Right side = template xlsx path (optional). Trim quotes and whitespace.

### P.2 — Validate inputs

**Expenses folder**:
- Use `Bash` (`ls -la "<path>"`) to confirm it exists and is a directory.
- `Glob` `*.pdf` (non-recursive). Stop if zero.
- If the user-provided path has no PDFs but contains an `expenses/` subfolder with PDFs, use the subfolder and tell the user.
- Resolve to absolute path via `realpath`.

**Template** (if provided):
- Must end in `.xlsx` (case-insensitive).
- Must exist. Resolve absolute path.

### P.3 — Classify PDFs

Each PDF:
- Filename contains `koinly` (case-insensitive) → **koinly** (dispatch `koinly-analyzer`).
- Filename contains `depreciation` (case-insensitive) → **capital** (dispatch `expense-extractor`, but it will be treated as a capital asset in Stage 1.5).
- Otherwise → **expense** (dispatch `expense-extractor`).

### P.4 — Collect taxpayer identity

Prompt the user via `AskUserQuestion` for **Taxpayer name** and **IRD number** (two separate questions in one call). Do not reuse stored identity — prompt every run. Keep these for the context.

### P.5 — Pre-flight summary

Print:

```
IR10 Fill — scanning <folder>
  Taxpayer: <name> (IRD <number>)
  Found N PDFs:
    - filename.pdf → expense-extractor
    - filename.pdf → koinly-analyzer
    - filename-Depreciation.pdf → expense-extractor (capital item)
  Template: <path> | none — will create from scratch
  Template spec: guides/IR10_TEMPLATE_STRUCTURE.md
  IR10 Guide:    guides/IR10_CONTEXT.md
```

Resolve `template_structure_path` and `ir10_guide_path` to absolute paths.

---

## STAGE 1: Extraction

### 1.1 — Dispatch extractors in parallel

For each classified PDF, dispatch via `Agent`:
- **koinly** → `subagent_type: "koinly-analyzer"`, prompt `"Analyze this Koinly tax report and return the JSON result per your instructions. PDF path: <abs>"`.
- **expense** or **capital** → `subagent_type: "expense-extractor"`, prompt `"Extract the expense from this invoice and return the JSON result per your instructions. PDF path: <abs>"`.

Include every dispatch in a single message so they run in parallel.

### 1.2 — Process each result

- Parse JSON. If it fails, record an issue with problem `"Subagent returned malformed JSON"` (first 500 chars) and move on — don't attempt to fix.
- Write a sidecar `<stem>.extracted.json` next to the source PDF with the parsed JSON (pretty-printed).
- Classify:
  - **Clean**: `status == "ok"` AND `confidence == "high"`.
  - **Issue**: anything else.

### 1.3 — Build context skeleton

Build the following in memory:

```json
{
  "taxpayer": { "name": "...", "ird_number": "..." },
  "balance_date": "<YYYY-03-31 for the relevant NZ tax year — infer from Koinly period_end or ask the user>",
  "extraction_status": "clean" | "has_issues",
  "expenses": [],
  "capital_items": [],
  "koinly_reports": [],
  "issues": [],
  "user_overrides": []
}
```

For each parsed extraction result:
- **capital** classification → goes to `capital_items` (regardless of extraction status). Convert the extractor's JSON into a capital item shape: fill `date_acquired`, `opening_amount` (from `nzd_amount`), `invoice`, and leave `depreciation_rate` and `ir10_box` **unset** — the user must provide them in Stage 1.4.
- **expense** classification → goes to `expenses`. Copy `suggested_ir10_category` into `result.ir10_category` as a default.
- **koinly** classification → goes to `koinly_reports`.

### 1.4 — Resolve issues and missing data (single batched prompt where possible)

Collect all pending questions and ask them together via `AskUserQuestion` (max 4 questions per call — split into multiple calls if needed):

1. **Low-confidence or missing NZD extractions** — for each issue, show original amount + currency, ask for the NZD amount from the bank statement, or `skip`.
2. **Expense category confirmation** — for each `expenses[*]` entry, show the auto-classified `ir10_category` and offer options: keep the suggestion, or pick another from the fixed list. Batch aggressively: if many invoices share the same suggested category and vendor, ask a single question covering them as a group.
3. **Capital item details** — for each `capital_items[*]` entry, ask for:
   - `depreciation_rate` — point the user at `https://myir.ird.govt.nz/tools/_/` (IRD depreciation rate lookup) in the question text so they can look up the correct rate for the asset.
   - `ir10_box` — which fixed-assets box: 33 Vehicles, 34 Plant and machinery, 35 Furniture and fittings, 36 Land, 37 Buildings, 38 Other fixed assets.
   Default suggestion: computer/laptop/monitor → 34 Plant and machinery; vehicles → 33; desks/chairs → 35.
4. **Balance date** if not inferable from Koinly — ask for the financial year end (usually `YYYY-03-31`).

Apply all answers to the context. Move resolved issues off `issues` and into `user_overrides` where applicable. Drop `skip`-ped items.

### 1.5 — Gate check

- If all extractions failed or were skipped, stop.
- If any issues remain unresolved, stop.
- Otherwise set `extraction_status = "clean"` and proceed.

---

## STAGE 2: Fill and review

### 2.1 — Write consolidated context

Write the full context object to `<expenses_folder>/ir10-context.json` (pretty-printed).

### 2.2 — Dispatch `tax-form-expert`

Output path: `<expenses_folder>/IR10-filled.xlsx`.

Dispatch `tax-form-expert` with:
- `context_json_path`: the file you just wrote.
- `template_structure_path`: absolute path to `guides/IR10_TEMPLATE_STRUCTURE.md`.
- `ir10_guide_path`: absolute path to `guides/IR10_CONTEXT.md`.
- `output_path`: the output xlsx.

Parse the JSON response.
- `status == "error"`: report to user, stop.
- `status == "ok"`: proceed.

### 2.3 — Dispatch `ir10-reviewer`

Dispatch with:
- `excel_path`: the output xlsx.
- `template_structure_path`: absolute path to `IR10_TEMPLATE_STRUCTURE.md`.
- `consolidated_context_json`: full context JSON inline.

Parse the JSON response.

### 2.4 — Handle review (max 3 iterations)

- `status == "pass"`: print any warnings as informational, proceed to 2.5.
- `status == "fail"`:
  - Split into `auto_fixable` and `non_auto_fixable`.
  - `auto_fixable`: re-dispatch `tax-form-expert` with a corrections note; then re-review.
  - `non_auto_fixable`: ask the user, apply overrides, re-dispatch, re-review.
  - After 3 iterations with unresolved errors, print them all and stop.

### 2.5 — Final output

Print the summary:

```
IR10 Workflow Complete

Excel file: <absolute path>
Taxpayer:   <name> (IRD <number>)

Sheet: IR10
  Box <N> — <label>: <value|formula> (source: <files>)
  ...

Sheet: Expenses (<count> rows)
  Total: <sum of Amount column>

Sheet: Depreciation (<count> rows)
  Total Depreciation EOY: <H total>
  Total Closing:          <I total>

Review status: <pass | pass with warnings | fail after max iterations>
<any remaining warnings listed here>
```

Use `boxes_filled` / `boxes_user_to_provide` from the `tax-form-expert` response to populate the box section.
