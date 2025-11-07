"""
Helper script to clear CSV files for a fresh first run.
This removes the current CSV so the next run will be treated as first run (no tagging).
"""
import os
from src.core.sheet_manager import SheetManager
from config.settings import GOOGLE_SHEET_CSV_FILENAME

def main():
    print("=" * 60)
    print("Clear CSV for Fresh Run")
    print("=" * 60)
    
    sheet_mgr = SheetManager()
    main_path = os.path.join(sheet_mgr.csv_storage_dir, GOOGLE_SHEET_CSV_FILENAME)
    backup_path = os.path.join(sheet_mgr.csv_storage_dir, "diffed_backup.csv")
    
    print(f"\nFiles to remove:")
    print(f"   Main CSV: {main_path}")
    print(f"   Backup CSV: {backup_path}")
    
    removed = []
    
    if os.path.exists(main_path):
        os.remove(main_path)
        removed.append("Main CSV")
        print(f"\n✅ Removed: {main_path}")
    
    if os.path.exists(backup_path):
        os.remove(backup_path)
        removed.append("Backup CSV")
        print(f"✅ Removed: {backup_path}")
    
    if not removed:
        print("\n⚠️  No CSV files found to remove")
        print("   Next run will already be treated as first run")
    else:
        print(f"\n✅ Removed {len(removed)} file(s)")
        print("   Next run will be treated as first run (no tagging)")
    
    print("\n" + "=" * 60)
    print("Ready for fresh run!")
    print("=" * 60)
    print("\nRun: python scripts\\tests\\test_delta_analysis.py")

if __name__ == "__main__":
    main()

