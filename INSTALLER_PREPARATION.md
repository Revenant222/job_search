# Installer Preparation Checklist

## What Needs to Be Done in Main Repository

### ✅ Already Done
- [x] Repository structure is organized
- [x] `requirements.txt` is complete and accurate
- [x] `.gitignore` properly configured
- [x] Documentation is in place (`docs/` folder)
- [x] Template files exist (`config/*_template.json`)

### 🔧 Still Needed

#### 1. Create `.env.example` File
**Purpose**: Template for users to create their own `.env` file

**File**: `.env.example` (in root)

**Content**:
```env
# Fuzzy Matching Thresholds
FUZZY_TITLE_THRESHOLD=85
FUZZY_SKILLS_THRESHOLD=70
FUZZY_GEOGRAPHY_THRESHOLD=80

# Web Scraping Configuration
REQUEST_TIMEOUT=8
MAX_RETRIES=3
RETRY_DELAY=1.5

# Google API Configuration
# Set to 'true' to use Service Account, 'false' for OAuth2
GOOGLE_USE_SERVICE_ACCOUNT=false

# Service Account Path (if using service account)
GOOGLE_SERVICE_ACCOUNT_PATH=config/service_account_credentials.json

# OAuth2 Credentials Path (if using OAuth2)
GOOGLE_CREDENTIALS_PATH=config/google_credentials.json

# Google Sheets API Scopes
# For service account (read-only): https://www.googleapis.com/auth/spreadsheets.readonly
# For OAuth2 (read-write): https://www.googleapis.com/auth/spreadsheets,https://www.googleapis.com/auth/drive.file
GOOGLE_SHEETS_SCOPES=https://www.googleapis.com/auth/spreadsheets.readonly

# Google Sheet Configuration
GOOGLE_SHEET_ID=1ZOJpVS3CcnrkwhpRgkP7tzf3wc4OWQj-uoWFfv4oHZE
GOOGLE_SHEET_RANGE=New Workbook!A8:Q
GOOGLE_SHEET_CSV_FILENAME=sheet_data.csv

# Application Configuration
LOG_LEVEL=INFO
DEBUG_MODE=False
```

**Why**: Installer can copy this to `.env` for users, giving them a starting template.

#### 2. Ensure Repository is Publicly Accessible
**Options**:
- **Option A**: Make main repo public on GitHub
- **Option B**: Create GitHub Releases (installer downloads release zip)
- **Option C**: Use a public mirror/backup

**Recommended**: Option B (Releases) - gives version control and doesn't require public repo

**Action**: Create a release tag (e.g., `v1.0.0`) when ready

#### 3. Add Version Information
**File**: `src/__init__.py` or create `VERSION.txt`

**Content**:
```python
# src/__init__.py
__version__ = "1.0.0"
```

**Why**: Installer can check version and prompt for updates.

#### 4. Create Installer-Friendly Entry Point
**File**: `scripts/batch/run_app.bat` (already exists, but verify)

**Verify it works standalone**:
```batch
@echo off
cd /d "%~dp0\..\.."
call .venv\Scripts\activate.bat
streamlit run src\streamlit_app.py
pause
```

**Why**: Installer will create shortcuts pointing to this.

#### 5. Add Installer Metadata (Optional)
**File**: `installer_config.json` (optional, for installer to read)

**Content**:
```json
{
    "app_name": "Job Search Application",
    "version": "1.0.0",
    "min_python_version": "3.9",
    "default_install_dir": "job_search_app",
    "repo_url": "https://github.com/Revenant222/job_search.git",
    "release_url": "https://github.com/Revenant222/job_search/releases/latest",
    "main_entry_point": "src/streamlit_app.py",
    "run_script": "scripts/batch/run_app.bat"
}
```

**Why**: Installer can read this for configuration instead of hardcoding.

#### 6. Test Clone/Download Process
**Actions**:
- [ ] Test cloning repo: `git clone <repo_url>`
- [ ] Test downloading release zip (if using releases)
- [ ] Verify all necessary files are included
- [ ] Test that `.venv` is NOT included (should be gitignored)
- [ ] Test that sensitive files are NOT included (`.env`, credentials)

#### 7. Update README for Installer Users
**Add section to README.md**:

```markdown
## 🚀 Quick Start (Using Installer)

1. Download `setup_wizard.exe` from [Releases](link)
2. Run the installer
3. Follow the on-screen instructions
4. Launch the application from the created shortcut

For manual setup, see [Setup Guide](docs/SETUP_GUIDE.md)
```

## Repository Structure Verification

Ensure these are present and correct:
- ✅ `requirements.txt` - All dependencies listed
- ✅ `README.md` - User-facing documentation
- ✅ `docs/` - All user guides
- ✅ `config/*_template.json` - Template files
- ✅ `src/` - All source code
- ✅ `scripts/batch/run_app.bat` - Launcher script
- ✅ `.gitignore` - Properly configured

Ensure these are NOT included (gitignored):
- ❌ `.venv/` - Virtual environment
- ❌ `.env` - User environment file
- ❌ `config/*_credentials.json` - Credential files
- ❌ `data/csv_source/*.csv` - User data
- ❌ `data/job_tags.json` - User data
- ❌ `logs/*.log` - Log files
- ❌ `.cursor/` - Internal notes

## GitHub Releases Setup (Recommended)

### Create Release Process:

1. **Tag a version**:
   ```bash
   git tag -a v1.0.0 -m "Initial release"
   git push origin v1.0.0
   ```

2. **Create GitHub Release**:
   - Go to GitHub → Releases → Draft new release
   - Select tag `v1.0.0`
   - Add release notes
   - GitHub auto-creates source code zip

3. **Installer Downloads**:
   - Installer can download: `https://github.com/Revenant222/job_search/archive/refs/tags/v1.0.0.zip`
   - Or latest: `https://github.com/Revenant222/job_search/archive/refs/heads/main.zip`

## Testing Checklist

Before installer can work properly:

- [ ] Repository clones successfully
- [ ] All files needed for app are present
- [ ] `requirements.txt` installs without errors
- [ ] App runs after fresh clone + venv setup
- [ ] `.env.example` exists and is complete
- [ ] Run script (`run_app.bat`) works
- [ ] No sensitive data in repo
- [ ] Documentation is complete

## Summary

**Minimum Required**:
1. ✅ Create `.env.example` file
2. ✅ Ensure repo is accessible (public or releases)
3. ✅ Verify `.gitignore` excludes sensitive files
4. ✅ Test that fresh clone works

**Nice to Have**:
- Version file (`VERSION.txt` or `src/__init__.py`)
- Installer config file (`installer_config.json`)
- GitHub Releases set up
- Updated README with installer instructions

The installer approach (publishing + automated setup) means you don't need to package Streamlit - users will have Python installed and run Streamlit normally, just with automated setup.

