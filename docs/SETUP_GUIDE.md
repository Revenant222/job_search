# Setup Guide for Job Search Application

## Prerequisites

- Python 3.9 or higher (Current: 3.12.5 ✓)
- Git
- Google Cloud Platform account (for Google Sheets integration - optional)

## Setup Steps

### 1. Virtual Environment (Already Created ✓)

The virtual environment has been created at `.venv`. To activate it:

**Windows PowerShell:**
```powershell
.venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**
```cmd
.venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

### 2. Dependencies (Already Installed ✓)

All dependencies from `requirements.txt` have been installed:
- Streamlit 1.51.0
- Pandas 2.3.3
- Google Sheets API libraries
- And more...

### 3. Environment Configuration (Optional)

The application uses `python-dotenv` to load environment variables. Create a `.env` file in the project root if you want to customize settings:

```
FUZZY_TITLE_THRESHOLD=85
FUZZY_SKILLS_THRESHOLD=70
FUZZY_GEOGRAPHY_THRESHOLD=80
REQUEST_TIMEOUT=8
MAX_RETRIES=3
RETRY_DELAY=1.5
GOOGLE_CREDENTIALS_PATH=config/google_credentials.json
LOG_LEVEL=INFO
DEBUG_MODE=False
```

### 4. Google Sheets Integration (Optional)

You can use either **OAuth2** (for interactive apps) or **Service Account** (for automated/background access).

#### Option A: OAuth2 (User-Based Authentication)

Best for interactive applications where users need to authenticate:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Sheets API and Google Drive API
4. Create OAuth2 credentials (Desktop application)
5. Download the credentials JSON file
6. Save it as `config/google_credentials.json`
   - Or update `GOOGLE_CREDENTIALS_PATH` in your `.env` file

The template for the credentials file structure is available at `config/google_credentials_template.json`.

#### Option B: Service Account (Automated Access)

Best for automated/background jobs and read-only access:

**📖 Complete Step-by-Step Walkthrough:** See [Google Service Account Setup Walkthrough](GOOGLE_SERVICE_ACCOUNT_SETUP_WALKTHROUGH.md) for detailed instructions with screenshots and direct links.

**Quick Summary:**
1. Create a project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the Google Sheets API for that project
3. Create a service account in the project
4. Download the JSON key file and save it as `config/service_account_credentials.json`
5. Share your Google Sheet with the service account email (Viewer permission)
6. Configure your `.env` file:
   ```env
   GOOGLE_USE_SERVICE_ACCOUNT=true
   GOOGLE_SERVICE_ACCOUNT_PATH=config/service_account_credentials.json
   GOOGLE_SHEETS_SCOPES=https://www.googleapis.com/auth/spreadsheets.readonly
   ```

**Quick Answer**: For view-only sheets, you don't need special GCP roles - just share the sheet with the service account email and use the `spreadsheets.readonly` scope.

**For detailed instructions with screenshots and troubleshooting:** See [GOOGLE_SERVICE_ACCOUNT_SETUP_WALKTHROUGH.md](GOOGLE_SERVICE_ACCOUNT_SETUP_WALKTHROUGH.md)

## Running the Application

### Streamlit App

With the virtual environment activated:

```powershell
streamlit run src/streamlit_app.py
```

Or use the main entry point:

```powershell
python src/main.py
```

The app will open in your default web browser at `http://localhost:8501`.

### Command Line Tool

The application can also be run as a command-line tool (if configured):

```powershell
job-filter-agent
```

## Verification

To verify everything is set up correctly:

```powershell
# Activate virtual environment
.venv\Scripts\Activate.ps1

# Verify Python and Streamlit
python -c "import streamlit; print('Streamlit:', streamlit.__version__)"

# Test app import
python -c "from src.streamlit_app import main; print('✓ App imports successfully')"
```

## Project Structure

```
job_search/
├── .venv/                  # Virtual environment (don't commit)
├── config/                 # Configuration files
│   ├── settings.py         # Application settings
│   └── *_template.json     # Credential templates
├── data/                   # Data storage
│   ├── csv_source/         # Source CSV files (from Google Sheets)
│   ├── csv_output/         # Generated CSV outputs
│   └── examples/           # Example CSV files
├── docs/                    # User-facing documentation
│   ├── SETUP_GUIDE.md      # This file
│   ├── CSV_FORMAT_GUIDE.md # CSV format documentation
│   └── ...                 # Other guides
├── scripts/                 # Utility and test scripts
│   ├── batch/              # Batch/PowerShell scripts
│   ├── tests/              # Test scripts
│   └── utilities/          # Utility scripts
├── src/                    # Source code
│   ├── core/              # Core functionality
│   ├── ui/                # UI components
│   ├── utils/             # Utility functions
│   ├── main.py            # Entry point
│   └── streamlit_app.py   # Streamlit application
├── tests/                  # Unit tests
├── requirements.txt        # Python dependencies
└── setup.py               # Package setup
```

## Troubleshooting

### Virtual Environment Issues

If you encounter activation issues:
- PowerShell may require execution policy changes: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- Try using the `.bat` file instead: `.venv\Scripts\activate.bat`

### Import Errors

If you get import errors:
1. Make sure the virtual environment is activated
2. Verify dependencies are installed: `pip list`
3. Reinstall if needed: `pip install -r requirements.txt`

### Google Sheets Authentication

If Google Sheets features don't work:
1. Verify the credentials file exists at the configured path
2. Check that the credentials are valid and not expired
3. Ensure the required APIs are enabled in Google Cloud Console

## Next Steps

- Run the Streamlit app to explore the UI
- Upload a CSV file with job data to test filtering
- Configure Google Sheets integration if needed (see [Google Service Account Setup Walkthrough](GOOGLE_SERVICE_ACCOUNT_SETUP_WALKTHROUGH.md))
- Review the project documentation in `docs/` folder

## Support

For issues or questions:
- Check the README.md for project overview
- Review the documentation in `docs/` folder
- See [CSV Format Guide](CSV_FORMAT_GUIDE.md) for CSV formatting help
- See [Quick Fix Guide](QUICK_FIX_GUIDE.md) for common issues

