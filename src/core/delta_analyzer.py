"""
Delta analysis module for detecting new jobs and applying tags.
"""
import os
import shutil
import pandas as pd
from typing import Optional, Tuple
from src.core.sheet_manager import SheetManager
from src.core.job_tagger import JobTagger
from src.core.data_processor import DataProcessor
from config.settings import (
    GOOGLE_SHEET_ID,
    GOOGLE_SHEET_RANGE,
    GOOGLE_SHEET_CSV_FILENAME
)
from src.utils.logger import app_logger


class DeltaAnalyzer:
    """
    Handles delta analysis: pulling from Google Sheets, comparing with previous data,
    and tagging new jobs.
    """
    
    def __init__(self, sheet_manager: Optional[SheetManager] = None, 
                 job_tagger: Optional[JobTagger] = None,
                 data_processor: Optional[DataProcessor] = None):
        """
        Initialize DeltaAnalyzer.
        
        Args:
            sheet_manager: SheetManager instance (creates new if not provided)
            job_tagger: JobTagger instance (creates new if not provided)
            data_processor: DataProcessor instance (creates new if not provided)
        """
        self.sheet_manager = sheet_manager or SheetManager()
        self.job_tagger = job_tagger or JobTagger()
        self.data_processor = data_processor or DataProcessor()
        self.logger = app_logger
    
    def pull_and_analyze(self, sheet_id: str = None, range_name: str = None,
                        csv_filename: str = None, tag_new_jobs: bool = True) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Pull data from Google Sheet, compare with previous CSV, and tag new jobs.
        
        Args:
            sheet_id: Google Sheet ID (uses config default if not provided)
            range_name: Range to read (uses config default if not provided)
            csv_filename: CSV filename for storage (uses config default if not provided)
            tag_new_jobs: Whether to automatically tag new jobs with "NEW" tag
            
        Returns:
            Tuple of (all_jobs_df, new_jobs_df)
        """
        # Use defaults from config if not provided
        sheet_id = sheet_id or GOOGLE_SHEET_ID
        range_name = range_name or GOOGLE_SHEET_RANGE
        csv_filename = csv_filename or GOOGLE_SHEET_CSV_FILENAME
        
        self.logger.info(f"Starting delta analysis for sheet {sheet_id}")
        
        # Step 1: Pull data from Google Sheet
        self.logger.info(f"Pulling data from sheet, range: {range_name}")
        new_df = self.sheet_manager.read_existing_results(sheet_id, range_name)
        
        if new_df.empty:
            self.logger.warning("No data retrieved from sheet")
            return pd.DataFrame(), pd.DataFrame()
        
        self.logger.info(f"Retrieved {len(new_df)} rows from sheet")
        
        # Step 2: Add job IDs if not present
        if 'job_id' not in new_df.columns:
            new_df = self.data_processor.add_job_ids(new_df)
        
        # Step 3: Load previous CSV for comparison
        previous_df = self.sheet_manager.load_previous_csv(csv_filename)
        
        # Step 3.5: Backup tag file before making changes (if not first run)
        # Consider it first run if no previous CSV exists OR if previous CSV is empty
        is_first_run = previous_df is None or previous_df.empty
        if not is_first_run:
            self._backup_tag_file()
        
        # Step 4: Detect new jobs
        new_jobs_df = self.sheet_manager.detect_new_jobs(new_df, previous_df)
        
        # Step 5: Tag new jobs with "NEW" tag (only on subsequent runs, not first run)
        if tag_new_jobs and not is_first_run and not new_jobs_df.empty:
            self.logger.info(f"Tagging {len(new_jobs_df)} new jobs with 'NEW' tag")
            for _, job in new_jobs_df.iterrows():
                job_id = str(job.get('job_id', ''))
                if job_id:
                    self.job_tagger.add_tag(job_id, "NEW")
        elif is_first_run:
            self.logger.info("First run: Skipping tag assignment (no previous data to compare)")
        
        # Step 6: Save current data as new baseline CSV (handles backup automatically)
        self.sheet_manager.save_csv_for_delta(new_df, csv_filename)
        
        # Step 7: Summary
        if is_first_run:
            self.logger.info(f"First run: Saved {len(new_df)} jobs as baseline")
        else:
            self.logger.info(f"Delta analysis complete: {len(new_jobs_df)} new jobs out of {len(new_df)} total")
        
        return new_df, new_jobs_df
    
    def get_new_jobs_count(self) -> int:
        """Get count of jobs with 'NEW' tag."""
        return len(self.job_tagger.get_jobs_with_tag("NEW"))
    
    def _backup_tag_file(self) -> bool:
        """
        Backup tag file before making changes (rolling backup, same as CSV).
        
        Returns:
            True if successful
        """
        try:
            tags_file = self.job_tagger.tags_file
            backup_file = tags_file.replace('.json', '_backup.json')
            
            if os.path.exists(tags_file):
                # Remove old backup if exists
                if os.path.exists(backup_file):
                    os.remove(backup_file)
                
                # Copy current to backup
                shutil.copy2(tags_file, backup_file)
                self.logger.info(f"Backed up tag file: {backup_file}")
                return True
            else:
                self.logger.info("No existing tag file to backup")
                return True
        except Exception as e:
            self.logger.error(f"Error backing up tag file: {e}")
            return False
    
    def clear_new_tags(self) -> bool:
        """
        Remove 'NEW' tag from all jobs (useful after reviewing new jobs).
        
        Returns:
            True if successful
        """
        new_job_ids = self.job_tagger.get_jobs_with_tag("NEW")
        count = len(new_job_ids)
        
        for job_id in new_job_ids:
            self.job_tagger.remove_tag(job_id, "NEW")
        
        self.logger.info(f"Cleared 'NEW' tag from {count} jobs")
        return True

