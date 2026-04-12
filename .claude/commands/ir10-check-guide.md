---
description: Check if the local IR10 guide is outdated and download the latest from IRD NZ if so
argument-hint: "[--force-download]"
allowed-tools: Read, Glob, Bash, WebSearch, WebFetch, Write
---

# Check IR10 Guide for Updates

Your job is to verify whether the IR10 guide in `guides/` is the current IRD-published version, and download the latest one if not.

## Context

- Authoritative publisher: **Inland Revenue New Zealand (IRD)** — `ird.govt.nz`.
- IRD publishes the IR10 guide as **IR10G** (PDF), usually named by tax year, e.g. `IR10G-2026.pdf` covers the year ended 31 March 2026.
- IRD's NZ tax year runs **1 April → 31 March**. A guide dated "2026" is the guide for the year *ending* 31 March 2026.
- Today's date (per the session context) should be used to determine which tax year is current; don't assume.

## Steps

### 1. Inspect the local guide

- `Glob` `guides/IR10G-*.pdf` to list what's present.
- If none exists, skip to step 3 (download).
- `Read` the first few pages of the newest local PDF to confirm:
  - The tax year it covers (look for phrases like "for the year ended 31 March YYYY").
  - Any "published" / "revised" / version date printed on the cover or footer.
- Record both the filename year and the internal year — they should match. If they don't, flag it.

### 2. Check IRD for the current version

- `WebSearch` for: `IR10 guide site:ird.govt.nz` and `IR10G <current tax year> filetype:pdf`.
- From results, identify the canonical IRD page for the IR10 guide (typically under `ird.govt.nz/.../ir10...`).
- `WebFetch` that page and extract:
  - The latest IR10G version/year IRD is currently publishing.
  - The direct PDF URL.
  - The "last updated" date if shown.
- Also look for any **Excel/CSV templates** or worksheets IRD offers alongside the IR10 (e.g. a financial-statements summary worksheet). If found, note the URL — do not download unless the user asks.

### 3. Compare and decide

Decision rules:
- **Up to date** — local year == IRD-published year AND no "revised" notice newer than the local PDF's published date. Report "no action needed" and stop.
- **Outdated** — IRD publishes a newer year, OR a revision of the same year with a later date. Proceed to download.
- **Ambiguous** — you can't confirm the IRD version (page layout changed, search inconclusive). Do NOT guess. Report what you found and ask the user how to proceed.

If the user passed `--force-download` as an argument, skip the comparison and download regardless.

### 4. Download (only if outdated or forced)

- Use `Bash` with `curl -L -o "guides/<new-filename>.pdf" "<url>"` (curl is available on Windows 10+).
- Name the file using IRD's own filename if possible, otherwise `IR10G-<year>.pdf`.
- **Do not delete the old file.** Keep prior versions in `guides/` as an audit trail — the portfolio story benefits from showing version history.
- After download, `Read` the first page of the new PDF to sanity-check it's actually the IR10 guide and not an error page or redirect HTML.

### 5. Report

Output a short structured summary:

```
Local guide:   IR10G-YYYY.pdf  (covers year ending 31 March YYYY, published <date>)
IRD current:   IR10G-YYYY.pdf  (<url>, last updated <date>)
Status:        up-to-date | outdated | ambiguous
Action taken:  none | downloaded guides/<file> | awaiting user decision
Templates:     <any Excel/worksheet URLs found, or "none">
Notes:         <anything noteworthy — format changes, new fields mentioned in changelog, etc.>
```

## Guardrails

- Never overwrite an existing PDF. If the target filename collides, append `-downloaded-YYYYMMDD`.
- Never fabricate a version date. If you can't read it, say so.
- The IRD website is the only acceptable source. Ignore third-party mirrors, accountant blogs, or cached copies.
