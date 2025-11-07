"""
Quick utility to extract Google Sheet ID from a URL.

Usage:
    python extract_sheet_id.py "https://docs.google.com/spreadsheets/d/1abc123/edit"
    
Or just run it and paste the URL when prompted.
"""
import sys
import re


def extract_sheet_id(url: str) -> str:
    """
    Extract Google Sheet ID from a URL.
    
    Supports various URL formats:
    - https://docs.google.com/spreadsheets/d/SHEET_ID/edit
    - https://docs.google.com/spreadsheets/d/SHEET_ID/edit#gid=0
    - https://docs.google.com/spreadsheets/d/SHEET_ID
    """
    # Pattern to match Sheet ID (between /d/ and / or ? or end of string)
    pattern = r'/spreadsheets/d/([a-zA-Z0-9-_]+)'
    match = re.search(pattern, url)
    
    if match:
        return match.group(1)
    else:
        # Try alternative pattern if the first doesn't match
        pattern2 = r'/d/([a-zA-Z0-9-_]+)'
        match2 = re.search(pattern2, url)
        if match2:
            return match2.group(1)
        raise ValueError("Could not extract Sheet ID from URL")


def main():
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        print("Enter your Google Sheets URL:")
        url = input().strip()
    
    try:
        sheet_id = extract_sheet_id(url)
        print("\n" + "=" * 60)
        print("Google Sheet ID:")
        print("=" * 60)
        print(f"\n{sheet_id}\n")
        print("=" * 60)
        print("\nUse this ID with the test script:")
        print(f"  python test_service_account.py \"{sheet_id}\" \"Sheet1!A1:B10\"")
        print("\nOr use it in your code/config as needed.")
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure your URL looks like:")
        print("  https://docs.google.com/spreadsheets/d/SHEET_ID/edit")
        sys.exit(1)


if __name__ == "__main__":
    main()

