"""
Helper script to restore the backup CSV as the main CSV.
Useful for testing delta analysis multiple times.
"""
import os
import shutil
from src.core.sheet_manager import SheetManager
from config.settings import GOOGLE_SHEET_CSV_FILENAME

def main():
    print("=" * 60)
    print("Restore Backup CSV")
    print("=" * 60)
    
    sheet_mgr = SheetManager()
    main_path = os.path.join(sheet_mgr.csv_storage_dir, GOOGLE_SHEET_CSV_FILENAME)
    backup_path = os.path.join(sheet_mgr.csv_storage_dir, "diffed_backup.csv")
    
    print(f"\nMain CSV: {main_path}")
    print(f"Backup CSV: {backup_path}")
    
    if not os.path.exists(backup_path):
        print("\n❌ No backup CSV found!")
        print("   Nothing to restore.")
        return
    
    if os.path.exists(main_path):
        print(f"\n⚠️  Main CSV exists - will be overwritten")
        response = input("   Continue? (y/n): ")
        if response.lower() != 'y':
            print("   Cancelled.")
            return
    
    # Copy backup to main
    shutil.copy2(backup_path, main_path)
    print(f"\n✅ Restored backup CSV to main CSV")
    print(f"   {backup_path} → {main_path}")
    
    # Show file sizes
    main_size = os.path.getsize(main_path) / 1024  # KB
    print(f"\n📊 File info:")
    print(f"   Main CSV: {main_size:.1f} KB")
    
    print("\n" + "=" * 60)
    print("Ready to test delta analysis again!")
    print("=" * 60)

if __name__ == "__main__":
    main()

