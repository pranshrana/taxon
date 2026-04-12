# CLAUDE.md

Guidance for Claude Code when working in this repo.

## What this is

A personal workflow that fills out **IR10 (Financial Statements Summary)** forms for **Inland Revenue New Zealand** from source financial data (invoice PDFs, crypto tax reports, bank statements). Built for the owner's own annual filing, not for distribution.

## Pipeline shape

Orchestration lives at the top level in `.claude/commands/ir10-fill.md` — subagents in Claude Code cannot dispatch other subagents, so the command drives everything and dispatches four leaf agents:

- `expense-extractor` — reads one invoice PDF, returns NZD total + category hint. Never converts currencies.
- `koinly-analyzer` — reads a Koinly crypto tax report PDF, returns gains / income / EOY holdings.
- `tax-form-expert` — consumes the consolidated context and writes a 3-sheet IR10 workbook.
- `ir10-reviewer` — validates the workbook against the template spec and the context.

The authoritative layout spec is `guides/IR10_TEMPLATE_STRUCTURE.md` — 3 sheets (`IR10`, `Expenses`, `Depreciation`), SUMIF-driven, with a straight-line depreciation schedule. Both `tax-form-expert` and `ir10-reviewer` read it as their source of truth. Box semantics live in `guides/IR10_CONTEXT.md`.

## Working preferences

- **Read the reference first.** Before changing the template or box mapping, read `guides/IR10_TEMPLATE_STRUCTURE.md` and any reference xlsx the user has added. Don't invent field lists.
- **Prefer Claude Code native features** (slash commands, subagents, skills, hooks) over standalone scripts when both would work. Add them only when a concrete task justifies it.
- **Ask before heavyweight dependencies.** Stdlib + `openpyxl` has been enough so far.
- **Auditability is non-negotiable.** Every NZD figure on the final IR10 must trace back to a printed number on a source PDF or a user override. Never compute FX conversions. Never silently fill a box from memory or guessing.
- **Confirm the IR10 form version** with the user before hard-coding field names — IRD updates the form periodically.

## Domain quick reference (IR10)

- Summary of financial statements filed alongside an income tax return (IR3 / IR4 / IR6 / IR7).
- Boxes 2–11 = income, 12–25 = expenses, 26–29 = profit/tax, 30–43 = assets, 44–51 = liabilities/equity, 52–59 = disclosures.
- Boxes 28, 29, 52, 59 are *tax* figures; everything else is accounting.
- Low-value asset threshold: **$1,000** (since 17 March 2021). Assets above that are capitalised and depreciated; below can be expensed immediately.
- Koinly crypto reports typically map: `income_summary_total` → Box 2, `capital_gains_net + other_gains_net` → Box 28, `end_of_year_balances.total_value` → Box 39 (Intangibles).

## Conventions

- Filename `*-Depreciation.pdf` in the expenses folder is treated as a capital item (goes to the Depreciation sheet), not an expense.
- Filename containing `koinly` (case-insensitive) is routed to `koinly-analyzer`.
- Expense extractor output drops a `.extracted.json` sidecar next to the source PDF.
- Consolidated context is written to `<expenses_folder>/ir10-context.json`.
- Final output is `<expenses_folder>/IR10-filled.xlsx`.
