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
    
    def read_existing_results(self, sheet_id: str, range_name: str = "Sheet1!A1:Z") -> pd.DataFrame:
        """
        Read existing results from Google Sheet.
        
        Args:
            sheet_id: Google Sheets ID
            range_name: A1 notation range (e.g., "New Workbook!A8:Q")
                        Note: Using "A8:Q" will read all rows from row 8 onwards in columns A-Q.
                        If you want all rows, you can use "A8:Q" and it will automatically
                        read until the last row with data.
            
        Returns:
            DataFrame with existing results, or empty DataFrame if error
        """
        if not self.service:
            self.logger.error("Google Sheets service not initialized")
            return pd.DataFrame()
        
        try:
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
            
            # First row is headers
            headers = values[0] if values else []
            
            # Remaining rows are data
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
            
            self.logger.info(f"Successfully read {len(df)} rows from sheet")
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
