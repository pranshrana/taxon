# IR10 Workbook Template Structure

This file is the **authoritative spec** for the IR10 Excel workbook. `tax-form-expert` writes files that conform to it; `ir10-reviewer` validates against it. Any deviation from this spec is a failure.

The template is a 3-sheet workbook. The IR10 sheet contains no hard-coded line-item values — everything except header, Koinly figures, and box 28 is a formula referencing the `Expenses` and `Depreciation` sheets. This keeps the form auditable: every number traces back to a row on a supporting sheet.

---

## Sheet 1: `IR10`

Visible layout (matches IRD form). Columns: A = group heading, B = line label, C = box number, D = value/formula, E = notes, F = reference URL.

### Header rows
| Cell | Value |
|---|---|
| A1 | `IR10` |
| B1 | `Financial statements summary` |
| F1 | IR10 form URL (from `guides/IR10_CONTEXT.md`) |
| F2 | IR10G guide URL |
| A4 | `Your full name` |
| B4 | **taxpayer name** (from context) |
| A5 | `Your IRD Number` |
| B5 | **taxpayer IRD number** (from context) |
| C6 | `Box` |
| E6 | `Notes` |
| F6 | `Reference` |

### Box rows (row ↔ box number)

| Row | A (group) | B (label) | C (box) | D (value/formula) |
|---|---|---|---|---|
| 8 | `Multiple activity indicator` | — | 1 | `"No"` or `"Yes"` |
| 10 | `Profit and loss statement` | — | — | — |
| 12 | `Gross income from` | `Sales and/or services` | 2 | literal (e.g. Koinly income summary total) |
| 14 | `Cost of goods sold` | `Opening stock (include work in progress)` | 3 | 0 |
| 15 | — | `Purchases` | 4 | 0 |
| 16 | — | `Closing stock (include work in progress)` | 5 | 0 |
| 18 | `Gross profit` | `(if a loss, put a minus sign in the last box)` | 6 | `=D12-D14+D15-D16` |
| 20 | `Other gross income` | `Interest received` | 7 | 0 |
| 21 | — | `Dividends received` | 8 | 0 |
| 22 | — | `Rental, lease and licence income` | 9 | 0 |
| 23 | — | `Other income` | 10 | 0 |
| 25 | `Total income` | `Add up all income entered in Boxes 6 to 10` | 11 | `=SUM(D18:D23)` |
| 27 | `Expenses (as per financial statements)` | `Bad debts` | 12 | `=SUMIF(Expenses!F:F,B27,Expenses!E:E)` |
| 28 | — | `Accounting depreciation and amortisation` | 13 | `=SUMIF(Expenses!F:F,B28,Expenses!E:E)+SUM(Depreciation!H3:H<dep_last>)` |
| 29 | — | `Insurance (exclude ACC levies)` | 14 | `=SUMIF(Expenses!F:F,B29,Expenses!E:E)` |
| 30 | — | `Interest expense` | 15 | `=SUMIF(Expenses!F:F,B30,Expenses!E:E)` |
| 31 | — | `Professional and consulting fees` | 16 | `=SUMIF(Expenses!F:F,B31,Expenses!E:E)` |
| 32 | — | `Rates` | 17 | `=SUMIF(Expenses!F:F,B32,Expenses!E:E)` |
| 33 | — | `Rental, lease and licence payments` | 18 | `=SUMIF(Expenses!F:F,B33,Expenses!E:E)` |
| 34 | — | `Repairs and maintenance` | 19 | `=SUMIF(Expenses!F:F,B34,Expenses!E:E)` |
| 35 | — | `Research and development` | 20 | `=SUMIF(Expenses!F:F,B35,Expenses!E:E)` |
| 36 | — | `Associated persons' remuneration` | 21 | `=SUMIF(Expenses!F:F,B36,Expenses!E:E)` |
| 37 | — | `Salaries and wages paid to employees` | 22 | `=SUMIF(Expenses!F:F,B37,Expenses!E:E)` |
| 38 | — | `Contractor and sub-contractor payments` | 23 | `=SUMIF(Expenses!F:F,B38,Expenses!E:E)` |
| 39 | — | `Other expenses` | 24 | `=SUMIF(Expenses!F:F,B39,Expenses!E:E)` |
| 41 | `Total expenses` | `Add up all expenses entered in Boxes 12 to 24` | 25 | `=SUM(D27:D39)` |
| 43 | `Exceptional items` | `(if there is a negative amount, put a minus sign in the last box)` | 26 | 0 |
| 45 | `Net profit/loss before tax` | `Box 11 less Box 25, add Box 26` | 27 | `=D25-D41+D43` |
| 47 | `Tax adjustments` | `(if there is a negative amount, put a minus sign in the last box)` | 28 | **literal formula** built from Koinly: `=<capital_gains_net>+<other_gains_net>` (the `+` preserves the sign of the negative other-gains value) |
| 49 | `Current year taxable profit/loss` | — | 29 | `=D45+D47` |
| 51 | `Balance sheet items` | — | — | — |
| 53 | `Current assets (as at balance date)` | `Accounts receivable (debtors)` | 30 | 0 |
| 54 | — | `Cash and deposits` | 31 | 0 |
| 55 | — | `Other current assets` | 32 | 0 |
| 57 | `Fixed assets (closing accounting value)` | `Vehicles` | 33 | `=SUMIF(Depreciation!J:J,33,Depreciation!I:I)` |
| 58 | — | `Plant and machinery` | 34 | `=SUMIF(Depreciation!J:J,34,Depreciation!I:I)` |
| 59 | — | `Furniture and fittings` | 35 | `=SUMIF(Depreciation!J:J,35,Depreciation!I:I)` |
| 60 | — | `Land` | 36 | `=SUMIF(Depreciation!J:J,36,Depreciation!I:I)` |
| 61 | — | `Buildings` | 37 | `=SUMIF(Depreciation!J:J,37,Depreciation!I:I)` |
| 62 | — | `Other fixed assets` | 38 | `=SUMIF(Depreciation!J:J,38,Depreciation!I:I)` |
| 64 | `Other non-current assets (as at balance date)` | `Intangibles` | 39 | literal (e.g. Koinly EOY total value) |
| 65 | — | `Shares/ownership interests` | 40 | 0 |
| 66 | — | `Term deposits` | 41 | 0 |
| 67 | — | `Other non-current assets` | 42 | 0 |
| 69 | `Total assets` | `Add up all assets entered in Boxes 30 to 42` | 43 | `=SUM(D53:D67)` |
| 71 | `Current liabilities (as at balance date)` | `Provisions` | 44 | 0 |
| 72 | — | `Accounts payable (creditors)` | 45 | 0 |
| 73 | — | `Current loans` | 46 | 0 |
| 74 | — | `Other current liabilities` | 47 | 0 |
| 75 | `Total current liabilities` | `Add up all liabilities entered in Boxes 44 to 47` | 48 | `=SUM(D71:D74)` |
| 77 | `Non-current liabilities (as at balance date)` | — | 49 | 0 |
| 79 | `Total liabilities` | `Add Box 48 to Box 49` | 50 | `=D75+D77` |
| 81 | `Owners' equity` | `(if in debit, put a minus sign in the last box)` | 51 | `=D69-D79` |
| 83 | `Other information` | `Tax depreciation` | 52 | `=D28` |
| 84 | — | `Untaxed realised gains/receipts` | 53 | 0 |
| 85 | — | `Additions to fixed assets` | 54 | `=SUMIF(Expenses!F:F,"Accounting depreciation and amortisation",Expenses!E:E)+SUM(Depreciation!E3:E<dep_last>)` |
| 86 | — | `Disposals of fixed assets` | 55 | 0 |
| 87 | — | `Dividends paid` | 56 | 0 |
| 88 | — | `Drawings` | 57 | 0 |
| 89 | — | `Current account year-end balances` | 58 | 0 |
| 90 | — | `Tax-deductible loss on disposal of fixed assets` | 59 | 0 |

`<dep_last>` = the last data row on the Depreciation sheet (= `2 + number of capital items`).

### Notes column (E)
Populate E12 with `Koinly/Income Summary/Total` when Box 2 carries Koinly income. Populate E47 with `Koinly/Capital gains summary (net) + Other gains (net)`. Populate E64 with `Koinly/End of year balances`. Populate E28 with `Fixed assets under $1000 + depreciation` and set G28 to the IRD depreciation URL.

---

## Sheet 2: `Expenses`

Row 1: `A1 = "EXPENSES"` (banner).
Row 2: header — `Date | Inv | Seller | Description | Amount | Type`.
Row 3+: one row per expense. Amount is NZD (GST-inclusive or exclusive per the taxpayer's basis). Type **must** match exactly one IR10 Box B-label from the table above (e.g. `Other expenses`, `Professional and consulting fees`, `Accounting depreciation and amortisation`).

The `Type` column drives every `SUMIF` in Boxes 12–24. A typo here silently zeros a box — `ir10-reviewer` checks that every Type value maps to an IR10 label.

---

## Sheet 3: `Depreciation`

Row 1: `A1 = "Straight Line Depreciation"` (banner).
Row 2: header — `Date | Inv | Seller | Description | Opening Amount | Depreciation % | Months Owned EOY | Depreciation Amount EOY Mar <year> | Closing Amount | IR10 Box`.

Columns A–I match the reference template. Column **J** is an additional helper: the integer IR10 box number for this asset's category (33 Vehicles, 34 Plant and machinery, 35 Furniture and fittings, 36 Land, 37 Buildings, 38 Other fixed assets). IR10 boxes 33–38 `SUMIF` against column J so the same sheet can hold mixed-category assets.

Row 3+: one row per capital item.
- `A` = acquisition date (used by the month-count formula).
- `B` = invoice number.
- `C` = seller / vendor.
- `D` = description.
- `E` = opening amount (NZD).
- `F` = depreciation rate (decimal, e.g. `0.4`). User-provided per item using the IRD lookup at `https://myir.ird.govt.nz/tools/_/`.
- `G` = `=CHOOSE(MONTH(A<row>),3,2,1,12,11,10,9,8,7,6,5,4)` — months owned to 31 March of the balance date year.
- `H` = `=IF(E<row><1000,E<row>,E<row>*F<row>*(G<row>/12))` — full expense if under $1000 (low-value asset rule), else straight-line.
- `I` = `=E<row>-H<row>` — closing book value.
- `J` = integer IR10 box number.

Last row (row `3 + N`): `G<n>="TOTAL"`, `H<n>=SUM(H3:H<dep_last>)`, `I<n>=SUM(I3:I<dep_last>)`. (Fixes the reference template's hard-coded `SUM(H3)` which breaks for >1 asset.)

---

## Cross-sheet invariants (enforced by `ir10-reviewer`)

1. Every `Expenses!F<row>` value must match exactly one IR10 Box B-label (12–24).
2. `SUM(Expenses!E3:E<last>) = IR10!D41` (Box 25, total expenses). Note: Box 25 also includes the accounting-depreciation adjustment from the Depreciation sheet via Box 13, so the equality only holds when the depreciation-sheet H-sum is zero; otherwise `Expenses-sum + Depreciation!H-sum = D41`.
3. For each capital item: row must have a valid IRD box number in column J (33–38); `F` must be in `(0, 1]`; `E > 0`.
4. `IR10!D28` literal must equal `capital_gains_net + other_gains_net` from the consolidated Koinly report (within 0.01).
5. `IR10!D12` literal must equal the Koinly `income_summary_total` (within 0.01).
6. `IR10!D64` literal must equal the Koinly `end_of_year_balances.total_value` (within 0.01).
7. `IR10!B4` and `IR10!B5` must be non-empty (taxpayer identity).
