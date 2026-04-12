import json
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.comments import Comment

CONTEXT = r"D:/AgenticEngineer/Projects/Tax2025_test/expenses/ir10-context.json"
OUT = r"D:/AgenticEngineer/Projects/Tax2025_test/expenses/IR10-filled.xlsx"

IR10_FORM_URL = "https://www.ird.govt.nz/-/media/project/ir/home/documents/forms-and-guides/ir1/ir10/ir10-2025.pdf"
IR10_GUIDE_URL = "https://www.ird.govt.nz/-/media/project/ir/home/documents/forms-and-guides/ir1/ir10g/ir10g-2025.pdf"
DEPR_URL = "https://myir.ird.govt.nz/tools/_/"

with open(CONTEXT, "r", encoding="utf-8") as f:
    ctx = json.load(f)

taxpayer = ctx["taxpayer"]
expenses = ctx["expenses"]
capital_items = ctx.get("capital_items", [])
koinly = ctx["koinly_reports"][0]["result"] if ctx.get("koinly_reports") else None

wb = Workbook()

# ---------------- Sheet 2: Expenses ----------------
exp_ws = wb.create_sheet("Expenses")
exp_ws["A1"] = "EXPENSES"
exp_ws["A1"].font = Font(bold=True, size=14)
headers = ["Date", "Inv", "Seller", "Description", "Amount", "Type"]
for i, h in enumerate(headers, start=1):
    c = exp_ws.cell(row=2, column=i, value=h)
    c.font = Font(bold=True)
    c.fill = PatternFill("solid", fgColor="B0C4DE")

row = 3
for e in expenses:
    r = e["result"]
    inv = r["invoice"]
    exp_ws.cell(row=row, column=1, value=inv.get("date"))
    exp_ws.cell(row=row, column=2, value=inv.get("number"))
    exp_ws.cell(row=row, column=3, value=inv.get("vendor"))
    exp_ws.cell(row=row, column=4, value=inv.get("description"))
    exp_ws.cell(row=row, column=5, value=r.get("nzd_amount"))
    exp_ws.cell(row=row, column=6, value=r.get("ir10_category"))
    row += 1
exp_last = row - 1

for col, width in zip("ABCDEF", [12, 16, 28, 45, 12, 36]):
    exp_ws.column_dimensions[col].width = width

# ---------------- Sheet 3: Depreciation ----------------
dep_ws = wb.create_sheet("Depreciation")
dep_ws["A1"] = "Straight Line Depreciation"
dep_ws["A1"].font = Font(bold=True, size=14)
# year for header: balance date year
bal_year = ctx.get("balance_date", "2025-03-31")[:4]
dep_headers = ["Date", "Inv", "Seller", "Description", "Opening Amount",
               "Depreciation %", "Months Owned EOY", f"Depreciation Amount EOY Mar {bal_year}",
               "Closing Amount", "IR10 Box"]
for i, h in enumerate(dep_headers, start=1):
    c = dep_ws.cell(row=2, column=i, value=h)
    c.font = Font(bold=True)
    c.fill = PatternFill("solid", fgColor="B0C4DE")

row = 3
for cap in capital_items:
    r = cap["result"]
    inv = r["invoice"]
    dep_ws.cell(row=row, column=1, value=r.get("date_acquired"))
    dep_ws.cell(row=row, column=2, value=inv.get("number"))
    dep_ws.cell(row=row, column=3, value=inv.get("vendor"))
    dep_ws.cell(row=row, column=4, value=inv.get("description"))
    dep_ws.cell(row=row, column=5, value=r.get("opening_amount"))
    dep_ws.cell(row=row, column=6, value=r.get("depreciation_rate"))
    dep_ws.cell(row=row, column=7, value=f"=CHOOSE(MONTH(A{row}),3,2,1,12,11,10,9,8,7,6,5,4)")
    dep_ws.cell(row=row, column=8, value=f"=IF(E{row}<1000,E{row},E{row}*F{row}*(G{row}/12))")
    dep_ws.cell(row=row, column=9, value=f"=E{row}-H{row}")
    dep_ws.cell(row=row, column=10, value=r.get("ir10_box"))
    row += 1
dep_last_data = row - 1
# TOTAL row
total_row = row
dep_ws.cell(row=total_row, column=7, value="TOTAL").font = Font(bold=True)
dep_ws.cell(row=total_row, column=8, value=f"=SUM(H3:H{dep_last_data})").font = Font(bold=True)
dep_ws.cell(row=total_row, column=9, value=f"=SUM(I3:I{dep_last_data})").font = Font(bold=True)

for col, width in zip("ABCDEFGHIJ", [12, 14, 22, 30, 14, 14, 16, 22, 14, 10]):
    dep_ws.column_dimensions[col].width = width

# ---------------- Sheet 1: IR10 ----------------
ir10 = wb.active
ir10.title = "IR10"

ir10["A1"] = "IR10"
ir10["A1"].font = Font(bold=True, size=16)
ir10["B1"] = "Financial statements summary"
ir10["B1"].font = Font(bold=True, size=14)
ir10["F1"] = IR10_FORM_URL
ir10["F2"] = IR10_GUIDE_URL

ir10["A4"] = "Your full name"
ir10["B4"] = taxpayer["name"]
ir10["A5"] = "Your IRD Number"
ir10["B5"] = taxpayer["ird_number"]

ir10["C6"] = "Box"
ir10["E6"] = "Notes"
ir10["F6"] = "Reference"
for cell in ("C6", "E6", "F6"):
    ir10[cell].font = Font(bold=True)

# Row layout
rows_spec = [
    # (row, A, B, box, D)
    (8,  "Multiple activity indicator", None, 1, "No"),
    (10, "Profit and loss statement", None, None, None),
    (12, "Gross income from", "Sales and/or services", 2, 0),
    (14, "Cost of goods sold", "Opening stock (include work in progress)", 3, 0),
    (15, None, "Purchases", 4, 0),
    (16, None, "Closing stock (include work in progress)", 5, 0),
    (18, "Gross profit", "(if a loss, put a minus sign in the last box)", 6, "=D12-D14+D15-D16"),
    (20, "Other gross income", "Interest received", 7, 0),
    (21, None, "Dividends received", 8, 0),
    (22, None, "Rental, lease and licence income", 9, 0),
    (23, None, "Other income", 10, 0),
    (25, "Total income", "Add up all income entered in Boxes 6 to 10", 11, "=SUM(D18:D23)"),
    (27, "Expenses (as per financial statements)", "Bad debts", 12, '=SUMIF(Expenses!F:F,B27,Expenses!E:E)'),
    (28, None, "Accounting depreciation and amortisation", 13, f'=SUMIF(Expenses!F:F,B28,Expenses!E:E)+SUM(Depreciation!H3:H{dep_last_data})'),
    (29, None, "Insurance (exclude ACC levies)", 14, '=SUMIF(Expenses!F:F,B29,Expenses!E:E)'),
    (30, None, "Interest expense", 15, '=SUMIF(Expenses!F:F,B30,Expenses!E:E)'),
    (31, None, "Professional and consulting fees", 16, '=SUMIF(Expenses!F:F,B31,Expenses!E:E)'),
    (32, None, "Rates", 17, '=SUMIF(Expenses!F:F,B32,Expenses!E:E)'),
    (33, None, "Rental, lease and licence payments", 18, '=SUMIF(Expenses!F:F,B33,Expenses!E:E)'),
    (34, None, "Repairs and maintenance", 19, '=SUMIF(Expenses!F:F,B34,Expenses!E:E)'),
    (35, None, "Research and development", 20, '=SUMIF(Expenses!F:F,B35,Expenses!E:E)'),
    (36, None, "Associated persons' remuneration", 21, '=SUMIF(Expenses!F:F,B36,Expenses!E:E)'),
    (37, None, "Salaries and wages paid to employees", 22, '=SUMIF(Expenses!F:F,B37,Expenses!E:E)'),
    (38, None, "Contractor and sub-contractor payments", 23, '=SUMIF(Expenses!F:F,B38,Expenses!E:E)'),
    (39, None, "Other expenses", 24, '=SUMIF(Expenses!F:F,B39,Expenses!E:E)'),
    (41, "Total expenses", "Add up all expenses entered in Boxes 12 to 24", 25, "=SUM(D27:D39)"),
    (43, "Exceptional items", "(if there is a negative amount, put a minus sign in the last box)", 26, 0),
    (45, "Net profit/loss before tax", "Box 11 less Box 25, add Box 26", 27, "=D25-D41+D43"),
    (47, "Tax adjustments", "(if there is a negative amount, put a minus sign in the last box)", 28, 0),
    (49, "Current year taxable profit/loss", None, 29, "=D45+D47"),
    (51, "Balance sheet items", None, None, None),
    (53, "Current assets (as at balance date)", "Accounts receivable (debtors)", 30, 0),
    (54, None, "Cash and deposits", 31, 0),
    (55, None, "Other current assets", 32, 0),
    (57, "Fixed assets (closing accounting value)", "Vehicles", 33, "=SUMIF(Depreciation!J:J,33,Depreciation!I:I)"),
    (58, None, "Plant and machinery", 34, "=SUMIF(Depreciation!J:J,34,Depreciation!I:I)"),
    (59, None, "Furniture and fittings", 35, "=SUMIF(Depreciation!J:J,35,Depreciation!I:I)"),
    (60, None, "Land", 36, "=SUMIF(Depreciation!J:J,36,Depreciation!I:I)"),
    (61, None, "Buildings", 37, "=SUMIF(Depreciation!J:J,37,Depreciation!I:I)"),
    (62, None, "Other fixed assets", 38, "=SUMIF(Depreciation!J:J,38,Depreciation!I:I)"),
    (64, "Other non-current assets (as at balance date)", "Intangibles", 39, 0),
    (65, None, "Shares/ownership interests", 40, 0),
    (66, None, "Term deposits", 41, 0),
    (67, None, "Other non-current assets", 42, 0),
    (69, "Total assets", "Add up all assets entered in Boxes 30 to 42", 43, "=SUM(D53:D67)"),
    (71, "Current liabilities (as at balance date)", "Provisions", 44, 0),
    (72, None, "Accounts payable (creditors)", 45, 0),
    (73, None, "Current loans", 46, 0),
    (74, None, "Other current liabilities", 47, 0),
    (75, "Total current liabilities", "Add up all liabilities entered in Boxes 44 to 47", 48, "=SUM(D71:D74)"),
    (77, "Non-current liabilities (as at balance date)", None, 49, 0),
    (79, "Total liabilities", "Add Box 48 to Box 49", 50, "=D75+D77"),
    (81, "Owners' equity", "(if in debit, put a minus sign in the last box)", 51, "=D69-D79"),
    (83, "Other information", "Tax depreciation", 52, "=D28"),
    (84, None, "Untaxed realised gains/receipts", 53, 0),
    (85, None, "Additions to fixed assets", 54, f'=SUMIF(Expenses!F:F,"Accounting depreciation and amortisation",Expenses!E:E)+SUM(Depreciation!E3:E{dep_last_data})'),
    (86, None, "Disposals of fixed assets", 55, 0),
    (87, None, "Dividends paid", 56, 0),
    (88, None, "Drawings", 57, 0),
    (89, None, "Current account year-end balances", 58, 0),
    (90, None, "Tax-deductible loss on disposal of fixed assets", 59, 0),
]

# Koinly-driven literal overrides
if koinly:
    inc = koinly.get("income", {})
    eoy = koinly.get("end_of_year_balances", {})
    income_total = inc.get("income_summary_total", 0) or 0
    cap_gains = inc.get("capital_gains_net", 0) or 0
    other_gains = inc.get("other_gains_net", 0) or 0
    eoy_total = eoy.get("total_value", 0) or 0
else:
    income_total = cap_gains = other_gains = eoy_total = 0

# Apply overrides to rows_spec dict form
overrides = {
    12: income_total,                    # Box 2
    47: f"={cap_gains}+{other_gains}",   # Box 28 literal formula
    64: eoy_total,                       # Box 39 Intangibles (per spec)
}

user_to_provide_boxes = {30, 31, 32, 39, 40, 41, 42, 44, 45, 46, 47, 49, 53, 55, 56, 57, 58, 59, 26}

for (r, a, b, box, d) in rows_spec:
    if a is not None:
        ir10.cell(row=r, column=1, value=a).font = Font(bold=True)
    if b is not None:
        ir10.cell(row=r, column=2, value=b)
    if box is not None:
        ir10.cell(row=r, column=3, value=box)
    if r in overrides:
        d = overrides[r]
    if d is not None:
        cell = ir10.cell(row=r, column=4, value=d)
        if isinstance(d, (int, float)):
            cell.number_format = "#,##0.00"

# Notes
ir10["E12"] = "Koinly/Income Summary/Total"
ir10["E47"] = "Koinly/Capital gains summary (net) + Other gains (net)"
ir10["E64"] = "Koinly/End of year balances"
ir10["E28"] = "Fixed assets under $1000 + depreciation"
ir10["F28"] = DEPR_URL

# User-to-provide comments on zero-literal boxes
for (r, a, b, box, d) in rows_spec:
    if box in user_to_provide_boxes and r not in overrides:
        cell = ir10.cell(row=r, column=4)
        if cell.value == 0:
            cell.comment = Comment("User to provide", "ir10-agent")

# Column widths
for col, width in zip("ABCDEF", [40, 42, 6, 18, 42, 40]):
    ir10.column_dimensions[col].width = width

# Right align D values
for (r, *_rest) in rows_spec:
    ir10.cell(row=r, column=4).alignment = Alignment(horizontal="right")

wb.save(OUT)
print("WROTE", OUT)
print("exp_last", exp_last, "dep_last_data", dep_last_data)
