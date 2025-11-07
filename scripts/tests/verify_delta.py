"""
Verify delta detection by checking a sample of "new" jobs against previous CSV.
This helps identify if column name mismatches are causing false positives.
"""
import pandas as pd
from src.core.sheet_manager import SheetManager
from src.core.data_processor import DataProcessor
from config.settings import GOOGLE_SHEET_CSV_FILENAME

def main():
    print("=" * 60)
    print("Delta Verification - Checking for False Positives")
    print("=" * 60)
    
    sheet_mgr = SheetManager()
    processor = DataProcessor()
    
    # Load both CSVs
    print("\nLoading CSVs...")
    current_df = sheet_mgr.load_previous_csv(GOOGLE_SHEET_CSV_FILENAME)
    
    import os
    backup_path = os.path.join(sheet_mgr.csv_storage_dir, "diffed_backup.csv")
    if os.path.exists(backup_path):
        previous_df = pd.read_csv(backup_path, encoding='utf-8')
        print(f"✅ Loaded current CSV: {len(current_df)} rows")
        print(f"✅ Loaded backup CSV: {len(previous_df)} rows")
    else:
        print("❌ No backup CSV found - can't verify")
        return
    
    # Normalize and generate IDs
    current_df = sheet_mgr._normalize_column_names(current_df.copy())
    previous_df = sheet_mgr._normalize_column_names(previous_df.copy())
    
    if 'job_id' not in current_df.columns:
        current_df = processor.add_job_ids(current_df)
    if 'job_id' not in previous_df.columns:
        previous_df = processor.add_job_ids(previous_df)
    
    # Check column names
    print(f"\n📊 Column Comparison:")
    print(f"   Current columns: {list(current_df.columns)[:10]}...")
    print(f"   Previous columns: {list(previous_df.columns)[:10]}...")
    
    # Check for required columns
    required = ['Company', 'Title', 'City']
    for col in required:
        in_current = col in current_df.columns
        in_previous = col in previous_df.columns
        print(f"   {col}: Current={in_current}, Previous={in_previous}")
    
    # Sample check: Pick a few jobs from current and see if they exist in previous
    print(f"\n🔍 Sampling Check:")
    print(f"   Checking if some 'current' jobs actually exist in previous data...")
    
    sample_size = min(10, len(current_df))
    sample_jobs = current_df.head(sample_size)
    
    matches_found = 0
    for idx, job in sample_jobs.iterrows():
        job_id = str(job.get('job_id', ''))
        company = str(job.get('Company', 'N/A'))
        title = str(job.get('Title', 'N/A'))[:50]
        
        # Check if this job_id exists in previous
        exists_in_previous = job_id in previous_df['job_id'].astype(str).values
        
        if exists_in_previous:
            matches_found += 1
            print(f"   ✅ Match: {company} - {title[:40]}...")
        else:
            # Try to find by Company+Title (without City, in case City changed)
            company_match = previous_df['Company'].astype(str).str.lower().str.strip() == str(company).lower().strip()
            title_match = previous_df['Title'].astype(str).str.lower().str.strip() == str(title).lower().strip()
            potential_match = previous_df[company_match & title_match]
            
            if len(potential_match) > 0:
                print(f"   ⚠️  Partial match (different City?): {company} - {title[:40]}...")
                print(f"      Current City: {job.get('City', 'N/A')}")
                print(f"      Previous City: {potential_match.iloc[0].get('City', 'N/A')}")
            else:
                print(f"   ❌ No match: {company} - {title[:40]}...")
    
    print(f"\n📈 Results:")
    print(f"   Sample size: {sample_size}")
    print(f"   Matches found: {matches_found}")
    print(f"   Match rate in sample: {(matches_found/sample_size*100):.1f}%")
    
    # Check for data quality issues
    print(f"\n📋 Data Quality Check:")
    for col in ['Company', 'Title', 'City']:
        if col in current_df.columns and col in previous_df.columns:
            current_empty = current_df[col].isna().sum()
            previous_empty = previous_df[col].isna().sum()
            print(f"   {col}: Current={current_empty} empty, Previous={previous_empty} empty")
    
    print("\n" + "=" * 60)
    print("Verification Complete!")
    print("=" * 60)
    print("\nIf match rate is low, possible causes:")
    print("  1. Column name mismatches (check warnings above)")
    print("  2. Data format differences (whitespace, capitalization)")
    print("  3. City field differences (jobs moved locations?)")
    print("  4. Actually that many new jobs were added")

if __name__ == "__main__":
    main()

