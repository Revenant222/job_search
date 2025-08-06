# AI Job Filter Agent - Technical Project Proposal

## Project Overview

An intelligent job filtering and verification system that reads job listings from Google Sheets, applies user-defined filters, verifies job posting validity through web scraping, and outputs results to a managed Google Sheets workspace for application tracking.

## Repository Architecture

### Recommended GitHub Structure
```
job-filter-agent/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── setup.py
├── config/
│   ├── __init__.py
│   ├── settings.py
│   └── google_credentials_template.json
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── streamlit_app.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── data_processor.py
│   │   ├── job_filter.py
│   │   ├── web_verifier.py
│   │   └── sheet_manager.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── fuzzy_matcher.py
│   │   ├── logger.py
│   │   └── validators.py
│   └── ui/
│       ├── __init__.py
│       ├── components.py
│       └── pages.py
├── data/
│   ├── csv_source/
│   └── csv_output/
├── logs/
├── tests/
│   ├── __init__.py
│   ├── test_data_processor.py
│   ├── test_job_filter.py
│   ├── test_web_verifier.py
│   └── test_sheet_manager.py
├── docs/
│   ├── setup_guide.md
│   ├── api_documentation.md
│   └── user_manual.md
└── examples/
    ├── sample_input.csv
    ├── sample_output_system_generated.csv
    └── sample_output_user_curated.csv
```

## Technical Specifications

### Core Technologies
- **Backend**: Python 3.9+
- **Frontend**: Streamlit
- **Data Processing**: pandas, numpy
- **Google Integration**: gspread, google-auth
- **Web Scraping**: requests, BeautifulSoup4
- **Fuzzy Matching**: fuzzywuzzy, python-Levenshtein
- **Logging**: python logging module
- **Testing**: pytest

### Key Dependencies
```
streamlit>=1.28.0
pandas>=2.0.0
gspread>=5.11.0
google-auth>=2.23.0
google-auth-oauthlib>=1.1.0
requests>=2.31.0
beautifulsoup4>=4.12.0
fuzzywuzzy>=0.18.0
python-Levenshtein>=0.21.0
python-dotenv>=1.0.0
urllib3>=2.0.0
pytest>=7.4.0
```

## Data Schema & Examples

### Input Data Structure (`examples/sample_input.csv`)
The system processes job data with the following 17-column structure:

```csv
Company Category,Company,Overall Job Category,Job Category,Title,Min Experience,Max Experience,Country,State,City,Location Type,JobType,Job Link,Activated Date,Skills,Min Salary,Max Salary
Gaming Company,Cloud Imperium Games,,,Executive Assistant,,,United Kingdom,England,Manchester,On Site,Full Time,https://cloudimperiumgames.wd1.myworkdayjobs.com/...,02 Aug 2025,"Excel, game texts, Multiplayer",,
Gaming Company,Devoteam,Engineering & Development,Devops,Azure Cloud Engineer,,,Netherlands,North Holland,Amsterdam,On Site,Full Time,https://jobs.smartrecruiters.com/devoteam/...,02 Aug 2025,"Agile Development, AWS, Azure, Azure DevOps, CI/CD, Docker, game texts, GitHub, Kubernetes, Podman, Terraform",,
```

**Key Observations from Sample Data:**
- **Experience Fields**: Can be numeric (2, 3, 5, 6, 7, 8) or empty
- **Salary Fields**: Mostly empty, one example shows "210000" for max salary
- **Skills**: Comma-separated lists, consistently include "game texts"
- **Geographic Data**: Mix of countries (US, UK, Netherlands, France, Japan, Singapore, India)
- **Location Types**: "On Site", "Remote", "Hybrid"
- **Job Categories**: Can be empty or contain hierarchical categories

### Output Data Structure

#### System Generated Output (`examples/sample_output_system_generated.csv`)
Complete data with all original columns plus verification metadata:

```csv
Company Category,Company,Overall Job Category,Job Category,Title,Min Experience,Max Experience,Country,State,City,Location Type,JobType,Job Link,Activated Date,Skills,Min Salary,Max Salary,Verification_Confidence,URL_Status_Code,Keywords_Found,Title_Match_Score,Job_Status,Date_Found,Last_Updated
Gaming Company,Cloud Imperium Games,,,Executive Assistant,,,United Kingdom,England,Manchester,On Site,Full Time,https://cloudimperiumgames.wd1.myworkdayjobs.com/...,02 Aug 2025,"Excel, game texts, Multiplayer",,,,,,,,,
```

**Added System Columns:**
- **Verification_Confidence**: None|Failed|Low|Medium|High
- **URL_Status_Code**: HTTP response code (200, 404, 500, etc.)
- **Keywords_Found**: List of matched keywords from verification
- **Title_Match_Score**: Fuzzy match percentage for job title
- **Job_Status**: NEW|Existing|Updated
- **Date_Found**: First discovery timestamp
- **Last_Updated**: Latest processing timestamp

#### User Curated Output (`examples/sample_output_user_curated.csv`)
Streamlined view with user-selected columns plus tracking fields:

```csv
Application_Status,Job_Status,Verification_Confidence,Company_Category,Job_Category,Job_Title,Job Link,Location_Type,Activated Date,Skills,Min Salary,Max Salary,Verification_Confidence,URL_Status_Code,Keywords_Found,Title_Match_Score,Job_Status,Date_Found,Last_Updated
Applied,,,,,,,,,,,,,,,,,,
Pending,,,,,,,,,,,,,,,,,,
Skipped,,,,,,,,,,,,,,,,,,
Not Selected,,,,,,,,,,,,,,,,,,
Closed,,,,,,,,,,,,,,,,,,
```

**User Management Columns:**
- **Application_Status**: Dropdown with 8 options (Applied, Pending, Skipped, Not Selected, Closed, Withdrawn, Offer Extended, Hired)
- **Job_Status**: System-managed (NEW|Existing|Updated) with color coding
- **User-Selected Columns**: Configurable subset of original data columns
- **Verification Metadata**: Duplicated from system tab for user convenience

**Note**: The sample shows some column duplication (Verification_Confidence appears twice) which will be cleaned up in implementation.

## Functional Requirements

### Fuzzy Matching Configuration

#### Default Thresholds (`config/settings.py`)
```python
FUZZY_MATCH_THRESHOLDS = {
    "title": 85,
    "skills": 70,
    "geography": 80,
}

# Centralized fuzzy matching utility
def fuzzy_match(input_str: str, candidates: list, threshold: int = 80) -> list:
    """Returns list of matches over threshold with scores"""
    pass
```

#### UI Controls
- **Threshold Sliders**: 0-100 range for each field type
- **Score Display**: Show match scores in Complete Data tab for transparency
- **Tooltips**: Explain tradeoffs (higher = stricter, lower = looser)

### Google API Authentication & Scopes

#### Required OAuth Scopes
```python
GOOGLE_API_SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',      # Read/write sheet data
    'https://www.googleapis.com/auth/drive.file'         # Create files in user's drive
]
```

#### Environment Configuration (`.env.example`)
```env
GOOGLE_SHEETS_SCOPES="https://www.googleapis.com/auth/spreadsheets,https://www.googleapis.com/auth/drive.file"
GOOGLE_CREDENTIALS_PATH=config/google_credentials.json
```

#### Credential Validation (`utils/validators.py`)
```python
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

def validate_credentials(creds: Credentials):
    """Validate and refresh Google API credentials"""
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise Exception("Invalid or expired Google API credentials.")
```

### User Interface Components

#### Streamlit's Role in V1
The Streamlit app serves as the primary user interface for:
- Loading and displaying filter configuration options dynamically
- Letting users input/select filters and connect Google Sheets
- Showing real-time progress bars and logs during processing
- Rendering results summaries and counts at completion

**V1 Limitations**: No state persistence between sessions, no background processing, no job scheduling.

#### 1. Filter Configuration Panel
- **Company Category**: Multi-select checkboxes (dynamically populated)
- **Overall Job Category**: Multi-select checkboxes (dynamically populated)  
- **Job Category**: Multi-select checkboxes (dynamically populated)
- **Location Type**: Multi-select checkboxes (dynamically populated)
- **Title Keywords**: Text input with fuzzy matching controls
- **Experience Range**: Numeric inputs (Min/Max, nullable)
- **Geography**: Text inputs with fuzzy matching for Country/State
- **Skills Keywords**: Text input with fuzzy matching
- **Salary Range**: Numeric inputs (Min/Max, nullable)
- **Fuzzy Match Thresholds**: Sliders for each field type

#### 2. Google Sheets Integration Panel
- Credential configuration interface
- Source sheet connection setup
- Output sheet creation and verification
- Column mapping and validation

#### 3. Processing Dashboard
- Real-time progress bars for data processing and web verification
- Job count summaries (Total → Filtered → Verified)
- Error logging display with expandable error panel
- Delta analysis results (New/Existing/Updated counts)

### Core Processing Modules

#### 1. Data Processor (`data_processor.py`)
```python
class DataProcessor:
    def __init__(self, credentials_path):
        # Initialize Google Sheets connection with validated credentials
        
    def download_source_data(self) -> pd.DataFrame:
        # Download and cache source data with timestamp
        # Store in csv_source/ with timestamp
        
    def generate_job_id(self, job_row: dict) -> str:
        # Create unique identifier: hash(company|title|location)
        # Avoid using URLs or volatile fields
        
    def analyze_filter_options(self, df: pd.DataFrame) -> dict:
        # Extract unique values for checkbox populations
        
    def apply_filters(self, df: pd.DataFrame, filters: dict) -> pd.DataFrame:
        # Apply user-defined filters with fuzzy matching
```

#### 2. Job Filter (`job_filter.py`)
```python
class JobFilter:
    def __init__(self, thresholds: dict = None):
        # Initialize with configurable fuzzy matching thresholds
        
    def filter_by_keywords(self, df: pd.DataFrame, column: str, keywords: list, threshold: int) -> pd.DataFrame:
        # Fuzzy keyword matching with score tracking
        
    def filter_by_range(self, df: pd.DataFrame, column: str, min_val: float, max_val: float) -> pd.DataFrame:
        # Numeric range filtering with null handling
        
    def filter_by_categories(self, df: pd.DataFrame, column: str, categories: list) -> pd.DataFrame:
        # Exact match categorical filtering
```

#### 3. Web Verifier (`web_verifier.py`)
```python
class WebVerifier:
    def __init__(self):
        # Initialize session with retry strategy and timeout
        self.session = self._setup_session_with_retries()
        
    def _setup_session_with_retries(self):
        # Configure requests session with HTTPAdapter and Retry strategy
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=1.5,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
        
    def verify_job_posting(self, job_link: str, job_title: str, keywords: list) -> dict:
        # **IMPORTANT**: Design for future parallel processing
        # This method must be stateless and thread-safe
        # Returns: {
        #     'confidence': 'None|Failed|Low|Medium|High',
        #     'url_status': int,
        #     'keywords_found': list,
        #     'title_match': bool,
        #     'title_match_score': float,
        #     'verification_date': datetime,
        #     'error': str (if applicable)
        # }
        
    def batch_verify_serial(self, jobs_df: pd.DataFrame) -> pd.DataFrame:
        # V1: Serial processing with progress tracking
        # V3+: Replace with parallel implementation
```

#### 4. Sheet Manager (`sheet_manager.py`)
```python
class SheetManager:
    def __init__(self, credentials_path):
        # Initialize Google Sheets API client with validated credentials
        
    def setup_output_sheet(self, template_columns: list) -> str:
        # Create and configure output sheet with proper formatting
        # Setup dropdown validation for Application_Status
        
    def read_existing_results(self, sheet_id: str) -> pd.DataFrame:
        # Load existing results for delta analysis
        
    def detect_changes(self, existing_job: dict, new_job: dict) -> bool:
        # Compare fields: title, location, salary, skills, categories
        # Ignore: URLs, post_date, application_status, notes
        
    def update_results(self, sheet_id: str, new_data: pd.DataFrame, existing_data: pd.DataFrame):
        # Perform delta updates with status preservation
        # Always preserve: Application_Status, Notes, Date_Found
        # Always update: Last_Updated timestamp
        
    def apply_conditional_formatting(self, sheet_id: str):
        # Color coding for NEW/Existing/Updated status
        # Sort by Job_Status (NEW/Updated at top)
```

### Delta Processing Logic

#### Unique Job Identification
```python
def generate_job_id(company: str, title: str, location: str) -> str:
    """Create reproducible hash from stable fields"""
    stable_key = f"{company.lower().strip()}|{title.lower().strip()}|{location.lower().strip()}"
    return hashlib.md5(stable_key.encode()).hexdigest()[:12]
```

#### Status Management
- **Application Status**: Dropdown with 8 options (Pending, Applied, Skipped, Closed, Not Selected, Offer Extended, Hired, Withdrawn)
- **Job Status**: System-managed (NEW, Existing, Updated)
- **Preservation Rule**: Never overwrite user-set Application_Status or Notes during updates

#### Change Detection
```python
def detect_changes(existing_job: dict, new_job: dict) -> bool:
    """Compare substantive fields only"""
    fields_to_check = ['title', 'min_salary', 'max_salary', 'skills', 'location', 'job_category']
    for field in fields_to_check:
        if existing_job.get(field) != new_job.get(field):
            return True
    return False
```

## Implementation Phases

### Phase 1: Core Data Processing (Weeks 1-2)
- Google Sheets API integration with proper authentication
- CSV fallback system with timestamped caching
- Basic filtering implementation with fuzzy matching
- Data validation and error handling
- Unique job ID generation system

### Phase 2: Web Verification System (Weeks 3-4)
- HTTP request handling with retry logic and timeouts
- Content parsing and keyword matching
- Confidence scoring algorithm
- **Serial processing only** with progress tracking
- Expandable error reporting panel

### Phase 3: Streamlit Interface (Weeks 5-6)
- Dynamic filter component generation
- Google credentials management UI
- Real-time processing dashboard with progress bars
- Results display and summary statistics
- Fuzzy matching threshold controls

### Phase 4: Delta Processing & Sheet Management (Weeks 7-8)
- Output sheet creation with proper formatting
- Delta analysis implementation with job ID tracking
- Status preservation logic
- Conditional formatting and sorting
- Two-tab output structure

### Phase 5: Testing & Documentation (Week 9)
- Comprehensive test suite
- User documentation with Google API setup guide
- Setup guides with OAuth scope explanations
- Performance optimization

## Retry & Backoff Strategy

### HTTP Request Strategy
- **Timeout**: 8 seconds per request
- **Retry Logic**: 3 attempts with exponential backoff (1.5s, 3s, 4.5s)
- **Retry Conditions**: Server errors only (500-504), not client errors (404)
- **Failure Handling**: Log and tag failures in output with error details

### Error Display
```python
# In Streamlit UI
with st.expander("View Verification Errors"):
    if failed_jobs_df is not None:
        st.table(failed_jobs_df[['company', 'title', 'error', 'url']])
```

## Output Sheet Structure

### Tab 1: User Curated Results
User-selected columns plus:
- **job_id**: Unique identifier (hidden from user view)
- **verification_confidence**: None|Failed|Low|Medium|High
- **application_status**: Dropdown (8 options)
- **job_status**: NEW|Existing|Updated (color-coded)
- **date_found**: First discovery timestamp
- **last_updated**: Latest verification timestamp
- **notes**: User-editable text field

### Tab 2: Complete System Data
All original columns from source sheet plus verification metadata:
- **job_id**: Unique identifier
- **url_status_code**: HTTP response code
- **keywords_found**: List of matched keywords
- **title_match_score**: Fuzzy match percentage
- **skills_match_scores**: Individual keyword match scores
- **geography_match_scores**: Location fuzzy match scores
- **verification_details**: JSON string with full verification data
- **error**: Error message if verification failed

## Error Handling & Logging

### Logging Strategy
- **Application Logs**: Stored in `logs/app_YYYYMMDD.log`
- **Error Logs**: Stored in `logs/error_YYYYMMDD.log`
- **Verification Logs**: Stored in `logs/verification_YYYYMMDD.log`

### Error Categories
1. **Google API Errors**: Credential issues, quota limits, network failures
2. **Web Scraping Errors**: Timeouts, blocked requests, parsing failures
3. **Data Processing Errors**: Invalid data formats, missing columns, type mismatches
4. **User Input Errors**: Invalid filters, malformed credentials, sheet access issues

## Security & Best Practices

### Credential Management
- Google credentials stored in user-specific files (not in repo)
- Environment variables for sensitive configuration
- OAuth scope validation with minimal required permissions
- Credential refresh handling

### Rate Limiting & Respectful Scraping
- 1-2 second delays between web requests (V1 serial processing)
- Google API quota monitoring
- Graceful degradation on API limits
- User agent rotation (future enhancement)

### Data Privacy
- No storage of job data beyond user-controlled sheets
- Local CSV caching with automatic cleanup
- User consent for data processing
- Minimal required OAuth scopes (`drive.file` not `drive`)

## Performance Considerations

### V1 Serial Processing
- **Expected Load**: ~300 jobs maximum per user session
- **Timeout Strategy**: 8 seconds per request
- **Maximum Runtime**: ~50 minutes worst case (typically much faster)
- **Progress Tracking**: Real-time UI updates with job-by-job progress

### Architecture for Future Parallel Processing (V3+)
- **Clean Method Boundaries**: `verify_job_posting(row) → result`
- **Stateless Design**: All verification methods thread-safe
- **Modular Structure**: Easy to replace serial batch processing with parallel

### Memory Management
- Stream processing for large datasets
- Timestamp-based CSV caching to avoid redundant API calls
- Configurable batch sizes for processing

## Success Metrics

### Functional Success
- Successfully filter 38K+ job dataset to <300 relevant positions
- >90% accuracy in web verification confidence scoring
- Zero data loss during delta updates
- Complete preservation of user application status
- Fuzzy matching accuracy within configured thresholds

### Performance Success (V1 Serial)
- Filter 38K jobs in <2 minutes
- Web verify 300 jobs in <50 minutes (typically <15 minutes)
- UI response time <3 seconds for all operations
- Memory usage <2GB during peak processing

## Google API Setup Guide

### Required Steps for Users
1. **Enable APIs**:
   - Google Sheets API: https://console.cloud.google.com/apis/library/sheets.googleapis.com
   - Google Drive API: https://console.cloud.google.com/apis/library/drive.googleapis.com

2. **Create OAuth Credentials**:
   - Go to: https://console.cloud.google.com/apis/credentials
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop App" as the app type
   - Download JSON and save as `config/google_credentials.json`

3. **Configure Environment**:
   ```env
   GOOGLE_SHEETS_SCOPES="https://www.googleapis.com/auth/spreadsheets,https://www.googleapis.com/auth/drive.file"
   GOOGLE_CREDENTIALS_PATH=config/google_credentials.json
   ```

### Scope Explanations
- **`spreadsheets`**: Read and write sheet data
- **`drive.file`**: Create/access only files created by this app (secure)
- **Avoid**: `drive` or `drive.readonly` (unnecessarily broad permissions)

## Risk Mitigation

### Technical Risks
- **Google API Changes**: Version pinning and comprehensive error handling
- **Website Blocking**: Retry strategies, respectful delays, user agent handling
- **Large Dataset Memory**: Streaming and chunked processing
- **Authentication Failures**: Clear setup documentation and validation

### User Experience Risks
- **Complex Setup**: Step-by-step Google API setup guide with screenshots
- **Data Loss**: Automated backups before each major operation
- **Performance Issues**: Progress indicators and realistic time estimates
- **Verification Accuracy**: Transparent fuzzy matching scores and confidence levels

## Future Enhancements

### V2 Features
- Save/load filter presets in Streamlit
- Enhanced error recovery and resume capability
- Advanced analytics dashboard
- Email notifications for new relevant jobs

### V3+ Features
- **Parallel Processing**: Replace serial verification with thread pools
- Machine learning for job relevance scoring
- Integration with job application tracking systems
- Mobile-responsive interface
- REST API for programmatic access

### Technical Improvements
- Containerization with Docker
- Cloud deployment options (Streamlit Cloud, AWS, etc.)
- Advanced caching strategies
- Real-time job monitoring and alerts

## Conclusion

This technical proposal outlines a comprehensive solution for automated job filtering and verification, designed with clear phase boundaries and future extensibility in mind. The V1 implementation focuses on core functionality with serial processing, while maintaining clean architecture for future parallel processing capabilities. The modular design ensures maintainability and the Google Sheets integration provides users with a familiar, powerful interface for managing their job search process.

The system addresses the core challenge of efficiently processing large job datasets (38K+ entries) while providing precise filtering to identify relevant opportunities (~50-300 jobs per user). With transparent fuzzy matching, comprehensive verification confidence scoring, and intelligent delta processing, users can maintain complete control over their application tracking workflow.