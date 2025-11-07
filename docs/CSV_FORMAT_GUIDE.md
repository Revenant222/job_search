# CSV Formatting Guide for Job Search Application

## Overview

This guide explains how to format your CSV files for the Job Search Application. Your CSV must contain **exactly 17 columns (A-Q)** with specific formatting requirements.

---

## Required Column Structure

### Column Order (A-Q)

| Column # | Column Name | Required | Data Type | Format Notes |
|----------|-------------|----------|-----------|--------------|
| A | **Company Category** | Yes | Text | Category of company (e.g., "Gaming Company") |
| B | **Company** | **REQUIRED** | Text | Company name (e.g., "Activision") |
| C | **Overall Job Category** | Yes | Text | High-level category (e.g., "Data & Analytics") |
| D | **Job Category** | Yes | Text | Specific category (e.g., "Data-analysis") |
| E | **Title** | **REQUIRED** | Text | Job title (e.g., "Senior Manager, Data Science") |
| F | **Min Experience** | Optional | Number | Minimum years (numeric only, no text) |
| G | **Max Experience** | Optional | Number | Maximum years (numeric only, no text) |
| H | **Country** | Yes | Text | Country name (e.g., "United States") |
| I | **State** | Optional | Text | State/Province (can be empty) |
| J | **City** | Optional | Text | City name (can be empty) |
| K | **Location Type** | Yes | Text | "Remote", "Hybrid", "On-site", etc. |
| L | **JobType** | Yes | Text | "Full-time", "Part-time", "Contract", etc. |
| M | **Job Link** | **REQUIRED** | URL | Full URL to job posting (must start with http:// or https://) |
| N | **Activated Date** | Yes | Date | Format: "DD MMM YYYY" (e.g., "29 Oct 2025") |
| O | **Skills** | Optional | Text | Comma-separated list (e.g., "python, sql, aws") |
| P | **Min Salary** | Optional | Number | Numeric value only (no $, commas, or currency symbols) |
| Q | **Max Salary** | Optional | Number | Numeric value only (no $, commas, or currency symbols) |

---

## Critical Formatting Rules

### 1. Required Columns (Cannot Be Empty)

These columns **MUST** have data for every row:
- **Company** (Column B)
- **Title** (Column E)
- **Job Link** (Column M)

### 2. Salary Formatting ⚠️ IMPORTANT

**INCORRECT FORMATS:**
```
❌ $134,320
❌ $248,404
❌ 134,320
❌ $134320
```

**CORRECT FORMAT:**
```
✅ 134320
✅ 248404
```

**Rules:**
- No dollar signs ($)
- No commas (,) as thousands separators
- No currency symbols
- Numbers only (e.g., `134320` not `$134,320`)

**How to Fix in Excel/Google Sheets:**
1. Select the salary columns (P and Q)
2. Remove formatting: Format → Clear Formatting
3. Use Find & Replace:
   - Find: `$` → Replace: (leave empty)
   - Find: `,` → Replace: (leave empty)

**Or use a formula:**
```
=VALUE(SUBSTITUTE(SUBSTITUTE(P2,"$",""),",",""))
```

### 3. Experience Formatting

**INCORRECT:**
```
❌ "5 years"
❌ "5+"
❌ "5-10"
```

**CORRECT:**
```
✅ 5        (for Min Experience)
✅ 10       (for Max Experience)
✅ (empty)  (if not specified)
```

**Rules:**
- Numbers only (no text)
- Can be empty if not specified
- No ranges in a single cell (use separate Min/Max columns)

### 4. Date Formatting

**Format:** `DD MMM YYYY`

**Examples:**
```
✅ 29 Oct 2025
✅ 02 Aug 2025
✅ 15 Jan 2026
```

**Common Mistakes:**
```
❌ 29/10/2025
❌ 10-29-2025
❌ October 29, 2025
❌ 2025-10-29
```

**Excel Date Conversion:**
1. Ensure your date is in a date format in Excel
2. Use custom format: `dd mmm yyyy`
3. Or use formula: `=TEXT(A1,"dd mmm yyyy")`

### 5. Skills Formatting

**Format:** Comma-separated list (single comma + space)

**CORRECT:**
```
python, sql, machine-learning, aws, docker
```

**INCORRECT:**
```
❌ python; sql; machine-learning  (semicolons)
❌ python|sql|machine-learning    (pipes)
❌ python sql machine-learning    (spaces only)
❌ python, sql,machine-learning   (inconsistent spacing)
```

**Best Practice:**
- Use lowercase with hyphens for multi-word skills: `machine-learning`, `game-texts`
- Separate each skill with: `, ` (comma + space)
- No trailing commas

### 6. URL Formatting

**CORRECT:**
```
✅ https://activision.wd1.myworkdayjobs.com/en-US/External/job/Santa-Monica/Senior-Manager--Data-Science-and-Economics_R026276
✅ http://example.com/job/123
```

**INCORRECT:**
```
❌ activision.wd1.myworkdayjobs.com/...  (missing http://)
❌ www.example.com/job  (missing http:// or https://)
```

**Rules:**
- Must start with `http://` or `https://`
- Must be a complete, valid URL

### 7. Location Fields

**Country, State, City:**
- Can be empty if not applicable
- Use full names: "United States" not "USA"
- For international: Use official country names

**Example:**
```
Country: United States
State: California
City: Santa Monica
```

**Or:**
```
Country: Lithuania
State: Vilnius County
City: Vilnius
```

---

## Example Row (Properly Formatted)

```
Gaming Company|Activision|Data & Analytics|Data-analysis|Senior Manager, Data Science and Economics|10||United States|California|Santa Monica|Hybrid|Full-time|https://activision.wd1.myworkdayjobs.com/en-US/External/job/Santa-Monica/Senior-Manager--Data-Science-and-Economics_R026276|29 Oct 2025|python, sql, machine-learning, data-science|134320|248404
```

**As CSV (comma-separated):**
```csv
Gaming Company,Activision,Data & Analytics,Data-analysis,Senior Manager Data Science and Economics,10,,United States,California,Santa Monica,Hybrid,Full-time,https://activision.wd1.myworkdayjobs.com/en-US/External/job/Santa-Monica/Senior-Manager--Data-Science-and-Economics_R026276,29 Oct 2025,"python, sql, machine-learning, data-science",134320,248404
```

---

## Common Issues and Solutions

### Issue 1: Salary Has Dollar Signs and Commas

**Problem:** `$134,320` in the CSV

**Solution:** 
- **Option 1 (Recommended):** Use the automated cleaning script:
  ```powershell
  python scripts/utilities/clean_csv_salaries.py your_file.csv
  ```
- **Option 2:** Use Excel's Find & Replace to remove `$` and `,`
- **Option 3:** Use formula: `=VALUE(SUBSTITUTE(SUBSTITUTE(P2,"$",""),",",""))`

### Issue 2: Date Format Wrong

**Problem:** Date shows as `10/29/2025` or `2025-10-29`

**Solution:**
1. Format the cell as Custom: `dd mmm yyyy`
2. Or use formula: `=TEXT(YOUR_DATE_CELL,"dd mmm yyyy")`

### Issue 3: Missing Required Columns

**Problem:** Application shows error: "Required column missing: Company"

**Solution:**
- Check that column headers exactly match the expected names (case-sensitive)
- Ensure columns are in the correct order (A-Q)

### Issue 4: URL Validation Fails

**Problem:** Job Link doesn't start with http:// or https://

**Solution:**
- Add `https://` prefix to all URLs
- Use formula: `=IF(LEFT(M2,4)="http",M2,"https://"&M2)`

### Issue 5: Skills Format Issues

**Problem:** Skills not parsing correctly

**Solution:**
- Ensure comma-space separation: `, `
- Check for hidden characters (copy to Notepad and back)
- Remove any trailing commas

---

## Excel/Google Sheets Cleanup Checklist

Before saving your CSV, verify:

- [ ] All required columns (B, E, M) have data for every row
- [ ] Salaries (P, Q) have NO dollar signs or commas - numbers only
- [ ] Dates (N) are in format "DD MMM YYYY" (e.g., "29 Oct 2025")
- [ ] Experience fields (F, G) are numbers only or empty
- [ ] URLs (M) all start with `http://` or `https://`
- [ ] Skills (O) are comma-space separated (e.g., "python, sql, aws")
- [ ] No extra columns beyond Q
- [ ] Headers are in row 1 and match exactly (case-sensitive)
- [ ] No merged cells
- [ ] No formulas (values only - use Paste Special → Values if needed)

---

## Quick Format Verification Script

After creating your CSV, you can test it in the application:

1. Open the Streamlit app
2. Upload your CSV file
3. Check for validation warnings/errors
4. Review the data summary to ensure all rows loaded correctly

---

## Template CSV Structure

Here's a template with headers and one example row:

```csv
Company Category,Company,Overall Job Category,Job Category,Title,Min Experience,Max Experience,Country,State,City,Location Type,JobType,Job Link,Activated Date,Skills,Min Salary,Max Salary
Gaming Company,Activision,Data & Analytics,Data-analysis,Senior Manager Data Science and Economics,10,,United States,California,Santa Monica,Hybrid,Full-time,https://activision.wd1.myworkdayjobs.com/en-US/External/job/Santa-Monica/Senior-Manager--Data-Science-and-Economics_R026276,29 Oct 2025,"python, sql, machine-learning, data-science",134320,248404
```

---

## Need Help?

If you're still having issues:

1. Check the application logs for specific validation errors
2. Verify your CSV opens correctly in a text editor (shows as comma-separated)
3. Ensure file encoding is UTF-8 (save as "CSV UTF-8" in Excel)
4. Try opening and re-saving the CSV to remove any hidden formatting

---

**Last Updated:** Based on application requirements and your sample data

