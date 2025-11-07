# Quick Fix Guide for Your CSV Data

## Current Status

Your CSV data is **almost perfect**! The only issue is salary formatting.

---

## Issue Found

**Salaries have dollar signs and commas:**
- `"$134,320"` ❌
- `"$248,404"` ❌  
- `"$133,900"` ❌

**Should be plain numbers:**
- `134320` ✅
- `248404` ✅
- `133900` ✅

---

## Two Ways to Fix

### Option 1: Automatic Fix (Recommended) ⚡

I've created a Python script that will automatically clean your CSV file.

**Steps:**
1. Save your CSV file (e.g., `my_jobs.csv`)
2. Run the cleaning script:

```powershell
# Activate virtual environment
.venv\Scripts\Activate.ps1

# Run the cleaning script (from project root)
python scripts/utilities/clean_csv_salaries.py my_jobs.csv
```

This will create a new file: `my_jobs_cleaned.csv` with all salaries fixed!

**Or specify output filename:**
```powershell
python scripts/utilities/clean_csv_salaries.py my_jobs.csv cleaned_jobs.csv
```

---

### Option 2: Manual Fix in Excel/Google Sheets

1. Open your CSV in Excel or Google Sheets
2. Select columns P and Q (Min Salary and Max Salary)
3. Press `Ctrl+H` (Find & Replace)
4. Find: `$` → Replace: (leave empty) → **Replace All**
5. Find: `,` → Replace: (leave empty) → **Replace All**
6. Save as CSV

---

## What Gets Fixed

**Before:**
```csv
"$134,320","$248,404"
"$133,900","$231,400"
,,
"$26,400","$30,000"
```

**After:**
```csv
134320,248404
133900,231400
,
26400,30000
```

Empty salary fields remain empty (which is fine ✅)

---

## Verify Your Data Format

After fixing salaries, your CSV should match this structure:

| Column | Example Value | Status |
|--------|---------------|--------|
| Company Category | Gaming Company | ✅ |
| Company | Activision | ✅ |
| Title | "Senior Manager, Data Science and Economics" | ✅ (quotes OK for commas) |
| Min Experience | 10 | ✅ (number) |
| Max Experience | (empty) | ✅ (allowed) |
| Country | United States | ✅ |
| State | California | ✅ |
| City | Santa Monica | ✅ |
| Location Type | Hybrid | ✅ |
| JobType | Full-time | ✅ |
| Job Link | https://... | ✅ |
| Activated Date | 29 Oct 2025 | ✅ |
| Skills | "python, sql, aws" | ✅ (quotes OK) |
| **Min Salary** | **134320** | ✅ (no $ or commas) |
| **Max Salary** | **248404** | ✅ (no $ or commas) |

---

## Testing the Cleaned File

After cleaning, test it in the application:

1. Run the Streamlit app:
   ```powershell
   .venv\Scripts\Activate.ps1
   streamlit run src\streamlit_app.py
   ```

2. Upload your cleaned CSV file
3. Check for any validation errors
4. You should see all jobs loaded successfully!

---

## Quick Reference

**Command to clean your CSV:**
```powershell
.venv\Scripts\Activate.ps1
python scripts/utilities/clean_csv_salaries.py your_file.csv
```

**What the script does:**
- Removes `$` from all salary values
- Removes `,` (commas) from all salary values  
- Converts salaries to numbers
- Keeps empty salary fields as empty
- Saves cleaned version with `_cleaned` suffix

---

**Your data format is excellent - just needs the salary columns cleaned!** 🎯

