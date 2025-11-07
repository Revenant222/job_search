# Scripts Directory

This directory contains utility scripts, test scripts, and batch files for the Job Search Application.

## Directory Structure

### `batch/`
Batch and PowerShell scripts for quick execution:
- **`run_app.bat`** / **`run_app.ps1`** - Launch the Streamlit application
- **`test_delta.bat`** - Run delta analysis tests

### `tests/`
Test and diagnostic scripts:
- **`test_delta_analysis.py`** - Test Google Sheets delta analysis and tagging
- **`test_service_account.py`** - Verify Google Service Account setup
- **`test_setup.py`** - Verify project setup and dependencies
- **`debug_delta.py`** - Debug delta analysis issues
- **`diagnose_duplicates.py`** - Analyze duplicate job IDs and data quality
- **`verify_delta.py`** - Verify delta analysis results

### `utilities/`
Utility scripts for data management:
- **`clear_csv_for_fresh_run.py`** - Clear CSV files for a fresh first run (no tagging)
- **`restore_backup_csv.py`** - Restore backup CSV file
- **`clean_csv_salaries.py`** - Clean salary columns in CSV files
- **`extract_sheet_id.py`** - Extract Google Sheet ID from URL
- **`verify_cleaned_csv.py`** - Verify cleaned CSV files

## Usage

All scripts should be run from the project root directory:

```bash
# Run from project root
python scripts/tests/test_delta_analysis.py
python scripts/utilities/clear_csv_for_fresh_run.py

# Or use batch files (Windows)
scripts\batch\run_app.bat
scripts\batch\test_delta.bat
```

## Notes

- Scripts use relative imports from `src.` and `config.` modules
- Ensure virtual environment is activated before running Python scripts
- Batch files automatically activate the virtual environment

