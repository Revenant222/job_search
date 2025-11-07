"""
Test script for delta analysis functionality.

This script demonstrates:
1. Pulling data from Google Sheets
2. Comparing with previous CSV
3. Tagging new jobs with "NEW" tag (only on subsequent runs)
4. Rolling backup system (one backup file)
"""
import os
from src.core.delta_analyzer import DeltaAnalyzer
from src.core.job_tagger import JobTagger
import pandas as pd


def main():
    print("=" * 60)
    print("Delta Analysis Test")
    print("=" * 60)
    
    # Initialize delta analyzer
    analyzer = DeltaAnalyzer()
    
    # Pull and analyze
    print("\nPulling data from Google Sheet and analyzing...")
    all_jobs_df, new_jobs_df = analyzer.pull_and_analyze(tag_new_jobs=True)
    
    # Display results
    print(f"\n✅ Analysis Complete!")
    print(f"   Total jobs: {len(all_jobs_df)}")
    print(f"   New jobs: {len(new_jobs_df)}")
    
    # Show match rate if not first run
    if len(new_jobs_df) < len(all_jobs_df) and len(all_jobs_df) > 0:
        match_count = len(all_jobs_df) - len(new_jobs_df)
        match_rate = (match_count / len(all_jobs_df) * 100)
        print(f"   Existing jobs: {match_count} ({match_rate:.1f}% match rate)")
    
    # Check if this was first run (no new jobs detected and no previous data means first run)
    is_first_run = len(new_jobs_df) == len(all_jobs_df) and len(all_jobs_df) > 0
    
    if is_first_run:
        print(f"\n📋 First Run:")
        print(f"   All {len(all_jobs_df)} jobs saved as baseline")
        print(f"   No tags assigned (no previous data to compare)")
    elif not new_jobs_df.empty:
        print(f"\n📋 New Jobs Detected:")
        print(f"   Columns: {list(new_jobs_df.columns)[:5]}...")
        print(f"\n   Sample new jobs:")
        for idx, (_, job) in enumerate(new_jobs_df.head(3).iterrows(), 1):
            company = job.get('Company', 'N/A')
            title = job.get('Title', 'N/A')
            job_id = job.get('job_id', 'N/A')
            print(f"   {idx}. {company} - {title} (ID: {job_id})")
    else:
        print(f"\n📋 No New Jobs:")
        print(f"   All jobs already exist in previous CSV")
    
    # Check tags
    tagger = analyzer.job_tagger
    new_tag_count = analyzer.get_new_jobs_count()
    print(f"\n🏷️  Tags:")
    print(f"   Jobs with 'NEW' tag: {new_tag_count}")
    print(f"   Total tagged jobs: {tagger.get_tagged_count()}")
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("  - Review the CSV file in data/csv_source/sheet_data.csv")
    print("  - Use the Streamlit app to filter and view jobs")
    print("  - Filter by 'NEW' tag to see only new jobs")


if __name__ == "__main__":
    main()

