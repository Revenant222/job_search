"""
Google Sheets manager module for AI Job Filter Agent.
Handles reading from Google Sheets and delta analysis.
"""
import os
import pandas as pd
from typing import Dict, Any, Optional, List
from pathlib import Path
from config.settings import (
    GOOGLE_USE_SERVICE_ACCOUNT,
    GOOGLE_SERVICE_ACCOUNT_PATH,
    GOOGLE_CREDENTIALS_PATH,
    GOOGLE_SHEETS_SCOPES
)
from src.utils.logger import app_logger

try:
    from google.oauth2 import service_account
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False


class SheetManager:
    """
    Handles Google Sheets operations including reading and delta analysis.
    """
    
    def __init__(self, credentials_path: Optional[str] = None, csv_storage_dir: str = "data/csv_source"):
        """
        Initialize SheetManager.
        
        Args:
            credentials_path: Path to Google API credentials (optional, uses config if not provided)
            csv_storage_dir: Directory to store CSV files for delta comparison
        """
        self.credentials_path = credentials_path
        self.csv_storage_dir = csv_storage_dir
        self.logger = app_logger
        
        # Ensure CSV storage directory exists
        os.makedirs(self.csv_storage_dir, exist_ok=True)
        
        # Initialize Google Sheets service
        self.service = None
        self._initialize_service()
    
    def _initialize_service(self) -> bool:
        """Initialize Google Sheets API service."""
        if not GOOGLE_API_AVAILABLE:
            self.logger.error("Google API libraries not available. Install: pip install google-api-python-client google-auth")
            return False
        
        try:
            credentials = None
            
            # Auto-detect: prefer service account if file exists, otherwise check config
            service_account_path = self.credentials_path or GOOGLE_SERVICE_ACCOUNT_PATH
            oauth_path = self.credentials_path or GOOGLE_CREDENTIALS_PATH
            
            use_service_account = GOOGLE_USE_SERVICE_ACCOUNT
            
            # Auto-detect: if service account file exists and OAuth doesn't, use service account
            if not use_service_account:
                if os.path.exists(service_account_path) and not os.path.exists(oauth_path):
                    use_service_account = True
                    self.logger.info(f"Auto-detected service account credentials: {service_account_path}")
            
            if use_service_account:
                # Use service account authentication
                creds_path = service_account_path
                if not os.path.exists(creds_path):
                    self.logger.error(f"Service account credentials not found: {creds_path}")
                    return False
                
                # Use read-only scope for service account
                scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
                
                credentials = service_account.Credentials.from_service_account_file(
                    creds_path,
                    scopes=scopes
                )
                self.logger.info(f"Using service account: {credentials.service_account_email}")
            else:
                # Use OAuth2 authentication (for future use)
                creds_path = oauth_path
                if not os.path.exists(creds_path):
                    self.logger.error(f"OAuth credentials not found: {creds_path}")
                    # Try service account as fallback
                    if os.path.exists(service_account_path):
                        self.logger.info(f"Falling back to service account: {service_account_path}")
                        scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
                        credentials = service_account.Credentials.from_service_account_file(
                            service_account_path,
                            scopes=scopes
                        )
                        self.logger.info(f"Using service account: {credentials.service_account_email}")
                    else:
                        return False
                else:
                    # OAuth2 flow would go here (not implemented yet)
                    self.logger.warning("OAuth2 authentication not yet implemented")
                    return False
            
            # Build the service
            self.service = build('sheets', 'v4', credentials=credentials)
            self.logger.info("Google Sheets API service initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing Google Sheets service: {e}")
            return False
    
    def _detect_header_row(self, values: List[List[str]], max_rows_to_check: int = 30) -> int:
        """
        Automatically detect which row contains the headers by looking for common column names.
        
        Uses multiple heuristics:
        1. Matches common job-related column names
        2. Checks for row with many non-empty cells (headers typically have 5+ columns)
        3. Prefers rows that look like headers (mostly text, not numbers/dates)
        
        Args:
            values: List of rows from the sheet
            max_rows_to_check: Maximum number of rows to check (default: 30)
            
        Returns:
            Index of the header row (0-based), or 0 if not found
        """
        if not values:
            return 0
        
        # Common job-related column names to look for (case-insensitive)
        # Expanded list to catch more variations
        common_headers = [
            'company', 'title', 'city', 'country', 'state', 'location',
            'job link', 'joblink', 'url', 'link', 'activated date', 'date',
            'skills', 'salary', 'experience', 'job type', 'location type',
            'category', 'job category', 'company category', 'overall job category',
            'min experience', 'max experience', 'min salary', 'max salary',
            'jobtype', 'job_type', 'location_type', 'activated_date'
        ]
        
        best_match_row = 0
        best_match_score = 0
        
        # Check first N rows for header patterns
        rows_to_check = min(max_rows_to_check, len(values))
        
        for row_idx in range(rows_to_check):
            row = values[row_idx]
            if not row or len(row) == 0:
                continue
            
            # Convert row to lowercase strings for comparison
            row_lower = [str(cell).strip().lower() if cell else '' for cell in row]
            
            # Heuristic 1: Count how many cells match common header names
            match_score = 0
            matched_headers = set()
            for header in common_headers:
                for cell in row_lower:
                    if cell and (header in cell or cell in header):
                        matched_headers.add(header)
                        match_score += 2  # Higher weight for header matches
                        break  # Count each header only once per row
            
            # Heuristic 2: Check if row has many non-empty cells (headers typically have 5+ columns)
            non_empty_count = sum(1 for cell in row_lower if cell)
            if non_empty_count >= 5:  # Headers typically have 5+ columns
                match_score += 3
            elif non_empty_count >= 3:
                match_score += 1
            
            # Heuristic 3: Prefer rows where most cells are text (not numbers)
            # Headers are usually text, data rows often have numbers
            text_cells = 0
            for cell in row_lower:
                if cell:
                    # Check if it's likely text (contains letters, not just numbers)
                    if any(c.isalpha() for c in cell):
                        text_cells += 1
            
            if non_empty_count > 0:
                text_ratio = text_cells / non_empty_count
                if text_ratio > 0.7:  # 70%+ text suggests headers
                    match_score += 2
            
            # Prefer rows with higher match scores
            if match_score > best_match_score:
                best_match_score = match_score
                best_match_row = row_idx
        
        self.logger.info(f"Detected header row at index {best_match_row} (row {best_match_row + 1}) with score {best_match_score}")
        if best_match_score == 0:
            self.logger.warning("No clear header row detected, using first row as headers")
        
        return best_match_row
    
    def read_existing_results(self, sheet_id: str, range_name: str = None, 
                             auto_detect_headers: bool = True) -> pd.DataFrame:
        """
        Read existing results from Google Sheet with automatic header detection.
        
        When auto_detect_headers=True, always downloads from A1 to allow header detection.
        The header row is automatically detected by analyzing the first 30 rows for common
        job-related column names.
        
        Args:
            sheet_id: Google Sheets ID
            range_name: A1 notation range (e.g., "Sheet1!A1:Z"). 
                        If None, extracts sheet name from config and uses A1:Z.
                        If auto_detect_headers=True, range is forced to start from A1.
            auto_detect_headers: If True, automatically detects the header row by scanning
                                for common column names. Downloads from A1 regardless of range_name.
                                If False, uses the first row as headers.
            
        Returns:
            DataFrame with existing results, or empty DataFrame if error
        """
        if not self.service:
            self.logger.error("Google Sheets service not initialized")
            return pd.DataFrame()
        
        try:
            # Extract sheet name from config or range_name
            sheet_name = None
            
            if range_name is None:
                # Use config default to get sheet name, but always start from A1
                from config.settings import GOOGLE_SHEET_RANGE
                if '!' in GOOGLE_SHEET_RANGE:
                    sheet_name = GOOGLE_SHEET_RANGE.split('!')[0]
                else:
                    sheet_name = "Sheet1"
            elif '!' in range_name:
                # Extract sheet name from provided range
                sheet_name = range_name.split('!')[0]
            else:
                # No sheet name in range, use Sheet1
                sheet_name = "Sheet1"
            
            # When auto-detecting headers, always download from A1 to get full context
            if auto_detect_headers:
                # Use a wide range to capture all columns (A1:Z covers columns A-Z)
                # Google Sheets API will automatically stop at the last row with data
                range_name = f"{sheet_name}!A1:Z"
                self.logger.info(f"Auto-detecting headers: downloading from {range_name}")
            else:
                # Use provided range or construct from sheet name
                if range_name and '!' in range_name:
                    # Range already has sheet name, use as-is
                    pass
                else:
                    # Construct range with sheet name
                    if range_name and not range_name.startswith(sheet_name):
                        range_name = f"{sheet_name}!{range_name}"
                    elif not range_name:
                        range_name = f"{sheet_name}!A1:Z"
            
            self.logger.info(f"Reading from sheet {sheet_id}, range: {range_name}")
            
            # Read the data
            result = self.service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                self.logger.warning(f"No data found in range {range_name}")
                return pd.DataFrame()
            
            # Detect header row if auto-detection is enabled
            header_row_idx = 0
            if auto_detect_headers:
                header_row_idx = self._detect_header_row(values)
                headers = values[header_row_idx] if header_row_idx < len(values) else []
                # Data rows start after the header row
                data_rows = values[header_row_idx + 1:] if header_row_idx + 1 < len(values) else []
            else:
                # First row is headers (original behavior)
                headers = values[0] if values else []
                data_rows = values[1:] if len(values) > 1 else []
            
            # Create DataFrame
            if data_rows:
                # Ensure headers match data columns
                max_cols = max(len(row) for row in data_rows) if data_rows else len(headers)
                headers_padded = headers + [f"Column_{i}" for i in range(len(headers), max_cols)]
                df = pd.DataFrame(data_rows, columns=headers_padded[:max_cols])
            else:
                # No data rows, just headers
                df = pd.DataFrame(columns=headers)
            
            # Clean up: remove completely empty rows
            df = df.dropna(how='all')
            
            self.logger.info(f"Successfully read {len(df)} rows from sheet (header row: {header_row_idx + 1})")
            return df
            
        except HttpError as e:
            if e.resp.status == 403:
                self.logger.error(f"Permission denied. Make sure the sheet is shared with the service account.")
            elif e.resp.status == 404:
                self.logger.error(f"Sheet not found. Check the sheet ID: {sheet_id}")
            else:
                self.logger.error(f"HTTP error reading sheet: {e}")
            return pd.DataFrame()
        except Exception as e:
            self.logger.error(f"Error reading from sheet: {e}")
            return pd.DataFrame()
    
    def save_csv_for_delta(self, df: pd.DataFrame, filename: str = "sheet_data.csv", 
                          backup_filename: str = "diffed_backup.csv") -> str:
        """
        Save DataFrame to CSV file for delta comparison with rolling backup.
        
        Backup logic:
        - First run: Save as main CSV
        - Second run: Rename previous CSV to backup, save new CSV
        - Subsequent runs: Overwrite backup with previous CSV, save new CSV
        
        This maintains one backup file to avoid system bloat.
        
        Args:
            df: DataFrame to save
            filename: Name of the main CSV file
            backup_filename: Name of the backup CSV file
            
        Returns:
            Path to saved file, or empty string if failed
        """
        try:
            main_file_path = os.path.join(self.csv_storage_dir, filename)
            backup_file_path = os.path.join(self.csv_storage_dir, backup_filename)
            
            # Check if previous CSV exists
            if os.path.exists(main_file_path):
                # Previous CSV exists - this is not the first run
                # Move previous CSV to backup (overwrite if exists)
                if os.path.exists(backup_file_path):
                    os.remove(backup_file_path)
                os.rename(main_file_path, backup_file_path)
                self.logger.info(f"Moved previous CSV to backup: {backup_file_path}")
            
            # Save new CSV as main file
            df.to_csv(main_file_path, index=False, encoding='utf-8')
            self.logger.info(f"Saved CSV for delta comparison: {main_file_path}")
            return main_file_path
        except Exception as e:
            self.logger.error(f"Error saving CSV: {e}")
            return ""
    
    def load_previous_csv(self, filename: str = "sheet_data.csv") -> Optional[pd.DataFrame]:
        """
        Load previous CSV file for delta comparison.
        
        Args:
            filename: Name of the CSV file to load
            
        Returns:
            DataFrame if file exists, None otherwise
        """
        file_path = os.path.join(self.csv_storage_dir, filename)
        
        if not os.path.exists(file_path):
            self.logger.info(f"No previous CSV found at {file_path} - this is the first run")
            return None
        
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
            self.logger.info(f"Loaded previous CSV with {len(df)} rows from {file_path}")
            return df
        except Exception as e:
            self.logger.error(f"Error loading previous CSV: {e}")
            return None
    
    def _normalize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize column names to handle variations (case, spacing, etc.).
        
        Args:
            df: DataFrame with potentially inconsistent column names
            
        Returns:
            DataFrame with normalized column names
        """
        # Common column name mappings
        column_mappings = {
            # Company variations
            'company': 'Company',
            'COMPANY': 'Company',
            'Company Name': 'Company',
            'company_name': 'Company',
            
            # Title variations
            'title': 'Title',
            'TITLE': 'Title',
            'Job Title': 'Title',
            'job_title': 'Title',
            'Position': 'Title',
            'position': 'Title',
            
            # City variations
            'city': 'City',
            'CITY': 'City',
            'Location': 'City',
            'location': 'City',
        }
        
        # Normalize: lowercase, strip whitespace
        df.columns = df.columns.str.strip()
        
        # Apply mappings
        df = df.rename(columns=column_mappings)
        
        return df
    
    def detect_new_jobs(self, new_df: pd.DataFrame, previous_df: Optional[pd.DataFrame], 
                       id_columns: List[str] = None) -> pd.DataFrame:
        """
        Detect new jobs by comparing new DataFrame with previous one.
        
        Uses job_id if available, otherwise creates IDs from Company+Title+City.
        Handles column name variations automatically.
        
        Args:
            new_df: New DataFrame from sheet
            previous_df: Previous DataFrame from CSV (None if first run)
            id_columns: Columns to use for generating job IDs (default: Company, Title, City)
            
        Returns:
            DataFrame containing only new jobs
        """
        if previous_df is None or previous_df.empty:
            self.logger.info("No previous data - all jobs are new")
            return new_df.copy()
        
        if new_df.empty:
            self.logger.warning("New data is empty")
            return pd.DataFrame()
        
        # Normalize column names first
        new_df = self._normalize_column_names(new_df.copy())
        previous_df = self._normalize_column_names(previous_df.copy())
        
        # Generate job IDs if not present
        if 'job_id' not in new_df.columns:
            from src.core.data_processor import DataProcessor
            processor = DataProcessor()
            new_df = processor.add_job_ids(new_df)
            self.logger.info(f"Generated job_ids for new data: {len(new_df)} jobs")
        
        if 'job_id' not in previous_df.columns:
            from src.core.data_processor import DataProcessor
            processor = DataProcessor()
            previous_df = processor.add_job_ids(previous_df)
            self.logger.info(f"Generated job_ids for previous data: {len(previous_df)} jobs")
        
        # Debug: Check for missing key columns
        required_cols = ['Company', 'Title', 'City']
        new_missing = [col for col in required_cols if col not in new_df.columns]
        prev_missing = [col for col in required_cols if col not in previous_df.columns]
        
        if new_missing:
            self.logger.warning(f"New data missing columns: {new_missing}. Available: {list(new_df.columns)[:10]}")
            # Try to find similar column names
            for missing_col in new_missing:
                similar = [col for col in new_df.columns if missing_col.lower() in col.lower() or col.lower() in missing_col.lower()]
                if similar:
                    self.logger.info(f"  Found similar columns for '{missing_col}': {similar}")
        if prev_missing:
            self.logger.warning(f"Previous data missing columns: {prev_missing}. Available: {list(previous_df.columns)[:10]}")
            # Try to find similar column names
            for missing_col in prev_missing:
                similar = [col for col in previous_df.columns if missing_col.lower() in col.lower() or col.lower() in missing_col.lower()]
                if similar:
                    self.logger.info(f"  Found similar columns for '{missing_col}': {similar}")
        
        # Find new jobs (jobs in new_df but not in previous_df)
        new_job_ids = set(new_df['job_id'].astype(str).dropna())
        previous_job_ids = set(previous_df['job_id'].astype(str).dropna())
        
        self.logger.info(f"Comparison: {len(new_job_ids)} new job IDs, {len(previous_job_ids)} previous job IDs")
        
        new_job_ids_only = new_job_ids - previous_job_ids
        
        if not new_job_ids_only:
            self.logger.info("No new jobs detected - all jobs already exist")
            return pd.DataFrame()
        
        # Filter to only new jobs
        new_jobs_df = new_df[new_df['job_id'].astype(str).isin(new_job_ids_only)].copy()
        
        match_count = len(new_df) - len(new_jobs_df)
        match_rate = (match_count / len(new_df) * 100) if len(new_df) > 0 else 0
        
        self.logger.info(f"Detected {len(new_jobs_df)} new jobs out of {len(new_df)} total")
        self.logger.info(f"Match rate: {match_rate:.1f}% existing jobs ({match_count} matched, {len(new_jobs_df)} new)")
        
        return new_jobs_df
    
    def setup_output_sheet(self, template_columns: List[str]) -> str:
        """
        Create and configure output sheet.
        (Not implemented - using CSV instead)
        
        Args:
            template_columns: List of column names for the sheet
            
        Returns:
            Sheet ID of created sheet
        """
        self.logger.info("Output sheet creation not implemented - using CSV instead")
        return "placeholder_sheet_id"
    
    def detect_changes(self, existing_job: Dict[str, Any], new_job: Dict[str, Any]) -> bool:
        """
        Detect changes between existing and new job data.
        
        Args:
            existing_job: Existing job data
            new_job: New job data
            
        Returns:
            True if changes detected, False otherwise
        """
        # Simple comparison - can be enhanced later
        key_fields = ['Company', 'Title', 'City', 'Job Link']
        
        for field in key_fields:
            if str(existing_job.get(field, '')) != str(new_job.get(field, '')):
                return True
        
        return False
    
    def update_results(self, sheet_id: str, new_data: pd.DataFrame, existing_data: pd.DataFrame):
        """
        Update results in Google Sheets.
        (Not implemented - using CSV instead)
        
        Args:
            sheet_id: Google Sheets ID
            new_data: New job data
            existing_data: Existing job data
        """
        self.logger.info("Sheet updates not implemented - using CSV instead")
    
    def apply_conditional_formatting(self, sheet_id: str):
        """
        Apply conditional formatting to sheet.
        (Not implemented - using CSV instead)
        
        Args:
            sheet_id: Google Sheets ID
        """
        self.logger.info("Conditional formatting not implemented - using CSV instead")
