"""
Debug script to check why delta detection might be tagging everything as new.
"""
import pandas as pd
from src.core.sheet_manager import SheetManager
from src.core.data_processor import DataProcessor
from config.settings import GOOGLE_SHEET_CSV_FILENAME

def main():
    print("=" * 60)
    print("Delta Detection Debug")
    print("=" * 60)
    
    sheet_mgr = SheetManager()
    processor = DataProcessor()
    
    # Load previous CSV
    previous_df = sheet_mgr.load_previous_csv(GOOGLE_SHEET_CSV_FILENAME)
    
    if previous_df is None:
        print("\n❌ No previous CSV found - this would be a first run")
        return
    
    print(f"\n✅ Previous CSV loaded: {len(previous_df)} rows")
    print(f"   Columns: {list(previous_df.columns)[:10]}...")
    
    # Check if job_id exists
    if 'job_id' in previous_df.columns:
        print(f"\n✅ Previous CSV has 'job_id' column")
        print(f"   Sample job_ids: {list(previous_df['job_id'].head(5))}")
    else:
        print(f"\n⚠️  Previous CSV does NOT have 'job_id' column")
        print(f"   Will need to generate IDs")
        
        # Generate IDs
        previous_df = processor.add_job_ids(previous_df)
        print(f"   Generated job_ids: {list(previous_df['job_id'].head(5))}")
    
    # Check for required columns
    required_cols = ['Company', 'Title', 'City']
    missing_cols = [col for col in required_cols if col not in previous_df.columns]
    
    if missing_cols:
        print(f"\n⚠️  Missing required columns: {missing_cols}")
        print(f"   Available columns: {list(previous_df.columns)}")
    else:
        print(f"\n✅ All required columns present")
    
    # Check for empty values in key columns
    print(f"\n📊 Data Quality Check:")
    for col in required_cols:
        if col in previous_df.columns:
            empty_count = previous_df[col].isna().sum()
            print(f"   {col}: {empty_count} empty values out of {len(previous_df)}")
    
    print("\n" + "=" * 60)
    print("Next: Pull from Google Sheet and compare...")
    print("=" * 60)

if __name__ == "__main__":
    main()

