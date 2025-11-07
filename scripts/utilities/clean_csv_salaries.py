"""
Quick script to clean salary columns in CSV files.
Removes dollar signs and commas from Min Salary and Max Salary columns.
"""
import pandas as pd
import sys
import os

def clean_salaries(input_file: str, output_file: str = None):
    """
    Clean salary columns in a CSV file.
    
    Args:
        input_file: Path to input CSV file
        output_file: Path to output CSV file (default: adds '_cleaned' to input filename)
    """
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found.")
        return False
    
    try:
        # Load the CSV
        print(f"Loading CSV from: {input_file}")
        df = pd.read_csv(input_file, encoding='utf-8')
        
        print(f"Found {len(df)} rows and {len(df.columns)} columns")
        
        # Check if salary columns exist
        if "Min Salary" not in df.columns:
            print("Warning: 'Min Salary' column not found")
        if "Max Salary" not in df.columns:
            print("Warning: 'Max Salary' column not found")
        
        # Clean Min Salary
        if "Min Salary" in df.columns:
            original_min = df["Min Salary"].copy()
            # Convert to string, remove $ and commas, convert back
            df["Min Salary"] = df["Min Salary"].astype(str).str.replace("$", "", regex=False).str.replace(",", "", regex=False)
            # Replace empty strings with NaN
            df["Min Salary"] = df["Min Salary"].replace("", None).replace("nan", None)
            # Convert to numeric
            df["Min Salary"] = pd.to_numeric(df["Min Salary"], errors='coerce')
            cleaned_count = sum(original_min.astype(str).str.contains("$|,", regex=True, na=False))
            if cleaned_count > 0:
                print(f"Cleaned {cleaned_count} Min Salary values")
        
        # Clean Max Salary
        if "Max Salary" in df.columns:
            original_max = df["Max Salary"].copy()
            # Convert to string, remove $ and commas, convert back
            df["Max Salary"] = df["Max Salary"].astype(str).str.replace("$", "", regex=False).str.replace(",", "", regex=False)
            # Replace empty strings with NaN
            df["Max Salary"] = df["Max Salary"].replace("", None).replace("nan", None)
            # Convert to numeric
            df["Max Salary"] = pd.to_numeric(df["Max Salary"], errors='coerce')
            cleaned_count = sum(original_max.astype(str).str.contains("$|,", regex=True, na=False))
            if cleaned_count > 0:
                print(f"Cleaned {cleaned_count} Max Salary values")
        
        # Determine output filename
        if output_file is None:
            base, ext = os.path.splitext(input_file)
            output_file = f"{base}_cleaned{ext}"
        
        # Save cleaned CSV
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"\nCleaned CSV saved to: {output_file}")
        print(f"Total rows: {len(df)}")
        
        # Show sample of cleaned salaries
        if "Min Salary" in df.columns or "Max Salary" in df.columns:
            print("\nSample of cleaned salary data:")
            salary_cols = [col for col in ["Min Salary", "Max Salary"] if col in df.columns]
            sample = df[salary_cols].head(10)
            print(sample.to_string())
        
        return True
        
    except Exception as e:
        print(f"Error processing file: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python clean_csv_salaries.py <input_file.csv> [output_file.csv]")
        print("\nExample:")
        print("  python clean_csv_salaries.py jobs.csv")
        print("  python clean_csv_salaries.py jobs.csv jobs_cleaned.csv")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = clean_salaries(input_file, output_file)
    if success:
        print("\n[SUCCESS] Cleaning completed successfully!")
    else:
        print("\n[ERROR] Cleaning failed. Please check the error messages above.")
        sys.exit(1)

