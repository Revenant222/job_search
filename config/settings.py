"""
Configuration settings for AI Job Filter Agent.
"""
import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Fuzzy Matching Configuration
FUZZY_MATCH_THRESHOLDS = {
    "title": int(os.getenv("FUZZY_TITLE_THRESHOLD", 85)),
    "skills": int(os.getenv("FUZZY_SKILLS_THRESHOLD", 70)),
    "geography": int(os.getenv("FUZZY_GEOGRAPHY_THRESHOLD", 80)),
}

# Web Scraping Configuration
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 8))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))
RETRY_DELAY = float(os.getenv("RETRY_DELAY", 1.5))

# Google API Configuration
# Use service account if configured, otherwise use OAuth2
GOOGLE_USE_SERVICE_ACCOUNT = os.getenv("GOOGLE_USE_SERVICE_ACCOUNT", "False").lower() == "true"

GOOGLE_SHEETS_SCOPES = os.getenv(
    "GOOGLE_SHEETS_SCOPES",
    "https://www.googleapis.com/auth/spreadsheets.readonly" if GOOGLE_USE_SERVICE_ACCOUNT 
    else "https://www.googleapis.com/auth/spreadsheets,https://www.googleapis.com/auth/drive.file"
).split(",")

# OAuth2 credentials (for user-based authentication)
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "config/google_credentials.json")

# Service account credentials (for automated/background access)
GOOGLE_SERVICE_ACCOUNT_PATH = os.getenv("GOOGLE_SERVICE_ACCOUNT_PATH", "config/service_account_credentials.json")

# Google Sheets Configuration
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "1ZOJpVS3CcnrkwhpRgkP7tzf3wc4OWQj-uoWFfv4oHZE")
GOOGLE_SHEET_RANGE = os.getenv("GOOGLE_SHEET_RANGE", "New Workbook!A8:Q")
GOOGLE_SHEET_CSV_FILENAME = os.getenv("GOOGLE_SHEET_CSV_FILENAME", "sheet_data.csv")

# Application Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"

# Data Processing Configuration
CSV_ENCODING = "utf-8"
CSV_DELIMITER = ","
MAX_JOBS_PER_SESSION = 300

# Output Configuration
OUTPUT_COLUMNS = [
    "Company Category", "Company", "Overall Job Category", "Job Category",
    "Title", "Min Experience", "Max Experience", "Country", "State", "City",
    "Location Type", "JobType", "Job Link", "Activated Date", "Skills",
    "Min Salary", "Max Salary"
]

VERIFICATION_COLUMNS = [
    "Verification_Confidence", "URL_Status_Code", "Keywords_Found",
    "Title_Match_Score", "Job_Status", "Date_Found", "Last_Updated"
]

USER_CURATED_COLUMNS = [
    "Application_Status", "Job_Status", "Verification_Confidence",
    "Company_Category", "Job_Category", "Job_Title", "Job Link",
    "Location_Type", "Activated Date", "Skills", "Min Salary", "Max Salary"
]

# Application Status Options
APPLICATION_STATUS_OPTIONS = [
    "Applied", "Pending", "Skipped", "Not Selected", "Closed",
    "Withdrawn", "Offer Extended", "Hired"
]

# Verification Confidence Levels
VERIFICATION_CONFIDENCE_LEVELS = ["None", "Failed", "Low", "Medium", "High"]

# Job Status Options
JOB_STATUS_OPTIONS = ["NEW", "Existing", "Updated"]

def get_config() -> Dict[str, Any]:
    """Get all configuration settings as a dictionary."""
    return {
        "fuzzy_match_thresholds": FUZZY_MATCH_THRESHOLDS,
        "request_timeout": REQUEST_TIMEOUT,
        "max_retries": MAX_RETRIES,
        "retry_delay": RETRY_DELAY,
        "google_use_service_account": GOOGLE_USE_SERVICE_ACCOUNT,
        "google_sheets_scopes": GOOGLE_SHEETS_SCOPES,
        "google_credentials_path": GOOGLE_CREDENTIALS_PATH,
        "google_service_account_path": GOOGLE_SERVICE_ACCOUNT_PATH,
        "google_sheet_id": GOOGLE_SHEET_ID,
        "google_sheet_range": GOOGLE_SHEET_RANGE,
        "google_sheet_csv_filename": GOOGLE_SHEET_CSV_FILENAME,
        "log_level": LOG_LEVEL,
        "debug_mode": DEBUG_MODE,
        "csv_encoding": CSV_ENCODING,
        "csv_delimiter": CSV_DELIMITER,
        "max_jobs_per_session": MAX_JOBS_PER_SESSION,
        "output_columns": OUTPUT_COLUMNS,
        "verification_columns": VERIFICATION_COLUMNS,
        "user_curated_columns": USER_CURATED_COLUMNS,
        "application_status_options": APPLICATION_STATUS_OPTIONS,
        "verification_confidence_levels": VERIFICATION_CONFIDENCE_LEVELS,
        "job_status_options": JOB_STATUS_OPTIONS,
    } 