"""
Diagnose why we're seeing duplicate job IDs and high "new" job counts.
"""
import pandas as pd
from src.core.sheet_manager import SheetManager
from src.core.data_processor import DataProcessor
from config.settings import GOOGLE_SHEET_CSV_FILENAME
import os

def main():
    print("=" * 60)
    print("Duplicate Job ID Diagnosis")
    print("=" * 60)
    
    sheet_mgr = SheetManager()
    processor = DataProcessor()
    
    # Load current CSV
    current_df = sheet_mgr.load_previous_csv(GOOGLE_SHEET_CSV_FILENAME)
    if current_df is None:
        print("❌ No current CSV found")
        return
    
    # Normalize and add IDs
    current_df = sheet_mgr._normalize_column_names(current_df.copy())
    if 'job_id' not in current_df.columns:
        current_df = processor.add_job_ids(current_df)
    
    print(f"\n📊 Current CSV Analysis:")
    print(f"   Total rows: {len(current_df)}")
    print(f"   Unique job IDs: {current_df['job_id'].nunique()}")
    print(f"   Duplicate IDs: {len(current_df) - current_df['job_id'].nunique()}")
    
    # Find duplicate IDs
    duplicate_ids = current_df[current_df.duplicated(subset=['job_id'], keep=False)]['job_id'].unique()
    print(f"\n🔍 Duplicate Analysis:")
    print(f"   Jobs with duplicate IDs: {len(duplicate_ids)} unique IDs")
    
    if len(duplicate_ids) > 0:
        print(f"\n   Sample duplicates (first 5):")
        for dup_id in duplicate_ids[:5]:
            dup_jobs = current_df[current_df['job_id'] == dup_id]
            print(f"\n   Job ID: {dup_id}")
            for idx, job in dup_jobs.iterrows():
                company = str(job.get('Company', 'N/A'))
                title = str(job.get('Title', 'N/A'))[:50]
                city = str(job.get('City', 'N/A'))
                print(f"      - {company} | {title} | {city}")
    
    # Check for empty values in key columns
    print(f"\n📋 Data Quality:")
    for col in ['Company', 'Title', 'City']:
        if col in current_df.columns:
            empty = current_df[col].isna().sum()
            empty_pct = (empty / len(current_df) * 100) if len(current_df) > 0 else 0
            print(f"   {col}: {empty} empty ({empty_pct:.1f}%)")
            
            # Check for whitespace-only values
            if current_df[col].dtype == 'object':
                whitespace_only = current_df[col].astype(str).str.strip().eq('').sum()
                if whitespace_only > 0:
                    print(f"      {whitespace_only} whitespace-only values")
    
    # Check column names
    print(f"\n📑 Column Names:")
    print(f"   Columns: {list(current_df.columns)[:15]}...")
    
    required = ['Company', 'Title', 'City']
    for col in required:
        exists = col in current_df.columns
        print(f"   {col}: {'✅' if exists else '❌'}")
        if not exists:
            # Find similar
            similar = [c for c in current_df.columns if col.lower() in c.lower() or c.lower() in col.lower()]
            if similar:
                print(f"      Similar: {similar}")
    
    print("\n" + "=" * 60)
    print("Diagnosis Complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()

