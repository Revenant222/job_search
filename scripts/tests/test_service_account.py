"""
Test script to verify Google Sheets service account connection.

This script tests:
1. Service account credentials can be loaded
2. Google Sheets API connection works
3. Can read from a test sheet (if provided)

Usage:
    python test_service_account.py [SHEET_ID] [RANGE]
    
Example:
    python test_service_account.py "1abc123def456" "Sheet1!A1:B10"
"""
import sys
import os
from pathlib import Path

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError as e:
    print(f"❌ Missing required package: {e}")
    print("\nPlease install required packages:")
    print("  pip install google-auth google-api-python-client")
    sys.exit(1)

# Configuration
SERVICE_ACCOUNT_FILE = "config/service_account_credentials.json"
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']


def test_credentials():
    """Test that service account credentials can be loaded."""
    print("=" * 60)
    print("TEST 1: Loading Service Account Credentials")
    print("=" * 60)
    
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"❌ ERROR: Credentials file not found: {SERVICE_ACCOUNT_FILE}")
        return None
    
    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        
        print(f"✅ Credentials loaded successfully")
        print(f"   Service Account Email: {credentials.service_account_email}")
        print(f"   Project ID: {credentials.project_id}")
        print(f"   Scopes: {', '.join(SCOPES)}")
        return credentials
    except Exception as e:
        print(f"❌ ERROR loading credentials: {e}")
        return None


def test_api_connection(credentials):
    """Test that Google Sheets API connection works."""
    print("\n" + "=" * 60)
    print("TEST 2: Google Sheets API Connection")
    print("=" * 60)
    
    try:
        service = build('sheets', 'v4', credentials=credentials)
        print("✅ Google Sheets API service built successfully")
        return service
    except Exception as e:
        print(f"❌ ERROR building API service: {e}")
        print("\nPossible issues:")
        print("  - Google Sheets API not enabled in GCP Console")
        print("  - Invalid credentials")
        return None


def test_sheet_access(service, sheet_id, credentials, range_name="Sheet1!A1:A1"):
    """Test reading from a specific sheet."""
    print("\n" + "=" * 60)
    print("TEST 3: Sheet Access Test")
    print("=" * 60)
    print(f"   Sheet ID: {sheet_id}")
    print(f"   Range: {range_name}")
    
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id, 
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        print(f"✅ Successfully accessed sheet!")
        print(f"   Retrieved {len(values)} row(s)")
        
        if values:
            print(f"\n   Sample data (first row):")
            print(f"   {values[0]}")
        
        return True
    except HttpError as e:
        if e.resp.status == 403:
            print(f"❌ PERMISSION DENIED")
            print(f"\n   Error: {e}")
            print("\n   Possible causes:")
            print("   1. Sheet not shared with service account")
            print(f"   2. Service account email: {credentials.service_account_email}")
            print("   3. Check sheet sharing permissions")
        elif e.resp.status == 404:
            print(f"❌ SHEET NOT FOUND")
            print(f"\n   Error: {e}")
            print("\n   Possible causes:")
            print("   1. Invalid Sheet ID")
            print("   2. Sheet doesn't exist")
        else:
            print(f"❌ ERROR accessing sheet: {e}")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def get_sheet_info(service, sheet_id):
    """Get basic information about the sheet."""
    print("\n" + "=" * 60)
    print("TEST 4: Sheet Information")
    print("=" * 60)
    
    try:
        sheet_metadata = service.spreadsheets().get(
            spreadsheetId=sheet_id
        ).execute()
        
        print(f"✅ Sheet Information Retrieved")
        print(f"   Title: {sheet_metadata.get('properties', {}).get('title', 'N/A')}")
        print(f"   Sheets: {len(sheet_metadata.get('sheets', []))}")
        
        for sheet in sheet_metadata.get('sheets', []):
            props = sheet.get('properties', {})
            print(f"     - {props.get('title', 'N/A')} (ID: {props.get('sheetId', 'N/A')})")
        
        return True
    except HttpError as e:
        if e.resp.status == 403:
            print(f"❌ PERMISSION DENIED - Cannot read sheet metadata")
        else:
            print(f"❌ ERROR: {e}")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Google Sheets Service Account Connection Test")
    print("=" * 60)
    print(f"\nCredentials file: {SERVICE_ACCOUNT_FILE}")
    print(f"Scopes: {', '.join(SCOPES)}")
    
    # Test 1: Load credentials
    credentials = test_credentials()
    if not credentials:
        print("\n❌ Cannot proceed without valid credentials")
        sys.exit(1)
    
    # Test 2: Build API service
    service = test_api_connection(credentials)
    if not service:
        print("\n❌ Cannot proceed without API connection")
        sys.exit(1)
    
    # Test 3 & 4: Test sheet access (if sheet ID provided)
    if len(sys.argv) > 1:
        sheet_id = sys.argv[1]
        range_name = sys.argv[2] if len(sys.argv) > 2 else "Sheet1!A1:A1"
        
        # Test sheet access
        access_ok = test_sheet_access(service, sheet_id, credentials, range_name)
        
        # Get sheet info
        if access_ok:
            get_sheet_info(service, sheet_id)
        
        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        if access_ok:
            print("✅ All tests passed! Service account is configured correctly.")
        else:
            print("⚠️  Credentials and API connection work, but sheet access failed.")
            print("   Make sure the sheet is shared with:")
            print(f"   {credentials.service_account_email}")
    else:
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print("✅ Credentials and API connection verified!")
        print("\nTo test sheet access, provide a Sheet ID:")
        print("  python test_service_account.py <SHEET_ID> [RANGE]")
        print("\nExample:")
        print("  python test_service_account.py \"1abc123def456\" \"Sheet1!A1:B10\"")


if __name__ == "__main__":
    main()

